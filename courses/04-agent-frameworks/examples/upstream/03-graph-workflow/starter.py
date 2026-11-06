"""Stage 4 练习 3：用 LangGraph 做条件分支与真正可暂停的 HITL。

流程像一条有岔路的轨道：先判断要不要查资料，再请模型写草稿，
接着用 ``interrupt()`` 停下来等人决定。只有收到 ``Command(resume=...)``
之后，图才会继续走到发布或拒绝。Path A 使用 Ollama；Path B 共用同一张图。
"""

# 先分类选择是否检索，再暂停等待决定；内存检查点只保留在当前进程中。

from __future__ import annotations

import os
import sys
# Literal 把允许返回的路由名写进类型说明，帮助核对条件边是否有对应目标。
from typing import Any, Literal

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langchain_openai import ChatOpenAI
# 内存检查点能在同一进程内暂停和恢复；进程退出就丢失，跨进程演示应使用后面的磁盘保存器。
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
# Command 携带恢复值或跳转信息；恢复暂停节点时要将人的决定放入 resume。
# interrupt 会把图暂停在审核点并保存待处理信息；收到恢复值之前，后续节点不会继续执行。
from langgraph.types import Command, interrupt
# TypedDict 描述共享状态有哪些字段，便于读代码和静态检查；它本身不会替你做运行时数据验证。
from typing_extensions import TypedDict

MODEL = os.environ.get("MODEL", "gemma4:e4b")


# 节点只返回自己更新的字段，状态会逐步补齐，因此 total=False 允许字段暂时缺失；TypedDict 不负责运行时拦截坏数据。
class State(TypedDict, total=False):
    # query：保留最初的问题，后续分类、检索与生成都围绕它工作；不要把检索结果覆盖成新的用户问题。
    query: str
    # needs_search：分类节点写入的路由决定，条件边据此选择检索或直接回答；这是程序规则，不是模型自行授权。
    needs_search: bool
    # search_result：保存实际查到的资料，生成节点必须读取这个字段，才有依据给出草稿。
    search_result: str
    # draft：保存尚未批准的候选内容，把“生成成功”和“允许发布”分成两个不同阶段。
    draft: str
    # approved：保存人工审核的布尔决定；必须明确为真或假，不能把任意非空字符串当作同意。
    approved: bool
    # final：保存审核之后的结果，供调用方确认本次最终是批准还是拒绝；本例的状态文字不代表真实外部发布。
    final: str


# 先确定任务类别，再把结果写回状态，后面的条件边据此选路。
def classify_node(state: State) -> dict[str, bool]:
    """用几个示范关键字决定要不要先走离线查询节点。"""
    # 把检索关键词中的英文统一为小写，避免大小写差异改变路由；中文字符保持原样。
    query = state["query"].lower()
    return {"needs_search": any(word in query for word in ("population", "weather", "latest", "人口", "天气", "最新"))}


# 将检索结果写入状态，后续生成节点需要实际读到这些资料。
def search_node(state: State) -> dict[str, str]:
    """从很小的离线资料表取值；这里不代表真正的搜索引擎。"""
    for key, value in {"taipei": "台北人口：约 260 万（固定教学数据）。", "台北": "台北人口：约 260 万（固定教学数据）。", "天气": "示例天气：晴，25 摄氏度。"}.items():
        if key in state["query"].lower():
            return {"search_result": value}
    return {"search_result": "离线资料库中没有匹配条目。"}


# 只决定下一条边，不在这个判断函数里执行检索。
def should_search(state: State) -> Literal["search", "respond"]:
    # 返回的是条件边要使用的目标名称；这里只选路，不执行检索，也不会生成回答。
    return "search" if state["needs_search"] else "respond"


def make_ollama_llm() -> ChatOpenAI:
    """用 OpenAI-compatible 接口连到本机 Ollama。"""
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
    return ChatOpenAI(model=MODEL, base_url="http://localhost:11434/v1", api_key="ollama", temperature=0)


