"""Stage 6 练习 3：Chunking — Path B concept demo（同 starter）。

Chunking 是纯资料前处理、不依赖 LLM。Path A == Path B。
要把 retrieval 结果丢给 Claude 生答案、见 练习 4 完整 RAG。
"""

# 同一资料用固定长度、段落、标题三种切法，观察证据是否被切断。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import SAMPLE_DOC, compare_strategies

if __name__ == "__main__":
    print("ℹ️ Chunking 跨 LLM provider 一致、Path A == Path B。")
    out = compare_strategies(SAMPLE_DOC, ["夜市里的食物"], k=1)
    for name, data in out.items():
        print(f"   {name}: {data['chunk_count']} chunks")
    # === 自我验证 ===
    assert set(out) == {"fixed_200_overlap_40", "paragraphs", "headings"}
    assert all(data["queries"] for data in out.values()), "每种切法都要跑查询"
    print("✅ 练习 3 (concept demo) 通过")
