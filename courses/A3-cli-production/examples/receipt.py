"""记录已知字段；未知费用必须为 null，不推算成免费。"""

# unknown/None 表示缺少测量，0 表示已确认数值为零；不要用零代替未知费用。
import json


def make_receipt(*, provider, model, result, seconds, input_tokens=None, output_tokens=None, cost=None):
    if seconds < 0 or result not in {"pass", "fail", "not_run"}:
        raise ValueError("无效运行结果")
    for value in (input_tokens, output_tokens):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("token 应为非负整数或 null")
    if cost is not None and cost < 0:
        raise ValueError("费用不能为负")
    return {"provider": provider, "model": model, "input_tokens": input_tokens,
            "output_tokens": output_tokens, "seconds": seconds, "cost": cost, "result": result}


if __name__ == "__main__":
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    print(json.dumps(make_receipt(provider="未运行示范", model="未运行", result="not_run", seconds=0), ensure_ascii=False, indent=2))
