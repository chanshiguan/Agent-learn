"""原题逐项覆盖与本轮修复的行为回归；不访问模型/远端账号。"""
import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from catalog import COURSES

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    path = ROOT / relative
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


production = load('review_production', '07-multi-agent-production/examples/production_case.py')
control = load('review_controls', '07-multi-agent-production/examples/control_eval.py')
collector = load('review_collector', '07-multi-agent-production/examples/collect_sources.py')
hook = load('review_hook', '05-claude-code-ecosystem/examples/observe_hook.py')
diff = load('review_diff_lab', 'A2-cli-workflow/examples/diff_lab.py')
auth = load('review_auth', 'A1-cli-intro/examples/auth_failures.py')


class OriginalCoverageTests(unittest.TestCase):
    def test_example_readme_reading_lists_are_also_covered(self):
        rows = json.loads((ROOT / 'reference/required-readings.json').read_text())
        base = ROOT / '_sources/upstream'
        for stage in [4, 5, 6, 7]:
            for path in (base / 'examples' / f'stage-{stage}').rglob('README.zh-Hans.md'):
                sections = [part for part in re.split(r'(?=^## )', path.read_text(), flags=re.M)
                            if re.match(r'##[^\n]*(必读|必修|学习资源)', part)]
                lines = '\n'.join(line for part in sections for line in part.splitlines() if re.match(r'^\s*-', line))
                expected = set(re.findall(r'\]\((https?://[^\s)]+)\)', lines))
                actual = {row['source'] for row in rows if row['source_document'] == str(path.relative_to(base))}
                self.assertEqual(expected, actual, str(path))

    def test_all_original_exercise_headings_have_distinct_answers(self):
        rows = json.loads((ROOT / 'reference/exercise-correspondence.json').read_text())
        self.assertEqual(len({row['id'] for row in rows}), len(rows))
        for slug, _, _, source, *_ in COURSES:
            raw = (ROOT / '_sources/upstream' / source).read_text()
            headings = re.findall(r'^#{2,3} (.+)$', raw, re.M)
            expected = {h for h in headings if re.search(r'(练习 \d|核心练习|动手练习 CLI|第一个练习|推荐小项目|最小决策|Model–Harness|选修 [AB])', h)}
            if slug.startswith('capstone-'):
                expected = {h for h in headings if h.startswith('Track ' + slug[-1].upper() + ' Capstone')}
            if slug == 'branch-teacher':
                expected.update(['Rubric 草稿', '常见错误整理'])
            actual = {row['source_heading'] for row in rows if row['course'] == slug and row['source_document'] == source}
            self.assertEqual(expected, actual, slug)
        for row in rows:
            self.assertGreaterEqual(len(row['acceptance']), 2)
            for path in row['answers'] + [row['lesson'], row['exercise']]:
                self.assertTrue((ROOT / path).is_file(), path)
            raw = (ROOT / '_sources/upstream' / row['source_document']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['source_sha256'])
        self.assertEqual({r['source_document'] for r in rows if r['scope'] == '直接支线练习'},
                         {'resources/advanced-rag.zh-Hans.md', 'resources/agent-memory.zh-Hans.md'})

    def test_team_package_uses_same_git_diff_skill(self):
        a = ROOT / 'A2-cli-workflow/examples/SKILL.md'
        b = ROOT / 'A3-cli-production/examples/team-plugin/skills/review-changes/SKILL.md'
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertIn('name: review-changes', a.read_text())
        self.assertIn('git diff --no-ext-diff', a.read_text())

    def test_second_lesson_and_shared_assets_unchanged(self):
        path = ROOT.parent / '.scratch/remaining-courses/full-review-2026-11-04/protected.json'
        for relative, digest in json.loads(path.read_text()).items():
            if relative.startswith('courses/03-tool-use-and-hello-agent/'):
                continue  # 用户本轮已授权润色第三课；第二课和共享素材仍受保护。
            self.assertEqual(hashlib.sha256((ROOT.parent / relative).read_bytes()).hexdigest(), digest, relative)

    def test_research_questions_reference_local_original_evidence(self):
        home = ROOT / 'branch-researcher/examples'
        evidence = json.loads((home / 'paper-evidence.json').read_text())
        answers = json.loads((home / 'reference-work.json').read_text())['original_three_questions']
        self.assertEqual({row['local_evidence_id'] for row in answers}, {row['id'] for row in evidence['evidence']})
        self.assertTrue(all(row['original_excerpt'] and row['location'] for row in evidence['evidence']))


