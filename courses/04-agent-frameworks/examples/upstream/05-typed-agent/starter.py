"""Stage 4 练习 5：用 Pydantic AI ``output_type`` 检查输出形状。

型别检查像表格的格子：它能确保栏位存在、种类正确、数字在范围内，
但不能证明内容是真的。真实性仍要靠可信来源与额外的语义检查。
"""

# 检查字段类型、范围与非空约束；结构合法不代表答案或置信度在事实层面正确。

from __future__ import annotations

import os
import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Field 把长度、范围等约束附在字段上；格式通过之后，还要核对业务规则和事实依据。
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

MODEL = os.environ.get("MODEL", "qwen2.5:3b")
OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434/v1")


# Pydantic 限制字段形状与范围，confidence 不表示经过统计校准的正确率。
class AnswerWithConfidence(BaseModel):
    """已验证的资料形状；它不是答案为真的证据。"""
    # answer：保存最终对外文本；非空只说明模型有输出，事实与引用是否正确仍要独立核对。
    # min_length：要求至少有指定数量的字符或元素，避免空答案、空来源列表看起来结构合法却无法使用。
    answer: str = Field(min_length=1, description="非空且不夸大确定性的中文答案。")
    # confidence：这里只约束模型自报值的范围，不能把它当成经过校准的真实正确率。
    # ge：设置包含边界的数值下限；类型正确但越界的值也必须被拒绝。
    # le：设置包含边界的数值上限，防止过大置信度或预算通过类型检查。
    confidence: float = Field(ge=0.0, le=1.0, description="置信度必须在 0.0 到 1.0 之间。")
    # sources：要求提供可回查的来源标签，让审核者能核对依据；标签存在不等于来源真的支持断言。
    # min_length：要求至少有指定数量的字符或元素，避免空答案、空来源列表看起来结构合法却无法使用。
    sources: list[str] = Field(min_length=1, description="至少提供一个非空的来源标签。")

    @field_validator("answer")
    @classmethod
    def answer_is_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("answer 不能为空白")
        return value.strip()

    @field_validator("sources")
    @classmethod
    def sources_are_nonempty_labels(cls, value: list[str]) -> list[str]:
        if not all(isinstance(item, str) and item.strip() for item in value):
            raise ValueError("sources 中的来源标签必须是非空字符串")
        return [item.strip() for item in value]


def make_ollama_model() -> OpenAIChatModel:
    """用目前 Pydantic AI 的 OpenAIChatModel 连到本机 Ollama。"""
    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    return OpenAIChatModel(MODEL, provider=OpenAIProvider(base_url=OLLAMA_BASE, api_key="ollama"))


def build_agent(model: Any | None = None) -> Agent:
    """建立会重试两次、并要求 AnswerWithConfidence 的 agent。"""
    return Agent(
        model or make_ollama_model(),
        # output_type：把最终答案约束为这个类型，尽早暴露缺字段或类型错误；仍需另做事实核对。
        output_type=AnswerWithConfidence,
        retries=2,
        instructions=(
            "返回 AnswerWithConfidence：给出非空中文答案、0 到 1 之间的置信度，"
            "以及至少一个来源标签。结构合法不能证明内容真实。"
        ),
    )


def run(question: str, model: Any | None = None) -> AnswerWithConfidence:
    """执行 agent，并在返回前再检查本练习的结果契约。"""
    output = build_agent(model).run_sync(question).output
    if not output.answer or not output.sources or not 0.0 <= output.confidence <= 1.0:
        raise RuntimeError("验证后的输出仍不符合本练习约定。")
    return output


if __name__ == "__main__":
    answer = run("台北人口是多少？")
    # 把 SDK 或模型对象转成普通数据，方便保存与返回；不要把对象的调试字符串当作协议 JSON。
    print(answer.model_dump())
    assert 0.0 <= answer.confidence <= 1.0
    assert answer.answer and answer.sources
