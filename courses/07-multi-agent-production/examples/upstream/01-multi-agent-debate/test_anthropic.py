"""Stage 7 练习 1 — Anthropic mock test。"""

# 本组测试围绕以下行为检查正反例：正反两方分别回答，再交给裁决者；意见一致不能代替事实证据。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter_anthropic import debate_anthropic, llm_call_anthropic, parse_winner


def test_debate_anthropic_3_calls():
    client = MagicMock()
    responses = ["pro", "con", "WINNER=CON. 理由更充分。"]
    client.messages.create.side_effect = [
        SimpleNamespace(content=[SimpleNamespace(type="text", text=r)]) for r in responses
    ]
    result = debate_anthropic("Q?", client=client)
    assert client.messages.create.call_count == 3
    assert "WINNER=CON" in result["judge"]
    assert result["winner"] == "CON"
    print("✅ test_debate_anthropic_3_calls")


def test_anthropic_rejects_empty_text_and_loose_judge_output():
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="   ")]
    )
    try:
        # 向配置的 Anthropic 模型发送提示并读取有效文本。
        llm_call_anthropic("system", "user", client=client)
    except ValueError as error:
        assert "空文本" in str(error)
    else:
        raise AssertionError("empty model output must fail")

    try:
        parse_winner("显然应该选 WINNER=PRO")
    except ValueError:
        pass
    else:
        raise AssertionError("Judge parser accepted extra text")
    print("✅ test_anthropic_rejects_empty_text_and_loose_judge_output")


if __name__ == "__main__":
    test_debate_anthropic_3_calls()
    test_anthropic_rejects_empty_text_and_loose_judge_output()
    print("\n🎉 通过")
