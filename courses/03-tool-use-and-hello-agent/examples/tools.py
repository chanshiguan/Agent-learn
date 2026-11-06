"""提供第三课使用的只读工具；天气数据固定，仅用于教学，不代表实时天气。"""

# 导入 json，用于解析模型生成的 JSON 参数字符串。
import json
# 导入 math，用于确认数值参数不是无穷大或 NaN。
import math

# 保存固定的示例气温；键是支持的城市，值是摄氏温度。
WEATHER = {"台北": 26.0, "北京": 18.0, "上海": 22.0}


# 根据中文城市名查询固定教学气温，不访问网络或真实天气服务。
def get_weather(city):
    # 只允许查询 WEATHER 中明确列出的三个城市。
    if city not in WEATHER:
        # 对不支持的城市给出可理解的错误和支持范围。
        raise ValueError("没有该城市的示例数据；支持台北、北京、上海")

    # 返回结构化结果，让模型能明确识别城市、温度、单位和数据来源。
    return {
        # 把城市和气温放在同一份结果中，多城市查询时才不会把某城市的数值套给另一座城市。
        "city": city,
        # 数值来自宿主维护的固定数据，模型只负责提出查询，不能自行填造工具结果。
        "temperature": WEATHER[city],
        # 明确标注单位，避免模型猜测数值是摄氏还是华氏。
        "unit": "celsius",
        # 提醒模型和用户这是教学数据，不能当作实时天气。
        "source": "教学固定数据，非实时",
    }


# 对两个数执行一次加、减、乘或除运算。
def calculator(operation, left, right):
    # 按已经验证过的运算枚举分支；让宿主完成精确运算，避免依赖模型心算。
    if operation == "add":
        # 这里得到最终数值，后续统一用 result 字段交回模型，便于下一次工具调用取用。
        result = left + right
    # 减法区分左右次序；工具接口明确 left 和 right，不能把两个数当无序集合。
    elif operation == "subtract":
        # 按调用者指定的 left − right 计算，避免把“从右数减去左数”当作同一个任务。
        result = left - right
    # 只做一项二元运算，复合表达式须由循环拆成多步，轨迹中才能逐步核对。
    elif operation == "multiply":
        # 乘法仍返回统一结果字段，多步任务无需为不同运算编写不同的取值方式。
        result = left * right
    # 参数验证保证剩余的合法 operation 只能是 divide。
    else:
        # 除法开始前先检查除数，避免 Python 抛出 ZeroDivisionError。
        if right == 0:
            # 用业务错误说明失败原因，稍后 execute 会把它转换为工具错误结果。
            raise ValueError("除数不能为零")
        # 除法可能返回小数；保留数值类型，下一工具才能继续计算，而不是从描述里提取数字。
        result = left / right

    # 使用字典返回结果，保持所有工具都提供结构化输出。
    return {"result": result}


# 在摄氏度和华氏度之间转换一个已知温度。
def convert_temperature(value, from_unit, to_unit):
    # 输入、输出单位相同时不需要计算，直接保留原值。
    if from_unit == to_unit:
        # 同单位转换应保持数值不变；这条路径避免错误地重复套用温度公式。
        result = value
    # 输入单位为摄氏度时，按公式转换为华氏度。
    elif from_unit == "celsius":
        # 华氏度 = 摄氏度 × 9 ÷ 5 + 32。
        result = value * 9 / 5 + 32
    # 参数验证保证剩余情况是从华氏度转换为摄氏度。
    else:
        # 摄氏度 =（华氏度 - 32）× 5 ÷ 9。
        result = (value - 32) * 5 / 9

    # 将结果保留两位小数，并明确返回目标单位。
    return {"value": round(result, 2), "unit": to_unit}


