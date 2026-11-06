"""Stage 7 练习 3：Observability — Path B（Anthropic usage 栏位）。

这条路记录供应商返回的 input_tokens 与 output_tokens，不自行猜 token 数。

运行方法：
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...
    python starter_anthropic.py
"""

# 一次任务对应 trace，内部步骤对应 span；同时记录耗时、错误与模型报告用量。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import os
import sys
import time
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import anthropic

from starter import TraceContext, require_text, trace_span

MODEL = os.environ.get("MODEL", "claude-haiku-4-5-20251001")


# 记录 Claude 实际返回的用量字段，不把模拟数据当真实计费记录。
def observable_agent_anthropic(question: str, ctx: TraceContext, client: Any = None) -> str:
    client = client or anthropic.Anthropic()
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    with trace_span(ctx, "llm_call", model=MODEL):
        resp = client.messages.create(
            # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
            # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
            model=MODEL, max_tokens=300,
            # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
            messages=[{"role": "user", "content": question}],
        )
        joined = " ".join(b.text for b in resp.content if b.type == "text")
        answer = require_text(joined, "Anthropic")
        # 向 ctx 累计服务报告的 token 用量。
        ctx.add_tokens(input_t=resp.usage.input_tokens, output_t=resp.usage.output_tokens)
    return answer


if __name__ == "__main__":
    ctx = TraceContext(request_id=f"req_{int(time.time()*1000)}")
    answer = observable_agent_anthropic("What's 2+2?", ctx)
    print(f"回答：{answer}")
    print(f"trace: {ctx.summary()}")
    print(f"\n✅ 练习 3 (Anthropic) 通过 — {MODEL} 返回的 usage 已写入 trace")
