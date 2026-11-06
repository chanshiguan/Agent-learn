"""Stage 6 练习 1 自我验证 — 不下载 model、用 mock。

运行方法：
    python test.py

验证内容：
    - find_nearest 排序正确（相关句子 sim 最高）
    - L2-normalized vector 的 dot product = cosine similarity
    - top_k 边界
"""

# 本组测试围绕以下行为检查正反例：先编码语料和查询，再按余弦相似度排名；同一空间的向量才可以比较。

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np

from starter import SENTENCES, find_nearest


def make_fake_model(vec_map: dict) -> MagicMock:
    """Mock SentenceTransformer：给定 text → vec 对应表。"""
    m = MagicMock()
    def encode(texts, **kw):
        out = np.array([vec_map.get(t, np.zeros(4)) for t in texts])
        # Normalize（模拟 normalize_embeddings=True）
        # 计算每条向量自身的长度，归一化后比较方向而不是长度；零向量要单独防止除零。
        # axis：指定沿哪一个维度计算；对每条向量分别计算长度时使用行维度，避免把整批数据混成一个值。
        # keepdims：保留长度为 1 的维度，使归一化时能按行广播相除，不会错配不同文本的向量。
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        # 零向量没有方向；将除数临时设为 1 可保持其仍为零，避免归一化产生 NaN 干扰排序。
        norms[norms == 0] = 1.0
        return out / norms
    m.encode.side_effect = encode
    return m


def test_top_1_is_most_similar():
    """构造 4 个 sentence、其中第 2 个跟 query 完全同向、应排第 1。"""
    sentences = ["a", "b", "c", "d"]
    # 故意做：b 跟 query 同向（→ similarity 1.0）
    vecs = {
        "a": np.array([1, 0, 0, 0], dtype=float),
        "b": np.array([0, 1, 0, 0], dtype=float),
        "c": np.array([0, 0, 1, 0], dtype=float),
        "d": np.array([0, 0, 0, 1], dtype=float),
        '查询样本 b': np.array([0, 1, 0, 0], dtype=float),
    }
    model = make_fake_model(vecs)
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    results = find_nearest('查询样本 b', sentences, top_k=2, model=model)
    assert results[0]["sentence"] == "b"
    assert results[0]["similarity"] == 1.0
    print("✅ test_top_1_is_most_similar")


def test_top_k_respected():
    sentences = ["a", "b", "c", "d", "e"]
    vecs = {s: np.random.rand(4) for s in sentences + ["q"]}
    model = make_fake_model(vecs)
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    results = find_nearest("q", sentences, top_k=3, model=model)
    assert len(results) == 3
    assert {r["rank"] for r in results} == {1, 2, 3}
    print("✅ test_top_k_respected")


def test_top_k_must_be_positive():
    model = make_fake_model({"a": np.array([1, 0]), "q": np.array([1, 0])})
    try:
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        find_nearest("q", ["a"], top_k=0, model=model)
    except ValueError as exc:
        assert "top_k" in str(exc)
    else:
        raise AssertionError("top_k=0 应该被拒绝")
    print("✅ test_top_k_must_be_positive")


def test_similarity_in_minus_one_to_one():
    """检查 L2 归一化后的余弦相似度是否落在 [-1, 1] 范围内。"""
    sentences = ["a", "b"]
    vecs = {
        "a": np.array([1, 0, 0, 0], dtype=float),
        "b": np.array([-1, 0, 0, 0], dtype=float),
        "q": np.array([1, 0, 0, 0], dtype=float),
    }
    model = make_fake_model(vecs)
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    results = find_nearest("q", sentences, top_k=2, model=model)
    # 已归一化的语料与查询做点积，得到余弦相似度；它表示相关程度，不是答案正确的概率。
    sims = [r["similarity"] for r in results]
    assert all(-1.0 - 1e-6 <= s <= 1.0 + 1e-6 for s in sims), f"sim 越界: {sims}"
    print("✅ test_similarity_in_minus_one_to_one")


def test_corpus_size():
    """SENTENCES corpus 应该有 100 个。"""
    assert len(SENTENCES) == 100, f"预期 100 个句子、得到 {len(SENTENCES)}"
    print("✅ test_corpus_size")


if __name__ == "__main__":
    test_top_1_is_most_similar()
    test_top_k_respected()
    test_top_k_must_be_positive()
    test_similarity_in_minus_one_to_one()
    test_corpus_size()
    print("\n🎉 全部通过 — embedding 逻辑正确（无需下载 model）")
