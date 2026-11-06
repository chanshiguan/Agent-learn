"""离线检查 B 路径的 Anthropic 后端配置与相同的任务交接。"""

# 本组测试围绕以下行为检查正反例：沿着研究、写作、审核看资料如何传递；角色名字不能代替实际的任务上下文。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import build_crew, simulate_handoff
from starter_anthropic import MODEL


def test_pinned_anthropic_provider_and_structure() -> None:
    assert MODEL == "anthropic/claude-haiku-4-5-20251001"
    crew = build_crew("react", llm_model=MODEL)
    assert [agent.role for agent in crew.agents] == ['研究者', '写作者', '审核者']
    assert len(crew.tasks[2].context) == 2


def test_anthropic_path_offline_handoff_behavior() -> None:
    result = simulate_handoff("langgraph")
    assert "LangGraph" in result["research"]
    assert result["verdict"] == "PASS"
    assert "max_iter=4" in result["stop_condition"]


if __name__ == "__main__":
    test_pinned_anthropic_provider_and_structure()
    test_anthropic_path_offline_handoff_behavior()
    print("全部通过")
