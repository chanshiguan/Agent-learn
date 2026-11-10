# 目的：把单道检索变成固定题单循环；本节仍不调用生成模型。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import json
import time
from pathlib import Path
from .files import load, save
from .rag import retrieve, answer, rewrite, rerank

# 目的：先开始计时，再找资料；无目标来源的题记为不适用，不凑进召回率。
# 预期：生成 evaluation.json，人工语义评分保持 null。
def evaluate(cases_file, method="keyword", generate=False, expand=False, reranking=False, rewriting=False, output="evaluation.json"):
    cases = json.loads(Path(cases_file).read_text(encoding="utf-8"))
    records = []
    for case in cases:
        started = time.monotonic()
        query = rewrite(case["question"]) if rewriting else case["question"]
        hits = retrieve(query, case.get("tenant", "demo"), case.get("book", "狂人日记"), method, expand=expand)
        if reranking:
            hits = rerank(case["question"], hits)
        prefixes = case.get("expected_document_prefixes", [])
        found = {prefix for prefix in prefixes if any(h["file"].startswith(prefix) for h in hits)}
        quotes = case.get("expected_quotes", [])
        record = {"id": case["id"], "question": case["question"], "query": query,
                  "source_ids": [h["id"] for h in hits], "sources": hits,
                  "document_recall": len(found) / len(prefixes) if prefixes else None,
                  "quote_hit": any(q in h["text"] for q in quotes for h in hits) if quotes else None,
                  "expected_insufficient": case.get("expected_insufficient", False),
                  "manual": {"answer_supported": None, "citation_supported": None, "age_appropriate": None}}
        # 检索测试默认不调用生成模型；generate 显式开启后才可能向云端发送讲稿片段。
        if generate:
            try:
                record["response"] = answer(case["question"], hits)
            except Exception as error:
                record["error_type"] = type(error).__name__
        record["seconds"] = round(time.monotonic() - started, 3)
        records.append(record)
    report = {"corpus_revision": load("corpus.json")["revision"], "method": method,
              "generated": generate, "options": {"expand": expand, "rerank": reranking, "rewrite": rewriting},
              "records": records, "quality_passed": None}
    save(output, report)
    return report

# 目的：三个人工字段必须分别为 true，证据不足行为也要匹配预期；少一项就不能放行。
# 预期：未评分的报告会失败，不能用缺省值蒙混过去。
def quality_gate(report_file):
    report = json.loads(Path(report_file).read_text(encoding="utf-8"))
    failures = []
    if not report.get("generated") or not report.get("records"):
        failures.append("没有真实生成记录。")
    for item in report.get("records", []):
        if item.get("error_type") or not item.get("response"):
            failures.append(f"{item['id']} 没有成功响应。")
        if not all(item.get("manual", {}).get(k) is True for k in ("answer_supported", "citation_supported", "age_appropriate")):
            failures.append(f"{item['id']} 缺少逐项人工通过结论。")
        if item.get("response", {}).get("insufficient") is not item.get("expected_insufficient"):
            failures.append(f"{item['id']} 的证据不足行为未达到预期。")
    return {"passed": not failures, "failures": failures,
            "scope": "仅这份题集的记录；不是生产容量、教学效果或公司上线批准"}
