"""真实 LangGraph：固定证据摘要→来源检查→人工批准；SQLite 跨进程恢复。"""

# 先读 execute 的新建/恢复分支，再看 build 的连接关系和三个节点。
import argparse
import json
from pathlib import Path
# TypedDict 描述共享状态有哪些字段，便于读代码和静态检查；它本身不会替你做运行时数据验证。
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
# interrupt 会把图暂停在审核点并保存待处理信息；收到恢复值之前，后续节点不会继续执行。
# Command 携带恢复值或跳转信息；恢复暂停节点时要将人的决定放入 resume。
from langgraph.types import interrupt, Command
# SQLite 检查点把状态写入磁盘，因此可在另一个进程恢复；外部动作是否重复仍需幂等控制。
from langgraph.checkpoint.sqlite import SqliteSaver

SOURCES = {'course-3': '工具调用由模型提出，应用执行，并把结果交回模型。'}


# 这些字段描述共享状态的形状；TypedDict 本身不执行运行时校验。
# 节点只返回自己更新的字段，状态会逐步补齐，因此 total=False 允许字段暂时缺失；TypedDict 不负责运行时拦截坏数据。
class State(TypedDict, total=False):
    topic: str
    # draft：保存尚未批准的候选内容，把“生成成功”和“允许发布”分成两个不同阶段。
    draft: str
    source_ids: list[str]
    checked: bool
    status: str
    published: bool


def summarize(state):
    # 固定摘录让本题只考流程；真实生成可以替换此节点，仍须走后续检查。
    return {'draft': SOURCES.get(state['topic'], ''),
            'source_ids': [state['topic']] if state['topic'] in SOURCES else [], 'published': False}


# 本题要求草稿等于固定资料摘录，来源存在且内容匹配才进入人工审核。
def check_sources(state):
    refs = state['source_ids']
    valid = bool(refs) and all(x in SOURCES for x in refs)
    valid = valid and state['draft'] == '\n'.join(SOURCES[x] for x in refs)
    return {'checked': valid, 'status': 'awaiting_review' if valid else 'blocked'}


# interrupt 暂停后等待外部传入布尔决定；恢复时本节点可能从头再跑。
def review(state):
    # 把待审草稿带到暂停事件中，等待人给出明确决定；恢复时该节点可能重新执行，暂停前不要放不可重复的外部动作。
    decision = interrupt({'draft': state['draft'], 'source_ids': state['source_ids'],
                          'action': '仅标记本地接受，不向外发布'})
    if type(decision) is not bool:
        raise ValueError('批准必须为布尔值')
    return {'status': 'accepted' if decision else 'rejected', 'published': decision}


# 来源检查失败直接结束，通过才进入 review；检查点由调用者传入。
def build(saver):
    # 以 State 作为图中各节点共享的数据约定；每个节点返回自己的更新，数据通过状态传递而非隐式全局变量。
    g = StateGraph(State)
    # 把 summarize 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    g.add_node('summarize', summarize)
    # 把 check 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    g.add_node('check', check_sources)
    # 把 review 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    g.add_node('review', review)
    # START 完成后进入 summarize，将这两步的执行先后固定在程序中。
    g.add_edge(START, 'summarize')
    # summarize 完成后进入 check，将这两步的执行先后固定在程序中。
    g.add_edge('summarize', 'check')
    # 由路由函数返回目标名称，再通过这张映射选边；返回了未登记的名称就不能继续，路径必须可核对。
    g.add_conditional_edges('check', lambda s: 'review' if s['checked'] else END)
    # review 完成后进入 END，将这两步的执行先后固定在程序中。
    g.add_edge('review', END)
    # 把节点与连线变成可运行的图；这一步是组装流程，还没有替用户执行一次任务。
    # checkpointer：把图的中间状态交给检查点保存器；暂停后恢复需要这份状态，单靠再次调用图无法找回进度。
    return g.compile(checkpointer=saver)


# 同一数据库和 thread_id 才指向同一个任务；已结束任务不能再次批准。
def execute(database, thread, topic='course-3', decision=None):
    # 运行配置必须在暂停和恢复时保持同一个会话标识，否则恢复会找不到刚才待审核的状态。
    # configurable：传递可在每次运行时指定的图配置；会话标识放在这里，供检查点系统定位历史状态。
    # thread_id：定位同一条工作流的检查点。暂停和恢复必须使用同一个值；换值通常会进入另一条会话。
    config = {'configurable': {'thread_id': thread}}
    # 检查点写入磁盘，下一进程使用同一数据库和 thread_id 才能继续。
    # 打开检查点数据库连接；路径决定保存在哪里，后续进程必须打开同一个库才能恢复。
    with SqliteSaver.from_conn_string(str(database)) as saver:
        graph = build(saver)
        # 读取指定会话已经保存的状态，用来确认暂停位置和待审核内容，而不是重新生成草稿。
        snapshot = graph.get_state(config)
        if decision is None:
            if snapshot.values:
                raise ValueError('任务编号已存在；请恢复任务或换新编号')
            graph.invoke({'topic': topic}, config)
        else:
            if not snapshot.next or snapshot.values.get('status') != 'awaiting_review':
                raise ValueError('该任务不在等待批准状态，不能重复或越过批准')
            # 把外部决定交回原暂停点，不重新创建一个跳过检查的新任务。
            graph.invoke(Command(resume=decision), config)
        # 读取指定会话已经保存的状态，用来确认暂停位置和待审核内容，而不是重新生成草稿。
        snapshot = graph.get_state(config)
        return {'state': snapshot.values, 'next': list(snapshot.next)}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    # required：明确哪些字段不可缺少；有默认值与必须提供是两种不同的接口约定。
    p.add_argument('--db', type=Path, required=True)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    # required：明确哪些字段不可缺少；有默认值与必须提供是两种不同的接口约定。
    p.add_argument('--thread', required=True)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    p.add_argument('--topic', default='course-3')
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    p.add_argument('--decision', choices=['accept', 'reject'])
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    a = p.parse_args()
    decision = None if a.decision is None else a.decision == 'accept'
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(execute(a.db, a.thread, a.topic, decision), ensure_ascii=False, indent=2))