# 把节点和条件边连接成图；阅读分支函数，确认什么情况下继续、暂停或结束。
def build_graph(llm: Any, checkpointer: Any | None = None) -> Any:
    """建立共用图；调用方可放入 Ollama 或 Anthropic chat model。"""
    def respond_node(state: State) -> dict[str, str]:
        # 直接回答路径不会产生 search_result，因此提供明确的缺省说明；不能为了缺字段伪造一条检索结果。
        context = state.get("search_result", "本次无需检索。")
        message = llm.invoke(f"请谨慎地用一句中文回答：{state['query']}\n离线资料：{context}")
        # 框架通常返回带 content 的消息对象，离线替身也可能直接返回文本；统一取正文并去除空白后才能判断是否真的有草稿。
        draft = str(getattr(message, "content", message)).strip()
        if not draft:
            raise RuntimeError("模型返回了空草稿。")
        return {"draft": draft}

    def review_node(state: State) -> dict[str, bool]:
        # 把待审草稿带到暂停事件中，等待人给出明确决定；恢复时该节点可能重新执行，暂停前不要放不可重复的外部动作。
        decision = interrupt({"action": "publish", "draft": state["draft"], "question": "是否批准这份草稿？"})
        # 只接受真正的布尔决定；字符串 "false" 在 Python 中也是真值，若直接判断真假会把拒绝误当作批准。
        if not isinstance(decision, bool):
            raise ValueError("人工审核必须用 true 或 false 恢复流程。")
        return {"approved": decision}

    def final_node(state: State) -> dict[str, str]:
        # 把批准与拒绝分支明确区分，供测试核对路由；这里仅生成教学状态文本，没有调用真实发布接口。
        prefix = "PUBLISHED" if state["approved"] else "REJECTED"
        # 把审核结论和对应草稿一起交还调用方，使人能确认被批准或拒绝的到底是哪一份内容。
        return {"final": f"{prefix}: {state['draft']}"}

    # 以 State 作为图中各节点共享的数据约定；每个节点返回自己的更新，数据通过状态传递而非隐式全局变量。
    graph = StateGraph(State)
    # 把 classify 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    graph.add_node("classify", classify_node)
    # 把 search 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    graph.add_node("search", search_node)
    # 把 respond 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    graph.add_node("respond", respond_node)
    # 把 review 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    graph.add_node("review", review_node)
    # 把 final 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    graph.add_node("final", final_node)
    # 每次新任务先分类，避免所有问题都机械地检索。
    graph.add_edge(START, "classify")
    # 由路由函数返回目标名称，再通过这张映射选边；返回了未登记的名称就不能继续，路径必须可核对。
    graph.add_conditional_edges("classify", should_search, {"search": "search", "respond": "respond"})
    # 检索完成后必须把结果交给生成节点，保证草稿用的是实际资料。
    graph.add_edge("search", "respond")
    # 生成草稿后进入人工审核，不能直接把模型输出视为已获批准。
    graph.add_edge("respond", "review")
    # 只有审核节点取得决定后才进入最终分支，保持生成与授权分开。
    graph.add_edge("review", "final")
    # 批准或拒绝都在这里结束，避免完成之后意外继续循环。
    graph.add_edge("final", END)
    # 把节点与连线变成可运行的图；这一步是组装流程，还没有替用户执行一次任务。
    # checkpointer：把图的中间状态交给检查点保存器；暂停后恢复需要这份状态，单靠再次调用图无法找回进度。
    return graph.compile(checkpointer=checkpointer or InMemorySaver())


def run(query: str, approve: bool, llm: Any | None = None, thread_id: str = "stage4-demo") -> dict[str, Any]:
    """先跑到人工审核点，再用同一个 ``thread_id`` 恢复执行。"""
    graph = build_graph(llm or make_ollama_llm())
    # 运行配置必须在暂停和恢复时保持同一个会话标识，否则恢复会找不到刚才待审核的状态。
    # configurable：传递可在每次运行时指定的图配置；会话标识放在这里，供检查点系统定位历史状态。
    # thread_id：定位同一条工作流的检查点。暂停和恢复必须使用同一个值；换值通常会进入另一条会话。
    config = {"configurable": {"thread_id": thread_id}}
    # 第一次运行应停在人工审核点；此时只有待审草稿，不能声称已经发布。
    paused = graph.invoke({"query": query}, config=config)
    if "__interrupt__" not in paused:
        raise RuntimeError("发布前应先暂停并等待人工审核。")
    # 把明确的批准或拒绝传回同一工作流；后面的检查用实际恢复结果判断是否完成。
    resumed = graph.invoke(Command(resume=approve), config=config)
    if not resumed.get("final"):
        raise RuntimeError("恢复后未生成最终结果。")
    return resumed


if __name__ == "__main__":
    approved = run("台北人口是多少？", approve=True)
    # thread_id：定位同一条工作流的检查点。暂停和恢复必须使用同一个值；换值通常会进入另一条会话。
    rejected = run("请介绍 Python", approve=False, thread_id="stage4-reject")
    print(approved["final"])
    print(rejected["final"])
    assert approved["final"].startswith("PUBLISHED:")
    assert rejected["final"].startswith("REJECTED:")
