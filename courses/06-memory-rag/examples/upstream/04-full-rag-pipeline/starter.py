"""Stage 6 练习 4：完整 RAG 流水线 — Path A（Ollama 默认、$0）。

document → chunk → embed → top-k retrieve → LLM 生答案

运行方法：
    pip install -r requirements.txt
    ollama pull qwen2.5:3b
    ollama serve
    python starter.py

验证：
    python test.py

预算：$0/run。Path B 用 Claude 生答案、见 starter_anthropic.py。
"""

# 索引阶段读取和切分资料，查询阶段先检索后生成；这是原题的基础管线。

from __future__ import annotations

import os
import sys
import uuid
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from openai import OpenAI

MODEL = os.environ.get("MODEL", "qwen2.5:3b")
OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434/v1")
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


# 固定教学知识库：用已知资料检查检索和引用流程，不把这些样例当作实时事实
KB_DOC = """# 公司入职教学样本

## 休假政策

全职员工每年享有 15 天带薪年假，按月累计。未用天数最多可结转 5 天至下一年。休假须至少提前一周通过人事门户申请。

## 远程办公

混合办公安排为每周到办公室 3 天、远程办公 2 天。完全远程办公须得到经理批准，并经人事部门审核。

## 费用报销

收据须在 30 天内通过 Concur 提交。超过 50 美元的餐费须事先批准。差旅只能通过公司的差旅门户预订。

## 技术栈

后端使用 Python 3.11 及以上版本，前端使用 React 18。代码审查是必需步骤；合并到 main 前至少需要一人批准。
"""


def chunk_doc(text: str) -> list[str]:
    """按标题边界切分，尽量将同一节内容保留在一起。"""
    import re
    sections = re.split(r"\n(?=#{1,3} )", text)
    return [s.strip() for s in sections if s.strip()]


# 先切分资料再加入向量库，查询阶段复用这个库。
def build_kb(
    doc: str,
    *,
    client: Any = None,
    embedding_function: Any = None,
    collection_name: str | None = None,
) -> Any:
    if client is None:
        import chromadb
        client = chromadb.EphemeralClient()
    if embedding_function is None:
        from chromadb.utils import embedding_functions
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            # model_name：选择文本编码模型；入库文档和查询必须用同一种编码方式，不能混用不同模型产生的向量。
            model_name=EMBED_MODEL,
        )
    # 集合名决定资料隔离与复用范围；独立实验不能误用另一次实验留下的索引。
    collection_name = collection_name or f"knowledge_base_{uuid.uuid4().hex[:8]}"
    # 按名称取得集合，不存在时创建；是否复用由 collection_name 决定，编码函数必须与已有索引一致。
    collection = client.get_or_create_collection(
        name=collection_name,
        # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
        embedding_function=embedding_function,
    )
    chunks = chunk_doc(doc)
    collection.add(
        # ids：为每条记录保留稳定标识，便于去重、更新和回查来源；不要只保存脱离原文的向量。
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        # documents：把可供人核对的原文与向量一起保存，生成答案时才能拿到证据，而不只是一个相似度分数。
        documents=chunks,
    )
    return collection


def retrieve(collection: Any, query: str, top_k: int = 2) -> list[str]:
    # 把单个问题作为一项批量查询，取 top_k 个候选；检索只返回资料，不会自动生成或验证答案。
    result = collection.query(query_texts=[query], n_results=top_k)
    # documents 外层对应查询批次；本次只传了一个问题，所以第 0 项才是这个问题的候选片段列表。
    return result["documents"][0]


def generate(query: str, contexts: list[str], llm: Any = None) -> str:
    """把检索片段和问题一起交给模型，要求只据此回答。"""
    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    llm = llm or OpenAI(base_url=OLLAMA_BASE, api_key="ollama")
    # 把检索片段明确拼成证据区域，使问题与资料可区分；片段里出现指令也不能提升为系统权限。
    context_text = "\n\n---\n\n".join(contexts)
    prompt = f"""只依据下面的资料用中文回答。若资料不包含答案，明确回复“资料中没有这项信息”。

参考资料：
{context_text}

问题：{query}

回答："""
    resp = llm.chat.completions.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=MODEL,
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content or ""


# 把检索结果传入生成步骤；不能省略检索却把模型回答称为 RAG。
def rag(
    query: str,
    doc: str = KB_DOC,
    llm: Any = None,
    top_k: int = 2,
    collection: Any = None,
) -> dict:
    """串起切分、索引、检索与生成的完整 RAG 流程。"""
    collection = collection or build_kb(doc)
    contexts = retrieve(collection, query, top_k=top_k)
    answer = generate(query, contexts, llm=llm)
    return {"query": query, "contexts": contexts, "answer": answer}


if __name__ == "__main__":
    queries = [
        "我每年有多少天年假？",
        "我可以完全远程办公吗？",
        "使用哪个 Python 版本？",
    ]
    for q in queries:
        print(f"\n❓ {q}")
        result = rag(q)
        print(f"   检索片段数：{len(result['contexts'])}")
        print(f"   回答：{result['answer']}")

    # === 自我验证 ===
    result = rag("我每年有多少天年假？")
    # 下面第一行检查检索片段是否包含休假天数；第二行在失败时展示实际检索片段。
    assert any('15 天' in c for c in result["contexts"]), \
        f"预期 retrieve 到含 15 days 的 chunk、得到 {result['contexts']}"
    assert result["answer"], "模型应返回文字答案"
    print("\n✅ 练习 4 通过 — 完整 RAG pipeline 跑通、$0/run（使用 Ollama {MODEL})")