# 定义提供给模型看的工具目录；这里只描述接口，不直接执行任何函数。
TOOLS = [
    {
        # 本例的 Chat Completions 协议用 function 表示宿主函数工具；这不表示服务端会自动执行 Python。
        "type": "function",
        # function 对象描述工具名称、用途和参数结构。
        "function": {
            # 名称必须与 TOOL_IMPL 中实际执行函数的键一致。
            "name": "get_weather",
            # 描述帮助模型判断什么时候应该调用该工具。
            "description": "查询台北、北京、上海的固定示例气温，单位摄氏。需要气温时使用；不是实时天气，不用于计算。",
            # parameters 使用 JSON Schema 风格描述模型应生成的参数。
            "parameters": {
                # 工具参数整体必须是一个对象。
                "type": "object",
                # properties 列出对象中允许出现的字段及其规则。
                "properties": {
                    # city 是字符串，并通过描述提示模型使用中文城市名。
                    "city": {"type": "string", "description": "中文城市名，例如台北"},
                },
                # city 是必填字段，缺少它就无法查询天气。
                "required": ["city"],
                # 禁止模型添加未定义参数，减少格式错误和意外输入。
                "additionalProperties": False,
            },
        },
    },
    {
        # 计算器也按同一函数协议声明，模型在同一 tools 列表中按任务选择名称。
        "type": "function",
        # 把计算器的名称、用途和参数放在同一接口描述中，模型提出的请求必须能对应到本地实现。
        "function": {
            # 工具名 calculator 与实际 Python 函数名保持一致。
            "name": "calculator",
            # 描述限定它只做一次四则运算，并把温度换算交给专用工具。
            "description": "对两个有限数字做一次四则运算。复合运算请分步调用；温度换算使用 convert_temperature。",
            # 定义计算器所需参数及限制。
            "parameters": {
                # 所有参数组合成一个 JSON 对象。
                "type": "object",
                # properties 分别定义运算名称和两个操作数。
                "properties": {
                    # operation 只能从四种允许的运算名称中选择。
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "四则运算名称",
                    },
                    # left 是减法的被减数或除法的被除数；上下限是本例的输入边界，执行器还会拒绝 NaN 和布尔值。
                    "left": {
                        "type": "number",
                        "minimum": -1000000,
                        "maximum": 1000000,
                        "description": "左操作数",
                    },
                    # right 是减数或除数；数值范围不能排除除零，所以除法实现还要单独检查 0。
                    "right": {
                        "type": "number",
                        "minimum": -1000000,
                        "maximum": 1000000,
                        "description": "右操作数",
                    },
                },
                # 一次计算必须同时提供运算名称及左右操作数。
                "required": ["operation", "left", "right"],
                # 拒绝计算器接口未定义的额外字段。
                "additionalProperties": False,
            },
        },
    },
    {
        # 温度换算作为独立函数公开，让模型能把“查询气温”和“转换单位”拆成有依赖的两步。
        "type": "function",
        # 接口同时要求数值、来源单位和目标单位，避免模型只给一个温度却让程序猜转换方向。
        "function": {
            # 工具名与 convert_temperature Python 函数对应。
            "name": "convert_temperature",
            # 描述强调该工具只换算已有数值，不负责查询天气。
            "description": "在摄氏与华氏之间换算已知温度。不查天气；需要先从天气结果取得温度。",
            # 定义待换算值、输入单位和输出单位。
            "parameters": {
                # 三个参数同样放在一个 JSON 对象中。
                "type": "object",
                # properties 描述每个允许字段的类型和取值范围。
                "properties": {
                    # value 必须是前一步取得的实际温度；这里的范围仅限制教学输入，不能证明气温真实或物理合理。
                    "value": {
                        "type": "number",
                        "minimum": -1000,
                        "maximum": 1000,
                        "description": "待换算的数值",
                    },
                    # from_unit 只能是摄氏或华氏的英文标识。
                    "from_unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "输入单位",
                    },
                    # to_unit 也只能是摄氏或华氏的英文标识。
                    "to_unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "输出单位",
                    },
                },
                # 三个字段缺一不可，否则无法明确完成换算。
                "required": ["value", "from_unit", "to_unit"],
                # 禁止温度换算接口出现未定义字段。
                "additionalProperties": False,
            },
        },
    },
]


# 建立“公开工具名 → 实际 Python 函数”的唯一执行映射。
TOOL_IMPL = {
    # 将模型使用的 get_weather 名称绑定到本地天气函数。
    "get_weather": get_weather,
    # 将模型使用的 calculator 名称绑定到本地计算函数。
    "calculator": calculator,
    # 将模型使用的 convert_temperature 名称绑定到本地换算函数。
    "convert_temperature": convert_temperature,
}


