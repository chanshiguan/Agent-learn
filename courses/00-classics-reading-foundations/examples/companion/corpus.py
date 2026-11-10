"""读取、去重、切分并保留来源；讲次不自动推断成原著章节。"""
import hashlib
import re
from pathlib import Path

from docx import Document
from .files import digest, load, save


def split_text(text, strategy="fixed", size=600, overlap=60):
    if not 0 <= overlap < size or size < 20:
        raise ValueError("需要 size >= 20 且 0 <= overlap < size。")
    if strategy in {"paragraph", "heading"}:
        # 标题模式的分组由外层处理；没有标题的文档不会凭空长出语义结构。
        return [(0, text)]
    return [(start, text[start:start + size]) for start in range(0, len(text), size - overlap)]


def ingest(source="data/input", strategy="fixed", size=600, overlap=60, tenant="demo", book="狂人日记"):
    source = Path(source)
    documents, chunks, duplicates, seen = [], [], [], {}
    annotations = load("ranges.json", {})
    for file in sorted(source.glob("*.docx")):
        version = hashlib.sha256(file.read_bytes()).hexdigest()
        if version in seen:
            duplicates.append({"file": file.name, "same_as": seen[version]})
            continue
        seen[version] = file.name
        document = Document(file)
        doc_id = digest([tenant, book, file.name])[:16]
        lecture = re.search(r"第([一二三四五六七八九十]+)讲", file.name)
        groups = []
        for position, paragraph in enumerate(document.paragraphs, 1):
            text = paragraph.text.strip()
            if not text:
                continue
            heading = paragraph.style.name.startswith("Heading") if paragraph.style else False
            if strategy == "heading" and groups and not heading:
                groups[-1][1] += "\n" + text
            else:
                groups.append([f"p{position:04d}", text])
        if not groups:
            # 整批成功后才发布新快照，避免把扫描件或空文档悄悄当作已完成的导入。
            raise ValueError(f"{file.name} 没有可读正文；本次导入未更新资料快照。")
        documents.append({"doc_id": doc_id, "version": version, "file": file.name,
                          "tenant": tenant, "book": book, "paragraphs": len(groups), "tables_skipped": len(document.tables)})
        for parent, text in groups:
            for start, part in split_text(text, strategy, size, overlap):
                chunk_id = digest([doc_id, version, parent, strategy, size, overlap, start])[:24]
                review = annotations.get(chunk_id, {})
                if review.get("reviewed") is True and (type(review.get("range_end")) is not int or review["range_end"] < 0):
                    raise ValueError("已审核的阅读范围必须是非负整数，不能用 true/false 代替。")
                chunks.append({"id": chunk_id, "doc_id": doc_id, "version": version,
                               "tenant": tenant, "book": book, "file": file.name,
                               "kind": "讲解稿", "lecture": lecture.group(1) if lecture else None,
                               "edition": None, "parent": parent, "start": start,
                               "end": start + len(part), "text": part,
                               "range_end": review.get("range_end"),
                               "range_reviewed": review.get("reviewed") is True})
    if not chunks:
        raise ValueError("没有可读正文，请检查输入目录；原文件不会被覆盖。")
    previous = load("corpus.json", {"documents": [], "chunks": []})
    documents += [d for d in previous["documents"] if (d.get("tenant", "demo"), d.get("book", "狂人日记")) != (tenant, book)]
    chunks += [c for c in previous["chunks"] if (c["tenant"], c["book"]) != (tenant, book)]
    result = {"documents": documents, "chunks": chunks, "duplicates": duplicates,
              "strategy": strategy, "size": size, "overlap": overlap}
    result["revision"] = digest(result)
    save("corpus.json", result)
    return {"documents": len(documents), "chunks": len(chunks), "duplicates": duplicates,
            "revision": result["revision"], "tables_skipped": sum(d["tables_skipped"] for d in documents)}


def visible(chunks, tenant, book, progress=None):
    # 先限制可见范围再排序，避免先检索出其他租户资料，再让模型自己过滤。
    result = [c for c in chunks if c["tenant"] == tenant and c["book"] == book]
    if progress is not None:
        result = [c for c in result if c.get("range_reviewed") is True
                  and type(c.get("range_end")) is int and 0 <= c["range_end"] <= progress]
    return result


def terms(text):
    # 中文双字片段是可解释的入门词面基线，不冒称完整分词器或 BM25。
    lower = text.lower()
    words = set(re.findall(r"[a-z0-9]+", lower))
    for run in re.findall(r"[\u4e00-\u9fff]+", lower):
        words.update(run[i:i + 2] for i in range(len(run) - 1))
    return words


def keyword_search(question, chunks, k=5):
    query = terms(question)
    ranked = []
    for chunk in chunks:
        matches = query & terms(chunk["text"])
        if matches:
            ranked.append({**chunk, "score": len(matches) / max(1, len(query))})
    return sorted(ranked, key=lambda c: (-c["score"], c["id"]))[:k]


def neighbors(hits, chunks):
    selected = {c["id"]: c for c in hits}
    for hit in hits:
        siblings = sorted((c for c in chunks if c["doc_id"] == hit["doc_id"] and c["parent"] == hit["parent"]), key=lambda c: c["start"])
        position = next((i for i, c in enumerate(siblings) if c["id"] == hit["id"]), -1)
        if position >= 0:
            for item in siblings[max(0, position - 1):position + 2]:
                selected[item["id"]] = item
    return list(selected.values())
