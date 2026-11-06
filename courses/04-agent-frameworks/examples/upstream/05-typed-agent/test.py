"""Path A 离线行为测试：使用 Pydantic AI 官方 TestModel，不连网。"""

# 本组测试围绕以下行为检查正反例：检查字段类型、范围与非空约束；结构合法不代表答案或置信度在事实层面正确。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pydantic import ValidationError
from pydantic_ai.models.test import TestModel
from starter import AnswerWithConfidence, run


def test_official_test_model_produces_valid_typed_output() -> None:
    model = TestModel(custom_output_args={"answer": "离线模拟答案", "confidence": 0.6, "sources": ["固定离线样本"]})
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    answer = run('测试问题', model=model)
    assert answer.answer == "离线模拟答案"
    assert answer.sources == ["固定离线样本"]


def test_invalid_contract_values_are_rejected() -> None:
    invalid = [
        {"answer": "ok", "confidence": 1.1, "sources": ["source"]},
        {"answer": "ok", "confidence": 0.5, "sources": "source"},
        {"answer": " ", "confidence": 0.5, "sources": ["source"]},
        {"answer": "ok", "confidence": 0.5, "sources": []},
    ]
    for payload in invalid:
        try:
            # 按 AnswerWithConfidence 的模型定义验证输入。
            # 在接收结果的边界执行运行时验证，尽早拒绝缺字段、错类型和越界值。
            AnswerWithConfidence.model_validate(payload)
        except ValidationError:
            pass
        else:
            raise AssertionError(f"这里应拒绝无效值：{payload!r}")


if __name__ == "__main__":
    test_official_test_model_produces_valid_typed_output()
    test_invalid_contract_values_are_rejected()
    print("全部通过")