# 按本课三个固定接口的规则验证工具名和参数，不实现完整 JSON Schema。
def validate_args(name, args):
    """验证工具是否存在，以及参数字段、类型、范围和枚举值是否合法。"""

    # 工具名必须存在于唯一执行映射中，不能执行任意 Python 函数。
    if name not in TOOL_IMPL:
        # 拒绝未知工具，避免模型生成的任意名字进入执行流程。
        raise ValueError("未知工具，拒绝执行")

    # 在提供给模型的 TOOLS 描述中找到当前工具的参数规则。
    schema = next(
        # 取出匹配工具的 parameters 对象作为验证依据。
        tool["function"]["parameters"]
        # 从同一份 TOOLS 定义取规则，避免给模型看的 Schema 与执行器验证规则各写一份而逐渐不一致。
        for tool in TOOLS
        # 只选择名称与本次调用相同的工具。
        if tool["function"]["name"] == name
    )

    # 参数必须是字典，并且字段集合必须与 required 完全相同。
    if not isinstance(args, dict) or set(args) != set(schema["required"]):
        # 同时拒绝缺失字段和额外字段，保持教学接口严格、可预测。
        raise ValueError("参数必须是对象，且字段必须与工具定义完全一致")

    # 逐个检查 schema 中声明的每个参数字段。
    for key, rule in schema["properties"].items():
        # 后面的类型、范围和枚举检查都针对模型实际提交的这个值，而不是只相信 Schema 已经约束生成。
        value = args[key]

        # 字符串必须类型正确、去空白后非空，并限制在 80 个字符以内。
        if rule["type"] == "string" and (
            not isinstance(value, str) or not value.strip() or len(value) > 80
        ):
            # 字符串不合格时指出具体字段，方便模型或开发者修正。
            raise ValueError(f"{key} 必须是 1–80 字符的非空字符串")

        # 数字字段需要额外检查 Python 类型、有限性和范围。
        if rule["type"] == "number":
            # 精确检查 int/float；bool 虽是 int 子类，但不能当作数值参数。
            if type(value) not in (int, float) or not math.isfinite(value):
                # 拒绝布尔值、字符串、NaN 和正负无穷。
                raise ValueError(f"{key} 必须是有限数字，不能是布尔值")

            # 按工具定义中的 minimum 和 maximum 检查数值范围。
            if not rule["minimum"] <= value <= rule["maximum"]:
                # 范围外数值可能无意义或导致不必要的大数运算，因此拒绝。
                raise ValueError(f"{key} 超出允许范围")

        # 带 enum 的字段只能使用 schema 明确列出的值。
        if "enum" in rule and value not in rule["enum"]:
            # 拒绝未知运算名或未知单位，防止函数进入错误分支。
            raise ValueError(f"{key} 不在允许枚举中")


# 统一完成授权检查、参数解析、参数验证、函数执行和错误封装。
def execute(name, raw_args, allowed_names):
    """执行一次已授权工具调用，并始终返回可交给模型的成功或错误字典。"""

    # 捕获可预期的输入和计算错误，不把 Python 异常堆栈暴露给模型。
    try:
        # 工具既要被本轮白名单允许，也要存在于全局实现映射中。
        if name not in allowed_names or name not in TOOL_IMPL:
            # 模型请求未授权或不存在的工具时，明确拒绝执行。
            raise ValueError("该工具未授权，拒绝执行")

        # 对字符串形式的参数设置长度上限，避免解析超大输入。
        if isinstance(raw_args, str) and len(raw_args) > 4096:
            # 参数过长时在 json.loads 前终止，减少不必要的资源消耗。
            raise ValueError("参数文本过长")

        # 模型通常返回 JSON 字符串；若调用方已传字典，则直接沿用。
        # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args

        # 在真正调用 Python 函数前验证全部参数规则。
        validate_args(name, args)

        # **args 把参数字典展开为关键字参数，并返回统一的成功结构。
        return {"ok": True, "data": TOOL_IMPL[name](**args)}

    # 只捕获预期的工具输入或计算错误；编程错误仍会向外抛出以便修复。
    except (ValueError, TypeError, OverflowError) as error:
        # 把异常转换成稳定的错误字典，让模型可以阅读原因并继续响应。
        return {
            "ok": False,
            "error": {"type": "tool_error", "message": str(error)},
        }
