# 目的：上一节每换一讲都要改代码。现在让运行命令选择文件，并阻止把输出写回 Word。
# 预期：写完这一步可先运行 python read_docx.py --help，看到两个位置参数；给出错误后缀时会停止。
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

# 目的：跳过空段，但不重新编号，后面引用仍能指回 Word 原来的位置。空正文应失败。
# 预期：用本页的 DOCX 与 JSON 两个路径参数运行，先打印已读取的非空段数 1；此时还没有写出 JSON。
document = Document(args.source)
paragraphs = []
for position, paragraph in enumerate(document.paragraphs, start=1):
    text = paragraph.text.strip()
    if text:
        # 保留 Word 正文中的位置，而不是过滤空段后重新编号，方便回查原文件。
        paragraphs.append({"id": f"p{position:04d}", "text": text})

if not paragraphs:
    parser.error("正文没有读出文字。请检查是否为扫描图片或主要内容在表格中。")


# 先观察中间结果，避免到写入后才发现正文没有读到。
print("已读取的非空段数：", len(paragraphs))

# 目的：只保存正文会丢失出处。文件名、指纹、段落数和字符数一起保存，后续能识别换稿。
# 预期：再次运行，多显示待保存的来源文件名；JSON 仍要等下一步写入。相同输入指纹相同，它不是原著页码。
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


# 写入之前先核对来源，防止把另一讲的内容保存成第一讲。
print("待保存的来源：", result["source_file"])

# 目的：JSON 是后续程序可读取的中间结果；先保留中文和缩进，方便你人工核查。
# 预期：第一讲输出 1 段、1302 字，生成 data/output/first.json。
args.output.parent.mkdir(parents=True, exist_ok=True)
# 保存为 UTF-8，并直接保留中文，便于用编辑器逐段核对，不必先读转义字符。
args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"来源：{result['source_file']}")
print(f"正文非空段落：{result['paragraph_count']}；字符数：{result['character_count']}")
print(f"输出：{args.output}")
if document.tables:
    print("注意：本章程序不读取表格；请在记录里说明这项遗漏。")
