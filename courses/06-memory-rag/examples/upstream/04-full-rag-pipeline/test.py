"""Stage 6 练习 4 自我验证 — 用 mock LLM 跑完整 RAG pipeline。
"""

# 本组测试围绕以下行为检查正反例：索引阶段读取和切分资料，查询阶段先检索后生成；这是原题的基础管线。

from __future__ import annotations

import re
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import KB_DOC, build_kb, chunk_doc, generate, rag, retrieve


class FakeCollection:
    def __init__(self):
        self.rows: dict[str, str] = {}

    def add(self, ids, documents):
        self.rows.update(dict(zip(ids, documents)))

    def query(self, query_texts, n_results):
        words = set(re.findall(r"[a-z0-9.]+|[\u4e00-\u9fff]", query_texts[0].lower()))
        # 给离线替身补充少量固定关联，让测试能构造相关与不相关结果；它不是通用语义理解。
        aliases = {"version": "python", "days": '休假', "remote": "remote"}
        words |= {aliases[word] for word in words if word in aliases}
        ranked = sorted(
            self.rows.values(),
            key=lambda text: len(words & set(re.findall(r"[a-z0-9.]+|[\u4e00-\u9fff]", text.lower()))),
            reverse=True,
        )[:n_results]
        return {"documents": [ranked]}


class FakeClient:
    def __init__(self):
        self.collections: dict[str, FakeCollection] = {}

    def get_or_create_collection(self, name, embedding_function=None):
        return self.collections.setdefault(name, FakeCollection())


def fake_kb():
    # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
    return build_kb(KB_DOC, client=FakeClient(), embedding_function=lambda rows: rows)


def test_build_kb_uses_fresh_collection_by_default():
    client = FakeClient()
    # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
    first = build_kb(KB_DOC, client=client, embedding_function=lambda rows: rows)
    # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
    second = build_kb("# 另一份文档\n\n这是另一份独立文档。", client=client, embedding_function=lambda rows: rows)
    assert first is not second
    print("✅ test_build_kb_uses_fresh_collection_by_default")


def make_mock_llm(answer: str = "离线模拟答案。"):
    llm = MagicMock()
    msg = SimpleNamespace(content=answer)
    choice = SimpleNamespace(message=msg)
    llm.chat.completions.create.return_value = SimpleNamespace(choices=[choice])
    return llm


def test_chunk_doc_produces_sections():
    chunks = chunk_doc(KB_DOC)
    # 样本文档有 4 个二级标题和 1 个一级标题，按标题切分应得到 5 块
    assert len(chunks) == 5, f"预期 5 个 chunk、得到 {len(chunks)}"
    print("✅ test_chunk_doc_produces_sections")


def test_retrieve_finds_relevant_section():
    collection = fake_kb()
    contexts = retrieve(collection, '年假天数', top_k=1)
    assert '15 天' in contexts[0], f"预期含 '15 days'、得到 {contexts[0]}"
    print("✅ test_retrieve_finds_relevant_section")


def test_generate_uses_context():
    llm = make_mock_llm("你每年有 15 天年假。")
    contexts = ["全职员工享有 15 天带薪年假。"]
    answer = generate("每年有多少天年假？", contexts, llm=llm)
    # 确认 prompt 带上了 context（mock 看 create() 收到的 messages）
    call_args = llm.chat.completions.create.call_args
    prompt = call_args.kwargs["messages"][0]["content"]
    assert '15 天' in prompt, "预期 prompt 含 context"
    assert "每年有多少天年假？" in prompt
    assert '15 天' in answer
    print("✅ test_generate_uses_context")


def test_rag_full_pipeline_with_mock_llm():
    llm = make_mock_llm("Python 3.11+.")
    result = rag("使用哪个 Python 版本？", llm=llm, collection=fake_kb())
    assert result["query"] == "使用哪个 Python 版本？"
    assert len(result["contexts"]) > 0
    assert "Python 3.11" in result["answer"]
    print("✅ test_rag_full_pipeline_with_mock_llm")


def test_rag_top_k_retrieval():
    """确认 retrieve 真的拿了 top_k 个 chunk。"""
    llm = make_mock_llm('示例答案。')
    result = rag('休假', llm=llm, top_k=3, collection=fake_kb())
    assert len(result["contexts"]) == 3
    print("✅ test_rag_top_k_retrieval")


if __name__ == "__main__":
    test_chunk_doc_produces_sections()
    test_build_kb_uses_fresh_collection_by_default()
    test_retrieve_finds_relevant_section()
    test_generate_uses_context()
    test_rag_full_pipeline_with_mock_llm()
    test_rag_top_k_retrieval()
    print("\n🎉 全部通过 — RAG pipeline 完整逻辑正确")
