"""Stage 4 练习 1：同一个 agent、两个 framework — LangGraph + Anthropic（Path B）。

跟 starter.py 同样的 LangGraph 图、只把 LLM backend 换成 Claude。

运行方法：
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...
    python starter_anthropic.py

预算：每次 ≈ $0.001（claude-haiku-4-5）。
Ollama 版本见 starter.py。
"""

# 保持问题和搜索资料相同，比较 LangGraph 的状态图与 CrewAI 的角色任务如何调用工具。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import os
import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langchain_anthropic import ChatAnthropic

from starter import run

MODEL = os.environ.get("MODEL", "claude-haiku-4-5-20251001")


if __name__ == "__main__":
    query = "请根据工具中的固定资料，用中文概括台北的信息。"
    print(f"❓ 问题：{query}（使用 Anthropic {MODEL}）")
    print("-" * 60)
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
    llm = ChatAnthropic(model=MODEL, temperature=0)
    result = run(query, llm=llm)
    print(f"✅ 最终结果：{result['final']}")
    print(f"   消息条数：{result['steps']}")
    assert result["final"], "摘要不得为空"
    assert result["steps"] >= 2, "应保留可观察的图执行轨迹"
    print("✅ 练习 1 (Anthropic path) 通过 — LangGraph + 固定 Anthropic model ID；费用依 tokens 计算")
