"""第七课评测示例：A 路径使用 Ollama。"""

# 固定题集与评分规则，保存每次试跑和基线差异；开发题与保留题分开使用。

from __future__ import annotations

import os
import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from eval_core import require_text, run_cli


MODEL = os.environ.get("MODEL", "qwen3.5:4b")
OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434/v1")


def new_ollama_client() -> Any:
    """实际调用时才加载兼容 OpenAI 协议的客户端，离线测试不初始化服务。"""
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "缺少可选依赖 'openai'. 请运行：pip install openai"
        ) from exc
    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    return OpenAI(base_url=OLLAMA_BASE, api_key="ollama")


def agent_answer(question: str, llm: Any = None) -> str:
    """把一道题交给本地模型，并拒绝空响应。"""
    llm = llm or new_ollama_client()
    response = llm.chat.completions.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=MODEL,
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[
            {
                "role": "system",
                "content": "用简洁中文回答，并严格遵守用户要求的格式。",
            },
            {"role": "user", "content": question},
        ],
    )
    return require_text(response.choices[0].message.content, "Agent")


def judge_answer(output: str, case: dict[str, Any], llm: Any = None) -> str:
    """使用同一服务执行指定的模型评分；严格要求返回 PASS 或 FAIL。"""
    llm = llm or new_ollama_client()
    prompt = (
        "只根据给定标准评价答案。"
        "只输出 PASS 或 FAIL。\n\n"
        f"问题：{case['input']}\n"
        f"验收标准：{'; '.join(case['success_criteria'])}\n"
        f"裁判评分规则：{case['grader']['value']}\n"
        f"回答： {output}"
    )
    response = llm.chat.completions.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=MODEL,
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": prompt}],
    )
    return require_text(response.choices[0].message.content, "Judge")


# === 自我验证 ===
assert MODEL.strip(), "MODEL 不能为空"
assert OLLAMA_BASE.startswith(("http://", "https://")), (
    "OLLAMA_API_BASE 必须是 HTTP(S) 地址"
)


if __name__ == "__main__":
    raise SystemExit(
        run_cli(
            agent_answer,
            # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
            model=MODEL,
            provider="ollama",
            judge_fn=judge_answer,
        )
    )
