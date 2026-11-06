"""Path A 离线行为测试：真的走分支、暂停与恢复，但不连网。"""

# 本组测试围绕以下行为检查正反例：先分类选择是否检索，再暂停等待决定；内存检查点只保留在当前进程中。

from __future__ import annotations

import sys
from types import SimpleNamespace

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import build_graph, classify_node, run, should_search, search_node


class FakeLLM:
    """只回固定格式的假模型，让图的行为可以重复验证。"""
    def invoke(self, prompt: str) -> SimpleNamespace:
        return SimpleNamespace(content=f"草稿依据：{prompt.splitlines()[-1]}")


def test_branch_choice_and_interrupt_resume() -> None:
    assert classify_node({"query": "台北最新人口"})["needs_search"] is True
    assert should_search({"needs_search": False}) == "respond"
    # 中文问题必须命中中文教学资料，不能只翻译屏幕上的答案而漏掉检索键。
    assert "25 摄氏度" in search_node({"query": "天气如何？"})["search_result"]
    assert "固定教学数据" in search_node({"query": "台北人口是多少？"})["search_result"]
    graph = build_graph(FakeLLM())
    # 运行配置必须在暂停和恢复时保持同一个会话标识，否则恢复会找不到刚才待审核的状态。
    # configurable：传递可在每次运行时指定的图配置；会话标识放在这里，供检查点系统定位历史状态。
    # thread_id：定位同一条工作流的检查点。暂停和恢复必须使用同一个值；换值通常会进入另一条会话。
    config = {"configurable": {"thread_id": "offline-approve"}}
    # 第一次运行应停在人工审核点；此时只有待审草稿，不能声称已经发布。
    paused = graph.invoke({"query": "台北最新人口"}, config=config)
    assert "__interrupt__" in paused
    # 读取指定会话已经保存的状态，用来确认暂停位置和待审核内容，而不是重新生成草稿。
    checkpoint = graph.get_state(config)
    assert "台北人口" in checkpoint.values["draft"]
    # Command 携带恢复值或跳转信息；恢复暂停节点时要将人的决定放入 resume。
    from langgraph.types import Command
    result = graph.invoke(Command(resume=True), config=config)
    assert result["final"].startswith("PUBLISHED:")


def test_rejection_uses_a_separate_checkpoint_thread() -> None:
    # thread_id：定位同一条工作流的检查点。暂停和恢复必须使用同一个值；换值通常会进入另一条会话。
    result = run("请介绍 Python", approve=False, llm=FakeLLM(), thread_id="offline-reject")
    assert result["final"].startswith("REJECTED:")
    assert "本次无需检索" in result["draft"]


if __name__ == "__main__":
    test_branch_choice_and_interrupt_resume()
    test_rejection_uses_a_separate_checkpoint_thread()
    print("全部通过")
