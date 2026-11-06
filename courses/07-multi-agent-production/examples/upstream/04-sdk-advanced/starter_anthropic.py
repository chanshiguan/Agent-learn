"""Stage 7 练习 4：SDK 进阶 — Path B（Anthropic streaming + prompt caching）。

这份小程序示范两个 SDK 功能：
1. **Streaming**：答案还在生成时，先显示已到达的文字。
2. **Prompt caching**：标记可重用的长前缀，再读 usage 判断是否建立或命中 cache。

运行方法：
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...
    python starter_anthropic.py
"""

# 流式片段要收齐并检查结束；缓存收益需看实际 usage，不能从配置存在推断。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import os
import sys
import time
from typing import Any, Iterator

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import anthropic

MODEL = os.environ.get("MODEL", "claude-haiku-4-5-20251001")
CACHE_MINIMUM_TOKENS = 4096
CACHE_DEMO_REPEAT = 1200


def require_text(value: str | None, label: str) -> str:
    """拒绝没有可用文字的响应，避免把空结果当作成功。"""
    text = (value or "").strip()
    if not text:
        raise ValueError(f"{label} 返回了空文本")
    return text


def build_cache_demo_prompt() -> str:
    """构造足够长且重复使用的前缀，用来观察缓存；是否命中仍以服务报告为准。"""
    rule = "参考规则：逐条对照提供的来源核对断言。"
    return "请只依据这些参考规则，用中文回答。\n" + (rule * CACHE_DEMO_REPEAT)


# 消费 Claude 文本流并检查有效内容，流式显示不代替最终验收。
def stream_anthropic(prompt: str, client: Any = None) -> Iterator[str]:
    client = client or anthropic.Anthropic()
    saw_non_whitespace = False
    with client.messages.stream(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=MODEL,
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        max_tokens=300,
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            if text:
                if text.strip():
                    saw_non_whitespace = True
                # 立即把当前有效文本片段交给调用者，不必等完整响应收齐。
                yield text
    if not saw_non_whitespace:
        raise ValueError("Anthropic stream 返回了空文本")


# 发送带缓存控制的请求，并保留实际用量用于判断是否命中缓存。
def cached_query(question: str, large_system_prompt: str, client: Any = None) -> dict:
    """发送可缓存前缀，并返回服务实际报告的用量；不根据请求参数猜测命中。"""
    client = client or anthropic.Anthropic()

    resp = client.messages.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=MODEL,
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        max_tokens=200,
        system=[
            {
                "type": "text",
                "text": large_system_prompt,
                "cache_control": {"type": "ephemeral"},   # Task.context 必须传入上游任务，当前角色才能读到它的实际结果
            }
        ],
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": question}],
    )

    # 用量来自服务实际报告，用于成本和预算核对；缺失时保留未知，不自行估算成确定账单。
    usage = resp.usage
    answer = require_text(" ".join(b.text for b in resp.content if b.type == "text"), "Anthropic")
    return {
        "answer": answer,
        "input_tokens": usage.input_tokens,
        "cache_creation_input_tokens": getattr(usage, "cache_creation_input_tokens", 0),
        "cache_read_input_tokens": getattr(usage, "cache_read_input_tokens", 0),
        "output_tokens": usage.output_tokens,
    }


if __name__ == "__main__":
    # 演示 1：流式接收文本，检查结束后是否得到有效内容
    print("=== 流式响应演示 ===")
    print("（逐片段接收……）\n")
    t0 = time.perf_counter()
    for delta in stream_anthropic("请用三句中文解释 Python 列表推导式。"):
        print(delta, end="", flush=True)
    print(f"\n[耗时 {time.perf_counter()-t0:.2f}s]\n")

    # 演示 2：连续两次发送同一长前缀，用服务实际报告的用量判断缓存是否命中。
    print("=== 提示词缓存演示 ===")
    big_system = build_cache_demo_prompt()
    print(f"演示前缀有 {len(big_system)} 个字符；本例记录的缓存门槛为 {CACHE_MINIMUM_TOKENS} tokens。字符数不等于 token 数，是否命中以响应为准。")
    r1 = cached_query("2 加 2 等于多少？", big_system)
    print(f"第 1 次：输入用量={r1['input_tokens']}, cache_create={r1['cache_creation_input_tokens']}, cache_read={r1['cache_read_input_tokens']}")
    r2 = cached_query("3 加 3 等于多少？", big_system)
    print(f"第 2 次：输入用量={r2['input_tokens']}, cache_create={r2['cache_creation_input_tokens']}, cache_read={r2['cache_read_input_tokens']}")

    if r2["cache_read_input_tokens"] > 0:
        print("\n✅ 服务用量表明第二次调用读取了缓存。")
    elif r1["cache_creation_input_tokens"] > 0:
        print("\nℹ️ 服务报告已创建缓存，但未报告第二次调用读取缓存。")
    else:
        print("\nℹ️ 服务没有报告缓存创建或读取，不能据此判断命中。")
    print(f"\n✅ 练习 4 (Anthropic) 通过 — streaming + usage inspection、Claude {MODEL}")
