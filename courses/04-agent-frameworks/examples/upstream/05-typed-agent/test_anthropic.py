"""Path B 离线行为测试：检查 Anthropic 设定，再用官方 TestModel 执行。"""

# 本组测试围绕以下行为检查正反例：检查字段类型、范围与非空约束；结构合法不代表答案或置信度在事实层面正确。

from __future__ import annotations

import sys
import os

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pydantic_ai.models.test import TestModel
from starter import run
from starter_anthropic import MODEL, make_anthropic_model


def test_anthropic_provider_construction() -> None:
    os.environ.setdefault("ANTHROPIC_API_KEY", "offline-test-key")
    model = make_anthropic_model()
    assert MODEL == "claude-haiku-4-5-20251001"
    assert model.model_name == MODEL


def test_path_b_behavior_with_official_offline_model() -> None:
    offline = TestModel(custom_output_args={"answer": "Anthropic 路径的离线回答", "confidence": 0.4, "sources": ["fixture"]})
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    answer = run('测试问题', model=offline)
    assert answer.answer.startswith("Anthropic 路径的离线回答")
    assert answer.confidence == 0.4


if __name__ == "__main__":
    test_anthropic_provider_construction()
    test_path_b_behavior_with_official_offline_model()
    print("全部通过")
