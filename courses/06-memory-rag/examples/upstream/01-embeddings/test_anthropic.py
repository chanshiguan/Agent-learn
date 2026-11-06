"""Stage 6 练习 1 — Path B 载入检查 + OpenAI mock 对照。

运行方法：
    python test_anthropic.py
"""

# 本组测试围绕以下行为检查正反例：先编码语料和查询，再按余弦相似度排名；同一空间的向量才可以比较。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np

from starter_anthropic import embed_openai


def test_embed_openai_with_mock():
    """Mock OpenAI client、确认 embed_openai 正确 normalize。"""
    fake_embeddings = [
        SimpleNamespace(embedding=[1.0, 0.0, 0.0]),
        SimpleNamespace(embedding=[0.0, 2.0, 0.0]),
    ]
    client = MagicMock()
    client.embeddings.create.return_value = SimpleNamespace(data=fake_embeddings)

    vecs = embed_openai(["a", "b"], client=client)
    # 归一化后两组向量的长度都应接近 1；这是后续用点积比较余弦相似度的前提
    assert abs(np.linalg.norm(vecs[0]) - 1.0) < 1e-6
    assert abs(np.linalg.norm(vecs[1]) - 1.0) < 1e-6
    print("✅ test_embed_openai_with_mock")


def test_starter_anthropic_loadable():
    import starter_anthropic
    assert hasattr(starter_anthropic, "MODEL")
    print("✅ test_starter_anthropic_loadable")


if __name__ == "__main__":
    test_embed_openai_with_mock()
    test_starter_anthropic_loadable()
    print("\n🎉 通过 — Path B 可载入 + normalize 正确")
