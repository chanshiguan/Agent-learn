"""离线验证边界、持久化和工具协议；不请求模型。"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


policy = module('policy_test', '08-agent-interfaces/examples/policy.py')
memory = module('memory_test', '06-memory-rag/examples/memory_store.py')
ranking = module('ranking_test', '06-memory-rag/examples/ranking_lab.py')
rag = module('rag_test', 'capstone-b/examples/rag_agent.py')
judge = module('judge_test', '07.5-advanced-agentic-concepts/examples/decision.py')
hook = module('hook_test', '05-claude-code-ecosystem/examples/observe_hook.py')
evidence = module('evidence_test', 'branch-everyday-users/examples/exercise.py')


class BoundaryTests(unittest.TestCase):
    def test_allowed_read(self):
        self.assertEqual(policy.check(' READ ', 'https://example.com'), 'ALLOW')

    def test_sensitive_action_needs_approval(self):
        for name in ['send', 'login', 'purchase', 'delete']:
            self.assertEqual(policy.check(name, 'https://example.com'), 'ASK')

    def test_host_spoofing_blocked(self):
        for url in ['https://example.com.evil.test', 'https://example.com@evil.test', 'https://user@example.com', 'file:///etc/passwd', 'https://example.com:bad', 'https://example.com:8443']:
            with self.subTest(url=url):
                self.assertEqual(policy.check('read', url), 'BLOCK')

    def test_unknown_action_blocked(self):
        self.assertEqual(policy.check('eval', 'https://example.com'), 'BLOCK')

    def test_hook_does_not_log_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            hook.observe({'hook_event_name': 'PostToolUse', 'secret': 'do-not-record'}, Path(directory))
            text = (Path(directory) / 'events.jsonl').read_text()
            self.assertNotIn('do-not-record', text)
            self.assertEqual(set(json.loads(text)), {'checked_at', 'event', 'tool_name', 'observed'})

    def test_safety_failure_cannot_be_offset_by_quality(self):
        base = {'pass_rate': .5, 'unsafe_actions': 0, 'latency': 10, 'tokens': 1000}
        candidate = dict(base, pass_rate=1, unsafe_actions=1)
        self.assertTrue(judge.decide(base, candidate).startswith('拒绝'))


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'memory.sqlite'
        self.store = memory.MemoryStore(self.path)

    def tearDown(self):
        self.store.close(); self.directory.cleanup()

    def put(self, **changes):
        args = dict(consent=True, expected_version=0, source='用户明确选择')
        args.update(changes)
        return self.store.put('alice', 'answer_style', '先短后长', **args)

    def test_restart_and_isolation(self):
        self.put(); self.store.close(); self.store = memory.MemoryStore(self.path)
        self.assertEqual(self.store.get('alice', 'answer_style')['value'], '先短后长')
        self.assertIsNone(self.store.get('bob', 'answer_style'))

    def test_consent_required(self):
        with self.assertRaises(ValueError): self.put(consent=False)

    def test_conflict_preserves_existing_memory(self):
        self.put()
        with self.assertRaises(ValueError): self.put(expected_version=0)
        self.assertEqual(self.store.get('alice', 'answer_style')['version'], 1)

    def test_update_and_delete(self):
        self.put(); self.put(expected_version=1)
        self.assertEqual(self.store.get('alice', 'answer_style')['version'], 2)
        self.store.delete('alice', 'answer_style')
        self.assertIsNone(self.store.get('alice', 'answer_style'))

    def test_expiration(self):
        with patch.object(memory.time, 'time', return_value=100): self.put(ttl=10)
        with patch.object(memory.time, 'time', return_value=111):
            self.assertIsNone(self.store.get('alice', 'answer_style'))


class EvidenceTests(unittest.TestCase):
    def test_branch_reference_contracts(self):
        for name in ['researcher', 'developer', 'teacher', 'knowledge-worker', 'everyday-users']:
            folder = ROOT / ('branch-' + name) / 'examples'
            source = json.loads((folder / 'input.json').read_text())
            answer = json.loads((folder / 'reference-answer.json').read_text())
            evidence.validate(answer, source)

    def test_unknown_citation_rejected(self):
        source = {'evidence': [{'id': 'e1', 'text': '测试'}]}
        answer = {'draft': '草稿', 'claims': [{'text': '句子', 'source_ids': ['e9'], 'status': 'supported'}], 'needs_confirmation': []}
        with self.assertRaises(ValueError): evidence.validate(answer, source)

    def test_rrf_and_recall(self):
        ranked = ranking.reciprocal_rank_fusion([['a', 'b'], ['b', 'a']])
        self.assertEqual(ranked, ['a', 'b'])
        self.assertEqual(ranking.metrics(ranked, {'a', 'b'}, 1)['recall'], .5)

    def test_duplicate_ranking_rejected(self):
        with self.assertRaises(ValueError): ranking.reciprocal_rank_fusion([['a', 'a']])


class RagTests(unittest.TestCase):
    def test_unknown_question_refuses(self):
        result = rag.run('月球基地在哪？')
        self.assertEqual(result['answer'], '资料不足，无法回答。')
        self.assertEqual(result['source_ids'], [])

    def test_actual_tool_history_and_final(self):
        counter = 0
        def ask(messages, force):
            nonlocal counter
            counter += 1
            if counter == 1:
                self.assertTrue(force)
                return {'role': 'assistant', 'tool_calls': [{'id': 'c1', 'function': {'name': 'retrieve', 'arguments': '{"query":"周一开放"}'}}]}
            self.assertEqual(messages[-1]['tool_call_id'], 'c1')
            return {'role': 'assistant', 'content': '{"answer":"09:00–18:00","source_ids":["hours"]}'}
        self.assertEqual(rag.run('周一开放', ask)['source_ids'], ['hours'])

    def test_direct_answer_without_retrieval_fails(self):
        with self.assertRaises(ValueError): rag.run('问', lambda *args: {'role': 'assistant', 'content': '{}'})

    def test_forbidden_tool_fails(self):
        response = {'role': 'assistant', 'tool_calls': [{'id': 'c1', 'function': {'name': 'send', 'arguments': '{}'}}]}
        with self.assertRaises(ValueError): rag.run('问', lambda *args: response)

    def test_tool_budget_stops_loop(self):
        count = 0
        def ask(*args):
            nonlocal count
            count += 1
            return {'role': 'assistant', 'tool_calls': [{'id': str(count), 'function': {'name': 'retrieve', 'arguments': '{"query":"开放"}'}}]}
        with self.assertRaises(RuntimeError): rag.run('开放', ask)
        self.assertEqual(count, 3)

    def test_unknown_citation_rejected(self):
        with self.assertRaises(ValueError): rag.validate_final({'answer': 'a', 'source_ids': ['fake']}, [{'id': 'hours'}])

    def test_no_evidence_requires_refusal(self):
        with self.assertRaises(ValueError): rag.validate_final({'answer': '乱猜', 'source_ids': []}, [])


if __name__ == '__main__':
    unittest.main()
