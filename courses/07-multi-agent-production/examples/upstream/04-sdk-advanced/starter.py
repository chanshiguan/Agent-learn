"""Stage 7 练习 4：SDK 进阶 — Path A（Ollama streaming）。

Production agent 两个必备 SDK 进阶 feature：
1. **Streaming**：答案还在生成时，就把已到达的文字先显示给用户。
2. **Prompt caching**：重用相同长前缀；实际是否命中要看供应商返回的 usage。

运行方法：
    pip install -r requirements.txt
    ollama pull qwen3.5:4b
    ollama serve
    python starter.py
"""

# 流式片段要收齐并检查结束；缓存收益需看实际 usage，不能从配置存在推断。

from __future__ import annotations

import os
import sys
import time
from typing import Any, Iterator

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


# 逐段读取输出；空片段不等于模型已经给出完整答案。
def stream_response(prompt: str, llm: Any = None) -> Iterator[str]:
    """每收到一个文本片段就向调用方交付；片段边界不保证等于一个词或 token。"""
    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    llm = llm or OpenAI(base_url=OLLAMA_BASE, api_key="ollama")
    stream = llm.chat.completions.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=MODEL,
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": prompt}],
        # stream：以增量片段接收响应，改善首字等待；工具参数必须收齐并校验后才能执行。
        stream=True,
    )
    saw_non_whitespace = False
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            if delta.strip():
                saw_non_whitespace = True
            # 立即把当前有效文本片段交给调用者，让调用者逐块显示或拼接。
            yield delta
    if not saw_non_whitespace:
        raise ValueError("Ollama stream 返回了空文本")


# 将有效片段拼成完整文本，再检查是否为空。
def stream_to_string(prompt: str, llm: Any = None) -> dict:
    """Helper：consume streaming generator + 统计 latency。"""
    t0 = time.perf_counter()
    first_token_at = None
    chunks = []
    for delta in stream_response(prompt, llm=llm):
        if first_token_at is None and delta.strip():
            first_token_at = time.perf_counter() - t0
        chunks.append(delta)
    total_latency = time.perf_counter() - t0
    text = require_text("".join(chunks), "Ollama stream")
    return {
        "text": text,
        "first_token_ms": (first_token_at or 0) * 1000,
        "total_latency_ms": total_latency * 1000,
        "chunk_count": len(chunks),
    }


if __name__ == "__main__":
    prompt = "请用三句中文解释 Python 列表推导式。"
    print(f"❓ {prompt}\n")
    print("（正在接收文本片段……）\n")

    t0 = time.perf_counter()
    for delta in stream_response(prompt):
        print(delta, end="", flush=True)
    total = time.perf_counter() - t0

    print(f"\n\n📊 Total: {total:.2f}s")
    print("✅ 练习 4 通过 — streaming SDK 能逐段显示答案")
    print("   请在自己的电脑量 first-token 与 total latency；速度会随模型和硬体改变")
