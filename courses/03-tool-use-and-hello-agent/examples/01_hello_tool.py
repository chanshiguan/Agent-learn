"""练习 1：演示模型调用一个工具并根据工具结果生成最终回答。"""

# 导入 Python 标准库 json，用于把字典转换为便于打印和传输的 JSON 字符串。
import json

# 导入系统提示词；它负责告诉模型自己的角色以及应如何使用工具。
from agent import SYSTEM
# 导入模型请求函数的工厂；make_ask 会创建一个连接本机 Ollama 的请求函数。
from model_client import make_ask
# 导入工具定义 TOOLS，以及负责安全执行工具的 execute 函数。
from tools import TOOLS, execute


# 把示例的完整流程放进 main，避免该文件被其他模块导入时自动发起模型请求。
def main():
    # 本练习只把 TOOLS 中的第一个工具 get_weather 提供给模型，保持示例简单。
    tools = [TOOLS[0]]

    # 创建模型请求函数；这里只完成客户端配置，还没有向模型发送消息。
    ask = make_ask()

    # 建立首轮对话历史，模型每一轮都会看到这个列表中的全部消息。
    # 这份历史同时保存问题、模型请求和工具观察；下一轮需要它们才能沿用真实结果，保持调用与结果的顺序。
    messages = [
        # system 消息提供最高层的行为说明，让模型知道工具调用规则。
        {"role": "system", "content": SYSTEM},
        # user 消息是本次练习实际要模型处理的问题。
        {"role": "user", "content": "查询台北的示例气温。"},
    ]

    # 第一次请求模型：期望模型识别出需要天气数据，并返回 get_weather 工具调用。
    first = ask(messages, tools)

    # 首轮只能正常结束或请求工具；其他原因通常表示输出异常或达到长度上限。
    if first["finish_reason"] not in ("stop", "tool_calls"):
        # 立即终止，防止继续处理一个不完整的模型响应。
        raise RuntimeError("首轮输出异常或被截断")

    # 取出标准化后的 assistant 消息，里面可能包含文本或 tool_calls。
    assistant = first["message"]

    # 读取工具调用列表；模型没有返回 tool_calls 时，用空列表代替 None。
    # 没有调用时才进入最终回答分支；空列表是“本轮不执行工具”，不是已经取得工具结果。
    calls = assistant.get("tool_calls") or []

    # 本练习只支持一次、一个工具调用，并要求调用带有可关联结果的唯一 ID。
    if len(calls) != 1 or not calls[0].get("id"):
        # 响应结构不符合教学预期时给出明确错误，而不是在后续索引时报模糊错误。
        raise RuntimeError("本练习要求恰好一个带 ID 的工具请求；检查模型、schema 和原始响应")

    # 把模型的工具调用消息加入历史；第二轮模型需要看到自己刚才发起的调用。
    messages.append(assistant)

    # 取出唯一的工具调用，供后续打印、执行以及关联工具结果使用。
    call = calls[0]

    # 打印模型提出的工具名和参数；ensure_ascii=False 让中文保持可读。
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    print("工具请求：", json.dumps(call, ensure_ascii=False))

    # 执行模型请求的工具；集合 {"get_weather"} 明确限制本练习只授权天气工具。
    result = execute(
        # 模型请求调用的函数名，例如 get_weather。
        call["function"]["name"],
        # 模型生成的函数参数，通常是 JSON 字符串，例如 {"city": "台北"}。
        call["function"]["arguments"],
        # 本轮允许执行的工具白名单，防止模型调用未授权函数。
        {"get_weather"},
    )

    # 打印本地工具的执行结果，方便观察“模型请求—程序执行”的中间过程。
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    print("工具结果：", json.dumps(result, ensure_ascii=False))

    # 把工具结果作为一条 tool 消息追加到对话历史，供模型生成最终答案。
    messages.append(
        {
            # role=tool 表明这不是用户或模型文本，而是一次工具执行结果。
            "role": "tool",
            # 用同一个调用 ID 把结果和模型之前发起的工具请求对应起来。
            "tool_call_id": call["id"],
            # API 的消息内容使用字符串，因此把结果字典序列化为 JSON。
            # 把结果编码成协议可接受的 JSON；模型收到的是工具数据，不能把其中的指令当作系统授权。
            # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
            "content": json.dumps(result, ensure_ascii=False),
        }
    )

    # 第二次请求模型：此时模型已看到工具结果，应据此生成自然语言答案。
    final = ask(messages, tools)

    # 固定两轮的入门示例要求第二轮直接结束，不能再次请求其他工具。
    if final["finish_reason"] != "stop" or final["message"].get("tool_calls"):
        # 若仍需调用工具，应升级为循环式 Agent，而不是继续硬编码第三、第四轮。
        raise RuntimeError("第二轮没有结束；需要通用 Agent Loop，而不是继续增加固定请求")

    # 从最终 assistant 消息中提取给用户看的文字内容。
    answer = final["message"].get("content")

    # 空字符串或 None 都不是有效答案，因此在这里显式失败。
    if not answer:
        # 明确指出问题来自最终答案为空，方便定位模型兼容性问题。
        raise RuntimeError("最终答案为空")

    # 输出模型结合天气工具结果生成的最终回答。
    print("最终答案：", answer)


# 只有直接运行本文件时 __name__ 才等于 "__main__"；被导入时不会进入此分支。
if __name__ == "__main__":
    # 启动上面定义的完整示例流程。
    main()
