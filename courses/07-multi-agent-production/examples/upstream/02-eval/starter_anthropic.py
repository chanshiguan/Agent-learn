"""第七课评测示例：B 路径使用 Anthropic。"""

# 固定题集与评分规则，保存每次试跑和基线差异；开发题与保留题分开使用。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import os
import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from eval_core import require_text, run_cli


MODEL = os.environ.get("MODEL", "claude-haiku-4-5-20251001")


def new_anthropic_client() -> Any:
    """实际调用时才加载 Anthropic 客户端，离线测试不需要初始化云服务。"""
    try:
        import anthropic
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "缺少可选依赖 'anthropic'. 请运行：pip install anthropic"
        ) from exc
    return anthropic.Anthropic()


def agent_answer_anthropic(question: str, client: Any = None) -> str:
    """把一道题交给 Claude，并拒绝空响应，避免把缺失答案继续交给评分器。"""
    client = client or new_anthropic_client()
    response = client.messages.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=MODEL,
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        max_tokens=200,
        system="用简洁中文回答，并严格遵守用户要求的格式。",
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": question}],
    )
    joined = " ".join(block.text for block in response.content if block.type == "text")
    return require_text(joined, "Anthropic agent")


def judge_answer_anthropic(
    output: str, case: dict[str, Any], client: Any = None
) -> str:
    """仅在题目指定模型评分时请求 Claude 裁判，返回值必须是 PASS 或 FAIL。"""
    client = client or new_anthropic_client()
    prompt = (
        "只根据给定标准评价答案。"
        "只输出 PASS 或 FAIL。\n\n"
        f"问题：{case['input']}\n"
        f"验收标准：{'; '.join(case['success_criteria'])}\n"
        f"裁判评分规则：{case['grader']['value']}\n"
        f"回答： {output}"
    )
    response = client.messages.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=MODEL,
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        max_tokens=10,
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": prompt}],
    )
    joined = " ".join(block.text for block in response.content if block.type == "text")
    return require_text(joined, "Anthropic Judge")


# === 自我验证 ===
assert MODEL.strip(), "MODEL 不能为空"
assert callable(agent_answer_anthropic), "Anthropic 适配器必须可调用"


if __name__ == "__main__":
    raise SystemExit(
        run_cli(
            agent_answer_anthropic,
            # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
            model=MODEL,
            provider="anthropic",
            judge_fn=judge_answer_anthropic,
        )
    )
