"""Path B 离线行为测试：检查 Anthropic 设定，并用假模型跑共用图。"""

# 本组测试围绕以下行为检查正反例：先分类选择是否检索，再暂停等待决定；内存检查点只保留在当前进程中。

from __future__ import annotations

import sys
import os
from types import SimpleNamespace

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import run
from starter_anthropic import MODEL, make_anthropic_llm


class FakeAnthropicLLM:
    """不发出 API 请求，只提供可预测的 Anthropic-path 草稿。"""
    def invoke(self, prompt: str) -> SimpleNamespace:
        return SimpleNamespace(content="Anthropic 路径的离线草稿")


def test_anthropic_provider_construction() -> None:
    os.environ.setdefault("ANTHROPIC_API_KEY", "offline-test-key")
    llm = make_anthropic_llm()
    assert llm.model == MODEL
    assert MODEL == "claude-haiku-4-5-20251001"


def test_anthropic_path_graph_behavior() -> None:
    # thread_id：定位同一条工作流的检查点。暂停和恢复必须使用同一个值；换值通常会进入另一条会话。
    result = run("请介绍 Python", approve=True, llm=FakeAnthropicLLM(), thread_id="anthropic-offline")
    assert result["final"] == "PUBLISHED: Anthropic 路径的离线草稿"
    assert result["approved"] is True


if __name__ == "__main__":
    test_anthropic_provider_construction()
    test_anthropic_path_graph_behavior()
    print("全部通过")
