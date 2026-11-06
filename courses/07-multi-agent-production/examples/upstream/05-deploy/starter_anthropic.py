"""Stage 7 练习 5：Deploy — Path B（FastAPI + Anthropic）。

跟 starter.py 同 HTTP API、agent_call 改成 anthropic SDK。

运行方法：
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...
    uvicorn starter_anthropic:app --reload --port 8000
    curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{"message": "hi"}'

费用请用实际 input/output tokens 乘上当期官方单价，不用固定猜测值。
"""

# 请求先过字段校验，再调用模型；健康检查、模型可用和答案正确分别验收。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

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

import anthropic
from fastapi import FastAPI, HTTPException
# Field 把长度、范围等约束附在字段上；格式通过之后，还要核对业务规则和事实依据。
from pydantic import BaseModel, Field, field_validator

MODEL = os.environ.get("MODEL", "claude-haiku-4-5-20251001")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("agent.api")


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
    input_tokens: int
    output_tokens: int


class ModelOutputError(ValueError):
    """上游模型没有返回可用文字。"""


def require_text(value: str | None, label: str) -> str:
    text = (value or "").strip()
    if not text:
        raise ModelOutputError(f"{label} 返回了空文本")
    return text


def agent_call_anthropic(message: str, max_tokens: int, client: Any = None) -> dict:
    client = client or anthropic.Anthropic()
    resp = client.messages.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        model=MODEL, max_tokens=max_tokens,
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": message}],
    )
    answer = require_text(" ".join(b.text for b in resp.content if b.type == "text"), "Anthropic")
    return {
        "answer": answer,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
    }


app = FastAPI(title="Agent API (Anthropic)", version="0.1.0")


@app.get("/health")
def health():
    """只检查服务进程能否响应，不请求模型，避免健康探测产生模型成本。"""
    return {"status": "ok", "model": MODEL}


# response_model：让返回内容按这个模型进行类型与字段验证；验证失败后是否重试仍受次数限制。
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    request_id = str(uuid.uuid4())
    t0 = time.perf_counter()
    logger.info(f"[{request_id}] chat request")
    try:
        result = agent_call_anthropic(req.message, req.max_tokens)
    except ModelOutputError as e:
        logger.warning(f"[{request_id}] upstream LLM 返回了空文本")
        raise HTTPException(status_code=502, detail="模型没有返回答案") from e
    except anthropic.APIConnectionError as e:
        logger.error(f"[{request_id}] 上游模型服务不可用")
        raise HTTPException(status_code=503, detail="模型服务不可用") from e
    except anthropic.RateLimitError as e:
        logger.warning(f"[{request_id}] 上游模型服务限制了请求频率")
        raise HTTPException(status_code=429, detail="请求频率受限") from e
    except Exception as e:  # noqa: BLE001
        logger.error(
            f"[{request_id}] 未预期的内部错误类型={type(e).__name__}"
        )
        raise HTTPException(status_code=500, detail="内部错误") from e

    latency_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"[{request_id}] done in {latency_ms:.0f}ms, tokens={result['input_tokens']}+{result['output_tokens']}")
    return ChatResponse(
        request_id=request_id, answer=result["answer"],
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        latency_ms=latency_ms, model=MODEL,
        input_tokens=result["input_tokens"], output_tokens=result["output_tokens"],
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
