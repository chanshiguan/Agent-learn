"""Stage 7 练习 4 自我验证 — streaming + stream_to_string。"""

# 本组测试围绕以下行为检查正反例：流式片段要收齐并检查结束；缓存收益需看实际 usage，不能从配置存在推断。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import stream_response, stream_to_string


def fake_streaming_llm(chunks: list[str]):
    """模拟可迭代的响应片段，用固定输入检查增量拼接。"""
    def make_chunk(delta):
        return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=delta))])
    llm = MagicMock()
    llm.chat.completions.create.return_value = iter([make_chunk(c) for c in chunks])
    return llm


def test_stream_response_yields_chunks():
    llm = fake_streaming_llm(['你好', " ", "world"])
    out = list(stream_response('你好', llm=llm))
    assert out == ['你好', " ", "world"]
    print("✅ test_stream_response_yields_chunks")


def test_stream_to_string_aggregates():
    llm = fake_streaming_llm(["a", "b", "c"])
    result = stream_to_string("q", llm=llm)
    assert result["text"] == "abc"
    assert result["chunk_count"] == 3
    print("✅ test_stream_to_string_aggregates")


def test_stream_to_string_skips_empty_deltas():
    """Streaming 偶尔有 None delta（initial / final chunk）、要 skip。"""
    def make_chunk(delta):
        return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=delta))])
    llm = MagicMock()
    llm.chat.completions.create.return_value = iter([
        make_chunk(None), make_chunk("a"), make_chunk(""), make_chunk("b"), make_chunk(None),
    ])
    result = stream_to_string("q", llm=llm)
    assert result["text"] == "ab"
    print("✅ test_stream_to_string_skips_empty_deltas")


def test_stream_rejects_an_all_empty_response():
    llm = fake_streaming_llm(["", None])
    try:
        # 生成列表：stream_response('q', llm=llm)。
        list(stream_response("q", llm=llm))
    except ValueError as error:
        assert "空文本" in str(error)
    else:
        raise AssertionError("empty stream must fail")
    print("✅ test_stream_rejects_an_all_empty_response")


def test_stream_rejects_whitespace_only_chunks():
    llm = fake_streaming_llm([" ", "\t"])
    try:
        # 生成列表：stream_response('q', llm=llm)。
        list(stream_response("q", llm=llm))
    except ValueError as error:
        assert "空文本" in str(error)
    else:
        raise AssertionError("whitespace-only stream must fail")
    print("✅ test_stream_rejects_whitespace_only_chunks")


if __name__ == "__main__":
    test_stream_response_yields_chunks()
    test_stream_to_string_aggregates()
    test_stream_to_string_skips_empty_deltas()
    test_stream_rejects_an_all_empty_response()
    test_stream_rejects_whitespace_only_chunks()
    print("\n🎉 全部通过 — streaming 逻辑正确")
