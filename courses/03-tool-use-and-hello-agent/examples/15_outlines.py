"""Outlines + Ollama：用输出类型约束生成，再验证抽取的业务含义。"""

# 通过输出约束生成 WeatherRecord；语法和类型可检查，天气是否真实仍须另验。

import os

# Field 把长度、范围等约束附在字段上；格式通过之后，还要核对业务规则和事实依据。
from pydantic import BaseModel, ConfigDict, Field
# Literal 把允许返回的路由名写进类型说明，帮助核对条件边是否有对应目标。
from typing import Literal


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


def main():
    import ollama
    import outlines

    # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
    # trust_env：设为 False 可避免继承系统代理等环境配置，使本地请求路径更可控；不会关闭 TLS 证书校验。
    client = ollama.Client(host="http://localhost:11434", timeout=60, trust_env=False)
    model = outlines.from_ollama(client, os.environ.get("OLLAMA_MODEL", "gemma4:e4b"))
    raw = model(
        "只抽取这句固定教学数据：台北26摄氏度。unit为celsius，source_kind为fixed_example。不要推测其他事实。",
        WeatherRecord,
        think=False,
        options={"temperature": 0, "num_predict": 512},
    )
    record = WeatherRecord.model_validate_json(raw)
    if record.city != "台北" or record.temperature != 26:
        raise ValueError("结构合法，但抽取值与原句不一致")
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(record.model_dump_json(indent=2))


if __name__ == "__main__":
    # 进入本文件的演示入口。
    main()
