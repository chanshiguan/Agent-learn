"""Stage 6 练习 3：Chunking 对照 — 3 种切法 A/B（纯 Python、$0）。

同一份文件 → 3 种切法：
  1. fixed-length（每 N 字一段、可加 overlap）
  2. paragraph-based（按段落切、保语义完整）
  3. heading-aware（看 # / ## 切、保章节 hierarchy）

对 5 个真实 query 比较 top-k 结果、看哪种切法捞到正确 context。

运行方法：
    pip install -r requirements.txt
    python starter.py

验证：
    python test.py
"""

# 同一资料用固定长度、段落、标题三种切法，观察证据是否被切断。

from __future__ import annotations

import re
import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


# 范例 markdown 文件（含 heading + paragraph）
SAMPLE_DOC = """# 台北旅行教学样本

## 饮食

台北以夜市闻名。士林夜市有臭豆腐和珍珠奶茶摊位。常见早餐包括蛋饼，以及搭配热豆浆的油条。

台北有不少精品咖啡店，例如 Fika Fika 和 GABEE。本教学样本中的价格为每杯约 150–250 新台币，不代表实时售价。

## 交通

台北捷运覆盖许多游览区域，可以使用悠游卡支付。本教学样本中的单程票价为 20–65 新台币；公交车通常较便宜，但可能较慢。

YouBike 是当地的共享单车服务。本教学样本使用每 30 分钟 10 新台币的固定费用。

## 天气

台北夏季炎热潮湿，样本温度为 32–35 摄氏度，并有午后雷雨；冬季样本温度为 15–20 摄氏度，可能连续下雨。样本文本建议在 10–11 月或 3–4 月游览。
"""


# === 3 个 chunking strategy ===

# 固定窗口依次切分；overlap 必须小于窗口大小，确保每轮都向前推进。
def chunk_fixed(text: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    """固定长度切（with overlap）。简单但会切坏句子 / 段落。"""
    if chunk_size < 1:
        raise ValueError("chunk_size 必须至少是 1")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap 必须介于 0 和 chunk_size - 1 之间")
    chunks = []
    i = 0
    # 每轮前进 chunk_size − overlap 个字符，保留相邻窗口的重叠；这里按字符切，不是按模型 token 切。
    while i < len(text):
        chunks.append(text[i:i + chunk_size])
        i += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]


# 按空行分段，尽量保留自然段内的条件与说明。
def chunk_paragraphs(text: str) -> list[str]:
    """按段落切（双 newline 为界）。保语义完整、但段落长短不一。"""
    return [p.strip() for p in text.split("\n\n") if p.strip()]


# 以 Markdown 标题作为结构边界，不依赖语义模型判断断点。
def chunk_headings(text: str) -> list[str]:
    """Heading-aware：按 # / ## 切、每个 section 含 heading + body、有 hierarchy 标记。"""
    sections = re.split(r"\n(?=#{1,3} )", text)
    return [s.strip() for s in sections if s.strip()]


# === 比较不同检索结果 ===

# 对当前切法得到的片段编码；换切法后需要重新生成对应向量。
def embed_chunks(chunks: list[str], model: Any) -> np.ndarray:
    # normalize_embeddings：把向量长度归一为 1，因此后面可以直接用点积计算余弦相似度，减少长度带来的干扰。
    # convert_to_numpy：让编码结果直接成为 NumPy 数组，后续矩阵点积和排序使用同一套数值运算。
    return model.encode(chunks, normalize_embeddings=True, convert_to_numpy=True)


def top_k_for_query(query: str, chunks: list[str], chunk_vecs: np.ndarray,
                    model: Any, k: int = 2) -> list[dict]:
    # 把单个问题编码为与语料同维度的向量；取第 0 项是因为编码接口接收的是一批文本。
    # normalize_embeddings：把向量长度归一为 1，因此后面可以直接用点积计算余弦相似度，减少长度带来的干扰。
    # convert_to_numpy：让编码结果直接成为 NumPy 数组，后续矩阵点积和排序使用同一套数值运算。
    q_vec = model.encode([query], normalize_embeddings=True, convert_to_numpy=True)[0]
    # 已归一化的语料与查询做点积，得到余弦相似度；它表示相关程度，不是答案正确的概率。
    sims = chunk_vecs @ q_vec
    # 按相似度由高到低取候选下标；argsort 默认升序，因此对分数取负后再排序。
    top_idx = np.argsort(-sims)[:k]
    return [{"chunk": chunks[i], "similarity": float(sims[i])} for i in top_idx]


# 固定文档和问题后比较各切法，避免同时改多个变量。
def compare_strategies(doc: str, queries: list[str], k: int = 2, model: Any = None) -> dict:
    """3 种 chunking、跑同样 query、返回对比结果。"""
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(EMBED_MODEL)

    strategies = {
        "fixed_200_overlap_40": chunk_fixed(doc, chunk_size=200, overlap=40),
        "paragraphs": chunk_paragraphs(doc),
        "headings": chunk_headings(doc),
    }

    results = {}
    for name, chunks in strategies.items():
        vecs = embed_chunks(chunks, model)
        per_query = []
        for q in queries:
            per_query.append({"query": q, "top": top_k_for_query(q, chunks, vecs, model, k=k)})
        results[name] = {"chunk_count": len(chunks), "queries": per_query}
    return results


if __name__ == "__main__":
    queries = [
        "夜市有哪些食物可以尝试？",
        "捷运票价是多少？",
        "一年中什么时间适合游览？",
        "如何使用共享单车？",
        "有哪些咖啡馆？",
    ]
    print("文档：台北旅行教学样本（三个二级标题）")
    print(f"查询问题：{len(queries)}\n")

    out = compare_strategies(SAMPLE_DOC, queries, k=2)
    for name, data in out.items():
        print(f"=== {name} ({data['chunk_count']} 个片段）===")
        for entry in data["queries"]:
            best = entry["top"][0]
            print(f"   Q: {entry['query']}")
            print(f"   → 相似度={best['similarity']:.3f}: {best['chunk'][:80]}...")
        print()

    # === 自我验证 ===
    assert out["headings"]["chunk_count"] <= 5, "heading chunks 应该少而 self-contained"
    assert set(out) == {"fixed_200_overlap_40", "paragraphs", "headings"}
    print("✅ 练习 3 通过 — 3 种 chunking 对照、$0/run")
    print("   观察：heading-aware 对 sectional query 最准；fixed-length 容易切坏句子")
