"""Stage 7 练习 1：Multi-Agent 辩论 — Path B（Anthropic Claude）。

这条路只更换模型供应商，不证明 Claude 一定比 Qwen 稳定或正确。
请用同一组固定案例比较两条路，再由人检查重要结论。

运行方法：
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...
    python starter_anthropic.py
"""

# 正反两方分别回答，再交给裁决者；意见一致不能代替事实证据。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import os
import re
import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import anthropic

MODEL = os.environ.get("MODEL", "claude-haiku-4-5-20251001")


def require_text(value: str | None, label: str) -> str:
    """拒绝没有可用文字的响应，避免把空结果当作成功。"""
    text = (value or "").strip()
    if not text:
        raise ValueError(f"{label} 返回了空文本")
    return text


# 裁决必须符合完整约定，不能在一段任意文本里找到关键词就接受。
def parse_winner(verdict: str) -> tuple[str, str]:
    """只接受 WINNER=PRO 或 WINNER=CON 加理由的裁决格式，防止从含糊文本中猜测胜方。"""
    match = re.fullmatch(r"WINNER=(PRO|CON)\s*[.:-]\s*(.+)", verdict.strip(), re.IGNORECASE)
    if not match:
        raise ValueError("裁判必须返回 WINNER=PRO 或 WINNER=CON，后面附上理由")
    return match.group(1).upper(), match.group(2).strip()


def llm_call_anthropic(system: str, user: str, client: Any = None) -> str:
    client = client or anthropic.Anthropic()
    resp = client.messages.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        model=MODEL, max_tokens=300, system=system,
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": user}],
    )
    joined = " ".join(b.text for b in resp.content if b.type == "text")
    return require_text(joined, "Anthropic")


def debate_anthropic(question: str, client: Any = None) -> dict:
    pro = llm_call_anthropic(
        "请从支持方 PRO 的立场回答用户问题，用两到三句简洁中文陈述理由。",
        question, client=client,
    )
    con = llm_call_anthropic(
        "请从反对方 CON 的立场回答用户问题，用两到三句简洁中文陈述理由。",
        question, client=client,
    )
    judge = llm_call_anthropic(
        "你是中立评判者。输出 WINNER=PRO 或 WINNER=CON，随后用一句中文解释理由。",
        f"问题：{question}\n\nPRO: {pro}\n\nCON: {con}",
        client=client,
    )
    winner, reason = parse_winner(judge)
    return {
        "question": question,
        "pro": pro,
        "con": con,
        "judge": judge,
        "winner": winner,
        "reason": reason,
    }


if __name__ == "__main__":
    q = "小团队应该使用框架，还是从零构建？"
    print(f"❓ {q}\n")
    r = debate_anthropic(q)
    for k in ("pro", "con", "judge"):
        print(f"{k.upper()}: {r[k]}\n")
    assert r["winner"] in {"PRO", "CON"}
    assert r["reason"]
    print(f"✅ 练习 1 (Anthropic) 通过 — Claude {MODEL}，三次调用都完成")
