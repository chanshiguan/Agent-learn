"""防止必读内容误标为选修，或新章节遗漏学习要求。"""
from pathlib import Path
import re
import unittest

from catalog import COURSES
from learning_priorities import PRIORITIES, LABELS
from code_notes import annotate_shell, data_line_notes

ROOT = Path(__file__).resolve().parents[1]


class LearningPriorityTests(unittest.TestCase):
    def test_every_article_has_an_explicit_priority(self):
        self.assertEqual(set(PRIORITIES), {row[0] for row in COURSES} | {'03-tool-use-and-hello-agent'})
        for slug, *_ in COURSES:
            home = ROOT / slug
            self.assertEqual(set(PRIORITIES[slug]['lessons']), {p.stem for p in (home / 'text').glob('*.md')})
            for stem, entry in PRIORITIES[slug]['lessons'].items():
                self.assertIn(entry['level'], LABELS)
                headings = re.findall(r'^## (.+)', (home / 'text' / (stem + '.md')).read_text(), re.M)
                self.assertLessEqual(set(entry['sections']), set(headings))
                html = (home / 'lessons' / (stem + '.html')).read_text()
                self.assertIn('aria-label="学习要求"', html)
                self.assertIn(LABELS[entry['level']], html)
                self.assertEqual(len(re.findall(r'<h2\b', html)), html.count('class="study-section"'))

    def test_required_topics_are_not_hidden_by_optional_implementations(self):
        for slug in ['04-agent-frameworks', '05-claude-code-ecosystem', '06-memory-rag', '07-multi-agent-production', '07.5-advanced-agentic-concepts', '08-agent-interfaces', 'capstone-b']:
            self.assertEqual(PRIORITIES[slug]['level'], 'core')
            for stem in ['01-guide', '02-readings', '99-exercises']:
                self.assertEqual(PRIORITIES[slug]['lessons'][stem]['level'], 'core')
        self.assertEqual(PRIORITIES['05-claude-code-ecosystem']['lessons']['04-extensions']['level'], 'extra')
        third = PRIORITIES['03-tool-use-and-hello-agent']['lessons']
        self.assertEqual(len(third), 15)
        for stem, entry in third.items():
            self.assertEqual(entry['level'], 'core' if int(stem[:4]) <= 8 else 'extra')

    def test_a_route_is_required_only_for_a_learners(self):
        for slug in ['A1-cli-intro', 'A2-cli-workflow', 'A3-cli-production', 'capstone-a']:
            self.assertEqual(PRIORITIES[slug]['level'], 'a')
        for slug in PRIORITIES:
            if slug.startswith('branch-'):
                self.assertEqual(PRIORITIES[slug]['level'], 'branch')

    def test_command_explanation_preserves_commands(self):
        original = 'cd /tmp/demo\npython -m unittest discover -v\npython example.py --live\n'
        annotated = annotate_shell(original)
        self.assertEqual(''.join(line for line in annotated.splitlines(keepends=True) if not line.startswith('#')), original)
        self.assertEqual(annotate_shell(annotated), annotated)

    def test_multiline_input_is_explained_without_inserting_data(self):
        source = 'prompt = f"""参考资料：\n{context_text}\n问题：{query}\n回答："""\n'
        notes = data_line_notes(source, 'python')
        self.assertEqual([row[0] for row in notes], [1, 2, 3, 4])
        self.assertIn('检索', notes[1][2])
        self.assertIn('问题', notes[2][2])
        self.assertEqual(source.splitlines()[1], '{context_text}')


if __name__ == '__main__':
    unittest.main()
