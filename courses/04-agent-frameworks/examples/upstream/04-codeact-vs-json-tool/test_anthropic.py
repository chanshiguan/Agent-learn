"""Path B 离线行为测试：不调用模型，也不执行模型产生的程序码。"""

# 本组测试围绕以下行为检查正反例：比较 JSON 参数调用与代码行动；算术用 AST 白名单，CodeAct 的执行依赖受限 Docker。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import run_json_tool_call
from starter_anthropic import MODEL, make_anthropic_model


def test_litellm_provider_configuration() -> None:
    model = make_anthropic_model()
    assert MODEL == "anthropic/claude-haiku-4-5-20251001"
    assert model.model_id == MODEL


def test_anthropic_path_uses_the_same_safe_json_boundary() -> None:
    assert run_json_tool_call({"name": "calculator", "arguments": {"expression": "8 / 2"}}) == "4.0"
    try:
        run_json_tool_call({"name": "shell", "arguments": {"command": "whoami"}})
    except ValueError:
        pass
    else:
        raise AssertionError("必须拒绝未授权的工具名称。")


if __name__ == "__main__":
    test_litellm_provider_configuration()
    test_anthropic_path_uses_the_same_safe_json_boundary()
    print("全部通过")
