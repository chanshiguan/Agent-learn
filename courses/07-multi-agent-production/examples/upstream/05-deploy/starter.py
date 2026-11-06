"""Stage 7 练习 5：Deploy — Path A（FastAPI + Ollama）。

把 agent 包进 FastAPI HTTP endpoint、production-style health check + structured logging。
本地端 `uvicorn starter:app` 就能跑、Docker / k8s / Lambda 都能 lift。

运行方法：
    pip install -r requirements.txt
    ollama pull qwen3.5:4b
    ollama serve
    uvicorn starter:app --reload --port 8000
    # 另一个 shell: curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{"message": "hi"}'

验证（不必启 server）:
    python test.py
"""

# 请求先过字段校验，再调用模型；健康检查、模型可用和答案正确分别验收。

from __future__ import annotations

import logging
import os
import sys
import time
import uuid
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from fastapi import FastAPI, HTTPException
from openai import APIConnectionError, OpenAI, RateLimitError
# Field 把长度、范围等约束附在字段上；格式通过之后，还要核对业务规则和事实依据。
from pydantic import BaseModel, Field, field_validator

MODEL = os.environ.get("MODEL", "qwen3.5:4b")
OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434/v1")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("agent.api")


# === 请求与响应的数据约定 ===

class ChatRequest(BaseModel):
    # min_length：要求至少有指定数量的字符或元素，避免空答案、空来源列表看起来结构合法却无法使用。
    # max_length：限制输入或输出的规模，防止意外的大文本拖慢处理或占满上下文。
    message: str = Field(min_length=1, max_length=4000)
    # ge：设置包含边界的数值下限；类型正确但越界的值也必须被拒绝。
    # le：设置包含边界的数值上限，防止过大置信度或预算通过类型检查。
    max_tokens: int = Field(default=300, ge=1, le=1000)

    @field_validator("message")
    @classmethod
    def message_must_contain_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message 必须包含非空白文本")
        return value


class ChatResponse(BaseModel):
    request_id: str
    # answer：保存最终对外文本；非空只说明模型有输出，事实与引用是否正确仍要独立核对。
    answer: str
    latency_ms: float
    model: str


class ModelOutputError(ValueError):
    """上游模型没有返回可用文字。"""


def require_text(value: str | None, label: str) -> str:
    text = (value or "").strip()
    if not text:
        raise ModelOutputError(f"{label} 返回了空文本")
    return text


# === Agent 的执行流程 ===

def agent_call(message: str, max_tokens: int, llm: Any = None) -> str:
    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    llm = llm or OpenAI(base_url=OLLAMA_BASE, api_key="ollama")
    resp = llm.chat.completions.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=MODEL,
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        max_tokens=max_tokens,
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": message}],
    )
    return require_text(resp.choices[0].message.content, "Ollama")


# === HTTP 请求入口：接收输入、调用 Agent、返回响应 ===

app = FastAPI(title="Agent API", version="0.1.0")


@app.get("/health")
def health():
    """只检查服务进程能否响应，不请求模型，避免健康探测产生模型成本。"""
    return {"status": "ok", "model": MODEL}


# response_model：让返回内容按这个模型进行类型与字段验证；验证失败后是否重试仍受次数限制。
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    request_id = str(uuid.uuid4())
    t0 = time.perf_counter()
    logger.info(f"[{request_id}] chat request received")
    try:
        answer = agent_call(req.message, req.max_tokens)
    except ModelOutputError as e:
        logger.warning(f"[{request_id}] upstream LLM 返回了空文本")
        raise HTTPException(status_code=502, detail="模型没有返回答案") from e
    except RateLimitError as e:
        logger.warning(f"[{request_id}] 上游模型服务限制了请求频率")
        raise HTTPException(status_code=429, detail="请求频率受限") from e
    except APIConnectionError as e:
        logger.error(f"[{request_id}] 上游模型服务不可用")
        raise HTTPException(status_code=503, detail="模型服务不可用") from e
    except Exception as e:  # noqa: BLE001
        logger.error(
            f"[{request_id}] 未预期的内部错误类型={type(e).__name__}"
        )
        raise HTTPException(status_code=500, detail="内部错误") from e

    latency_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"[{request_id}] chat done in {latency_ms:.0f}ms")
    return ChatResponse(
        request_id=request_id, answer=answer,
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        latency_ms=latency_ms, model=MODEL,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
