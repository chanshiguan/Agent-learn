"""Stage 6 练习 1：Embeddings — Path B（cloud embedding 对照）。

Anthropic 没提供官方 embedding API、官方推荐 Voyage AI。OpenAI 也是常见选择。
这份示范用 OpenAI 的 text-embedding-3-small 对照本机 sentence-transformers。

运行方法：
    pip install -r requirements.txt
    export OPENAI_API_KEY=sk-...    # OR set VOYAGE_API_KEY
    python starter_anthropic.py

预算：每次 ≈ $0.00002 per 100 sentences（text-embedding-3-small）。极便宜。
但**对 RAG demo / 个人实验，本机 sentence-transformers 完全够用**——cloud embedding 主要差别在 multilingual 跟 long-context 场景。
"""

# 先编码语料和查询，再按余弦相似度排名；同一空间的向量才可以比较。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import os
import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np

MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")


# 这个路径调用 OpenAI 的 embedding 服务；文件名中的 Anthropic 不代表它提供了向量接口。
def embed_openai(texts: list[str], client: Any = None) -> np.ndarray:
    """通过已配置的 Embedding 接口取得向量；响应顺序对应输入顺序。"""
    from openai import OpenAI
    client = client or OpenAI()
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    resp = client.embeddings.create(model=MODEL, input=texts)
    vecs = np.array([d.embedding for d in resp.data])
    # 按行归一化，后续点积才表示余弦相似度，而不是同时受向量长度影响
    # 计算每条向量自身的长度，归一化后比较方向而不是长度；零向量要单独防止除零。
    # axis：指定沿哪一个维度计算；对每条向量分别计算长度时使用行维度，避免把整批数据混成一个值。
    # keepdims：保留长度为 1 的维度，使归一化时能按行广播相除，不会错配不同文本的向量。
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / norms


# 云端生成向量后仍要计算相似度并排序，比较规则与本地路径一致。
def find_nearest_openai(query: str, sentences: list[str], top_k: int = 3) -> list[dict]:
    from openai import OpenAI
    client = OpenAI()
    # 语料向量表示待比较的候选句子；必须与查询使用同一编码器，否则点积没有可比意义。
    sent_vecs = embed_openai(sentences, client=client)
    # 把单个问题编码为与语料同维度的向量；取第 0 项是因为编码接口接收的是一批文本。
    q_vec = embed_openai([query], client=client)[0]
    # 每条语料向量与查询做点积；前面已归一化，所以这里就是余弦相似度，分数越高表示方向越接近。
    sims = sent_vecs @ q_vec
    # 按相似度由高到低取候选下标；argsort 默认升序，因此对分数取负后再排序。
    top_idx = np.argsort(-sims)[:top_k]
    return [
        {"sentence": sentences[i], "similarity": float(sims[i]), "rank": int(rank)}
        for rank, i in enumerate(top_idx, 1)
    ]


if __name__ == "__main__":
    from starter import SENTENCES
    query = "我喜欢用 Python 编程"
    print(f"❓ 问题：{query}（使用 OpenAI {MODEL}）")
    print("-" * 60)
    results = find_nearest_openai(query, SENTENCES, top_k=5)
    for r in results:
        print(f"   #{r['rank']} 相似度={r['similarity']:.3f}: {r['sentence']}")
    # === 自我验证 ===
    assert len(results) == 5, f"预期 5 条结果、得到 {len(results)}"
    assert results[0]["similarity"] >= results[-1]["similarity"], "结果应由相似到不相似排序"
    print("\n✅ 练习 1 (Path B cloud) 通过 — OpenAI embeddings 返回正常")
    print("   对照本机版本（starter.py）、看 ranking 差异")
