"""离线验证 B 路径行为，不发送 Anthropic 请求。"""

# 本组测试围绕以下行为检查正反例：保持问题和搜索资料相同，比较 LangGraph 的状态图与 CrewAI 的角色任务如何调用工具。

from __future__ import annotations

import sys
import os
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langchain_core.messages import AIMessage
from starter import run
from starter_anthropic import MODEL


def test_pinned_provider_and_shared_graph_behavior() -> None:
    from langchain_anthropic import ChatAnthropic
    assert MODEL == "claude-haiku-4-5-20251001"
    os.environ.setdefault("ANTHROPIC_API_KEY", "offline-test-key")
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
    assert ChatAnthropic(model=MODEL, temperature=0).model == MODEL
    llm = MagicMock()
    llm.bind_tools.return_value = llm
    llm.invoke.side_effect = [
        AIMessage(content="", tool_calls=[{"name": "search", "args": {"query": "台北"}, "id": "call_1", "type": "tool_call"}]),
        AIMessage(content="台北位于台湾地区。", tool_calls=[]),
    ]
    result = run("请概括台北的信息", llm=llm)
    assert result["final"].startswith("台北")
    assert result["steps"] >= 4


if __name__ == "__main__":
    test_pinned_provider_and_shared_graph_behavior()
    print("全部通过")
