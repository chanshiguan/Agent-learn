"""Stage 7 练习 1 自我验证 — mock 3 个 LLM call。"""

# 本组测试围绕以下行为检查正反例：正反两方分别回答，再交给裁决者；意见一致不能代替事实证据。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import debate, llm_call, parse_winner


def make_llm(responses: list[str]):
    llm = MagicMock()
    llm.chat.completions.create.side_effect = [
        SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=r))])
        for r in responses
    ]
    return llm


def test_llm_call_basic():
    llm = make_llm(["ok"])
    out = llm_call("请简洁回答", '你好', llm=llm)
    assert out == "ok"
    print("✅ test_llm_call_basic")


def test_llm_call_rejects_empty_text():
    llm = make_llm(["   "])
    try:
        llm_call("请简洁回答", '你好', llm=llm)
    except ValueError as error:
        assert "空文本" in str(error)
    else:
        raise AssertionError("empty model output must fail")
    print("✅ test_llm_call_rejects_empty_text")


def test_parse_winner_requires_the_whole_contract():
    assert parse_winner("WINNER=CON. 证据更明确") == ("CON", "证据更明确")
    for invalid in ("也许 WINNER=PRO", "WINNER=PRO", "PRO. good"):
        try:
            parse_winner(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid Judge output accepted: {invalid}")
    print("✅ test_parse_winner_requires_the_whole_contract")


def test_debate_3_calls():
    """debate 应该打 3 次 LLM（pro, con, judge）、且 judge 看到两边 argument。"""
    llm = make_llm([
        "PRO: 框架可以节省开发时间。",
        "CON: 框架可能增加迁移成本。",
        "WINNER=PRO. 对小团队而言，节省时间的收益大于框架依赖成本。",
    ])
    result = debate("小团队应该使用框架吗？", llm=llm)
    assert llm.chat.completions.create.call_count == 3
    assert "框架可以节省开发时间" in result["pro"]
    assert "框架可能增加迁移成本" in result["con"]
    assert "WINNER=PRO" in result["judge"]
    assert result["winner"] == "PRO"

    # 第 3 个 call（judge）的 user prompt 应该包含 pro + con
    third_call = llm.chat.completions.create.call_args_list[2]
    judge_user = third_call.kwargs["messages"][1]["content"]
    assert "框架可以节省开发时间" in judge_user
    assert "框架可能增加迁移成本" in judge_user
    print("✅ test_debate_3_calls")


def test_debate_independent_pro_con():
    """确认 pro / con 各自独立 call、不互相看到（避免 bias propagation）。"""
    llm = make_llm(["支持观点", "反对观点", "WINNER=PRO. 证据更明确"])
    # 分别生成正反观点，再让评判角色按契约选择结果。
    debate("test", llm=llm)
    # 第 1 个 call (pro) 的 user prompt 应该 = question、不含 con
    first = llm.chat.completions.create.call_args_list[0]
    assert first.kwargs["messages"][1]["content"] == "test"
    print("✅ test_debate_independent_pro_con")


if __name__ == "__main__":
    test_llm_call_basic()
    test_llm_call_rejects_empty_text()
    test_parse_winner_requires_the_whole_contract()
    test_debate_3_calls()
    test_debate_independent_pro_con()
    print("\n🎉 全部通过 — multi-agent debate 逻辑正确")
