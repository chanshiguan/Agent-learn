"""Stage 7 练习 1：Multi-Agent 辩论 — Path A（Ollama）。

2 个 agent 对同一个问题持相反立场辩论、第 3 个 judge agent 评分。
这个小例子只示范角色分工。多看一个观点不代表答案更正确、bias 更低；
请用固定 eval 验证，医疗、法律或其他高风险工作仍要由合格的人员审查。

运行方法：
    pip install -r requirements.txt
    ollama pull qwen3.5:4b
    ollama serve
    python starter.py
"""

# 正反两方分别回答，再交给裁决者；意见一致不能代替事实证据。

from __future__ import annotations

import os
import re
import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from openai import OpenAI

MODEL = os.environ.get("MODEL", "qwen3.5:4b")
OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434/v1")


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


def llm_call(system: str, user: str, llm: Any = None) -> str:
    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    llm = llm or OpenAI(base_url=OLLAMA_BASE, api_key="ollama")
    resp = llm.chat.completions.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=MODEL,
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return require_text(resp.choices[0].message.content, "LLM")


def debate(question: str, llm: Any = None) -> dict:
    """三个角色分别提出支持意见、反对意见并裁决；最终结论仍需检查。"""
    pro_argument = llm_call(
        system="请从支持方 PRO 的立场回答用户问题，用两到三句简洁中文陈述理由。",
        user=question, llm=llm,
    )
    con_argument = llm_call(
        system="请从反对方 CON 的立场回答用户问题，用两到三句简洁中文陈述理由。",
        user=question, llm=llm,
    )
    judge_verdict = llm_call(
        system="你是中立评判者，请阅读双方观点，选出证据较充分的一方。"
               "请按 WINNER=PRO 或 WINNER=CON 加一句中文理由的格式回答。",
        user=f"问题：{question}\n\nPRO: {pro_argument}\n\nCON: {con_argument}",
        llm=llm,
    )
    winner, reason = parse_winner(judge_verdict)
    return {
        "question": question,
        "pro": pro_argument,
        "con": con_argument,
        "judge": judge_verdict,
        "winner": winner,
        "reason": reason,
    }


if __name__ == "__main__":
    q = "小团队应该使用 LangGraph/CrewAI 等框架，还是从零构建 Agent？"
    print(f"❓ 问题：{q}\n")
    result = debate(q)
    print(f"PRO:    {result['pro']}\n")
    print(f"CON:    {result['con']}\n")
    print(f"裁判：{result['judge']}")
    assert result["winner"] in {"PRO", "CON"}
    assert result["reason"]
    print("\n✅ 练习 1 通过 — 三个角色都回复，Judge 格式也正确")
