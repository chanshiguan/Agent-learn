"""Instructor：类型化抽取、字段验证、最多两次抽取尝试。"""

# 先看 WeatherRecord 的字段限制，再看 main 中的调用与解析；合法结构仍可能包含错误事实。

import json
import os
# Literal 把允许返回的路由名写进类型说明，帮助核对条件边是否有对应目标。
from typing import Literal

# Field 把长度、范围等约束附在字段上；格式通过之后，还要核对业务规则和事实依据。
from pydantic import BaseModel, ConfigDict, Field, model_validator


class WeatherRecord(BaseModel):
    # strict：要求接口按支持的严格结构生成参数；执行层仍应校验语义与业务权限。
    model_config = ConfigDict(extra="forbid", strict=True)
    # min_length：要求至少有指定数量的字符或元素，避免空答案、空来源列表看起来结构合法却无法使用。
    # max_length：限制输入或输出的规模，防止意外的大文本拖慢处理或占满上下文。
    city: str = Field(min_length=1, max_length=80)
    # ge：设置包含边界的数值下限；类型正确但越界的值也必须被拒绝。
    # le：设置包含边界的数值上限，防止过大置信度或预算通过类型检查。
    temperature: float = Field(ge=-100, le=100)
    unit: Literal["celsius"]
    source_kind: Literal["fixed_example"]

    @model_validator(mode="after")
    def match_input_fact(self):
        # 本例输入是固定句子，因此可以验证抽取是否忠实，而非只验结构。
        if self.city != "台北" or self.temperature != 26:
            raise ValueError("输入只给出台北26摄氏度，不允许补造其他城市或数值")
        return self


def main():
    import instructor
    import httpx
    from openai import OpenAI

    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
    # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
    base = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=60, max_retries=0,
                  # http_client：显式注入底层 HTTP 客户端，让代理、超时等行为与这个案例的运行条件一致。
                  # trust_env：设为 False 可避免继承系统代理等环境配置，使本地请求路径更可控；不会关闭 TLS 证书校验。
                  # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
                  http_client=httpx.Client(trust_env=False, timeout=60))
    client = instructor.from_openai(base, mode=instructor.Mode.JSON)
    record = client.chat.completions.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=os.environ.get("OLLAMA_MODEL", "gemma4:e4b"),
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": "抽取固定教学数据：台北26摄氏度。unit用celsius，source_kind用fixed_example。"}],
        # response_model：让返回内容按这个模型进行类型与字段验证；验证失败后是否重试仍受次数限制。
        # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
        response_model=WeatherRecord, max_retries=1,
        # reasoning_effort：配置模型支持的推理行为；这里的值必须与所用服务兼容，不能当作所有模型通用的开关。
        # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        reasoning_effort="none", temperature=0, max_tokens=512,
    )
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # 把 SDK 或模型对象转成普通数据，方便保存与返回；不要把对象的调试字符串当作协议 JSON。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(record.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # 进入本文件的演示入口。
    main()
