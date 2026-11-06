"""首轮演示四种工具选择；后续恢复 auto，避免强制调用导致无限循环。"""

# tool_choice 影响模型能否请求工具；执行层仍要核对实际请求，不能只相信设置。

import argparse
import os

from agent import print_run, run_agent
from tools import TOOLS


# 把命令行选项转成接口要求的字符串或指定函数对象。
def choice_value(mode):
    if mode == "specific":
        return {"type": "function", "function": {"name": "get_weather"}}
    if mode not in ("auto", "none", "required"):
        raise ValueError("未知工具选择模式")
    return mode


# 首轮使用指定策略，收到结果后的后续轮恢复 auto；总轮数仍受循环限制。
def make_choice_ask(mode):
    from openai import OpenAI

    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
    # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=60, max_retries=0)
    first = True

    def ask(messages, tools):
        nonlocal first
        choice = choice_value(mode) if first else "auto"
        # 即使服务端错误地返回了请求，none 模式的执行白名单仍为空。
        response = client.chat.completions.create(
            # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
            # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
            model=os.environ.get("OLLAMA_MODEL", "gemma4:e4b"), messages=messages,
            # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
            tools=TOOLS if mode == "none" else tools, tool_choice=choice,
            # reasoning_effort：配置模型支持的推理行为；这里的值必须与所用服务兼容，不能当作所有模型通用的开关。
            # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
            # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
            reasoning_effort="none", temperature=0, max_tokens=768,
        )
        first = False
        selected = response.choices[0]
        if mode in ("required", "specific") and len(messages) == 2:
            if not selected.message.tool_calls:
                raise RuntimeError("当前模型/接口未实现该工具选择约束；本实验不通过")
            if mode == "specific" and any(call.function.name != "get_weather" for call in selected.message.tool_calls):
                raise RuntimeError("返回了未指定的工具")
        if mode == "none" and selected.message.tool_calls:
            raise RuntimeError("接口违反 none 约束，禁止执行")
        # 把 SDK 或模型对象转成普通数据，方便保存与返回；不要把对象的调试字符串当作协议 JSON。
        # exclude_none：省略值为 None 的可选字段，避免把“未返回”误写成一项有内容的协议字段。
        return {"message": selected.message.model_dump(exclude_none=True), "finish_reason": selected.finish_reason,
                "tokens": response.usage.total_tokens if response.usage else 0}

    return ask


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("mode", choices=["auto", "none", "required", "specific"])
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    question = "你好，用一句话回应。" if args.mode == "none" else "查询台北的示例气温。"
    # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
    print_run(run_agent(question, make_choice_ask(args.mode), tools=[] if args.mode == "none" else TOOLS))
