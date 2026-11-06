"""练习 6：同题、同模型、同循环，比较弱描述与明确 schema。"""

# 对同一题集比较清楚与含糊的工具说明；先读 score，再看 main 如何保存每题结果。

import argparse
import copy
import json
import re
from pathlib import Path

from agent import run_agent
from model_client import make_ask
from tools import TOOLS


# 根据该题的预期工具与参数评分，不能仅凭最终回答看起来合理就判通过。
def score(case, result):
    actions = [event for event in result["trace"] if event["event"] == "action"]
    observations = [event for event in result["trace"] if event["event"] == "observation"]
    names = [event["name"] for event in actions]
    if names != case["actions"]:
        return False, f"工具顺序不符：{names}"
    if not result["answer"].strip():
        return False, "答案为空"
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    arguments = [json.loads(event["arguments"]) if isinstance(event["arguments"], str)
                 else event["arguments"] for event in actions]
    if case.get("city") and arguments[0].get("city") != case["city"]:
        return False, "查询城市错误"
    if case.get("error"):
        failed = bool(observations) and not observations[-1]["result"]["ok"]
        explained = any(word in result["answer"] for word in ("没有", "无法", "不支持", "无数据"))
        return failed and explained, "错误结果及无法查询说明"
    if any(not event["result"]["ok"] for event in observations):
        return False, "工具执行失败"
    if case["id"] == "math" and any(arguments[0].get(key) != case[key] for key in ("operation", "left", "right")):
        return False, "运算参数错误"
    if case["id"] == "chain":
        converted = arguments[1]
        dependent = (actions[1]["step"] > actions[0]["step"]
                     and converted.get("value") == observations[0]["result"]["data"]["temperature"]
                     and converted.get("from_unit") == "celsius" and converted.get("to_unit") == "fahrenheit")
        if not dependent:
            return False, "未等到天气结果，或换算没有使用实际温度及正确单位"
    if "number" in case:
        # 中文常与数值相连，“气温为26.0摄氏度”也应识别。
        numbers = [float(value) for value in re.findall(r"(?<![\d.])-?\d+(?:\.\d+)?(?![\d.])", result["answer"])]
        if not any(abs(value - case["number"]) < 0.01 for value in numbers):
            return False, "最终数值不符"
    if case.get("unit_words") and not any(word in result["answer"] for word in case["unit_words"]):
        return False, "最终答案缺少正确单位"
    return True, "通过规则检查；仍需人工复核最终答案"


# 保留工具名和字段类型，同时削弱描述与参数约束；这是整组 Schema 的比较，不能单独归因于某个字段。
def weak_schema():
    tools = copy.deepcopy(TOOLS)
    for tool in tools:
        function = tool["function"]
        function["description"] = "处理数据"
        params = function["parameters"]
        params.pop("additionalProperties", None)
        params.pop("required", None)
        for rule in params["properties"].values():
            for key in ("description", "enum", "minimum", "maximum"):
                rule.pop(key, None)
    return tools


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--repeat", type=int, default=5)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--variant", choices=["both", "good", "weak"], default="both")
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    if not 1 <= args.repeat <= 20:
        parser.error("repeat 必须在 1–20 之间")
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    cases = json.loads(Path(__file__).with_name("eval_cases.json").read_text())
    ask = make_ask()
    rows = []
    variants = {"good": TOOLS, "weak": weak_schema()}
    if args.variant != "both":
        variants = {args.variant: variants[args.variant]}
    # 每轮交替版本顺序，减少固定顺序造成的热身差异；不是严谨统计实验。
    for repeat in range(args.repeat):
        ordered = list(variants.items())
        if repeat % 2:
            ordered.reverse()
        for variant, tools in ordered:
            for case in cases:
                try:
                    # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
                    result = run_agent(case["question"], ask, tools=tools)
                    passed, reason = score(case, result)
                    row = {"variant": variant, "repeat": repeat + 1, "case": case["id"],
                           "passed": passed, "reason": reason, "answer": result["answer"],
                           "trace": result["trace"], "tokens": result["tokens"]}
                except Exception as error:
                    row = {"variant": variant, "repeat": repeat + 1, "case": case["id"],
                           "passed": False, "reason": f"{type(error).__name__}: {error}"}
                rows.append(row)
                print(f"{variant} | 第{repeat + 1}次 | {case['id']} | {row['passed']} | {row['reason']}")
    output = Path(__file__).with_name("eval_results.json")
    # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    for variant in variants:
        selected = [row for row in rows if row["variant"] == variant]
        print(f"{variant} 成功 {sum(row['passed'] for row in selected)}/{len(selected)}")
    print("完整记录：", output)


if __name__ == "__main__":
    # 进入本文件的演示入口。
    main()
