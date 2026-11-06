"""从给定句子抽取数据，不查天气、不执行工具。"""

# 结构化输出限制回答字段；解析成功后，仍要检查温度数值和数据来源。

import json

from openai import OpenAI
import os

# properties：逐字段描述参数结构，帮助模型知道怎样填写请求；这些描述不会自动执行 Python 函数。
SCHEMA = {"type": "object", "properties": {
    "city": {"type": "string"},
    "temperature": {"type": "number"},
    # enum：把可选值限制在已实现的分支内，避免出现程序没有处理的拼写或选项。
    "unit": {"type": "string", "enum": ["celsius"]},
}, "required": ["city", "temperature", "unit"], "additionalProperties": False}


def main():
    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
    # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=60, max_retries=0)
    response = client.chat.completions.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=os.environ.get("OLLAMA_MODEL", "gemma4:e4b"),
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": "从这句话抽取 JSON，不要查询：台北的示例气温为摄氏 26 度。"}],
        # response_format：约束回答的外形，便于程序解析；结构正确不代表数值、事实或引用正确。
        response_format={"type": "json_schema", "json_schema": {"name": "weather_record", "schema": SCHEMA}},
        # reasoning_effort：配置模型支持的推理行为；这里的值必须与所用服务兼容，不能当作所有模型通用的开关。
        # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        reasoning_effort="none", temperature=0, max_tokens=256,
    )
    choice = response.choices[0]
    if choice.finish_reason != "stop" or choice.message.refusal:
        raise RuntimeError("输出截断或拒答，不能当作成功 JSON")
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    record = json.loads(choice.message.content or "")
    if not isinstance(record, dict) or set(record) != {"city", "temperature", "unit"}:
        raise ValueError("结构错误")
    if record != {"city": "台北", "temperature": 26, "unit": "celsius"}:
        raise ValueError("JSON 合法但没有忠实抽取原句")
    if type(record["temperature"]) not in (int, float):
        raise ValueError("温度类型错误")
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    # 进入本文件的演示入口。
    main()
