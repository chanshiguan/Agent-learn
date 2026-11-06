"""检查教学顺序、前后章导航和原例注释的可重建性。"""
import ast
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
import shutil
import tempfile
import unittest

from catalog import COURSES, LESSON_ORDER, ordered_lessons
from commented_examples import annotate_upstream

ROOT = Path(__file__).resolve().parents[1]


class ChapterNav(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'nav' and attrs.get('aria-label') == '章节导航':
            self.inside = True
        if self.inside and tag == 'a':
            self.links.append(attrs['href'])

    def handle_endtag(self, tag):
        if tag == 'nav':
            self.inside = False


class LessonSequenceTests(unittest.TestCase):
    def test_every_chapter_appears_once_with_exercises_last(self):
        for slug, *_ in COURSES:
            source = ROOT / slug / 'text'
            paths = ordered_lessons(source)
            self.assertCountEqual(paths, source.glob('*.md'))
            self.assertEqual(paths[-1].stem, '99-exercises')

    def test_prerequisites_precede_composite_projects(self):
        for slug, sequence in {
            '04-agent-frameworks': ['04-patterns', '05-original-labs', '06-framework-apis', '03-workshop'],
            '06-memory-rag': ['08-example-readings', '05-original-labs', '03-workshop', '04-advanced', '06-abc-experiment'],
            '07-multi-agent-production': ['07-example-readings', '05-original-labs', '03-workshop', '06-complete-project'],
            'A2-cli-workflow': ['04-original-cli', '03-workshop'],
        }.items():
            order = [path.stem for path in ordered_lessons(ROOT / slug / 'text')]
            positions = [order.index(name) for name in sequence]
            self.assertEqual(positions, sorted(positions), slug)

    def test_navigation_follows_the_same_order_as_the_index(self):
        for slug, *_ in COURSES:
            home = ROOT / slug
            paths = ordered_lessons(home / 'text')
            index = (home / 'index.html').read_text().split('<ol class="lesson-list">', 1)[1].split('</ol>', 1)[0]
            index_positions = [index.index(f'href="lessons/{path.stem}.html"') for path in paths]
            self.assertEqual(index_positions, sorted(index_positions), slug)
            for i, path in enumerate(paths):
                nav = ChapterNav()
                nav.feed((home / 'lessons' / (path.stem + '.html')).read_text())
                previous = paths[i - 1].stem + '.html' if i else '../index.html'
                following = paths[i + 1].stem + '.html' if i + 1 < len(paths) else '../../index.html'
                self.assertEqual(nav.links, [previous, following], str(path))

    def test_unlisted_chapter_cannot_silently_disappear(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / '04-agent-frameworks/text'
            source.mkdir(parents=True)
            for name in LESSON_ORDER['04-agent-frameworks'] + ['new-chapter']:
                (source / (name + '.md')).write_text('# 示例\n')
            with self.assertRaises(ValueError):
                ordered_lessons(source)

    def test_chinese_tutor_bundle_has_runnable_local_references(self):
        folder = ROOT / '05-claude-code-ecosystem/examples/upstream/tool-calling-tutor/evals'
        cases = json.loads((folder / 'evals.json').read_text())['cases']
        self.assertEqual(len(cases), 5)
        self.assertTrue(all(case['locale'] == 'zh-Hans' for case in cases))
        result = subprocess.run([sys.executable, str(folder / 'check_evals.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_localized_examples_rebuild_exactly_from_reviewed_overlay(self):
        with tempfile.TemporaryDirectory() as directory:
            for slug, _, _, _, _, stage in COURSES:
                if not stage:
                    continue
                home = Path(directory) / slug
                original = ROOT / '_sources/upstream/examples' / ('stage-' + stage)
                copied = home / 'examples/upstream'
                shutil.copytree(original, copied)
                annotate_upstream(home)
                for path in copied.rglob('*'):
                    if not path.is_file() or path.suffix not in {'.py', '.md', '.json', '.yaml', '.yml', '.js', '.txt'}:
                        continue
                    if path.suffix == '.py':
                        ast.parse(path.read_text())
                    self.assertEqual(path.read_bytes(), (ROOT / slug / path.relative_to(home)).read_bytes())
            changed = Path(directory) / '04-agent-frameworks/examples/upstream/01-same-agent-two-frameworks/starter.py'
            changed.write_text(changed.read_text() + '\n# 模拟原例更新\n')
            with self.assertRaises(ValueError):
                annotate_upstream(Path(directory) / '04-agent-frameworks')


if __name__ == '__main__':
    unittest.main()
