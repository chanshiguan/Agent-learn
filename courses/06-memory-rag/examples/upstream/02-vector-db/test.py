"""Stage 6 练习 2 自我验证 — Chroma collection + query 逻辑。

运行方法：
    python test.py

测试使用 fake collection，不下载 embedding model，也不连 API。
"""

# 本组测试围绕以下行为检查正反例：先建立 collection 并写入资料，再比较字词与向量查询；保留 ID 才能回到原记录。

from __future__ import annotations

import re
import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import DOCS, build_collection, index_docs, keyword_query, semantic_query


class FakeCollection:
    """只模拟本课会用到的 Chroma 行为，测试时不下载模型。"""

    def __init__(self):
        self.rows: dict[str, dict] = {}

    def count(self):
        return len(self.rows)

    def get(self):
        return {
            "ids": list(self.rows),
            "documents": [row["text"] for row in self.rows.values()],
        }

    def add(self, ids, documents, metadatas):
        for doc_id, text, metadata in zip(ids, documents, metadatas):
            self.rows[doc_id] = {"text": text, "metadata": metadata}

    def query(self, query_texts, n_results):
        # 这个离线替身按字符或词重叠近似排序，只用来验证管线；不能用它的结果证明真实向量模型质量。
        query_words = set(re.findall(r"[a-z]+|[\u4e00-\u9fff]", query_texts[0].lower()))
        # 给离线替身补充少量固定关联，让测试能构造相关与不相关结果；它不是通用语义理解。
        aliases = {"typed": "typing", "drink": '咖啡', "language": "python"}
        query_words |= {aliases[word] for word in query_words if word in aliases}
        ranked = sorted(
            self.rows.items(),
            key=lambda item: len(query_words & set(re.findall(r"[a-z]+|[\u4e00-\u9fff]", item[1]["text"].lower()))),
            reverse=True,
        )[:n_results]
        return {
            "ids": [[doc_id for doc_id, _ in ranked]],
            "documents": [[row["text"] for _, row in ranked]],
            "distances": [[float(i) for i in range(len(ranked))]],
        }


class FakeClient:
    def __init__(self):
        self.collections: dict[str, FakeCollection] = {}

    def get_or_create_collection(self, name, embedding_function=None):
        return self.collections.setdefault(name, FakeCollection())


def fresh_collection():
    # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
    return build_collection(client=FakeClient(), embedding_function=lambda rows: rows)


def test_default_memory_collections_are_isolated():
    client = FakeClient()
    # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
    first = build_collection(client=client, embedding_function=lambda rows: rows)
    # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
    second = build_collection(client=client, embedding_function=lambda rows: rows)
    assert first is not second
    print("✅ test_default_memory_collections_are_isolated")


def test_docs_corpus_shape():
    assert len(DOCS) == 8
    assert all({"id", "text", "category"} <= d.keys() for d in DOCS)
    print("✅ test_docs_corpus_shape")


def test_index_and_count():
    collection = fresh_collection()
    index_docs(collection, DOCS)
    # 先确认集合中有多少记录，用于处理空库和限制返回数量，避免对空索引盲目查询。
    assert collection.count() == 8, f"预期 8 doc、得到 {collection.count()}"
    print("✅ test_index_and_count")


def test_semantic_query_ranks_relevant_first():
    """问题含“咖啡”时，离线排序应召回第 3 条咖啡馆资料。"""
    collection = fresh_collection()
    index_docs(collection, DOCS)
    results = semantic_query(collection, "哪里能喝到好咖啡", top_k=3)
    top_ids = [r["id"] for r in results]
    assert "3" in top_ids, f"预期 doc 3（coffee shops）出现在 top-3、得到 {top_ids}"
    print("✅ test_semantic_query_ranks_relevant_first")


def test_keyword_vs_semantic_difference():
    """分别检查向量接口与关键词接口；这里的替身按字词重叠排序，不证明语义泛化。"""
    collection = fresh_collection()
    index_docs(collection, DOCS)

    # 用中文问题检查候选 ID 能否回到对应的原始资料。
    sem_results = semantic_query(collection, "使用动态类型的编程语言", top_k=2)
    sem_ids = [r["id"] for r in sem_results]
    assert "2" in sem_ids, f"semantic 应抓到 doc 2、得到 {sem_ids}"

    # 关键词基线只做子串匹配，传入明确关键词“咖啡”，不把它当作中文分词器。
    # 检查命中的原文确实包含关键词，防止返回数量正确但内容不对应。
    kw_results = keyword_query(DOCS, '咖啡', top_k=3)
    assert any('咖啡' in r["text"].lower() for r in kw_results)
    print("✅ test_keyword_vs_semantic_difference")


def test_top_k_respected():
    collection = fresh_collection()
    index_docs(collection, DOCS)
    assert len(semantic_query(collection, "test", top_k=2)) == 2
    assert len(semantic_query(collection, "test", top_k=5)) == 5
    print("✅ test_top_k_respected")


if __name__ == "__main__":
    test_docs_corpus_shape()
    test_default_memory_collections_are_isolated()
    test_index_and_count()
    test_semantic_query_ranks_relevant_first()
    test_keyword_vs_semantic_difference()
    test_top_k_respected()
    print("\n🎉 全部通过 — Chroma vector DB 逻辑正确")
