"""Stage 6 练习 2：Vector DB（ChromaDB）— Path A（本机、$0）。

把 embedding 存进 Chroma、做 semantic query、对照 keyword search。

运行方法：
    pip install -r requirements.txt
    python starter.py

验证：
    python test.py

预算：$0。Chroma 跑在本机 SQLite 后端、规模到万笔都 OK。
"""

# 先建立 collection 并写入资料，再比较字词与向量查询；保留 ID 才能回到原记录。

from __future__ import annotations

import sys
import uuid
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOCS = [
    {"id": "1", "text": "台北是台湾地区的城市，以夜市和科技产业闻名。", "category": "city"},
    {"id": "2", "text": "Python 是一种使用动态类型的高级编程语言。", "category": "tech"},
    {"id": "3", "text": "台北的一些咖啡馆使用单一产地咖啡豆制作手冲咖啡。", "category": "food"},
    {"id": "4", "text": "机器学习模型从训练数据中学习规律。", "category": "tech"},
    {"id": "5", "text": "台湾地区的夜市供应臭豆腐等街头小吃。", "category": "food"},
    {"id": "6", "text": "JavaScript 常用于网页前端开发。", "category": "tech"},
    {"id": "7", "text": "东京是日本的首都；本例使用约 1400 万的固定人口样本。", "category": "city"},
    {"id": "8", "text": "神经网络通过多层带权重的连接处理输入。", "category": "tech"},
]


# 创建本题要用的资料集合；检查客户端种类，区分内存数据与持久数据。
def build_collection(
    path: str = ":memory:",
    collection_name: str | None = None,
    *,
    client: Any = None,
    embedding_function: Any = None,
) -> Any:
    """建立 / 取回 chroma collection。path=':memory:' 表 in-memory。"""
    if client is None:
        import chromadb
        client = (
            chromadb.EphemeralClient()
            if path == ":memory:"
            else chromadb.PersistentClient(path=path)
        )
    if embedding_function is None:
        from chromadb.utils import embedding_functions
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            # model_name：选择文本编码模型；入库文档和查询必须用同一种编码方式，不能混用不同模型产生的向量。
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )
    if collection_name is None:
        # 集合名决定资料隔离与复用范围；独立实验不能误用另一次实验留下的索引。
        collection_name = (
            f"stage06_demo_{uuid.uuid4().hex[:8]}"
            if path == ":memory:"
            else "stage06_demo_zh"
        )
    # 按名称取得集合，不存在时创建；是否复用由 collection_name 决定，编码函数必须与已有索引一致。
    collection = client.get_or_create_collection(
        # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
        name=collection_name, embedding_function=embedding_function,
    )
    return collection


# 写入时把文档内容与 ID 对应起来，后面查询才能知道命中了哪份资料。
def index_docs(collection: Any, docs: list[dict]) -> None:
    """批量写入文档，使用稳定 ID 把正文和元数据关联起来。"""
    # 先确认集合中有多少记录，用于处理空库和限制返回数量，避免对空索引盲目查询。
    if collection.count() > 0:
        # 先排除已有 ID，避免同一批文档重跑时触发重复写入或警告
        # 先读取已存在的标识或记录，避免重跑示例时重复写入同一资料。
        existing = set(collection.get()["ids"])
        # 只把尚未存在的记录交给写入步骤，使同一输入重跑时不重复增加资料。
        new = [d for d in docs if d["id"] not in existing]
    else:
        # 只把尚未存在的记录交给写入步骤，使同一输入重跑时不重复增加资料。
        new = docs
    if not new:
        return
    collection.add(
        # ids：为每条记录保留稳定标识，便于去重、更新和回查来源；不要只保存脱离原文的向量。
        ids=[d["id"] for d in new],
        # documents：把可供人核对的原文与向量一起保存，生成答案时才能拿到证据，而不只是一个相似度分数。
        documents=[d["text"] for d in new],
        # metadatas：保存分类或权限等辅助信息，供检索过滤与追溯使用；元数据存在不代表过滤已自动生效。
        metadatas=[{"category": d["category"]} for d in new],
    )


# 向量相似性用于找相关候选，返回候选不等于已经回答问题。
def semantic_query(collection: Any, query: str, top_k: int = 3) -> list[dict]:
    """通过向量检索返回相关文档，并保留 ID 方便回查来源。"""
    # 把单个问题作为一项批量查询，取 top_k 个候选；检索只返回资料，不会自动生成或验证答案。
    result = collection.query(query_texts=[query], n_results=top_k)
    return [
        {"id": result["ids"][0][i], "text": result["documents"][0][i],
         "distance": result["distances"][0][i]}
        for i in range(len(result["ids"][0]))
    ]


# 按字面词匹配作为对照，观察与向量检索的不同。
def keyword_query(docs: list[dict], query: str, top_k: int = 3) -> list[dict]:
    """简化 keyword search（substring match、无 BM25）。"""
    q = query.lower()
    matches = [d for d in docs if any(w in d["text"].lower() for w in q.split() if len(w) >= 2)]
    return matches[:top_k]


if __name__ == "__main__":
    print("正在建立内存中的 Chroma 集合……")
    collection = build_collection()
    index_docs(collection, DOCS)
    # 先确认集合中有多少记录，用于处理空库和限制返回数量，避免对空索引盲目查询。
    print(f"   已写入资料条数：{collection.count()} 条。\n")

    query = "在亚洲城市哪里能喝到好咖啡"
    print(f"❓ 问题：{query}")
    print("-" * 60)

    print("\n🔍 向量检索：")
    for r in semantic_query(collection, query, top_k=3):
        print(f"   d={r['distance']:.3f} [{r['id']}] {r['text']}")

    print("\n📝 关键词检索（子串匹配）：")
    for r in keyword_query(DOCS, query, top_k=3):
        print(f"   [{r['id']}] {r['text']}")

    # === 自我验证 ===
    sem_top = semantic_query(collection, query, top_k=1)
    assert sem_top[0]["id"] in {"3", "1"}, f"预期 coffee 或 Taipei 句、得到 {sem_top[0]}"
    # 先确认集合中有多少记录，用于处理空库和限制返回数量，避免对空索引盲目查询。
    assert collection.count() == len(DOCS), "每份文件应只存一次"
    print("\n✅ 练习 2 通过 — Chroma vector DB 跑通、$0/run")
    print("   观察：query 没「coffee」字眼、keyword 漏；semantic 抓得到")
