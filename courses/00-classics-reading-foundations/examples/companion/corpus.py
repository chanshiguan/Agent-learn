# 目的：把读取一讲扩成整理多讲，仍保留可回查的文件名和段落位置。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import hashlib
import re
from pathlib import Path
from docx import Document
from .files import digest, load, save

# 目的：模型窗口有限，先用可计算的长度和重叠建立基线，后面才能比较其他切法。
# 预期：600 字块、60 字重叠的下一起点是 540；非法重叠会报错。
def split_text(text, strategy="fixed", size=600, overlap=60):
    if not 0 <= overlap < size or size < 20:
        raise ValueError("需要 size >= 20 且 0 <= overlap < size。")
    if strategy in {"paragraph", "heading"}:
        # 标题模式的分组由外层处理；没有标题的文档不会凭空长出语义结构。
        return [(0, text)]
    return [(start, text[start:start + size]) for start in range(0, len(text), size - overlap)]

# 目的：外层循环负责文件，内层负责段落与块；一次全部成功后才替换 corpus.json。
# 预期：五份原始讲稿不改动；600/60 应得到 15 块，空正文会拒绝。
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

# 目的：先限制机构和作品，避免排完名才发现搜索了别人的资料。
# 预期：不同作品的块在评分前就被排除。
def visible(chunks, tenant, book, progress=None):
    # 先限制可见范围再排序，避免先检索出其他租户资料，再让模型自己过滤。
    result = [c for c in chunks if c["tenant"] == tenant and c["book"] == book]
    if progress is not None:
        result = [c for c in result if c.get("range_reviewed") is True
                  and type(c.get("range_end")) is int and 0 <= c["range_end"] <= progress]
    return result

# 目的：用中文相邻双字片段和英文数字词建立可解释基线，不把它叫作完整分词器。
# 预期：命中只表示词面相关；没有资料的事实不会因此出现。
def terms(text):
    # 中文双字片段是可解释的入门词面基线，不冒称完整分词器或 BM25。
    lower = text.lower()
    words = set(re.findall(r"[a-z0-9]+", lower))
    for run in re.findall(r"[\u4e00-\u9fff]+", lower):
        words.update(run[i:i + 2] for i in range(len(run) - 1))
    return words

# 目的：计算问题与每块文字的词面交集，按分数排序并保留前五条。
# 预期：命中只表示词面相关；没有资料的事实不会因此出现。
def keyword_search(question, chunks, k=5):
    query = terms(question)
    ranked = []
    for chunk in chunks:
        matches = query & terms(chunk["text"])
        if matches:
            ranked.append({**chunk, "score": len(matches) / max(1, len(query))})
    return sorted(ranked, key=lambda c: (-c["score"], c["id"]))[:k]

# 目的：检索小块容易缺少前因；只补同一父段落附近内容，避免把不相关文档拼在一起。
# 预期：每个块只出现一次，范围过滤在扩展前已经完成。
def neighbors(hits, chunks):
    selected = {c["id"]: c for c in hits}
    for hit in hits:
        siblings = sorted((c for c in chunks if c["doc_id"] == hit["doc_id"] and c["parent"] == hit["parent"]), key=lambda c: c["start"])
        position = next((i for i, c in enumerate(siblings) if c["id"] == hit["id"]), -1)
        if position >= 0:
            for item in siblings[max(0, position - 1):position + 2]:
                selected[item["id"]] = item
    return list(selected.values())
