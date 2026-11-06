"""Stage 6 练习 2：Vector DB — Path B 概念展示。

Chroma 本身是本机 vector DB、不依赖 LLM provider。Path B 跟 Path A 跑出来一样。
RAG 流水线里的 LLM 步骤（generation）会在练习 4 才出现——这题只测 retrieval。

要切 cloud-grade embedding（OpenAI / Voyage）见 starter.py 注解：
    把 embed_fn 换成 OpenAIEmbeddingFunction(api_key=..., model_name=...)
"""

# 先建立 collection 并写入资料，再比较字词与向量查询；保留 ID 才能回到原记录。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import DOCS, build_collection, index_docs, semantic_query

if __name__ == "__main__":
    print("ℹ️ Vector DB（Chroma）跨 LLM provider 一致。Path A == Path B。")
    print("   Cloud embedding 替换在 build_collection() 注解、不必跑 LLM。\n")
    collection = build_collection()
    index_docs(collection, DOCS)
    results = semantic_query(collection, "亚洲城市中的咖啡", top_k=2)
    for r in results:
        print(f"   {r}")
    # === 自我验证 ===
    # 先确认集合中有多少记录，用于处理空库和限制返回数量，避免对空索引盲目查询。
    assert collection.count() == len(DOCS), "全部文件都应写入 collection"
    assert len(results) == 2, "top_k=2 应返回两笔"
    print("✅ 练习 2 (concept demo) 通过")
