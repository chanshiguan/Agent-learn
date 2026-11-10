"""把一份讲稿的正文段落保存为 JSON，保留回查来源所需的信息。"""

import argparse
import hashlib
import json
from pathlib import Path

from docx import Document


parser = argparse.ArgumentParser(description="读取一份 DOCX 讲稿")
parser.add_argument("source", type=Path, help="输入的 .docx 文件")
parser.add_argument("output", type=Path, help="新生成的 .json 文件")
args = parser.parse_args()
if not args.source.is_file() or args.source.suffix.lower() != ".docx":
    parser.error("输入必须是存在的 .docx 文件。先检查路径和引号。")
if args.output.suffix.lower() != ".json":
    parser.error("输出请使用 .json 扩展名，避免误把原讲稿当成输出覆盖。")

document = Document(args.source)
paragraphs = []
for position, paragraph in enumerate(document.paragraphs, start=1):
    text = paragraph.text.strip()
    if text:
        # 保留 Word 正文中的位置，而不是过滤空段后重新编号，方便回查原文件。
        paragraphs.append({"id": f"p{position:04d}", "text": text})

if not paragraphs:
    parser.error("正文没有读出文字。请检查是否为扫描图片或主要内容在表格中。")

result = {
    "source_file": args.source.name,
    "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
    "source_kind": "讲解稿",
    "unit": "Word 正文段落，不是原著章回",
    "paragraph_count": len(paragraphs),
    "character_count": sum(len(item["text"]) for item in paragraphs),
    "skipped_table_count": len(document.tables),
    "paragraphs": paragraphs,
}

args.output.parent.mkdir(parents=True, exist_ok=True)
# 保存为 UTF-8，并直接保留中文，便于用编辑器逐段核对，不必先读转义字符。
args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"来源：{result['source_file']}")
print(f"正文非空段落：{result['paragraph_count']}；字符数：{result['character_count']}")
print(f"输出：{args.output}")
if document.tables:
    print("注意：本章程序不读取表格；请在记录里说明这项遗漏。")
