"""Stage 4 练习 3 Path B：把同一张 LangGraph 图接到 ChatAnthropic。

流程、暂停点与人工核准规则都不变；只有负责写草稿的模型不同。
"""

# 先分类选择是否检索，再暂停等待决定；内存检查点只保留在当前进程中。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import os
import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langchain_anthropic import ChatAnthropic
from starter import run

MODEL = os.environ.get("MODEL", "claude-haiku-4-5-20251001")


def make_anthropic_llm() -> ChatAnthropic:
    """建立使用固定 model ID 的 Anthropic chat model。"""
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
    return ChatAnthropic(model=MODEL, temperature=0)


if __name__ == "__main__":
    result = run("台北人口是多少？", approve=True, llm=make_anthropic_llm())
    print(result["final"])
    assert result["final"].startswith("PUBLISHED:")
    assert "台北" in result["final"]
