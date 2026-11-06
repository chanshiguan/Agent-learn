"""Stage 6 练习 5 — Path B mock test。
"""

# 本组测试围绕以下行为检查正反例：保存事实后按问题检索，再放入模型上下文；持久化、授权与删除是不同能力。

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import MemoryStore
from test import FakeClient
from starter_anthropic import chat_anthropic


def test_chat_anthropic_uses_memory_in_system_prompt():
    # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
    mem = MemoryStore(client=FakeClient(), embedding_function=lambda rows: rows)
    # 把经本例规则允许的事实写入记忆；是否能保存这类信息仍要在入口确定，不能见到文本就永久保存。
    mem.remember("用户喜欢 Python。")

    client = MagicMock()
    block = SimpleNamespace(type="text", text="我推荐 Python。")
    client.messages.create.return_value = SimpleNamespace(content=[block])

    result = chat_anthropic("请推荐一种编程语言。", mem, client=client)
    call_args = client.messages.create.call_args
    system_msg = call_args.kwargs["system"]
    assert "用户喜欢 Python。" in system_msg
    print("✅ test_chat_anthropic_uses_memory_in_system_prompt")


if __name__ == "__main__":
    test_chat_anthropic_uses_memory_in_system_prompt()
    print("\n🎉 Path B mock test 通过")
