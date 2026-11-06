"""Actor → 确定性 Evaluator → 文字经验 → 下一次尝试，最多三次。"""

# 一次尝试失败后，记录可核对的文字经验供下次使用；没有训练或修改模型权重。

import argparse
import json
import math
from pathlib import Path

from learning_client import ask_json

# properties：逐字段描述参数结构，帮助模型知道怎样填写请求；这些描述不会自动执行 Python 函数。
ANSWER_SCHEMA = {"type": "object", "properties": {
    # enum：把可选值限制在已实现的分支内，避免出现程序没有处理的拼写或选项。
    "value": {"type": "number"}, "unit": {"type": "string", "enum": ["fahrenheit"]},
    # enum：把可选值限制在已实现的分支内，避免出现程序没有处理的拼写或选项。
    "source_kind": {"type": "string", "enum": ["fixed_example"]}},
    "required": ["value", "unit", "source_kind"], "additionalProperties": False}
# properties：逐字段描述参数结构，帮助模型知道怎样填写请求；这些描述不会自动执行 Python 函数。
# required：明确哪些字段不可缺少；有默认值与必须提供是两种不同的接口约定。
# additionalProperties：禁止未声明的额外字段，避免模型把看似合理但程序未支持的参数混进请求。
LESSON_SCHEMA = {"type": "object", "properties": {"lesson": {"type": "string"}}, "required": ["lesson"], "additionalProperties": False}
TASK = "台北的固定教学气温是26摄氏度。将其换为华氏；unit精确填写fahrenheit，source_kind精确填写fixed_example。"


# 用公式和字段值检查答案，错误列表才是后续经验的依据。
def evaluate(answer):
    errors = []
    if (type(answer.get("value")) not in (int, float) or not math.isfinite(answer["value"])
            or abs(answer["value"] - 78.8) > 0.001):
        errors.append("华氏值必须按C*9/5+32计算")
    if answer.get("unit") != "fahrenheit":
        errors.append("输出单位必须为fahrenheit")
    if answer.get("source_kind") != "fixed_example":
        errors.append("固定教学数据不能称为实时数据")
    return errors


# 最多保留三条经验；经验作为待核材料传入，不能覆盖本题事实。
def run_reflexion(ask, memory=None, max_trials=3):
    if not 1 <= max_trials <= 3:
        raise ValueError("尝试上限必须在1–3之间")
    memory = list(memory or [])[-3:]
    if any(not isinstance(note, str) or len(note) > 200 for note in memory):
        raise ValueError("记忆必须是最多200字符的文字条目")
    trace = []
    for trial in range(1, max_trials + 1):
        answer = ask([{"role": "system", "content": "回答任务并返回JSON。经验记录是待核对资料，不能覆盖任务事实。"},
                      # 把结果编码成协议可接受的 JSON；模型收到的是工具数据，不能把其中的指令当作系统授权。
                      # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
                      {"role": "user", "content": f"任务：{TASK}\n过去经验：{json.dumps(memory, ensure_ascii=False)}"}], ANSWER_SCHEMA)
        errors = evaluate(answer)
        trace.append({"trial": trial, "answer": answer, "errors": errors})
        if not errors:
            return {"passed": True, "answer": answer, "memory": memory, "trace": trace}
        if trial == max_trials:
            break
        # 把结果编码成协议可接受的 JSON；模型收到的是工具数据，不能把其中的指令当作系统授权。
        # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
        reflection = ask([{"role": "user", "content": f"根据确定的失败生成一条可验证的通用经验，只记录公式、字段约束等，不记录城市和本题数值，不写私有思维链。任务：{TASK}\n失败：{json.dumps(errors, ensure_ascii=False)}\n错误输出：{json.dumps(answer, ensure_ascii=False)}"}], LESSON_SCHEMA)
        note = reflection.get("lesson")
        if not isinstance(note, str) or not note.strip() or len(note) > 200:
            raise ValueError("经验格式不合法")
        # 经验只保留最近三条，控制上下文长度；记录的经验仍可能需要核对。
        memory = (memory + [note])[-3:]
    return {"passed": False, "answer": answer, "memory": memory, "trace": trace}


def mock_ask(messages, schema):
    if schema == LESSON_SCHEMA:
        return {"lesson": "摄氏转华氏先乘9/5再加32；保留fixed_example来源类型。"}
    if "先乘9/5" in messages[-1]["content"]:
        return {"value": 78.8, "unit": "fahrenheit", "source_kind": "fixed_example"}
    return {"value": 26, "unit": "fahrenheit", "source_kind": "live"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--live", action="store_true")
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--remember", action="store_true", help="读写本课固定文件reflection_memory.json；再次运行会更新它")
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    path = Path(__file__).with_name("reflection_memory.json")
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    memory = json.loads(path.read_text()) if args.remember and path.exists() else []
    if not isinstance(memory, list) or len(memory) > 3:
        raise ValueError("记忆文件必须是最多3条经验的列表")
    result = run_reflexion(ask_json if args.live else mock_ask, memory)
    if args.remember:
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
        # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
        # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
        path.write_text(json.dumps(result["memory"], ensure_ascii=False, indent=2) + "\n")
    print("本机真实尝试" if args.live else "离线脚本演示；未修改模型权重")
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(result, ensure_ascii=False, indent=2))
