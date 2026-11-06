"""Stage 7 练习 3：Observability — Path A（Ollama）。

Production agent 必备 4 个 telemetry：
1. **Latency**：每个 LLM call 多久（追 p50/p95/p99）
2. **Token usage**：input / output / total tokens（追 cost）
3. **Trace**：multi-step agent 的每一步（debug + audit）
4. **Errors**：捕 exception + retry count

运行方法：
    pip install -r requirements.txt
    ollama pull qwen3.5:4b
    ollama serve
    python starter.py
"""

# 一次任务对应 trace，内部步骤对应 span；同时记录耗时、错误与模型报告用量。

from __future__ import annotations

import json
import logging
import os
import sys
import time
from contextlib import contextmanager
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from openai import OpenAI

MODEL = os.environ.get("MODEL", "qwen3.5:4b")
OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434/v1")


def require_text(value: str | None, label: str) -> str:
    """拒绝没有可用文字的响应，避免把空结果当作成功。"""
    text = (value or "").strip()
    if not text:
        raise ValueError(f"{label} 返回了空文本")
    return text

# 结构化日志保留时间、调用和用量字段；实际部署可接入日志平台，但不要把密钥和完整私有资料写入日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger("agent.observability")


# === 4 个 telemetry primitives ===

class TraceContext:
    """Per-request trace context. Production 通常用 OpenTelemetry。"""

    def __init__(self, request_id: str):
        self.request_id = request_id
        self.spans: list[dict] = []
        self.total_tokens = {"input": 0, "output": 0}
        self.errors: list[str] = []

    def add_span(self, name: str, latency_ms: float, **extras):
        span = {"name": name, "latency_ms": latency_ms, **extras}
        self.spans.append(span)
        # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
        logger.info(f"[{self.request_id}] span={name} ms={latency_ms:.1f} {json.dumps(extras)}")

    def add_tokens(self, input_t: int, output_t: int):
        self.total_tokens["input"] += input_t
        self.total_tokens["output"] += output_t

    def add_error(self, msg: str):
        self.errors.append(msg)
        logger.error(f"[{self.request_id}] error={msg}")

    def summary(self) -> dict:
        total_ms = sum(s["latency_ms"] for s in self.spans)
        return {
            "request_id": self.request_id,
            "total_latency_ms": total_ms,
            "span_count": len(self.spans),
            "input_tokens": self.total_tokens["input"],
            "output_tokens": self.total_tokens["output"],
            "error_count": len(self.errors),
        }


# 步骤开始时计时，结束或出错时都留下记录，便于定位失败所在。
@contextmanager
def trace_span(ctx: TraceContext, name: str, **extras):
    """Context manager 计时 + 记 span；只保存安全的例外类别。"""
    t0 = time.perf_counter()
    error_type = None
    try:
        yield
    except Exception as exc:
        error_type = type(exc).__name__
        # 向 ctx 登记错误信息。
        ctx.add_error(f"{name}: {error_type}")
        raise
    # 无论成功还是失败，都执行这里的收尾步骤。
    finally:
        latency_ms = (time.perf_counter() - t0) * 1000
        # 向 ctx 登记一个阶段的耗时与状态。
        ctx.add_span(name, latency_ms, error=error_type, **extras)


# === 为 Agent 增加调用记录 ===

# 在模型调用周围记录耗时、用量与异常；日志存在不证明回答正确。
def observable_agent(question: str, ctx: TraceContext, llm: Any = None) -> str:
    """为一次模型调用记录起止时间和 token 用量，便于定位延迟与成本。"""
    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    llm = llm or OpenAI(base_url=OLLAMA_BASE, api_key="ollama")

    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    with trace_span(ctx, "llm_call", model=MODEL):
        resp = llm.chat.completions.create(
            # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
            model=MODEL,
            # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
            messages=[{"role": "user", "content": question}],
        )
        answer = require_text(resp.choices[0].message.content, "Ollama")
        # 用量必须取自服务响应；部分 Ollama 版本不提供用量字段，此时应保留未知。
        # 用量来自服务实际报告，用于成本和预算核对；缺失时保留未知，不自行估算成确定账单。
        usage = getattr(resp, "usage", None)
        if usage:
            # 向 ctx 累计服务报告的 token 用量。
            ctx.add_tokens(
                input_t=getattr(usage, "prompt_tokens", 0),
                output_t=getattr(usage, "completion_tokens", 0),
            )

    return answer


# 把多个调用组织进同一条 trace，每个步骤有自己的 span。
def multi_step_agent(question: str, llm: Any = None) -> dict:
    """模拟 multi-step agent：search → reason → answer、每步 traced。"""
    ctx = TraceContext(request_id=f"req_{int(time.time()*1000)}")

    with trace_span(ctx, "search"):
        # 按指定秒数等待。
        time.sleep(0.05)  # 用固定等待模拟工具耗时，便于检查计时记录，不进行真实网络搜索
        search_result = "固定模拟检索结果，对应问题：" + question

    answer = observable_agent(f"依据资料：'{search_result}', 回答：{question}", ctx, llm=llm)

    return {
        "answer": answer,
        "trace_summary": ctx.summary(),
        "spans": ctx.spans,
    }


if __name__ == "__main__":
    print("正在运行带观测记录的 Agent……\n")
    result = multi_step_agent("What's 2+2?")
    print(f"\n📊 执行轨迹汇总：")
    for k, v in result["trace_summary"].items():
        print(f"   {k}: {v}")
    print(f"\n📝 Spans:")
    for s in result["spans"]:
        print(f"   {s['name']}: {s['latency_ms']:.1f}ms")

    assert result["trace_summary"]["span_count"] >= 2  # search + llm_call
    print("\n✅ 练习 3 通过 — request、span、latency、usage 与 error 都能被记录")
