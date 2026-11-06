"""离线检查 Anthropic 响应适配，不评价真实模型的回答能力。"""

# 本组测试围绕以下行为检查正反例：固定题集与评分规则，保存每次试跑和基线差异；开发题与保留题分开使用。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter_anthropic import agent_answer_anthropic, judge_answer_anthropic


def test_agent_answer_anthropic_mock() -> None:
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="东京")]
    )
    output = agent_answer_anthropic("日本的首都是哪里？", client=client)
    assert output == "东京"


def test_agent_answer_anthropic_rejects_empty_text() -> None:
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="")]
    )
    try:
        # 用 Anthropic 模型回答当前评测题并拒绝空文本。
        agent_answer_anthropic("日本的首都是哪里？", client=client)
    except ValueError as error:
        assert "空文本" in str(error)
    else:
        raise AssertionError("empty model output must fail")


def test_judge_answer_anthropic_mock() -> None:
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="PASS")]
    )
    case = {
        "input": "这个答案正确吗？",
        "success_criteria": ["答案正确。"],
        "grader": {"type": "llm_judge", "value": "请按给定标准判断。"},
    }
    assert judge_answer_anthropic("yes", case, client=client) == "PASS"


if __name__ == "__main__":
    test_agent_answer_anthropic_mock()
    print("PASS test_agent_answer_anthropic_mock")
    test_agent_answer_anthropic_rejects_empty_text()
    print("PASS test_agent_answer_anthropic_rejects_empty_text")
    test_judge_answer_anthropic_mock()
    print("PASS test_judge_answer_anthropic_mock")
    print("\n🎉 3/3 passed — no network or API key used")
