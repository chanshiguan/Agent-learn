r"""Stage 4 练习 2：用 CrewAI + Ollama 做有界的三角色交接。

3 个 agent 各有角色：
- Researcher 找资料（用 search tool）
- Writer 写稿（拿 researcher 的结果写成 blog 段落）
- Critic 审稿（检查 factual + tone）

这里使用 ``Process.sequential``，让三个角色像接力一样依序交接。

运行方法：
    py -3.11 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    ollama pull qwen2.5:3b
    ollama serve
    .\.venv\Scripts\python.exe starter.py

验证：
    .\.venv\Scripts\python.exe test.py

模型 API 预算：$0（Ollama）。执行时间依硬体、模型与 prompt 而变。
对照 Anthropic 版见 ``starter_anthropic.py``。
"""

# 沿着研究、写作、审核看资料如何传递；角色名字不能代替实际的任务上下文。

from __future__ import annotations

import os
import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool

MODEL = os.environ.get("MODEL", "ollama/qwen2.5:3b")
OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")


# === 模型可请求的工具 ===

# 查询固定教学资料，没有访问实时搜索服务；不存在的条目应明确返回缺失。
def search_knowledge_base(query: str) -> str:
    """查询固定的离线示范资料表，不代表真正的搜索引擎。"""
    db = {
        "react": "ReAct（Yao 等，2022）将判断、行动和观察组织成交替循环，是本课讨论的 Agent 模式之一。",
        "langgraph": "LangGraph 是 LangChain 提供的图式 Agent 编排框架，重点管理状态与检查点。",
        "crewai": "CrewAI 按角色组织多个 Agent；定义 Agent、Task 和 Crew 后，通过 kickoff() 启动任务。",
    }
    return db.get(query.strip().lower(), f"没有此条目：{query}")


@tool("search")
def search(query: str) -> str:
    """从固定的离线资料库返回一个条目。

    Args:
        query: 要查询的小写主题键，例如 ``react``。
    """
    return search_knowledge_base(query)


# 用固定研究结果演示交接资料，便于检查写作与审核是否收到必要证据。
def simulate_handoff(topic: str) -> dict[str, str]:
    """离线走完 Researcher → Writer → Critic，让交接结果可以直接测试。"""
    research = search_knowledge_base(topic)
    draft = f"{topic.title()}与 Agent 构建有关，资料如下：{research}"
    verdict = "PASS" if research != f"没有此条目：{topic}" and research in draft else "ISSUES: 缺少有来源的研究资料"
    return {"input": topic, "research": research, "draft": draft, "verdict": verdict, "stop_condition": "固定三个角色；每个 Agent 的迭代上限为 max_iter=4。"}


# === Crew 设计 ===

