"""离线检查 A 路径的任务交接与实际 CrewAI 配置结构。"""

# 本组测试围绕以下行为检查正反例：沿着研究、写作、审核看资料如何传递；角色名字不能代替实际的任务上下文。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from crewai import Process
from starter import build_crew, simulate_handoff


def test_offline_research_writer_critic_handoff() -> None:
    result = simulate_handoff("react")
    assert result["input"] == "react"
    assert "ReAct" in result["research"]
    assert result["research"] in result["draft"]
    assert result["verdict"] == "PASS"
    assert result["stop_condition"] == "固定三个角色；每个 Agent 的迭代上限为 max_iter=4。"


def test_crewai_sequential_context_structure() -> None:
    crew = build_crew("react")
    assert crew.process == Process.sequential
    assert [agent.role for agent in crew.agents] == ['研究者', '写作者', '审核者']
    assert len(crew.tasks) == 3
    assert crew.tasks[1].context == [crew.tasks[0]]
    assert crew.tasks[2].context == [crew.tasks[0], crew.tasks[1]]
    assert all(agent.max_iter == 4 for agent in crew.agents)


if __name__ == "__main__":
    test_offline_research_writer_critic_handoff()
    test_crewai_sequential_context_structure()
    print("全部通过")
