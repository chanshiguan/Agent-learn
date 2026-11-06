"""Stage 4 练习 4 Path B：用 LiteLLM 的固定 Anthropic model ID 跑 CodeAct。

它和 Path A 共用同一组工具、Docker 边界与最多四步的限制。
"""

# 比较 JSON 参数调用与代码行动；算术用 AST 白名单，CodeAct 的执行依赖受限 Docker。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import os
import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from smolagents import LiteLLMModel
from starter import run

MODEL = os.environ.get("MODEL", "anthropic/claude-haiku-4-5-20251001")


def make_anthropic_model() -> LiteLLMModel:
    """建立 Smolagents 可识别的 Anthropic LiteLLM model。"""
    return LiteLLMModel(model_id=MODEL)


if __name__ == "__main__":
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    result = run("查询台北人口除以纽约人口的比值。", model=make_anthropic_model())
    print(result["final"])
    assert result["final"]
    assert MODEL.startswith("anthropic/")
