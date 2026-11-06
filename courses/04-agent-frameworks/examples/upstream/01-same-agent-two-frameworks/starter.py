"""Stage 4 练习 1：同一个 agent、两个 framework — LangGraph + Ollama（Path A、默认）。

任务：搜索 + 摘要的小 agent。给一个 query、agent 用 search tool 拿资料、回一段摘要。
这份用 LangGraph。对照的 CrewAI 版本见 starter_crewai.py。

运行方法：
    pip install -r requirements.txt
    ollama pull gemma4:e4b
    ollama serve
    python starter.py

验证：
    python test.py

模型 API 预算：$0（Ollama）；本机硬体与电力仍有成本。对照 Anthropic 版见 starter_anthropic.py。
"""

# 保持问题和搜索资料相同，比较 LangGraph 的状态图与 CrewAI 的角色任务如何调用工具。

from __future__ import annotations

import os
import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# HumanMessage 标明用户输入的角色，避免把任务文字和工具观察混在一起。
# ToolMessage 带工具请求 ID，告诉模型哪次调用产生了这份观察结果。
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
# 消息 reducer 会合并新旧消息；节点只返回新增消息时，旧对话仍被保留而不会整段覆盖。
from langgraph.graph.message import add_messages
# Annotated 在类型上附带额外处理规则；这里的 reducer 决定状态更新时是追加消息还是覆盖旧消息。
# TypedDict 描述共享状态有哪些字段，便于读代码和静态检查；它本身不会替你做运行时数据验证。
from typing_extensions import Annotated, TypedDict

MODEL = os.environ.get("MODEL", "gemma4:e4b")


# === 模型可请求的工具 ===

@tool
def search(query: str) -> str:
    """按主题检索固定的离线教学资料；支持“台北”和 react agent 两个查询键。"""
    db = {
        "台北": "台北是台湾地区的城市，示例人口约 260 万，以夜市闻名。",
        "react agent": "ReAct（推理与行动）是一种让判断、行动与观察交替进行的 Agent 模式。",
    }
    return db.get(query.strip().lower(), f"没有此条目：{query}")


# === LangGraph 状态定义 ===

class State(TypedDict):
    # 把 add_messages 作为合并规则：新一轮消息追加到历史，而不是替换整段对话，工具结果才不会丢失。
    messages: Annotated[list, add_messages]


# 把节点和条件边连接成图；阅读分支函数，确认什么情况下继续、暂停或结束。
def build_graph(llm: Any) -> Any:
    """组一个 search → summarize 的图：LLM 看 query 决定要不要调用 search、看到 tool result 后给摘要。"""
    # 把工具说明提供给模型，使它能提出结构化调用；真正执行仍由后面的工具节点负责。
    llm_with_tools = llm.bind_tools([search])

    def agent_node(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    def tool_node(state: State):
        msg = state["messages"][-1]
        results = []
        for call in msg.tool_calls:
            name = call.get("name")
            args = call.get("args")
            # 模型给出的名称只是请求；执行前再次校验白名单，防止模型请求一个未授权函数。
            if name != "search":
                raise ValueError(f"未知工具：{name!r}")
            # 把输入边界一次检查清楚：必须是对象、只能有 query、值必须是字符串。Schema 描述本身不能替执行器做这项检查。
            if not isinstance(args, dict) or set(args) != {"query"} or not isinstance(args["query"], str):
                raise ValueError("search 只接受一个名为 query 的字符串参数。")
            # 直到名称和参数都通过验证才真正调用工具；返回值是观察数据，不是新的控制指令。
            obs = search.invoke(args)
            # 使用原请求 ID 封装工具观察，模型才能知道这份结果回答哪一次调用；多工具时尤其不能省略关联。
            results.append(ToolMessage(content=obs, tool_call_id=call["id"]))
        return {"messages": results}

    def should_continue(state: State) -> str:
        # 最新模型消息仍含工具请求就进入执行节点，否则结束；退出依据是协议字段，不是模型文字中写了“完成”。
        return "tools" if state["messages"][-1].tool_calls else END

    # 以 State 作为图中各节点共享的数据约定；每个节点返回自己的更新，数据通过状态传递而非隐式全局变量。
    g = StateGraph(State)
    # 把 agent 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    g.add_node("agent", agent_node)
    # 把 tools 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    g.add_node("tools", tool_node)
    # 把这个节点设为新任务的入口，明确第一步由谁处理。
    g.set_entry_point("agent")
    # 由路由函数返回目标名称，再通过这张映射选边；返回了未登记的名称就不能继续，路径必须可核对。
    g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    # 执行工具后回到模型，让模型依据观察决定继续调用还是给出答案。
    g.add_edge("tools", "agent")
    # 流程图到这里才完成组装；实际请求要等 run 中的 invoke，便于先检查图结构再执行。
    return g.compile()


def run(query: str, llm: Any = None) -> dict:
    """Public entrypoint: 跑一轮 agent、返回 final message + steps。"""
    llm = llm or ChatOpenAI(
        # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
        # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
        base_url="http://localhost:11434/v1", api_key="ollama",
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
        model=MODEL, temperature=0,
    )
    graph = build_graph(llm)
    # recursion_limit：限制图的执行步数，用来兜住意外循环；它不是 Python 函数递归深度。
    final_state = graph.invoke({"messages": [HumanMessage(content=query)]}, config={"recursion_limit": 6})
    return {
        "final": final_state["messages"][-1].content,
        "steps": len(final_state["messages"]),
    }


if __name__ == "__main__":
    query = "请根据工具中的固定资料，用中文概括台北的信息。"
    print(f"❓ 问题：{query}（使用 Ollama {MODEL}）")
    print("-" * 60)
    result = run(query)
    print(f"✅ 最终结果：{result['final']}")
    print(f"   消息条数：{result['steps']}")
    assert result["final"], "摘要不得为空"
    assert result["steps"] >= 2, "应保留可观察的图执行轨迹"
    print("✅ 练习 1 通过 — LangGraph + Ollama qwen2.5:3b、模型 API $0")