# 把角色和任务组织到同一个 Crew，重点看任务间的 context 如何传递。
def build_crew(topic: str, llm_model: str = MODEL) -> Crew:
    """建立三个固定角色；每个 agent 最多迭代四次且不能自行委派。"""
    os.environ["OPENAI_API_BASE"] = f"{OLLAMA_BASE}/v1"
    os.environ["OPENAI_API_KEY"] = "ollama"

    researcher = Agent(
        # role：说明这名 Agent 的职责，帮助拆分工作；角色名称本身不会自动创建独立权限或可靠协作。
        role='研究者',
        # goal：告诉这个角色要完成什么成果；与角色名称相比，具体目标更能决定它会寻找哪些信息。
        goal=f"从资料库检索以下主题的简洁事实：{topic}。",
        # backstory：给模型补充角色职责与工作方式；它影响生成行为，但不能替代执行层的工具权限检查。
        backstory="你负责检索资料库，并用中文返回未经编造的原始事实条目。",
        # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
        tools=[search],
        llm=llm_model,
        # verbose：关闭框架的详细过程输出，减少噪声；需要调试时查看明确记录的轨迹，而不是把终端文字当完整审计。
        verbose=False,
        # allow_delegation：禁止角色自行继续委派，保持本例只有明确安排的角色和任务，避免工作范围不断扩大。
        allow_delegation=False,
        # max_iter：限制这个角色自身的推理与工具迭代次数；多个角色仍会累加成本，需要分别设置上限。
        max_iter=4,
    )
    writer = Agent(
        # role：说明这名 Agent 的职责，帮助拆分工作；角色名称本身不会自动创建独立权限或可靠协作。
        role='写作者',
        # goal：告诉这个角色要完成什么成果；与角色名称相比，具体目标更能决定它会寻找哪些信息。
        goal=f"用两句中文介绍以下主题：{topic}.",
        # backstory：给模型补充角色职责与工作方式；它影响生成行为，但不能替代执行层的工具权限检查。
        backstory="你根据研究者提供的资料，写一段简洁的中文博客引言。",
        llm=llm_model,
        # verbose：关闭框架的详细过程输出，减少噪声；需要调试时查看明确记录的轨迹，而不是把终端文字当完整审计。
        verbose=False,
        # allow_delegation：禁止角色自行继续委派，保持本例只有明确安排的角色和任务，避免工作范围不断扩大。
        allow_delegation=False,
        # max_iter：限制这个角色自身的推理与工具迭代次数；多个角色仍会累加成本，需要分别设置上限。
        max_iter=4,
    )
    critic = Agent(
        # role：说明这名 Agent 的职责，帮助拆分工作；角色名称本身不会自动创建独立权限或可靠协作。
        role='审核者',
        # goal：告诉这个角色要完成什么成果；与角色名称相比，具体目标更能决定它会寻找哪些信息。
        goal="核对写作者的引言是否有研究资料支持，并检查语气是否合适。",
        # backstory：给模型补充角色职责与工作方式；它影响生成行为，但不能替代执行层的工具权限检查。
        backstory="你是严格的编辑，负责指出没有依据的内容和语气问题，并用中文说明。",
        llm=llm_model,
        # verbose：关闭框架的详细过程输出，减少噪声；需要调试时查看明确记录的轨迹，而不是把终端文字当完整审计。
        verbose=False,
        # allow_delegation：禁止角色自行继续委派，保持本例只有明确安排的角色和任务，避免工作范围不断扩大。
        allow_delegation=False,
        # max_iter：限制这个角色自身的推理与工具迭代次数；多个角色仍会累加成本，需要分别设置上限。
        max_iter=4,
    )

    research_task = Task(
        description=f"检索主题 `{topic}`，用中文报告查到的资料。",
        # expected_output：说明任务应交付什么，方便下一角色消费和人工核对；这段文字并不是自动验证器。
        expected_output="从资料库取得的一到两句中文事实说明。",
        # agent：明确由哪个角色执行任务，防止任务说明存在却没有实际执行者。
        agent=researcher,
    )
    write_task = Task(
        description="使用研究者的资料，写两句中文博客引言。",
        # expected_output：说明任务应交付什么，方便下一角色消费和人工核对；这段文字并不是自动验证器。
        expected_output="由两句中文组成的引言段落。",
        # agent：明确由哪个角色执行任务，防止任务说明存在却没有实际执行者。
        agent=writer,
        # context：把前面任务的实际结果交给当前任务。只在提示词里提到“研究者”并不能自动传递研究资料。
        context=[research_task],
    )
    critic_task = Task(
        description="检查引言是否得到研究资料支持。"
                    "没有问题时报告 PASS，否则用中文列出问题。",
        # expected_output：说明任务应交付什么，方便下一角色消费和人工核对；这段文字并不是自动验证器。
        expected_output="输出 'PASS: [中文引言]' 或 'ISSUES: [中文问题列表]'。",
        # agent：明确由哪个角色执行任务，防止任务说明存在却没有实际执行者。
        agent=critic,
        # context：把前面任务的实际结果交给当前任务。只在提示词里提到“研究者”并不能自动传递研究资料。
        context=[research_task, write_task],
    )

    return Crew(
        # agents：列出这次协作允许使用的角色；固定名单使参与者和成本范围可检查。
        agents=[researcher, writer, critic],
        # tasks：按工作顺序列出任务；任务顺序应与资料依赖一致，而不是为了多个 Agent 而拆分。
        tasks=[research_task, write_task, critic_task],
        # process：选择任务调度方式；sequential 让前一任务完成后再进入下一任务，不代表并行执行。
        process=Process.sequential,
        # verbose：关闭框架的详细过程输出，减少噪声；需要调试时查看明确记录的轨迹，而不是把终端文字当完整审计。
        verbose=False,
    )


def run(topic: str, llm_model: str = MODEL) -> dict:
    """执行 crew，并把最终结果与可观察的停止条件一起返回。"""
    crew = build_crew(topic, llm_model=llm_model)
    # 让 Crew 真正开始按任务依赖执行；创建 Agent 和 Task 对象本身不会产生最终工作成果。
    result = crew.kickoff()
    return {"final": str(result), "topic": topic, "stop_condition": "固定三个角色；每个 Agent 的迭代上限为 max_iter=4。"}


if __name__ == "__main__":
    topic = "react"
    print(f"❓ 主题：{topic}（使用 CrewAI 和 Ollama {MODEL}）")
    print(f"   三个角色：研究者 → 写作者 → 审核者（顺序执行）")
    print("-" * 60)
    result = run(topic)
    print(f"✅ 最终结果（审核者判定）：\n{result['final']}")
    assert result["final"], "审核者应给出明确判定"
    assert "max_iter=4" in result["stop_condition"]
    print("\n✅ 练习 2 通过 — 3-agent crew 跑完、模型 API $0")
