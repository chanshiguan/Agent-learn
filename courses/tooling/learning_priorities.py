"""目录与正文共用学习标记，具体范围维护在 learning-priorities.json。"""
import json
import re
from html import escape, unescape
from pathlib import Path

PRIORITIES = json.loads((Path(__file__).resolve().parents[1] / 'reference/learning-priorities.json').read_text())
LABELS = {'core': '主线必读', 'a': 'A 线必读', 'branch': '身份分支选读',
          'extra': '扩展选读', 'mixed': '必读概念 · 实作按需', 'lookup': '参考查阅'}


def badge(entry):
    return f'<span class="study-badge study-{entry["level"]}">{LABELS[entry["level"]]}</span>'


def banner(slug, stem=None):
    course = PRIORITIES[slug]
    entry = course['lessons'][stem] if stem else course
    onward = '<p><a href="../../04-agent-frameworks/index.html">主线验收通过后，进入第四课 →</a></p>' if slug == '03-tool-use-and-hello-agent' and stem == '0008-exercises' else ''
    return ('<aside class="study-priority" aria-label="学习要求">' + badge(entry)
            + f'<strong>{escape(course["route"])}</strong><p>{escape(entry["note"])}</p>' + onward + '</aside>')


def mark_sections(html, slug, stem):
    entry = PRIORITIES[slug]['lessons'][stem]
    def mark(match):
        title = unescape(re.sub('<[^>]+>', '', match.group(2)))
        section = entry['sections'].get(title, {'level': entry['level'], 'note': ''})
        note = f'<p class="study-section-note">{escape(section["note"])}</p>' if section['note'] else ''
        return match.group(0) + '<div class="study-section">' + badge(section) + note + '</div>'
    return re.sub(r'(<h2\b[^>]*>)(.*?)(</h2>)', mark, html, flags=re.S)
