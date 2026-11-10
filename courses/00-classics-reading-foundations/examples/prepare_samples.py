"""从公开 Markdown 生成确定的 DOCX；不读取私人知识库，也不联网。"""

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from docx import Document


MATERIALS = Path(__file__).resolve().parents[1] / "public-materials"


def render_docx(markdown):
    # 只去掉标题标记，保留文字与段内换行，供后续“长段落切块”实验使用。
    text = re.sub(r"^#{1,6} +", "", markdown, flags=re.MULTILINE).strip()
    document = Document()
    props = document.core_properties
    props.author = "名著伴读课程"
    props.last_modified_by = ""
    props.title = text.splitlines()[0]
    props.subject = "课程自编讲解稿"
    props.comments = "由公开 Markdown 生成；非私人授课转写稿。"
    props.created = props.modified = datetime(2000, 1, 1, tzinfo=timezone.utc)
    document.add_paragraph(text)
    buffer = BytesIO()
    document.save(buffer)
    result = BytesIO()
    # DOCX 本质是 ZIP；固定条目时间，避免相同正文因生成时间不同而改变指纹。
    with ZipFile(buffer) as source, ZipFile(result, "w", ZIP_DEFLATED) as target:
        for name in sorted(source.namelist()):
            entry = ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            target.writestr(entry, source.read(name))
    return result.getvalue(), text


def prepare(output):
    manifest = json.loads((MATERIALS / "manifest.json").read_text(encoding="utf-8"))
    pending, records = [], []
    for item in manifest["documents"]:
        source = MATERIALS / item["text"]
        content, text = render_docx(source.read_text(encoding="utf-8"))
        destination = output / item["file"]
        # 先检查完全部输入再写文件，避免遇到冲突时只更新了一半样本。
        if destination.exists() and destination.read_bytes() != content:
            raise ValueError(f"已有不同内容，未覆盖：{destination.name}；请备份后改用空目录。")
        pending.append((destination, content))
        records.append({"file": item["file"], "source": "public-materials/" + item["text"],
                        "source_kind": manifest["source_kind"], "lecture": item["lecture"],
                        "sha256": hashlib.sha256(content).hexdigest(),
                        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                        "bytes": len(content), "paragraph_count": 1, "character_count": len(text)})
    output.mkdir(parents=True, exist_ok=True)
    for destination, content in pending:
        if not destination.exists():
            destination.write_bytes(content)
    # 清单只记录仓库内的来源名，不写作者电脑的绝对路径。
    record = {"version": manifest["version"], "documents": records}
    (output.parent / "sample-manifest.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/input"))
    args = parser.parse_args()
    try:
        result = prepare(args.output)
    except ValueError as error:
        parser.error(str(error))
    print(f"已准备 {len(result['documents'])} 份课程自编讲解稿；来源见 data/sample-manifest.json。")
