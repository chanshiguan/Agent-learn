"""Stage 7 练习 4 — Anthropic streaming + cached_query mock."""

# 本组测试围绕以下行为检查正反例：流式片段要收齐并检查结束；缓存收益需看实际 usage，不能从配置存在推断。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter_anthropic import build_cache_demo_prompt, cached_query, stream_anthropic


def test_stream_anthropic_yields_text():
    """模拟 Anthropic 流式上下文管理器，测试读取与关闭流程而不请求真实服务。"""
    stream_obj = MagicMock()
    stream_obj.text_stream = iter(['你好', "，世界"])
    stream_obj.__enter__ = MagicMock(return_value=stream_obj)
    stream_obj.__exit__ = MagicMock(return_value=False)

    client = MagicMock()
    client.messages.stream.return_value = stream_obj

    out = list(stream_anthropic('你好', client=client))
    assert out == ['你好', "，世界"]
    print("✅ test_stream_anthropic_yields_text")


def test_stream_anthropic_rejects_whitespace_only_chunks():
    stream_obj = MagicMock()
    stream_obj.text_stream = iter([" ", "\t"])
    stream_obj.__enter__ = MagicMock(return_value=stream_obj)
    stream_obj.__exit__ = MagicMock(return_value=False)
    client = MagicMock()
    client.messages.stream.return_value = stream_obj

    try:
        # 生成列表：stream_anthropic('hi', client=client)。
        list(stream_anthropic('你好', client=client))
    except ValueError as error:
        assert "空文本" in str(error)
    else:
        raise AssertionError("whitespace-only stream must fail")
    print("✅ test_stream_anthropic_rejects_whitespace_only_chunks")


def test_cached_query_passes_cache_control():
    """确认 cache_control 真的传进去 system param。"""
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="ok")],
        usage=SimpleNamespace(
            input_tokens=10, output_tokens=2,
            cache_creation_input_tokens=2000, cache_read_input_tokens=0,
        ),
    )
    result = cached_query("Q?", "较长的系统提示词", client=client)
    call_kwargs = client.messages.create.call_args.kwargs
    system_arg = call_kwargs["system"]
    assert isinstance(system_arg, list)
    assert system_arg[0]["cache_control"] == {"type": "ephemeral"}
    assert result["cache_creation_input_tokens"] == 2000
    print("✅ test_cached_query_passes_cache_control")


def test_cache_demo_is_deliberately_long():
    prompt = build_cache_demo_prompt()
    # 中文没有用空格分词；这里仅检查前缀足够长，不把字符数冒充服务的 token 数。
    assert len(prompt) > 20000
    print("✅ test_cache_demo_is_deliberately_long")


def test_cached_query_rejects_empty_text():
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(
        content=[],
        usage=SimpleNamespace(
            input_tokens=10,
            output_tokens=0,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        ),
    )
    try:
        cached_query("Q?", build_cache_demo_prompt(), client=client)
    except ValueError as error:
        assert "空文本" in str(error)
    else:
        raise AssertionError("empty cached response must fail")
    print("✅ test_cached_query_rejects_empty_text")


if __name__ == "__main__":
    test_stream_anthropic_yields_text()
    test_stream_anthropic_rejects_whitespace_only_chunks()
    test_cached_query_passes_cache_control()
    test_cache_demo_is_deliberately_long()
    test_cached_query_rejects_empty_text()
    print("\n🎉 通过 — streaming + caching API contract 正确")
