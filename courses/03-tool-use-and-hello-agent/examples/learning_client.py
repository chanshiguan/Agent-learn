"""反思、CodeAct 和小型检索实验共用的本地 JSON 请求入口。"""

# 进阶实验共用的 JSON 请求入口；接口返回字符串后仍要解析，不能把 usage 当回答。

import json
import os


# 把给定 schema 随请求发送，再把响应正文解析为 Python 数据。
def ask_json(messages, schema):
    from openai import OpenAI

    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
    # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=60, max_retries=0)
    response = client.chat.completions.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        model=os.environ.get("OLLAMA_MODEL", "gemma4:e4b"), messages=messages,
        # response_format：约束回答的外形，便于程序解析；结构正确不代表数值、事实或引用正确。
        response_format={"type": "json_schema", "json_schema": {"name": "learning_record", "schema": schema}},
        # reasoning_effort：配置模型支持的推理行为；这里的值必须与所用服务兼容，不能当作所有模型通用的开关。
        # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        reasoning_effort="none", temperature=0, max_tokens=1024,
    )
    choice = response.choices[0]
    if choice.finish_reason != "stop" or choice.message.refusal:
        raise RuntimeError(f"输出未正常完成：{choice.finish_reason}")
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    value = json.loads(choice.message.content or "")
    if not isinstance(value, dict):
        raise ValueError("预期 JSON 对象")
    return value
