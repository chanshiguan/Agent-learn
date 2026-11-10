"""真实 Embedding 与持久 Qdrant；模型缓存和索引版本分别记录。"""
import os
import uuid
from functools import lru_cache
from contextlib import closing

from .files import data_dir, digest, load, save
from .corpus import visible

MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODEL_REVISION = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"


@lru_cache(maxsize=1)
def encoder():
    from sentence_transformers import SentenceTransformer
    # CPU 是两种生成模型路线共同的起点；首次会下载权重，不能当作离线已准备好。
    # 显式指定公开仓库提交，不依赖库的私有配置字段，也不跟随会移动的 main。
    return SentenceTransformer(MODEL, revision=MODEL_REVISION, device="cpu", cache_folder=str(data_dir() / "models"))


def embed(texts):
    model = encoder()
    lengths = [len(model.tokenizer.encode(t, add_special_tokens=True)) for t in texts]
    if any(length > model.max_seq_length for length in lengths):
        raise ValueError(f"片段超过 Embedding 的 {model.max_seq_length} token 窗口，请减小切块；不静默截断。")
    return model.encode(texts, batch_size=8, normalize_embeddings=True).tolist()


def connection():
    from qdrant_client import QdrantClient
    # 离线单元测试可明确选择 local；课程第 10 章默认连接真实 Qdrant 服务。
    if os.environ.get("QDRANT_MODE") == "local":
        return closing(QdrantClient(path=str(data_dir() / "qdrant-local")))
    return closing(QdrantClient(url=os.environ.get("QDRANT_URL", "http://127.0.0.1:6333"),
                        api_key=os.environ.get("QDRANT_API_KEY") or None, timeout=30))


def build_index():
    from qdrant_client import models
    corpus = load("corpus.json")
    if not corpus:
        raise ValueError("先整理 corpus.json。")
    encoder()
    # 加载时已锁定这个提交；缓存与查询必须使用相同版本，升级需要明确改值并重建。
    revision = MODEL_REVISION
    identity = digest([MODEL, revision])[:12]
    cache = load(f"embedding-cache-{identity}.json", {})
    vectors = []
    new_count = 0
    for chunk in corpus["chunks"]:
        key = digest(chunk["text"])
        if key not in cache:
            cache[key] = embed([chunk["text"]])[0]
            new_count += 1
        vectors.append(cache[key])
    save(f"embedding-cache-{identity}.json", cache)
    name = f"reading_{corpus['revision'][:12]}_{identity}"
    with connection() as db:
        if not db.collection_exists(name):
            db.create_collection(name, vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE))
        for start in range(0, len(vectors), 32):
            points = [models.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL, c["id"])), vector=v, payload=c)
                      for c, v in zip(corpus["chunks"][start:start + 32], vectors[start:start + 32])]
            db.upsert(name, points=points, wait=True)
        if db.count(name, exact=True).count != len(vectors):
            raise ValueError("索引条数不符，不切换活动版本。")
    # 新集合完整后才发布指针。旧集合保留用于回滚；清理需要显式维护操作。
    index = {"collection": name, "corpus_revision": corpus["revision"], "model": MODEL,
             "model_revision": revision, "dimension": len(vectors[0]), "count": len(vectors), "new_embeddings": new_count}
    save("index.json", index)
    return index


def semantic_search(question, tenant, book, progress=None, k=5):
    from qdrant_client import models
    index, corpus = load("index.json"), load("corpus.json")
    if not index or not corpus or index["corpus_revision"] != corpus["revision"]:
        raise ValueError("活动索引与资料版本不一致，请完成索引构建；不返回旧版证据。")
    if index["model"] != MODEL or index["model_revision"] != MODEL_REVISION:
        raise ValueError("Embedding 版本已变，必须重建索引。")
    required = [models.FieldCondition(key="tenant", match=models.MatchValue(value=tenant)),
                models.FieldCondition(key="book", match=models.MatchValue(value=book))]
    if progress is not None:
        required += [models.FieldCondition(key="range_reviewed", match=models.MatchValue(value=True)),
                     models.FieldCondition(key="range_end", range=models.Range(lte=progress))]
    with connection() as db:
        points = db.query_points(index["collection"], query=embed([question])[0],
                                 query_filter=models.Filter(must=required), limit=k, with_payload=True).points
    # 不同存储后端对布尔值和数字的比较可能不同；以当前资料的权限规则再次核对。
    # 正文也从当前快照取得，避免旧索引载荷绕过已修订的阅读范围。
    allowed = {c["id"]: c for c in visible(corpus["chunks"], tenant, book, progress)}
    return [{**allowed[p.payload["id"]], "score": p.score} for p in points if p.payload.get("id") in allowed]


def fuse(first, second, k=5):
    scores, items = {}, {}
    for result in (first, second):
        for position, item in enumerate(result, 1):
            items[item["id"]] = item
            scores[item["id"]] = scores.get(item["id"], 0) + 1 / (60 + position)
    return [{**items[key], "score": scores[key]} for key in sorted(scores, key=lambda x: (-scores[x], x))[:k]]
