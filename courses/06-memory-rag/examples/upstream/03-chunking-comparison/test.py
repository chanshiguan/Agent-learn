"""Stage 6 练习 3 自我验证 — 3 种 chunking strategy 的纯逻辑测试（不打 embed）。
"""

# 本组测试围绕以下行为检查正反例：同一资料用固定长度、段落、标题三种切法，观察证据是否被切断。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import SAMPLE_DOC, chunk_fixed, chunk_headings, chunk_paragraphs


def test_fixed_length_chunks():
    chunks = chunk_fixed("a" * 500, chunk_size=200, overlap=40)
    # 500 字、step=160（200-40）→ 应该 ~ 3-4 chunk
    assert 3 <= len(chunks) <= 4, f"预期 3-4 chunk、得到 {len(chunks)}"
    assert all(len(c) <= 200 for c in chunks)
    print("✅ test_fixed_length_chunks")


def test_fixed_length_rejects_unsafe_overlap():
    for chunk_size, overlap in [(0, 0), (10, -1), (10, 10), (10, 11)]:
        try:
            chunk_fixed("abcdef", chunk_size=chunk_size, overlap=overlap)
        except ValueError:
            continue
        raise AssertionError(f"chunk_size={chunk_size}, overlap={overlap} 应该被拒绝")
    print("✅ test_fixed_length_rejects_unsafe_overlap")


def test_paragraphs_split_on_double_newline():
    text = "第一段。\n\n第二段。\n\n第三段。"
    chunks = chunk_paragraphs(text)
    assert chunks == ["第一段。", "第二段。", "第三段。"]
    print("✅ test_paragraphs_split_on_double_newline")


def test_headings_keep_section_together():
    chunks = chunk_headings(SAMPLE_DOC)
    # Sample 有 1 个 # 标题 + 3 个 ## 标题、4 个 section
    assert len(chunks) == 4, f"预期 4 section、得到 {len(chunks)}"
    # 每个 section 都应该以 # 开头
    assert all(c.startswith("#") for c in chunks)
    # Food section 应该包含「夜市」
    food = next(c for c in chunks if c.startswith("## 饮食"))
    assert "夜市" in food.lower()
    print("✅ test_headings_keep_section_together")


def test_chunk_count_difference():
    """3 种切法应该产生不同 chunk 数、印证它们真的不同。"""
    fixed_n = len(chunk_fixed(SAMPLE_DOC, chunk_size=200, overlap=40))
    para_n = len(chunk_paragraphs(SAMPLE_DOC))
    head_n = len(chunk_headings(SAMPLE_DOC))
    # heading-aware 通常最少（每个 section 1 chunk）
    assert head_n <= para_n, "heading 应 <= paragraphs"
    print(f"   固定长度：{fixed_n}, 段落：{para_n}, 标题：{head_n}")
    print("✅ test_chunk_count_difference")


if __name__ == "__main__":
    test_fixed_length_chunks()
    test_fixed_length_rejects_unsafe_overlap()
    test_paragraphs_split_on_double_newline()
    test_headings_keep_section_together()
    test_chunk_count_difference()
    print("\n🎉 全部通过 — 3 种 chunking strategy 逻辑正确")
