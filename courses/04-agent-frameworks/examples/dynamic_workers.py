"""真实 LangGraph Send 与 reducer；工作函数固定，离线检验编排。"""

# 一个文档对应一个工作者输入；本例验证真实图的动态分发，不调用生成模型。
import argparse
import json
import operator
# Annotated 在类型上附带额外处理规则；这里的 reducer 决定状态更新时是追加消息还是覆盖旧消息。
# TypedDict 描述共享状态有哪些字段，便于读代码和静态检查；它本身不会替你做运行时数据验证。
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


# checks 使用加法 reducer 合并并行结果，避免后返回的结果覆盖前一个。
class State(TypedDict):
    documents: list[dict]
    checks: Annotated[list[dict], operator.add]
    report: dict


# 每个工作者只接收自己负责的文档，避免依赖未分配的共享输入。
class WorkerState(TypedDict):
    document: dict


# 先拒绝空输入和重复 ID，否则汇总时无法判断有没有漏查或覆盖。
def validate(state):
    documents = state['documents']
    ids = [doc['id'] for doc in documents]
    if not documents or len(ids) != len(set(ids)):
        raise ValueError('文档不能为空，ID 不能重复')
    return {'report': {}}


# 文档数量决定 Send 的数量；每条 Send 指定节点名和该节点收到的状态。
def dispatch(state):
    return [Send('check_document', {'document': doc}) for doc in state['documents']]


# 只检查约定的两个词，返回状态更新；不要把它当内容正确性审查。
def check_document(state: WorkerState):
    doc = state['document']
    missing = [word for word in ('目的', '运行') if word not in doc['text']]
    return {'checks': [{'id': doc['id'], 'missing': missing, 'ok': not missing}]}


# 先核对结果数量，再按 ID 排序；只有全部工作者通过，整份报告才通过。
def merge(state):
    checks = sorted(state['checks'], key=lambda row: row['id'])
    if len(checks) != len(state['documents']):
        raise ValueError('工作者结果不完整')
    return {'report': {'status': 'PASS' if all(x['ok'] for x in checks) else 'FAIL',
                       'checks': checks}}


def run(documents):
    # 以 State 作为图中各节点共享的数据约定；每个节点返回自己的更新，数据通过状态传递而非隐式全局变量。
    graph = StateGraph(State)
    # 把 validate 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    graph.add_node('validate', validate)
    # 把 check_document 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    graph.add_node('check_document', check_document)
    # 把 merge 注册为一个可调度节点；后面的连线使用这个名称找到对应处理函数。
    graph.add_node('merge', merge)
    # START 完成后进入 validate，将这两步的执行先后固定在程序中。
    graph.add_edge(START, 'validate')
    # dispatch 返回的 Send 决定这次有多少工作者，不是提前固定两条分支。
    # 由路由函数返回目标名称，再通过这张映射选边；返回了未登记的名称就不能继续，路径必须可核对。
    graph.add_conditional_edges('validate', dispatch, ['check_document'])
    # check_document 完成后进入 merge，将这两步的执行先后固定在程序中。
    graph.add_edge('check_document', 'merge')
    # merge 完成后进入 END，将这两步的执行先后固定在程序中。
    graph.add_edge('merge', END)
    # 把节点与连线变成可运行的图；这一步是组装流程，还没有替用户执行一次任务。
    return graph.compile().invoke({'documents': documents, 'checks': [], 'report': {}})['report']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--fixed', action='store_true')
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    docs = [{'id': 'a', 'text': '目的：演示。运行：python app.py'},
            {'id': 'b', 'text': '目的：核查。' + ('运行：python check.py' if args.fixed else '')}]
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(run(docs), ensure_ascii=False, indent=2))
