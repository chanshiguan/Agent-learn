"""Stage 4 练习 5 Path B：用固定 Anthropic model ID 跑同一个输出契约。"""

# 检查字段类型、范围与非空约束；结构合法不代表答案或置信度在事实层面正确。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import os
import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pydantic_ai.models.anthropic import AnthropicModel
from starter import run

MODEL = os.environ.get("MODEL", "claude-haiku-4-5-20251001")


def make_anthropic_model() -> AnthropicModel:
    """建立 Pydantic AI 目前支援的 Anthropic model 物件。"""
    return AnthropicModel(MODEL)


if __name__ == "__main__":
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    answer = run("台北人口是多少？", model=make_anthropic_model())
    # 把 SDK 或模型对象转成普通数据，方便保存与返回；不要把对象的调试字符串当作协议 JSON。
    print(answer.model_dump())
    assert answer.answer and answer.sources
    assert 0.0 <= answer.confidence <= 1.0
