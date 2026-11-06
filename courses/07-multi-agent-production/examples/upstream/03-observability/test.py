"""Stage 7 练习 3 自我验证 — TraceContext + trace_span 逻辑。"""

# 本组测试围绕以下行为检查正反例：一次任务对应 trace，内部步骤对应 span；同时记录耗时、错误与模型报告用量。

from __future__ import annotations

import sys
import time
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import TraceContext, multi_step_agent, observable_agent, trace_span


def test_trace_context_basic():
    ctx = TraceContext("req_1")
    # 向 ctx 登记一个阶段的耗时与状态。
    ctx.add_span("test_span", 12.5, kind="test")
    # 向 ctx 累计服务报告的 token 用量。
    ctx.add_tokens(input_t=100, output_t=50)
    s = ctx.summary()
    assert s["span_count"] == 1
    assert s["input_tokens"] == 100
    assert s["output_tokens"] == 50
    assert s["total_latency_ms"] == 12.5
    print("✅ test_trace_context_basic")


def test_trace_span_records_latency():
    ctx = TraceContext("req_2")
    with trace_span(ctx, "sleep_10ms"):
        # 按指定秒数等待。
        time.sleep(0.01)
    assert ctx.spans[0]["latency_ms"] >= 5
    assert ctx.spans[0]["name"] == "sleep_10ms"
    print("✅ test_trace_span_records_latency")


def test_trace_span_records_error():
    ctx = TraceContext("req_3")
    secret = "sk-ant-secret-marker"
    with TestCase().assertLogs("agent.observability", level="INFO") as captured:
        try:
            with trace_span(ctx, "fail_span"):
                raise ValueError(secret)
        except ValueError:
            pass
    assert len(ctx.errors) == 1
    assert ctx.errors[0] == "fail_span: ValueError"
    assert ctx.spans[0].get("error") == "ValueError"
    assert secret not in repr(ctx.errors)
    assert secret not in repr(ctx.spans)
    assert secret not in "\n".join(captured.output)
    print("✅ test_trace_span_records_error")


def test_observable_agent_records_tokens():
    llm = MagicMock()
    msg = SimpleNamespace(content='你好')
    resp = SimpleNamespace(
        choices=[SimpleNamespace(message=msg)],
        usage=SimpleNamespace(prompt_tokens=20, completion_tokens=5),
    )
    llm.chat.completions.create.return_value = resp

    ctx = TraceContext("req_4")
    out = observable_agent("hi?", ctx, llm=llm)
    assert out == '你好'
    assert ctx.total_tokens["input"] == 20
    assert ctx.total_tokens["output"] == 5
    assert len(ctx.spans) == 1
    print("✅ test_observable_agent_records_tokens")


def test_observable_agent_records_empty_output_as_error():
    llm = MagicMock()
    llm.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=""))],
        usage=None,
    )
    ctx = TraceContext("req_empty")
    try:
        observable_agent("hi?", ctx, llm=llm)
    except ValueError as error:
        assert "空文本" in str(error)
    else:
        raise AssertionError("empty model output must fail")
    assert ctx.summary()["error_count"] == 1
    assert ctx.spans[0]["error"]
    print("✅ test_observable_agent_records_empty_output_as_error")


def test_multi_step_agent_has_multiple_spans():
    llm = MagicMock()
    msg = SimpleNamespace(content="42")
    resp = SimpleNamespace(
        choices=[SimpleNamespace(message=msg)],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=3),
    )
    llm.chat.completions.create.return_value = resp

    result = multi_step_agent("What's 2+2?", llm=llm)
    assert result["trace_summary"]["span_count"] >= 2  # search + llm_call
    print("✅ test_multi_step_agent_has_multiple_spans")


if __name__ == "__main__":
    test_trace_context_basic()
    test_trace_span_records_latency()
    test_trace_span_records_error()
    test_observable_agent_records_tokens()
    test_observable_agent_records_empty_output_as_error()
    test_multi_step_agent_has_multiple_spans()
    print("\n🎉 全部通过 — observability primitive 逻辑正确")
