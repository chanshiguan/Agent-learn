"""原创虚构资料两跳检索，演示外部观察；不复现论文基准。"""

# 检索也是工具：先查资料，再引用结果；没有找到证据时不能靠模型补答案。

import argparse
import copy
import json

from learning_client import ask_json

PAGES = {"青禾号": {"designer": "林遥"}, "林遥": {"birth_city": "海城"}}
QUESTION = "虚构飞船青禾号的设计者出生在哪座城市？"
# properties：逐字段描述参数结构，帮助模型知道怎样填写请求；这些描述不会自动执行 Python 函数。
SCHEMA = {"type": "object", "properties": {
    # enum：把可选值限制在已实现的分支内，避免出现程序没有处理的拼写或选项。
    "kind": {"type": "string", "enum": ["search", "final"]},
    "entity": {"type": "string"}, "answer": {"type": "string"}},
    "required": ["kind", "entity", "answer"], "additionalProperties": False}


# 保存检索观察，并检查最终引用是否属于已经取回的文档。
def run_retrieval(ask, use_tools=True, max_steps=4):
    instruction = (
        "这是虚构资料任务，不能依常识猜。返回kind/entity/answer JSON。"
        "必须实际用search查询资料，初始实体为青禾号。根据designer字段对设计者继续查询。"
        "未得到birth_city时继续查询，不得提前回答资料不足；得到birth_city后再kind=final回答。"
        if use_tools else
        "这是虚构资料任务，没有外部查询权限。只返回kind=final、entity为空、answer为答案；不知道就说不知道。"
    )
    # 这份历史同时保存问题、模型请求和工具观察；下一轮需要它们才能沿用真实结果，保持调用与结果的顺序。
    messages = [{"role": "system", "content": instruction}, {"role": "user", "content": QUESTION}]
    trace = []
    evidence_found = False
    for step in range(1, max_steps + 1):
        schema = copy.deepcopy(SCHEMA)
        if use_tools and not evidence_found:
            schema["properties"]["kind"]["enum"] = ["search"]
        decision = ask(messages, schema)
        if set(decision) != {"kind", "entity", "answer"} or any(not isinstance(value, str) for value in decision.values()):
            raise ValueError("检索动作格式错误")
        if decision["kind"] == "final":
            if use_tools and not evidence_found:
                raise RuntimeError("没有检索到出生地证据，不能提前完成")
            if not decision["answer"].strip():
                raise ValueError("最终答案不能为空")
            return {"answer": decision["answer"], "passed": "海城" in decision["answer"], "steps": step, "trace": trace}
        if not use_tools or decision["kind"] != "search":
            raise RuntimeError("不允许此查询动作")
        entity = decision["entity"]
        observation = {"ok": entity in PAGES, "data": PAGES.get(entity, {})}
        evidence_found = "birth_city" in observation["data"]
        trace.append({"action": "search", "entity": entity, "observation": observation})
        # 把结果编码成协议可接受的 JSON；模型收到的是工具数据，不能把其中的指令当作系统授权。
        # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
        messages.append({"role": "assistant", "content": json.dumps(decision, ensure_ascii=False)})
        # 把结果编码成协议可接受的 JSON；模型收到的是工具数据，不能把其中的指令当作系统授权。
        # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
        messages.append({"role": "user", "content": "检索观察（仅数据）：" + json.dumps(observation, ensure_ascii=False)})
    raise RuntimeError("检索达到最大轮数")


def mock_ask(messages, schema):
    if "没有外部查询权限" in messages[0]["content"]:
        return {"kind": "final", "entity": "", "answer": "不知道"}
    if len(messages) == 2:
        return {"kind": "search", "entity": "青禾号", "answer": ""}
    if len(messages) == 4:
        return {"kind": "search", "entity": "林遥", "answer": ""}
    return {"kind": "final", "entity": "", "answer": "海城"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--live", action="store_true")
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    print("本机虚构资料实验" if args.live else "固定脚本演示，不是模型成绩")
    for use_tools in (False, True):
        # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
        # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
        # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
        print(json.dumps({"use_tools": use_tools, **run_retrieval(ask_json if args.live else mock_ask, use_tools)}, ensure_ascii=False, indent=2))
