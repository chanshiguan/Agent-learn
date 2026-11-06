"""Path A 离线行为测试：不调用 CodeAgent.run，也不执行模型程序码。"""

# 本组测试围绕以下行为检查正反例：比较 JSON 参数调用与代码行动；算术用 AST 白名单，CodeAct 的执行依赖受限 Docker。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import MAX_NUMBER, codeact_executor_config, evaluate_arithmetic, run_json_tool_call


def test_json_tool_and_ast_evaluator() -> None:
    assert run_json_tool_call({"name": "calculator", "arguments": {"expression": "2 + 3 * (4 - 1)"}}) == "11.0"
    assert evaluate_arithmetic("-4 / 2") == -2.0


def test_ast_guards_reject_code_and_unsafe_values() -> None:
    for expression in ("__import__('os')", "2 / 0", f"{MAX_NUMBER + 1}"):
        try:
            evaluate_arithmetic(expression)
        except (SyntaxError, ValueError):
            pass
        else:
            raise AssertionError(f"受限解释器应拒绝：{expression!r}")


def test_codeact_uses_loopback_control_and_limits() -> None:
    config = codeact_executor_config()
    assert "additional_imports" not in config
    assert config["allow_pickle"] is False
    assert config["host"] == "127.0.0.1"
    assert config["container_run_kwargs"]["network_mode"] == "bridge"
    assert config["container_run_kwargs"]["cap_drop"] == ["ALL"]
    assert config["container_run_kwargs"]["security_opt"] == ["no-new-privileges"]


if __name__ == "__main__":
    test_json_tool_and_ast_evaluator()
    test_ast_guards_reject_code_and_unsafe_values()
    test_codeact_uses_loopback_control_and_limits()
    print("全部通过")
