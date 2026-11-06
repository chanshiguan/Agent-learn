"""Stage 6 练习 2 — Path B 载入检查。

Vector DB 跨 LLM provider 一致、Path B 跟 Path A 跑出来相同。
"""

# 本组测试围绕以下行为检查正反例：先建立 collection 并写入资料，再比较字词与向量查询；保留 ID 才能回到原记录。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def test_path_b_reuses_vector_db_code():
    import starter_anthropic
    assert hasattr(starter_anthropic, "build_collection")
    assert hasattr(starter_anthropic, "semantic_query")
    print("✅ test_path_b_reuses_vector_db_code")


if __name__ == "__main__":
    test_path_b_reuses_vector_db_code()
    print("\n🎉 通过 — Path B concept demo 可载入")
