"""Stage 7 练习 5 自我验证 — FastAPI endpoint + error handling。
"""

# 本组测试围绕以下行为检查正反例：请求先过字段校验，再调用模型；健康检查、模型可用和答案正确分别验收。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient
from openai import APIConnectionError, RateLimitError

from starter import app, agent_call

client = TestClient(app)


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "model" in body
    print("✅ test_health_endpoint")


def test_chat_endpoint_happy_path():
    """Mock 上游 LLM、确认 /chat 回 ChatResponse shape。"""
    fake_resp = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="你好！"))]
    )
    with patch("starter.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = fake_resp
        r = client.post("/chat", json={"message": '你好'})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == "你好！"
    assert "request_id" in body
    assert body["latency_ms"] >= 0
    print("✅ test_chat_endpoint_happy_path")


def test_chat_returns_503_on_upstream_unavailable():
    """模拟 Ollama down、回 503 而非 500。"""
    with patch("starter.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = APIConnectionError(
            request=MagicMock()
        )
        r = client.post("/chat", json={"message": '你好'})
    assert r.status_code == 503
    assert "不可用" in r.json()["detail"]
    print("✅ test_chat_returns_503_on_upstream_unavailable")


def test_chat_returns_429_on_upstream_rate_limit():
    with patch("starter.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = RateLimitError(
            message="rate limited",
            response=MagicMock(status_code=429, headers={}),
            body=None,
        )
        r = client.post("/chat", json={"message": '你好'})
    assert r.status_code == 429
    print("✅ test_chat_returns_429_on_upstream_rate_limit")


def test_chat_validates_input_schema():
    """缺 message field、应该 422 Unprocessable Entity（FastAPI 自动验 Pydantic schema）。"""
    r = client.post("/chat", json={})
    assert r.status_code == 422
    print("✅ test_chat_validates_input_schema")


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


def test_chat_returns_502_on_empty_model_output():
    fake_resp = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=""))]
    )
    with patch("starter.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = fake_resp
        r = client.post("/chat", json={"message": '你好'})
    assert r.status_code == 502
    print("✅ test_chat_returns_502_on_empty_model_output")


def test_chat_500_does_not_log_secret():
    secret = "sk-ant-secret-marker"
    # 第一行让模型调用模拟异常；第二行替换 logger.error 并保存为 log_error，供后续确认日志不含秘密。
    with patch("starter.agent_call", side_effect=RuntimeError(secret)), \
         patch("starter.logger.error") as log_error:
        r = client.post("/chat", json={"message": '你好'})

    assert r.status_code == 500
    assert r.json()["detail"] == "内部错误"
    rendered_call = repr(log_error.call_args)
    assert secret not in rendered_call
    assert "RuntimeError" in rendered_call
    assert not log_error.call_args.kwargs.get("exc_info")
    print("✅ test_chat_500_does_not_log_secret")


def test_agent_call_unit():
    """agent_call function 单元测试（无 HTTP）。"""
    fake_resp = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))]
    )
    llm = MagicMock()
    llm.chat.completions.create.return_value = fake_resp
    # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
    out = agent_call('你好', max_tokens=100, llm=llm)
    assert out == "ok"
    print("✅ test_agent_call_unit")


if __name__ == "__main__":
    test_health_endpoint()
    test_chat_endpoint_happy_path()
    test_chat_returns_503_on_upstream_unavailable()
    test_chat_returns_429_on_upstream_rate_limit()
    test_chat_validates_input_schema()
    test_chat_rejects_blank_message()
    test_chat_rejects_oversized_message()
    test_chat_rejects_excessive_max_tokens()
    test_chat_returns_502_on_empty_model_output()
    test_chat_500_does_not_log_secret()
    test_agent_call_unit()
    print("\n🎉 全部通过 — FastAPI agent endpoint 逻辑正确")
