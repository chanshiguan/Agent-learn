# 目的：沿用第一章 JSON 的字段；一条开关决定是否提供资料，其余请求条件保持一致。
# 预期：manual-context.json 和 manual-no-context.json 可以并排核对。
import argparse
import json
from pathlib import Path
from .files import save
from .models import complete
from .rag import answer


def main():
    parser = argparse.ArgumentParser(description="手工选择一段资料")
    parser.add_argument("--file", default="data/output/first.json")
    parser.add_argument("--start", type=int, default=200)
    parser.add_argument("--chars", type=int, default=900)
    parser.add_argument("--question", default="这份讲稿怎样解释文言文序言与白话日记的关系？")
    parser.add_argument("--no-context", action="store_true")
    args = parser.parse_args()
    document = json.loads(Path(args.file).read_text(encoding="utf-8"))
    text = document["paragraphs"][0]["text"][args.start:args.start + args.chars]
    if args.no_context:
        result = complete([{"role": "user", "content": args.question}])
        result["knowledge_base_used"] = False
    else:
        if not text:
            raise ValueError("范围内没有文字，请检查起点与长度。")
        result = answer(args.question, [{"id": "manual-01", "file": document["source_file"],
                         "kind": "讲解稿", "text": text, "start": args.start}])
    name = "manual-no-context.json" if args.no_context else "manual-context.json"
    save(name, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
