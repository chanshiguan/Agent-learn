"""按发布清单打包公开课程，拒绝混入未列出的业务文件。"""

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


course = Path(__file__).resolve().parents[1]
root = course.parents[1]
manifest = json.loads((root / "publication-files.json").read_text(encoding="utf-8"))
samples = json.loads((course / "examples/data/sample-manifest.json").read_text(encoding="utf-8"))
for item in samples["documents"]:
    content = (course / "examples/data/input" / item["file"]).read_bytes()
    if hashlib.sha256(content).hexdigest() != item["sha256"]:
        raise ValueError("公开样本已改变，请核对公开 Markdown 并重新准备样本，再更新发布清单。")

files = []
for name in manifest["files"]:
    file = root / name
    # 清单不允许跳出发布目录；符号链接也不应把外部资料带进包。
    if file.is_symlink() or not file.resolve().is_relative_to(root) or not file.is_file():
        raise ValueError(f"发布清单包含不可打包路径：{name}")
    files.append(file)

output = course / "classics-companion-course.zip"
temporary = output.with_suffix(".zip.tmp")
try:
    with ZipFile(temporary, "w", ZIP_DEFLATED) as archive:
        for file in files:
            archive_name = Path("classics-companion-course") / file.relative_to(root)
            if file == course / "resources.html":
                # 解压包内不链接自身 ZIP；网站目录仍保留下载入口。
                content = file.read_text().replace('<a href="classics-companion-course.zip" download><strong>下载完整课程包 ↓</strong><span>讲义、拓展、示例与五份课程自编样本。</span></a>', '<div class="package-ready"><strong>公开课程包已在本地</strong><p>本目录已包含讲义、代码和五份新编样本，可以开始练习。</p></div>')
                archive.writestr(str(archive_name), content)
            else:
                archive.write(file, archive_name)
        archive.write(root / "publication-files.json", "classics-companion-course/publication-files.json")
    # 先写临时文件，成功关闭后再替换，避免失败时留下半个课程包。
    temporary.replace(output)
finally:
    temporary.unlink(missing_ok=True)
print(f"公开课程包：{output.name}，{output.stat().st_size} 字节")
