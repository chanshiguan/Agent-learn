"""Stage 4 练习 1：同一个 agent、CrewAI 版本对照（Ollama 预设）。

跟 starter.py (LangGraph) 同一个任务：search + summarize。
看程序码风格差异——CrewAI 用 Agent + Task 抽象、LangGraph 用 StateGraph + node。

运行方法：
    pip install -r requirements.txt   # 含 crewai
    ollama pull gemma4:e4b
    ollama serve
    python starter_crewai.py

模型 API 预算：$0（Ollama）；本机硬体与电力仍有成本。

⚠️ 注意：模型、prompt 与工具描述都可能改变步数；用相同题组比较，不先假设哪个 backend 较稳。
"""

# 保持问题和搜索资料相同，比较 LangGraph 的状态图与 CrewAI 的角色任务如何调用工具。

from __future__ import annotations

import os
import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from crewai import Agent, Crew, Task
from crewai.tools import tool

MODEL = os.environ.get("MODEL", "ollama/gemma4:e4b")  # LiteLLM 用提供商前缀识别请求应交给哪种后端
OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")


# 查询固定教学资料，没有访问实时搜索服务；不存在的条目应明确返回缺失。
def search_knowledge_base(query: str) -> str:
    """按主题检索固定的离线教学资料；支持“台北”和 react agent 两个查询键。"""
    db = {
        "台北": "台北是台湾地区的城市，示例人口约 260 万，以夜市闻名。",
        "react agent": "ReAct（推理与行动）是一种让判断、行动与观察交替进行的 Agent 模式。",
    }
    return db.get(query.strip().lower(), f"没有此条目：{query}")


@tool("search")
def search(query: str) -> str:
    """检索本例固定的离线资料库。"""
    return search_knowledge_base(query)


# 把角色和任务组织到同一个 Crew，重点看任务间的 context 如何传递。
def build_crew(query: str, llm_model: str = MODEL) -> Crew:
    """CrewAI 风格：一个 agent + 一个 task。"""
    os.environ["OPENAI_API_BASE"] = f"{OLLAMA_BASE}/v1"
    os.environ["OPENAI_API_KEY"] = "ollama"

    researcher = Agent(
        # role：说明这名 Agent 的职责，帮助拆分工作；角色名称本身不会自动创建独立权限或可靠协作。
        role='研究者',
        # goal：告诉这个角色要完成什么成果；与角色名称相比，具体目标更能决定它会寻找哪些信息。
        goal="查找指定主题，并用中文概括检索到的资料。",
        # backstory：给模型补充角色职责与工作方式；它影响生成行为，但不能替代执行层的工具权限检查。
        backstory="你负责检索资料库，并用中文给出简洁摘要。",
        # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
        tools=[search],
        llm=llm_model,
        # verbose：关闭框架的详细过程输出，减少噪声；需要调试时查看明确记录的轨迹，而不是把终端文字当完整审计。
        verbose=False,
    )
    task = Task(
        description=query,
        # expected_output：说明任务应交付什么，方便下一角色消费和人工核对；这段文字并不是自动验证器。
        expected_output="依据检索结果写成的一到两句中文摘要。",
        # agent：明确由哪个角色执行任务，防止任务说明存在却没有实际执行者。
        agent=researcher,
    )
    # agents：列出这次协作允许使用的角色；固定名单使参与者和成本范围可检查。
    # tasks：按工作顺序列出任务；任务顺序应与资料依赖一致，而不是为了多个 Agent 而拆分。
    # verbose：关闭框架的详细过程输出，减少噪声；需要调试时查看明确记录的轨迹，而不是把终端文字当完整审计。
    return Crew(agents=[researcher], tasks=[task], verbose=False)


def run(query: str, llm_model: str = MODEL) -> dict:
    crew = build_crew(query, llm_model=llm_model)
    # 让 Crew 真正开始按任务依赖执行；创建 Agent 和 Task 对象本身不会产生最终工作成果。
    result = crew.kickoff()
    return {"final": str(result), "steps": None}


if __name__ == "__main__":
    query = "请根据工具中的固定资料，用中文概括台北的信息。"
    print(f"❓ 问题：{query}（使用 CrewAI 和 Ollama {MODEL}）")
    print("-" * 60)
    result = run(query)
    print(f"✅ 最终结果：{result['final']}")
    assert result["final"], "摘要不得为空"
    assert result["steps"] is None
    print("✅ CrewAI 版本通过 — 同样任务、不同 framework、模型 API $0")
    print("   对照 starter.py（LangGraph）看程序码风格差异")
