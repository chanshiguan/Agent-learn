"""Stage 7 练习 3 — Anthropic mock test。"""

# 本组测试围绕以下行为检查正反例：一次任务对应 trace，内部步骤对应 span；同时记录耗时、错误与模型报告用量。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import TraceContext
from starter_anthropic import observable_agent_anthropic


def test_observable_anthropic_records_provider_tokens():
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="42")],
        usage=SimpleNamespace(input_tokens=15, output_tokens=2),
    )
    ctx = TraceContext("req_1")
    out = observable_agent_anthropic("2+2?", ctx, client=client)
    assert "42" in out
    assert ctx.total_tokens["input"] == 15
    assert ctx.total_tokens["output"] == 2
    print("✅ test_observable_anthropic_records_provider_tokens")


def test_observable_anthropic_records_empty_output_as_error():
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(
        content=[], usage=SimpleNamespace(input_tokens=1, output_tokens=0)
    )
    ctx = TraceContext("req_empty")
    try:
        observable_agent_anthropic("2+2?", ctx, client=client)
    except ValueError as error:
        assert "空文本" in str(error)
    else:
        raise AssertionError("empty model output must fail")
    assert ctx.summary()["error_count"] == 1
    print("✅ test_observable_anthropic_records_empty_output_as_error")


if __name__ == "__main__":
    test_observable_anthropic_records_provider_tokens()
    test_observable_anthropic_records_empty_output_as_error()
    print("\n🎉 通过")
