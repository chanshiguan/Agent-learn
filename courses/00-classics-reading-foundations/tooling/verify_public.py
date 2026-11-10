"""验证公开文件白名单、样本来源和静态教材链接；不会执行模型或部署。"""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

course = Path(__file__).resolve().parents[1]
root = course.parents[1]
sys.path.insert(0, str(course / "examples"))
from prepare_samples import render_docx

manifest = json.loads((root / "publication-files.json").read_text())
materials = json.loads((course / "public-materials/manifest.json").read_text())
sample_bytes = {row["file"]: render_docx((course / "public-materials" / row["text"]).read_text())[0]
                for row in materials["documents"]}
allowed_data = {f"examples/data/input/{name}" for name in sample_bytes} | {"examples/data/sample-manifest.json"}
files = []
for name in manifest["files"]:
    file = root / name
    if file.is_symlink() or not file.resolve().is_relative_to(root) or not file.is_file():
        raise ValueError(f"发布文件缺失或越界：{name}")
    if any(part in {".git", ".scratch", ".venv", "__pycache__", "node_modules", "learning-records"} for part in file.relative_to(root).parts):
        raise ValueError(f"发布清单不应包含运行或私人目录：{name}")
    if file.name == ".env" or file.name.startswith(".env."):
        raise ValueError("发布清单包含环境凭据文件。")
    if file.is_relative_to(course / "examples/data") and str(file.relative_to(course)) not in allowed_data:
        raise ValueError(f"发布清单混入未批准数据：{name}")
    if file.suffix == ".docx" and (file.name not in sample_bytes or file.read_bytes() != sample_bytes[file.name]):
        raise ValueError("Word 文件与公开 Markdown 生成结果不符。")
    if file.suffix in {".md", ".html", ".json", ".py", ".js", ".mjs", ".yaml", ".yml"}:
        text = file.read_text()
        # 只查实际个人绝对路径，正常教材中的路径说明和合成测试字符串不算凭据。
        if re.search(r"/Users/[A-Za-z0-9._-]+/", text):
            raise ValueError(f"文件含个人电脑路径：{name}")
    files.append(file)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids = [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag in {"a", "link", "script"} and (value := attrs.get("href") or attrs.get("src")):
            self.links.append(value)


pages = [file for file in files if file.suffix == ".html" and not file.is_relative_to(course / "examples")]
for file in pages:
    parsed = Page(file.read_text())
    assert len(parsed.ids) == len(set(parsed.ids)), file.name
    for link in parsed.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = (file.parent / unquote(url.path)).resolve() if url.path else file
        assert target.is_relative_to(root) and target.is_file(), (file.name, link)
        if url.fragment and target.suffix == ".html":
            assert unquote(url.fragment) in Page(target.read_text()).ids, (file.name, link)
blocks = 0
for file in [*(course / "text").glob("*.md"), course / "reference.md"]:
    for block in re.findall(r"```bash\n(.*?)\n```", file.read_text(), re.S):
        assert block.startswith("# "), file.name
        subprocess.run(["bash", "-n"], input=block, text=True, check=True)
        blocks += 1
with ZipFile(course / "classics-companion-course.zip") as archive:
    actual = {name for name in archive.namelist() if name.endswith(".docx")}
    expected = {f"classics-companion-course/courses/{course.name}/examples/data/input/{name}" for name in sample_bytes}
    assert actual == expected
    for name in actual:
        assert archive.read(name) == sample_bytes[Path(name).name]
    allowed = {"classics-companion-course/" + name for name in manifest["files"]} | {"classics-companion-course/publication-files.json"}
    assert set(archive.namelist()) == allowed, "压缩包内容与发布白名单不同。"
print(json.dumps({"public_files": len(files), "public_docx": len(sample_bytes), "static_pages": len(pages),
                  "shell_blocks": blocks, "package_allowlist": "passed"}, ensure_ascii=False))
