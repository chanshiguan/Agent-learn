"""离线核对 CrewAI 的角色和任务结构，不启动 Crew 或联网。"""

# 本组测试围绕以下行为检查正反例：保持问题和搜索资料相同，比较 LangGraph 的状态图与 CrewAI 的角色任务如何调用工具。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter_crewai import build_crew, search_knowledge_base


def test_offline_search_and_visible_crewai_structure() -> None:
    assert "台北" in search_knowledge_base("台北")
    assert "没有此条目" in search_knowledge_base("unknown")
    crew = build_crew("请概括台北的信息")
    assert [agent.role for agent in crew.agents] == ['研究者']
    assert len(crew.tasks) == 1
    assert crew.tasks[0].agent.role == '研究者'


if __name__ == "__main__":
    test_offline_search_and_visible_crewai_structure()
    print("全部通过")
