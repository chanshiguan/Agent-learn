"""Stage 6 练习 3 — Path B concept demo 载入检查。"""

# 本组测试围绕以下行为检查正反例：同一资料用固定长度、段落、标题三种切法，观察证据是否被切断。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def test_loadable():
    import starter_anthropic
    assert hasattr(starter_anthropic, "compare_strategies")
    print("✅ test_loadable")


if __name__ == "__main__":
    test_loadable()
    print("\n🎉 通过")
