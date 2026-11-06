"""Stage 6 练习 4 — Path B 自我验证（mock Anthropic client）。
"""

# 本组测试围绕以下行为检查正反例：索引阶段读取和切分资料，查询阶段先检索后生成；这是原题的基础管线。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter_anthropic import generate_anthropic


def make_anthropic_client(answer: str):
    client = MagicMock()
    block = SimpleNamespace(type="text", text=answer)
    client.messages.create.return_value = SimpleNamespace(content=[block])
    return client


def test_generate_anthropic_uses_context():
    client = make_anthropic_client("Python 3.11+.")
    answer = generate_anthropic("Python 版本要求是什么？", ["我们使用 Python 3.11 及以上版本。"], client=client)
    call_args = client.messages.create.call_args
    prompt = call_args.kwargs["messages"][0]["content"]
    assert "Python 3.11" in prompt
    assert answer == "Python 3.11+."
    print("✅ test_generate_anthropic_uses_context")


if __name__ == "__main__":
    test_generate_anthropic_uses_context()
    print("\n🎉 Path B mock test 通过")
