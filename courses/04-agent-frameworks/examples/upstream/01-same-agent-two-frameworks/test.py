"""Stage 4 练习 1 自我验证 — Path A（Ollama starter.py，LangGraph 版）。

运行方法：
    python test.py

用 mock LLM 取代真实 API、不打网路。
"""

# 本组测试围绕以下行为检查正反例：保持问题和搜索资料相同，比较 LangGraph 的状态图与 CrewAI 的角色任务如何调用工具。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langchain_core.messages import AIMessage

from starter import build_graph, run, search


def test_search_tool_basic():
    assert "台北" in search.invoke({"query": "台北"})
    assert "没有此条目" in search.invoke({"query": "unknown_topic"})
    print("✅ test_search_tool_basic")


def test_run_with_mock_llm():
    """Mock LangChain LLM — agent 第一轮叫 search、第二轮收尾。"""
    llm = MagicMock()
    # 第一轮：tool_calls (search Taipei)
    tool_call_msg = AIMessage(
        content="",
        tool_calls=[{"name": "search", "args": {"query": "台北"}, "id": "call_1", "type": "tool_call"}],
    )
    # 第二轮：纯文字 summary
    final_msg = AIMessage(content="台北是台湾地区的城市，示例人口约 260 万。")
    llm.bind_tools.return_value = llm  # 链式：bind_tools 回自己
    llm.invoke.side_effect = [tool_call_msg, final_msg]

    result = run("请概括台北的信息", llm=llm)
    assert "台北" in result["final"]
    assert result["steps"] >= 3  # 检查完整消息链：用户问题、模型请求、工具结果、最终回答都必须保留
    print("✅ test_run_with_mock_llm")


def test_run_skip_tool_when_known():
    """Mock：LLM 直接给答案、不调用 tool。"""
    llm = MagicMock()
    final_msg = AIMessage(content="Python 是一种编程语言。", tool_calls=[])
    llm.bind_tools.return_value = llm
    llm.invoke.return_value = final_msg

    result = run("Python 是什么", llm=llm)
    assert "Python" in result["final"]
    assert result["steps"] == 2
    print("✅ test_run_skip_tool_when_known")


def test_reject_unknown_tool_name():
    """模型不能把未知名称偷偷当成 search 执行。"""
    llm = MagicMock()
    llm.bind_tools.return_value = llm
    llm.invoke.return_value = AIMessage(
        content="",
        tool_calls=[{"name": "delete_files", "args": {"query": "台北"}, "id": "call_bad", "type": "tool_call"}],
    )

    try:
        run("请概括台北的信息", llm=llm)
    except ValueError as error:
        assert '未知工具' in str(error)
    else:
        raise AssertionError("必须拒绝未授权的工具名")
    print("✅ test_reject_unknown_tool_name")


if __name__ == "__main__":
    test_search_tool_basic()
    test_run_with_mock_llm()
    test_run_skip_tool_when_known()
    test_reject_unknown_tool_name()
    print("全部通过")
