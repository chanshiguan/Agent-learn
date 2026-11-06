"""Stage 4 练习 4：比较有界 CodeAct 与安全的 JSON tool 算术路径。

JSON tool 只允许固定工具与固定参数；算式先转成 AST，再逐节点检查。
CodeAct 会执行模型产生的 Python，所以只在受限制的 Docker 容器里示范。
Jupyter 控制埠只绑到主机的 127.0.0.1；容器仍可能连网，因此这不是 production
sandbox。两条路都设有步数与输入边界。
"""

# 比较 JSON 参数调用与代码行动；算术用 AST 白名单，CodeAct 的执行依赖受限 Docker。

from __future__ import annotations

import ast
import os
import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from smolagents import CodeAgent, OpenAIServerModel, ToolCallingAgent, tool

MODEL = os.environ.get("MODEL", "qwen2.5:3b")
OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434/v1")
MAX_AST_NODES = 40
MAX_NUMBER = 1_000_000


# 解析表达式后只允许约定的算术节点，并限制数值与表达式规模。
def evaluate_arithmetic(expression: str) -> float:
    """只计算小型算术 AST；模型文字不会交给 ``eval`` 或 ``exec``。"""
    if not isinstance(expression, str) or len(expression) > 120:
        raise ValueError("表达式必须是最多 120 字符的字符串。")
    # 只把模型源码解析为语法树，不运行它；后面还要逐节点白名单检查，解析成功不代表安全。
    tree = ast.parse(expression, mode="eval")
    if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
        raise ValueError("表达式过于复杂。")

    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = float(node.value)
            if abs(value) > MAX_NUMBER:
                raise ValueError("数值的绝对值超出允许范围。")
            return value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            return visit(node.operand) if isinstance(node.op, ast.UAdd) else -visit(node.operand)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
            if right == 0: raise ValueError("除数不能为零。")
            return left / right
        raise ValueError(f"不支持的算术语法：{type(node).__name__}")

    value = visit(tree)
    if abs(value) > MAX_NUMBER:
        raise ValueError("计算结果的绝对值超出允许范围。")
    return value


@tool
def calculator(expression: str) -> str:
    """在长度和数值范围限制内计算一个简单算术表达式。

    Args:
        expression: 只允许数字、括号，以及 +、-、*、/ 四种运算符。
    """
    try:
        return str(evaluate_arithmetic(expression))
    except (SyntaxError, ValueError) as error:
        return f"错误：{error}"


@tool
def lookup_fact(query: str) -> str:
    """只从固定白名单返回一项离线事实。

    Args:
        query: Either ``台北人口`` or ``纽约人口``.
    """
    facts = {'台北人口': "2602000", '纽约人口': "8336000"}
    return facts.get(query.strip().lower(), f"未知条目：{query}")


# 先验证工具名称和参数，再执行对应函数；模型字符串不会被当 Python 程序运行。
def run_json_tool_call(call: dict[str, Any]) -> str:
    """JSON tool 边界：工具名、参数形状与算式都要先通过检查。"""
    if not isinstance(call, dict) or set(call) != {"name", "arguments"}:
        raise ValueError("工具请求必须且只能包含 name 和 arguments。")
    if call["name"] != "calculator" or not isinstance(call["arguments"], dict) or set(call["arguments"]) != {"expression"}:
        raise ValueError("只允许调用 calculator，并传入 expression 参数。")
    return calculator.forward(expression=call["arguments"]["expression"])


# Docker 控制通道与容器执行权限分开设置；有配置仍要通过真实容器测试。
def codeact_executor_config() -> dict[str, Any]:
    """缩小示范容器权限，并把 Jupyter 控制埠只绑到本机。"""
    return {
        "allow_pickle": False,
        "host": "127.0.0.1",
        "container_run_kwargs": {
            "network_mode": "bridge",
            "mem_limit": "256m",
            "pids_limit": 64,
            "cap_drop": ["ALL"],
            "security_opt": ["no-new-privileges"],
        },
    }


# 把模型接到 CodeAgent 和受限执行器，运行前需要对应 Docker 环境。
def build_codeact_agent(model: Any | None = None, executor_type: str = "docker") -> CodeAgent:
    """建立最多走四步、且预设只在 Docker 里执行程序码的 agent。"""
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    model = model or OpenAIServerModel(model_id=MODEL, api_base=OLLAMA_BASE, api_key="ollama")
    executor_kwargs = codeact_executor_config() if executor_type == "docker" else {}
    # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    # max_steps：限制循环最多执行多少步；它是程序的停止条件，不能只在提示词里写“不要无限循环”。
    return CodeAgent(tools=[calculator, lookup_fact], model=model, max_steps=4, additional_authorized_imports=[], executor_type=executor_type, executor_kwargs=executor_kwargs)


# 模型通过结构化工具请求行动，工具内部仍负责输入检查。
def build_json_agent(model: Any) -> ToolCallingAgent:
    """建立同工具集合的 JSON tool 对照组。"""
    # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    # max_steps：限制循环最多执行多少步；它是程序的停止条件，不能只在提示词里写“不要无限循环”。
    return ToolCallingAgent(tools=[calculator, lookup_fact], model=model, max_steps=4)


def run(question: str, model: Any | None = None) -> dict[str, str]:
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    agent = build_codeact_agent(model=model)
    try:
        return {"final": str(agent.run(question))}
    # 无论成功还是失败，都执行这里的收尾步骤。
    finally:
        agent.cleanup()


if __name__ == "__main__":
    result = run("查询台北人口和纽约人口，用台北人口除以纽约人口，并报告比值。")
    print(result["final"])
    assert result["final"]
    assert run_json_tool_call({"name": "calculator", "arguments": {"expression": "2 + 3 * 4"}}) == "14.0"
