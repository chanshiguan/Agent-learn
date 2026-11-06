"""Stage 7 练习 5 — Anthropic FastAPI endpoint test。"""

# 本组测试围绕以下行为检查正反例：请求先过字段校验，再调用模型；健康检查、模型可用和答案正确分别验收。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import anthropic
from fastapi.testclient import TestClient

from starter_anthropic import app

client = TestClient(app)


def test_health_anthropic():
    r = client.get("/health")
    assert r.status_code == 200
    print("✅ test_health_anthropic")


def test_chat_anthropic_happy_path():
    fake_resp = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="Hi!")],
        usage=SimpleNamespace(input_tokens=10, output_tokens=2),
    )
    with patch("starter_anthropic.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.return_value = fake_resp
        r = client.post("/chat", json={"message": '你好'})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == "Hi!"
    assert body["input_tokens"] == 10
    assert body["output_tokens"] == 2
    print("✅ test_chat_anthropic_happy_path")


def test_chat_anthropic_429_on_rate_limit():
    with patch("starter_anthropic.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.side_effect = anthropic.RateLimitError(
            message="rate limited", response=MagicMock(status_code=429), body=None,
        )
        r = client.post("/chat", json={"message": '你好'})
    assert r.status_code == 429
    print("✅ test_chat_anthropic_429_on_rate_limit")


def test_chat_anthropic_503_on_connection_error():
    with patch("starter_anthropic.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.side_effect = anthropic.APIConnectionError(
            request=MagicMock()
        )
        r = client.post("/chat", json={"message": '你好'})
    assert r.status_code == 503
    print("✅ test_chat_anthropic_503_on_connection_error")


def test_chat_rejects_blank_message():
    r = client.post("/chat", json={"message": "   "})
    assert r.status_code == 422
    print("✅ test_chat_rejects_blank_message")


def test_chat_rejects_oversized_message():
    r = client.post("/chat", json={"message": "x" * 4001})
    assert r.status_code == 422
    print("✅ test_chat_rejects_oversized_message")


def test_chat_rejects_excessive_max_tokens():
    r = client.post("/chat", json={"message": '你好', "max_tokens": 1001})
    assert r.status_code == 422
    print("✅ test_chat_rejects_excessive_max_tokens")


def test_chat_anthropic_502_on_empty_model_output():
    fake_resp = SimpleNamespace(
        content=[], usage=SimpleNamespace(input_tokens=1, output_tokens=0)
    )
    with patch("starter_anthropic.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.return_value = fake_resp
        r = client.post("/chat", json={"message": '你好'})
    assert r.status_code == 502
    print("✅ test_chat_anthropic_502_on_empty_model_output")


def test_chat_500_does_not_log_secret():
    secret = "sk-ant-secret-marker"
    with patch(
        "starter_anthropic.agent_call_anthropic",
        side_effect=RuntimeError(secret),
    ), patch("starter_anthropic.logger.error") as log_error:
        r = client.post("/chat", json={"message": '你好'})

    assert r.status_code == 500
    assert r.json()["detail"] == "内部错误"
    rendered_call = repr(log_error.call_args)
    assert secret not in rendered_call
    assert "RuntimeError" in rendered_call
    assert not log_error.call_args.kwargs.get("exc_info")
    print("✅ test_chat_500_does_not_log_secret")


if __name__ == "__main__":
    test_health_anthropic()
    test_chat_anthropic_happy_path()
    test_chat_anthropic_429_on_rate_limit()
    test_chat_anthropic_503_on_connection_error()
    test_chat_rejects_blank_message()
    test_chat_rejects_oversized_message()
    test_chat_rejects_excessive_max_tokens()
    test_chat_anthropic_502_on_empty_model_output()
    test_chat_500_does_not_log_secret()
    print("\n🎉 通过 — Anthropic FastAPI endpoint 正确")
