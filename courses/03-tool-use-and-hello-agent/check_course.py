"""检查本课 HTML 的本地链接、锚点及案例源码是否完整展示。"""

import ast
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent


class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.links = []
        self.ids = set()
        self.codes = []
        self.in_code = False
        self.current_code = ""
        self.duplicates = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.duplicates.append(attrs["id"])
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])
        if tag == "code":
            self.in_code = True
            self.current_code = ""

    def handle_data(self, data):
        if self.in_code:
            self.current_code += data

    def handle_endtag(self, tag):
        if tag == "code" and self.in_code:
            self.codes.append(self.current_code)
            self.in_code = False


def main():
    paths = [ROOT.parent / "index.html", ROOT / "index.html", *(ROOT / "lessons").glob("*.html"),
             *(ROOT / "reference").glob("*.html")]
    documents = {path.resolve(): Document(path) for path in paths}
    errors = []
    checked = 0
    for path, document in documents.items():
        errors.extend(f"{path.name}: 重复锚点 {identifier}" for identifier in document.duplicates)
        for link in document.links:
            url = urlsplit(link)
            if url.scheme in ("http", "https"):
                errors.append(f"{path.name}: 学习页含外链 {link}")
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.is_file():
                errors.append(f"{path.name}: 找不到本地文件 {link}")
                continue
            if url.fragment and target.suffix == ".html":
                target_doc = documents.get(target) or Document(target)
                if unquote(url.fragment) not in target_doc.ids:
                    errors.append(f"{path.name}: 找不到锚点 {link}")
            checked += 1
    library = documents[(ROOT / "reference/code-library.html").resolve()]
    for path in (ROOT / "examples").iterdir():
        if path.suffix in (".py", ".patch") or path.name in ("eval_cases.json", "requirements.txt", "requirements-libraries.txt"):
            if path.read_text().strip() not in library.codes:
                errors.append(f"代码集未完整同步：{path.name}")
        if path.suffix == ".py":
            ast.parse(path.read_text(), filename=str(path))
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"通过：{len(paths)} 个 HTML，{checked} 个本地引用，案例源码完整同步，无学习外链或失效锚点。")


if __name__ == "__main__":
    main()
