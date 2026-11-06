"""Stage 6 练习 1：Embeddings — Path A（本机 sentence-transformers、$0）。

把 100 个句子转成 vector、查 nearest neighbors。理解 cosine similarity / distance。

运行方法：
    pip install -r requirements.txt
    python starter.py   # 第一次会自动下载 model (需要下载多语言模型权重)

验证：
    python test.py

预算：$0（model 跑在 CPU）。Path B 用 cloud embedding（OpenAI / Voyage）见 starter_anthropic.py。
"""

# 先编码语料和查询，再按余弦相似度排名；同一空间的向量才可以比较。

from __future__ import annotations

import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


SENTENCES = [
    "猫坐在垫子上。",
    "一只狗正在公园里追球。",
    "台北位于台湾地区。",
    "Python 是一种编程语言。",
    "机器学习模型从数据中学习规律。",
    "神经网络的部分设计受到生物神经系统的启发。",
    "台北的一些咖啡馆提供手冲咖啡。",
    "JavaScript 可以在网页浏览器中运行。",
    "天气预报说，明天会下雨。",
    "猫和狗都是常见的家庭宠物。",
] + [f"无关的填充样本，编号 {i}." for i in range(90)]


# 使用同一模型编码所有文本；首次加载可能下载权重。
def embed(texts: list[str], model: Any = None) -> np.ndarray:
    """将一批文本编码为 L2 归一化向量，便于直接用点积比较余弦相似度。"""
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL_NAME)
    # normalize_embeddings：把向量长度归一为 1，因此后面可以直接用点积计算余弦相似度，减少长度带来的干扰。
    # convert_to_numpy：让编码结果直接成为 NumPy 数组，后续矩阵点积和排序使用同一套数值运算。
    return model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)


# 查询和语料都编码后按相似度排序，top_k 控制最多取多少条。
def find_nearest(query: str, sentences: list[str], top_k: int = 3, model: Any = None) -> list[dict]:
    """返回余弦相似度最高的 top_k 个句子，同时保留分数与名次。"""
    if top_k < 1:
        raise ValueError("top_k 必须至少是 1")
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL_NAME)
    # 语料向量表示待比较的候选句子；必须与查询使用同一编码器，否则点积没有可比意义。
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    sent_vecs = embed(sentences, model=model)
    # 把单个问题编码为与语料同维度的向量；取第 0 项是因为编码接口接收的是一批文本。
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    q_vec = embed([query], model=model)[0]
    # 前面已将向量归一化，所以点积就是余弦相似度；它不是答案正确率
    # 每条语料向量与查询做点积；前面已归一化，所以这里就是余弦相似度，分数越高表示方向越接近。
    sims = sent_vecs @ q_vec
    # 按相似度由高到低取候选下标；argsort 默认升序，因此对分数取负后再排序。
    top_idx = np.argsort(-sims)[:top_k]
    return [
        {"sentence": sentences[i], "similarity": float(sims[i]), "rank": int(rank)}
        for rank, i in enumerate(top_idx, 1)
    ]


if __name__ == "__main__":
    query = "我喜欢用 Python 编程"
    print(f"❓ 问题：{query}")
    print(f"   使用 {MODEL_NAME} 编码 {len(SENTENCES)} 条句子……")
    print("-" * 60)

    results = find_nearest(query, SENTENCES, top_k=5)
    for r in results:
        print(f"   #{r['rank']} 相似度={r['similarity']:.3f}: {r['sentence']}")

    # === 自我验证 ===
    # 下面第一行检查首名是否与编程有关；第二行提供失败消息，带回实际命中的句子。
    assert "Python" in results[0]["sentence"] or "programming" in results[0]["sentence"].lower(), \
        f"预期 top-1 跟 programming 相关、得到 {results[0]['sentence']}"
    assert len(results) == 5, f"预期 5 条结果、得到 {len(results)}"
    print("\n✅ 练习 1 通过 — sentence-transformers 在本机跑通、$0/run")
    print("   观察：cosine similarity 越高、语义越近")
