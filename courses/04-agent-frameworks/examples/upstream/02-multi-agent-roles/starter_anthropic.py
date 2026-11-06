r"""Stage 4 练习 2 Path B：用 Anthropic 跑同一个三角色 CrewAI 流程。

CrewAI 用 provider-prefixed model string 选择后端；
``crewai[anthropic]`` 会安装 Anthropic provider，这份范例再固定 model ID。

运行方法：
    $env:ANTHROPIC_API_KEY="sk-ant-..."
    .\.venv\Scripts\python.exe starter_anthropic.py

实际费用依 tokens、调用次数与重试而变；README 提供公式与 $0.10 支出上限。
"""

# 沿着研究、写作、审核看资料如何传递；角色名字不能代替实际的任务上下文。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import os
import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import run

MODEL = os.environ.get("MODEL", "anthropic/claude-haiku-4-5-20251001")  # 提供商前缀让框架选择对应后端，模型名本身不足以确定调用路径


if __name__ == "__main__":
    topic = "react"
    print(f"❓ 主题：{topic}（使用 CrewAI 和 Anthropic {MODEL}）")
    print(f"   三个角色：研究者 → 写作者 → 审核者（顺序执行）")
    print("-" * 60)
    result = run(topic, llm_model=MODEL)
    print(f"✅ 最终结果（审核者判定）：\n{result['final']}")
    assert result["final"], "审核者应给出明确判定"
    assert "max_iter=4" in result["stop_condition"]
    print("\n✅ 练习 2 (Anthropic path) 通过 — 3-agent crew 已走到有界停止条件")
