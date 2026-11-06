"""生成后续课程；只读教材源文件，不执行案例。"""
from pathlib import Path
from html import escape, unescape
from urllib.parse import urlsplit, unquote
import hashlib
import json
import os
import re
import shutil
from markdown_it import MarkdownIt
from catalog import COURSES, ordered_lessons
from commented_examples import annotate_upstream
from learning_priorities import PRIORITIES, badge, banner, mark_sections
from code_notes import file_notes, file_kind, notes_html, write_notes_file

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
UPSTREAM = ROOT / "_sources/upstream"
MD = MarkdownIt("commonmark", {"html": True}).enable("table")
SOURCES = {}


def rel(path, page):
    return os.path.relpath(path, page.parent)


def sid(url):
    return hashlib.sha256(url.encode()).hexdigest()[:12]


def mirror(path):
    return ROOT / "_sources/pages" / (str(path.relative_to(UPSTREAM)).replace("/", "--") + ".html")


def shell(title, body, target, home=None):
    nav = f'<a href="{rel(ROOT / "index.html", target)}">全部课程与路线</a>'
    if home:
        for label, name in [("本课目录", "index.html"), ("本地阅读", "reference/readings.html"), ("完整代码", "reference/code.html"), ("课后练习", "lessons/99-exercises.html")]:
            nav += f'<a href="{rel(home / name, target)}">{label}</a>'
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><link rel="stylesheet" href="{rel(PROJECT / 'assets/course.css', target)}"><link rel="stylesheet" href="{rel(ROOT / 'assets/later.css', target)}"></head><body><main><nav class="course-nav">{nav}</nav><article class="lesson-body">{body}</article><footer>遇到不懂的地方，把课程编号、小节和实际输出发给我。读完资料不代表已掌握；请用课末练习检验。<br>中文讲解与本地案例 · 来源快照 2026-11-03 · <a href="{rel(UPSTREAM / 'LICENSE', target)}">上游 MIT © Wenyu Chiou</a> · <a href="{rel(ROOT / 'reference/version-notes.md', target)}">版本差异说明</a></footer></main><script src="{rel(ROOT / 'assets/later.js', target)}"></script></body></html>'''


def github_slug(text):
    text = re.sub(r'<[^>]+>', '', text).lower()
    return re.sub(r'[^\w\- ]', '', text).replace(' ', '-')


def anchor_ids(path):
    text = path.read_text()
    explicit = set(re.findall(r'\bid=["\']([^"\']+)', text))
    headings = re.findall(r'^#{1,6} (.+)', text, flags=re.M)
    return explicit | {github_slug(h) for h in headings} | {'h'+sid(h) for h in headings} | {'top'}


UNRESOLVED = {}


def resolve_reference(href, origin, target, label=''):
    parts = urlsplit(unescape(href))
    if parts.scheme in {'http', 'https'}:
        url = unescape(href)
        SOURCES.setdefault(url, {'title': label or url, 'contexts': []})['contexts'].append(label)
        return rel(ROOT / 'reference/source-readings.html', target) + '#s' + sid(url)
    if parts.scheme:
        key = sid(str(origin)+href)
        UNRESOLVED[key] = {'origin':str(origin.relative_to(ROOT)), 'target':href, 'reason':'外部应用入口，不是本地学习步骤'}
        return rel(ROOT/'reference/navigation-notes.html',target)+'#n'+key
    path = (origin.parent/unquote(parts.path)).resolve() if parts.path else origin
    decoded=unquote(parts.path)
    if '${CLAUDE_SKILL_DIR}' in decoded:
        base=origin.parent.parent if origin.parent.name=='translations' else origin.parent
        path=(base/decoded.replace('${CLAUDE_SKILL_DIR}/','')).resolve()
    if path.is_dir():
        candidates=[path/'README.zh-Hans.md',path/'README.md']
        path=next((candidate for candidate in candidates if candidate.is_file()),path)
    if not path.is_file() and path.suffix == '.md':
        name = path.name.replace('.en.md','.zh-Hans.md').replace('.zh-TW.md','.zh-Hans.md')
        if not name.endswith('.zh-Hans.md'):
            name = path.stem+'.zh-Hans.md'
        alternate=path.with_name(name)
        if alternate.is_file(): path=alternate
    if not path.is_file() and path.name.endswith('.zh-Hans.md'):
        untranslated=path.with_name(path.name.replace('.zh-Hans.md','.md'))
        if untranslated.is_file(): path=untranslated
    fragment=unquote(parts.fragment)
    if path.is_file():
        if path.suffix=='.md':
            dest=mirror(path) if path.is_relative_to(UPSTREAM) else path.parent.parent/'lessons'/path.with_suffix('.html').name if path.parent.name=='text' else path
            if fragment and fragment not in anchor_ids(path):
                matches=[a for a in anchor_ids(path) if a.lstrip('-')==fragment.lstrip('-')]
                if len(matches)==1: fragment=matches[0]
                else: return navigation_note(origin,href,target,'原锚点不存在；保留问题供核对，不静默跳页首')
        else: dest=path
        result='' if dest==target else rel(dest,target)
        return result+('#'+fragment if fragment else '')
    if not origin.is_relative_to(UPSTREAM):
        raise FileNotFoundError(f'{origin}: {href}')
    return navigation_note(origin,href,target,'原仓库附属入口未在教学快照中；不是本课必修前提')


def navigation_note(origin,href,target,reason):
    key=sid(str(origin)+href)
    UNRESOLVED[key]={'origin':str(origin.relative_to(ROOT)),'target':href,'reason':reason}
    return rel(ROOT/'reference/navigation-notes.html',target)+'#n'+key


def render(text, origin, target):
    def embed(match):
        path=(origin.parent/match.group(1)).resolve()
        return '\n\n```'+file_kind(path)+'\n'+path.read_text()+'\n```\n\n'
    text=re.sub(r'\{\{code:([^}]+)\}\}',embed,text)
    text=re.sub(r'<div[^>]*markdown="1"[^>]*>|</div>','',text)
    text=re.sub(r'^>.*(?:繁體中文|繁体中文).*$', '',text,flags=re.M)
    text=re.sub(r'<!--.*?-->','',text,flags=re.S)
    text=re.sub(r'</summary>\s*','</summary>\n\n',text)
    text=re.sub(r'\s*</details>','\n\n</details>\n\n',text)
    tokens=MD.parse(text)
    aliases=[]
    explicit=set(re.findall(r'\bid=["\']([^"\']+)',text))
    for index,token in enumerate(tokens):
        if token.type=='heading_open':
            heading=tokens[index+1].content
            token.attrSet('id','h'+sid(heading))
            alias=github_slug(heading)
            if alias and alias not in explicit:
                aliases.append(('h'+sid(heading),alias));explicit.add(alias)
    output=MD.renderer.render(tokens,MD.options,{})
    # 不能在 JSON 或提示词原值中插入注释，按实际显示的行号配说明表。
    for token in tokens:
        if token.type == 'fence' and not origin.is_relative_to(UPSTREAM):
            explanation = notes_html(token.content, token.info.strip())
            if explanation:
                rendered_code = MD.renderer.render([token], MD.options, {})
                output = output.replace(rendered_code, rendered_code + explanation, 1)
    for heading,alias in aliases:
        output=output.replace(f'id="{heading}"',f'data-heading-alias="{escape(alias)}" id="{heading}"',1)
        output=re.sub(r'(<h[1-6]\b[^>]*id="'+heading+r'"[^>]*>)',lambda m:'<span id="'+escape(alias)+'"></span>'+m.group(1),output,count=1)
    def link(match):
        href=resolve_reference(match.group(2),origin,target,unescape(re.sub(r'<[^>]+>','',match.group(4))))
        return match.group(1)+escape(href,quote=True)+match.group(3)+match.group(4)+'</a>'
    output=re.sub(r'(<a\b[^>]*?href=")([^"]*)("[^>]*>)(.*?)</a>',link,output,flags=re.S)
    def image_link(match):
        href=unescape(match.group(2));path=(origin.parent/unquote(urlsplit(href).path)).resolve()
        if path.is_file(): return match.group(1)+escape(rel(path,target),quote=True)+match.group(3)
        # 保留具体图名并显式报告，不能把丢图伪装为已提供图解。
        return match.group(1)+escape(resolve_reference(href,origin,target),quote=True)+match.group(3)
    output=re.sub(r'(<img\b[^>]*?src=")([^"]*)(")',image_link,output)
    return '<span id="top"></span>'+output


def write(target, text):
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def main():
    exercises = json.loads((ROOT/'reference/exercise-correspondence.json').read_text())
    for path in sorted(UPSTREAM.rglob("*.md")):
        target = mirror(path)
        body = '<p class="source-note">原课程本地核对资料，保留原内容与顺序。外链已改为本地阅读入口。命令中的原仓库路径请按本课运行指南换成实际位置；版本差异见本课说明。MIT © 2026 Wenyu Chiou。</p>'
        body += render(path.read_text(), path, target)
        write(target, shell(path.stem, body, target))
    for slug, number, title, source, prereq, stage in COURSES:
        home = ROOT / slug
        original = UPSTREAM / source
        if stage:
            shutil.copytree(UPSTREAM / 'examples' / f'stage-{stage}', home / 'examples/upstream', dirs_exist_ok=True)
            shutil.copy2(UPSTREAM / 'LICENSE', home / 'examples/upstream/LICENSE')
            annotate_upstream(home)
        source_dir = home / 'text'
        pages = []
        lesson_paths = ordered_lessons(source_dir)
        for lesson_index, path in enumerate(lesson_paths):
            filename = path.name
            label = path.read_text().splitlines()[0].lstrip('# ')
            path = source_dir / filename
            if not path.is_file():
                raise FileNotFoundError(path)
            target = home / 'lessons' / filename.replace('.md', '.html')
            raw = path.read_text()
            headings = re.findall(r'^## (.+)', raw, flags=re.M)
            toc = '<aside class="toc"><strong>本章目录</strong><ul>' + ''.join(f'<li><a href="#h{sid(h)}">{escape(h)}</a></li>' for h in headings) + '</ul></aside>' if len(headings) > 2 else ''
            rendered = render(raw, path, target)
            rendered = mark_sections(rendered, slug, path.stem)
            if toc:
                rendered = re.sub(r'(</h1>)', lambda match: match.group(1) + toc, rendered, count=1)
            body = f'<p class="eyebrow">{escape(number)} · {escape(title)}</p>' + banner(slug, path.stem) + rendered
            previous = lesson_paths[lesson_index - 1] if lesson_index else None
            following = lesson_paths[lesson_index + 1] if lesson_index + 1 < len(lesson_paths) else None
            previous_link = f'<a href="{previous.stem}.html">← {escape(previous.read_text().splitlines()[0].lstrip("# "))}</a>' if previous else '<a href="../index.html">← 本课目录</a>'
            following_link = f'<a href="{following.stem}.html">{escape(following.read_text().splitlines()[0].lstrip("# "))} →</a>' if following else '<a href="../../index.html">完成本课验收后，查看下一课路线 →</a>'
            body += f'<nav class="next-prev" aria-label="章节导航">{previous_link}{following_link}</nav>'
            write(target, shell(label, body, target, home))
            pages.append((target, label))
        target = home / 'reference/code.html'
        codebody = '<h1>完整代码与配置</h1><p>下列内容直接读取实际文件，注释解释步骤的用途、参数含义与设计原因。提示词、示例问题和工具返回已改成简体中文；JSON 和多行文本另附行号说明，避免把注释变成模型输入。examples/upstream 为原课程 MIT 示例的中文教学副本，输入与对应的匹配规则、断言同步维护；原始快照另存供核对。先按中文讲义选一个案例运行。</p><p><a href="line-notes.md">下载与文件行号对应的数据说明</a></p>'
        write_notes_file(home)
        for path in sorted((home / 'examples').rglob('*')):
            if not path.is_file() or path.name == '.DS_Store' or path.suffix in {'.pyc', '.db', '.sqlite'} or '__pycache__' in path.parts:
                continue
            text = path.read_text()
            codebody += f'<details id="f{sid(str(path.relative_to(home)))}"><summary>{escape(str(path.relative_to(home)))}</summary><p><a href="{rel(path,target)}">打开完整文件</a></p><pre><code>{escape(text)}</code></pre>' + file_notes(path) + '</details>'
        write(target, shell('完整代码', codebody, target, home))
        target = home / 'reference/readings.html'
        body = '<h1>本课阅读入口</h1><p>学习所需知识在本地讲义中。外部网站仅在来源记录中保留，供核查，不是完成课程的步骤。</p>'
        body += f'<p><a href="{rel(home / "lessons/02-readings.html",target)}">必修文章中文整合</a></p><p><a href="{rel(mirror(original),target)}">原课程全部小节与资源清单（本地）</a></p><p><a href="{rel(ROOT / "reference/source-readings.html",target)}">全套资料知识卡</a></p>'
        write(target, shell('本课阅读', body, target, home))
        target = home / 'reference/coverage.html'
        mapping = json.loads((home/'coverage.json').read_text())
        body = '<h1>知识、案例与验收对应表</h1><p>下表按本课需要掌握的能力核对；资料目录保留不等于教学覆盖。来源全文、教程相关能力与目录介绍的范围分开记录。</p><table><tr><th>原课要求与资料</th><th>本地讲解</th><th>完整案例/答案</th><th>验收</th></tr>'
        for row in mapping:
            body += '<tr><td>'+escape(row['requirement'])+'</td>'
            for field in ['lesson','example','assessment']:
                destination, fragment = (row[field].split('#',1)+[''])[:2] if '#' in row[field] else (row[field],'')
                href=rel(home/destination,target)+('#'+fragment if fragment else '')
                body += '<td><a href="'+escape(href)+'">'+escape(row[field])+'</a></td>'
            body += '</tr>'
        body += '</table><h2>逐份必读来源与能力边界</h2><p>逐一对应冻结原课必读清单。例子可能是通用能力实验，只有明确说明时才是供应商 API 实现；选用参考不要求安装全部产品。未运行的宿主/远端验收仍须实际执行。</p>'
        readings = json.loads((ROOT/'reference/required-readings.json').read_text())
        for reading in [row for row in readings if row['course'] == slug]:
            body += '<section id="r'+sid(reading['source'])+'"><h3>'+escape(reading['title'])+'</h3><p>'+escape(reading['scope'])+'</p><ul>'
            body += ''.join('<li>'+escape(point)+'</li>' for point in reading['knowledge_points'])+'</ul><p>'
            for field,label in [('lesson','精确讲解'),('example','案例/参考产物'),('assessment','练习与验收')]:
                path,fragment=(reading[field].split('#',1)+[''])[:2]
                href=rel(ROOT/path,target)+('#'+fragment if fragment else '')
                body += '<a href="'+escape(href)+'">'+label+'</a> · '
            body += '</p><p>'+escape(reading['boundary'])+'</p></section>'
        if not any(row['course']==slug for row in readings):
            body += '<p>本结业课没有独立外部必读清单，继承前置路线的阅读与实作要求；按本课综合项目验收。</p>'
        body += '<h2>原题、参考答案与验收逐项对应</h2><p>每个原题独立列出；选修、支线与综合题保留原来的范围。代码或配置已提供，不等于真实服务测试已执行。</p>'
        for exercise in [row for row in exercises if row['course']==slug]:
            body += exercise_entry(exercise, target)
        body += '<h2>原文目录核对</h2><p>保留上游结构和资源定位，不能把这个目录当作知识已经教完的证据。</p><ul>'
        for heading in re.findall(r'^#{2,4} (.+)', original.read_text(), flags=re.M):
            body += f'<li><a href="{rel(mirror(original),target)}#h{sid(heading)}">{escape(heading)}</a></li>'
        body += '</ul>'
        write(target, shell('覆盖表', body, target, home))
        target = home / 'index.html'
        body = f'<p class="eyebrow">原课程 {escape(number)}</p><h1>{escape(title)}</h1>' + banner(slug) + f'<p class="route">{escape(prereq)}</p><p>以“读懂 → 跑通 → 独立修改 → 验收”为一课。以下是课内章节，不是新增的原课程编号。主线文章中的选读小节会单独标记；课后练习按所选路线完成。</p><ol class="lesson-list">'
        for p, label in pages[:-1]:
            body += f'<li>{badge(PRIORITIES[slug]["lessons"][p.stem])} <a href="{rel(p,target)}">{label}</a></li>'
        body += '<li><span class="study-badge study-lookup">随案例查阅</span><a href="reference/code.html">完整案例与配置文件</a></li><li><span class="study-badge study-lookup">参考查阅</span><a href="reference/coverage.html">原课对应表与本地核对资料</a></li>'
        body += f'<li>{badge(PRIORITIES[slug]["lessons"][pages[-1][0].stem])}<a href="{rel(pages[-1][0],target)}">课后练习：目的、任务、验收、提示与答案</a></li></ol>'
        body += '<p>按上面的顺序学习即可，文件名中的数字不一定是阅读顺序。完整代码和对应表供随时查阅；最后用课后练习检查掌握情况。运行案例时使用该章指定的 Python 路径：主项目环境与框架专用环境可能不同。已经在项目根目录时，无需重复 cd。</p>'
        write(target, shell(title, body, target, home))
        write(home / 'README.md', f'# {number} · {title}\n\n打开 [本课首页](index.html)。\n\n先修：{prereq}。\n\n原课程：{source}\n\n讲义源文件在 text/，网页在 lessons/；完整案例在 examples/；最后一章为练习。上游代码保留 MIT 许可。\n')
        write(home / 'RESOURCES.md', f'# {title} 资料\n\n## Knowledge\n\n- [原课程](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/9ef03ca034704bf9cdd403673b3116fda7ec8672/{source})：范围与原练习依据，已提供本地版。\n- [本课整合阅读](lessons/02-readings.html)：必读与必要前置知识。\n- [逐项来源记录](../reference/SOURCES.md)：原始 URL 仅供核查。\n\n## Wisdom\n\n不要求注册社区或公开作业。先把练习结果交给本地教师对话核查。\n')
    from reading_cards import card
    from source_topics import destination
    target = ROOT / 'reference/source-readings.html'
    body = '<h1>参考资料的本地知识卡</h1><p>指定文章的概念结合各课阅读章学习；工具仓库按本课涉及用途和边界讲解。来源网址在 SOURCES.md 中，不要求访问。知识卡不是整个外部网站的逐页翻译。</p><label>按名称或主题查找 <input type="search" data-source-filter placeholder="例如：Memory、LangGraph、评测"></label>'
    for url, info in SOURCES.items():
        rendered = MD.render(card(url,info))
        rendered = re.sub(r'<a\b[^>]*>(.*?)</a>', r'\1', rendered, flags=re.S)
        local_topic = destination(url)
        if local_topic:
            rendered += '<p><a href="'+rel(ROOT/local_topic[0],target)+'">本课相关知识点：'+escape(local_topic[1])+'</a></p>'
        else:
            rendered += '<p>范围：此来源没有直接必读精确映射；这里只是参考索引，不能据此判断已完整教学。原课选修与目录用途以本课对应表为准。</p>'
        body += f'<details data-source-card id="s{sid(url)}"><summary>{escape(info["title"])}</summary>{rendered}</details>'
    write(target, shell('资料知识卡', body, target))
    notes=ROOT/'reference/navigation-notes.html'
    note_body='<h1>原仓库附属导航说明</h1><p>这里明确列出非教学入口的不可用目标，不将它们伪装成可用章节。学习使用每课知识、案例与验收表。</p>'
    for key,record in UNRESOLVED.items():
        note_body+='<section id="n'+key+'"><h2>'+escape(record['target'])+'</h2><p>'+escape(record['origin'])+'</p><p>'+escape(record['reason'])+'</p></section>'
    write(notes,shell('导航说明',note_body,notes))
    write(ROOT/'reference/navigation-audit.json',json.dumps(UNRESOLVED,ensure_ascii=False,indent=2))
    write(ROOT / 'reference/SOURCES.md', '# 来源记录\n\n原课程固定提交：9ef03ca034704bf9cdd403673b3116fda7ec8672；原课核对日期 2026-11-03；补充核读见 [2026-11-04 来源记录](SOURCES-UPDATES-2026-11-04.md)。\n\n' + '\n'.join(f'- [{info["title"]}]({url})' for url, info in SOURCES.items()))
    target = ROOT/'reference/exercise-correspondence.html'
    body = '<h1>原题—讲解—完整答案—验收</h1><p>固定提交 9ef03ca034704bf9cdd403673b3116fda7ec8672；本次复核上游 HEAD 一致。范围为第四课起的 16 个课程目录，不改第二、三课。逐题对应不是替学习者勾选已完成。</p>'
    for exercise in exercises:
        body += exercise_entry(exercise, target)
    write(target, shell('原题与答案逐项对应',body,target))
    build_homepage()
    print(f'生成 {len(COURSES)} 个课程目录；{len(SOURCES)} 个来源入口。')


def build_homepage():
    source = ROOT / 'STUDY-GUIDE.md'
    target = ROOT / 'index.html'
    body = render(source.read_text(), source, target)
    write(target, shell('学习顺序与验收 · AI Learn', body, target))


def exercise_entry(row, target):
    body = '<section id="exercise-'+escape(row['id'])+'"><h3>'+escape(row['id']+' · '+row['source_heading'])+'</h3>'
    body += '<p>'+escape(row['scope'])+' · <a href="'+rel(ROOT/row['lesson'],target)+'">中文实作与判断</a> · <a href="'+rel(ROOT/row['exercise'],target)+'">课末作业</a></p><p>完整参考：'
    body += '、'.join('<a href="'+rel(ROOT/path,target)+'">'+escape(Path(path).name)+'</a>' for path in row['answers'])+'</p><ul>'
    body += ''.join('<li>'+escape(criterion)+'</li>' for criterion in row['acceptance'])+'</ul>'
    body += '<p>'+escape(row['boundary'])+'</p></section>'
    return body


if __name__ == '__main__':
    main()
