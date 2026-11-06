"""静态链接、源码语法和完整展示检查；不执行上游代码。"""
import ast
import json
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from catalog import COURSES

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs: self.links.append(attrs[key])


def main():
    paths = [ROOT / 'index.html'] + list((ROOT / '_sources/pages').glob('*.html')) + list((ROOT / 'reference').glob('*.html'))
    for slug, *_ in COURSES: paths += list((ROOT / slug).rglob('*.html'))
    pages = {}
    for path in paths:
        p = Page(); p.feed(path.read_text()); pages[path.resolve()] = p
    errors = []; references = 0
    for path, page in pages.items():
        for href in page.links:
            parts = urlsplit(href)
            if parts.scheme or parts.netloc:
                if parts.scheme in {'http', 'https'}: errors.append(f'网页含外链：{path.name}: {href}')
                continue
            dest = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            references += 1
            if not dest.exists(): errors.append(f'断链：{path}: {href}')
            elif parts.fragment and dest in pages and unquote(parts.fragment) not in pages[dest].ids:
                errors.append(f'缺锚点：{path}: {href}')
    py_count = 0; embedded = 0
    for slug, *_ in COURSES:
        home = ROOT / slug
        html = unescape((home / 'reference/code.html').read_text())
        for path in (home / 'examples').rglob('*.py'):
            text = path.read_text(); ast.parse(text, filename=str(path)); py_count += 1
            if text not in html: errors.append(f'代码未完整展示：{path}')
            embedded += 1
        for row in json.loads((home/'coverage.json').read_text()):
            for field in ['lesson','example','assessment']:
                parts=urlsplit(row[field])
                destination=(home/parts.path).resolve()
                if not destination.is_file(): errors.append(f'覆盖表目标缺失：{slug}/{row[field]}')
                elif parts.fragment and (destination not in pages or parts.fragment not in pages[destination].ids):
                    errors.append(f'覆盖表缺精确锚点：{slug}/{row[field]}')
        for required in ['01-guide.html', '02-readings.html', '03-workshop.html', '99-exercises.html']:
            if not (home / 'lessons' / required).exists(): errors.append(f'缺课程页面：{slug}/{required}')
    print(f'HTML={len(pages)}；本地引用={references}；Python语法={py_count}；完整源码展示={embedded}')
    for error in errors: print(error)
    if errors: raise SystemExit(1)


if __name__ == '__main__':
    main()
