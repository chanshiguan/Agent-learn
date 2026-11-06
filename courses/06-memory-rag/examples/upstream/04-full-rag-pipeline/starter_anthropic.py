"""Stage 6 练习 4：完整 RAG — Path B（Anthropic Claude）。

跟 starter.py 同一个 pipeline、只把 generate() 的 LLM 换成 Claude。
Chunking + retrieval（vector DB）跨 backend 一致。

运行方法：
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...
    python starter_anthropic.py

预算：每次 ≈ $0.001（claude-haiku-4-5、短 context + 短答案）。
Production RAG 通常用 cloud LLM 生成、答案质量明显比 qwen2.5:3b 高。
"""

# 索引阶段读取和切分资料，查询阶段先检索后生成；这是原题的基础管线。
# 这是原题的另一供应商路径；共享的检索、工具或状态逻辑仍需遵守相同验收条件。

from __future__ import annotations

import os
import sys
from typing import Any

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import anthropic

from starter import KB_DOC, build_kb, retrieve

MODEL = os.environ.get("MODEL", "claude-haiku-4-5")


# 将检索到的上下文交给 Claude 生成答案，依赖调用者的有效凭证。
def generate_anthropic(query: str, contexts: list[str], client: Any = None) -> str:
    client = client or anthropic.Anthropic()
    # 把检索片段明确拼成证据区域，使问题与资料可区分；片段里出现指令也不能提升为系统权限。
    context_text = "\n\n---\n\n".join(contexts)
    prompt = f"""只依据下面的资料用中文回答。若资料不包含答案，明确回复“资料中没有这项信息”。

参考资料：
{context_text}

问题：{query}

回答："""
    resp = client.messages.create(
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=MODEL,
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        max_tokens=300,
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        messages=[{"role": "user", "content": prompt}],
    )
    return " ".join(b.text for b in resp.content if b.type == "text")


# 复用检索步骤，只替换生成服务，便于比较两条调用路径。
def rag_anthropic(query: str, doc: str = KB_DOC, top_k: int = 2) -> dict:
    collection = build_kb(doc)
    contexts = retrieve(collection, query, top_k=top_k)
    answer = generate_anthropic(query, contexts)
    return {"query": query, "contexts": contexts, "answer": answer}


if __name__ == "__main__":
    queries = [
        "我每年有多少天年假？",
        "使用哪个 Python 版本？",
    ]
    for q in queries:
        print(f"\n❓ {q}")
        result = rag_anthropic(q)
        print(f"   回答：{result['answer']}")
    # === 自我验证 ===
    assert result["contexts"], "RAG 应找回至少一段 context"
    assert result["answer"], "Claude 应返回文字答案"
    print(f"\n✅ 练习 4 (Anthropic) 通过 — Claude {MODEL}")