class ExerciseBehaviorTests(unittest.TestCase):
    def test_managed_retrieval_cleans_only_new_resources(self):
        from unittest.mock import MagicMock, patch
        from types import SimpleNamespace
        lab = load('review_managed_retrieval', '06-memory-rag/examples/managed_retrieval.py')
        for status in ['completed', 'failed']:
            client = MagicMock()
            client.vector_stores.create.return_value = SimpleNamespace(id='new-store')
            client.files.create.return_value = SimpleNamespace(id='new-file')
            client.vector_stores.files.create_and_poll.return_value = SimpleNamespace(status=status)
            client.vector_stores.search.return_value.model_dump.return_value = {'data': []}
            with patch.object(lab, 'OpenAI', return_value=client):
                if status == 'failed':
                    with self.assertRaises(RuntimeError): lab.run()
                    client.vector_stores.search.assert_not_called()
                else:
                    self.assertFalse(lab.run()['answer_generated'])
            client.vector_stores.delete.assert_called_once_with('new-store')
            client.files.delete.assert_called_once_with('new-file')
            client.close.assert_called_once()

    def test_memory_original_five_steps_apply_table_preference(self):
        program = ROOT / '06-memory-rag/examples/memory_lifecycle.py'
        result = json.loads(subprocess.check_output([sys.executable, str(program)], text=True))
        self.assertTrue(result['passed'])
        self.assertEqual(result['updated']['expires_at'] - result['updated']['updated_at'], 3600)
        self.assertIsNone(result['other_user_before_deletion'])

    def test_existing_memory_database_migration_preserves_unknown_timestamp(self):
        import sqlite3
        memory = load('review_memory_store', '06-memory-rag/examples/memory_store.py')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'old.db'
            db = sqlite3.connect(path)
            db.execute('CREATE TABLE memories (owner TEXT, name TEXT, value TEXT, source TEXT, expires REAL, version INTEGER, PRIMARY KEY(owner,name))')
            db.execute('INSERT INTO memories VALUES (?,?,?,?,?,?)', ('alice', 'answer_style', '先短后长', '历史选择', 99999999999, 1))
            db.commit(); db.close()
            store = memory.MemoryStore(path)
            self.assertIsNone(store.get('alice', 'answer_style')['updated_at'])
            store.put('alice', 'answer_style', '先给表格', consent=True, expected_version=1, source='当前选择')
            self.assertIsNotNone(store.get('alice', 'answer_style')['updated_at'])
            store.close()

    def test_hook_identifies_write_and_edit_without_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            for tool in ['Write', 'Edit', 'secret-as-tool']:
                result = hook.observe({'hook_event_name': 'PreToolUse', 'tool_name': tool,
                                       'tool_input': {'content': 'DO-NOT-LOG'}}, Path(directory))
                self.assertEqual(result['tool_name'], tool if tool != 'secret-as-tool' else 'other')
                self.assertIsNotNone(datetime.fromisoformat(result['checked_at']).utcoffset())
            text = (Path(directory) / 'events.jsonl').read_text()
            self.assertNotIn('DO-NOT-LOG', text)
            self.assertNotIn('secret-as-tool', text)

    def test_diff_exercise_has_two_actual_defects_and_complete_fix(self):
        with tempfile.TemporaryDirectory() as directory:
            broken = diff.run(Path(directory) / 'broken', 'broken')
            fixed = diff.run(Path(directory) / 'fixed', 'fixed')
            self.assertIn('+从仓库根目录执行 `python3 missing.py`', broken['diff'])
            self.assertIn('+[操作说明](missing-guide.md)', broken['diff'])
            self.assertNotEqual(broken['check_exit'], 0)
            self.assertEqual(fixed['check_exit'], 0)
            self.assertEqual(fixed['diff_check_exit'], 0)
            self.assertEqual(set(fixed['status'].splitlines()), {' M README.md', ' M docs/README.md'})
            # 只改一份不得通过：恢复第二份为基线，保留可信检查器。
            folder = Path(directory) / 'fixed'
            (folder / 'docs/README.md').write_text(diff.BEFORE)
            result = subprocess.run([sys.executable, 'check.py'], cwd=folder, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            with self.assertRaises(ValueError):
                diff.run(folder, 'fixed')

    def test_auth_failures_distinguish_login_and_key(self):
        result = auth.run()
        self.assertEqual([row['observed'] for row in result['records']], ['login', 'api_key', 'model', 'permission', 'connection'])
        self.assertTrue(all(row['passed'] for row in result['records']))
        self.assertEqual(result['network_calls'], 0)

    def test_three_sources_and_complete_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            production.prepare(directory)
            result = production.resume(directory, 'approve')
            self.assertEqual(len(result['sources']), 3)
            self.assertEqual({c['source_id'] for c in result['claims']}, {s['id'] for s in result['sources']})
            for source in result['sources']:
                self.assertIsNotNone(datetime.fromisoformat(source['retrieved_at']).utcoffset())
            for field in ['task_id', 'result', 'sources', 'trace', 'seconds', 'usage', 'errors', 'state_version', 'approval']:
                self.assertIn(field, result)
            self.assertEqual(result['approval']['effective'], 'approved')

    def test_revise_cancels_old_version_and_requires_new_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            old, new = Path(directory) / 'old', Path(directory) / 'new'
            production.prepare(old)
            claims = json.loads((ROOT / '07-multi-agent-production/examples/revision-claims.json').read_text())
            state = production.revise(old, new, claims)
            self.assertEqual(state['status'], 'waiting_for_approval')
            self.assertEqual(production.resume(old, 'approve')['status'], 'cancelled')
            receipt = production.resume(new, 'approve')
            self.assertEqual(receipt['artifact_version'], 2)
            production.resume(new, 'approve')
            self.assertEqual(len(json.loads((new / 'ledger.json').read_text())['executed']), 1)
            self.assertFalse((old / 'ledger.json').exists())

    def test_invalid_revision_preserves_original_waiting_state(self):
        with tempfile.TemporaryDirectory() as directory:
            old, new = Path(directory) / 'old', Path(directory) / 'new'
            production.prepare(old)
            with self.assertRaises(ValueError):
                production.revise(old, new, [{'text': '无需人工批准', 'source_id': 'approval'}])
            self.assertEqual(json.loads((old / 'state.json').read_text())['status'], 'waiting_for_approval')

    def test_tampering_has_failed_attempt_and_no_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            production.prepare(directory)
            (Path(directory) / 'draft.json').write_text('{}')
            with self.assertRaises(ValueError):
                production.resume(directory, 'approve')
            failure = json.loads((Path(directory) / 'failed-attempt.json').read_text())
            self.assertEqual(failure['status'], 'FAILED')
            self.assertTrue(failure['errors'])
            self.assertFalse((Path(directory) / 'ledger.json').exists())

    def test_control_eval_has_five_executed_cases_and_rejects_false_success(self):
        result = control.evaluate()
        self.assertEqual(result['passed'], 5)
        self.assertEqual(len(result['rows']), 5)
        row = copy.deepcopy(result['rows'][1])
        row['receipt']['result'] = '没有资料但编造结果'
        with tempfile.TemporaryDirectory() as directory:
            grade = control.grade(row['case'], row['receipt'], Path(directory))
            self.assertEqual(grade['status'], 'FAIL')

    def test_source_collection_keeps_three_real_local_originals(self):
        with tempfile.TemporaryDirectory() as directory:
            sources = collector.collect(directory)
            self.assertEqual(len(sources), 3)
            for source in sources:
                self.assertIn(source['text'], Path(source['full_text_file']).read_text())
                self.assertIn(collector.COMMIT, source['url'])
                self.assertIn('本地', source['origin'])
            state = production.prepare(Path(directory) / 'task', sources=sources)
            self.assertEqual(state['status'], 'waiting_for_approval')


if __name__ == '__main__':
    unittest.main()
