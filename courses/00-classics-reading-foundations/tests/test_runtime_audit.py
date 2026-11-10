"""审查回归只验证程序边界；模型与流式 SDK 替身不代表真实生成质量。"""
import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from companion import actions, measure, operations, service, state
from companion.files import load, save
from companion.tools import ReaderTools


class RuntimeAuditTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {"READING_DATA_DIR": self.directory.name, "DAILY_JOB_LIMIT": "40"})
        self.environment.start()
        state.initialize()
        self.actor = state.Actor("demo", "audit-reader")
        self.session = state.create_session(self.actor)
        self.chunk = {"id": "future-source", "tenant": "demo", "book": "狂人日记",
                      "text": "结局线索位于后文。", "range_reviewed": True, "range_end": 10}
        save("corpus.json", {"revision": "fixture", "chunks": [self.chunk]})

    def tearDown(self):
        for handler in operations._logger.handlers[:]:
            handler.close()
            operations._logger.removeHandler(handler)
        self.environment.stop()
        self.directory.cleanup()

    def test_changed_reading_scope_rejects_late_draft(self):
        current = state.update_session(self.actor, self.session, history=[{"role": "user", "content": "讨论后文"}])

        def changed_scope(messages):
            state.update_session(self.actor, current, history=[], progress=0, strict=True)
            return {"message": {"content": "旧范围的草稿"}}

        with patch.object(service, "complete", side_effect=changed_scope), self.assertRaises(ValueError):
            service.make_draft(self.actor, self.session["id"], "note", "scope-race")
        self.assertEqual(actions.pending(self.actor), [])

    def test_changed_conversation_rejects_late_draft(self):
        current = state.update_session(self.actor, self.session, history=[{"role": "user", "content": "旧讨论"}])

        def changed_history(messages):
            state.update_session(self.actor, current, history=[{"role": "user", "content": "新讨论"}])
            return {"message": {"content": "旧讨论的草稿"}}

        with patch.object(service, "complete", side_effect=changed_history), self.assertRaises(ValueError):
            service.make_draft(self.actor, self.session["id"], "note", "history-race")
        self.assertEqual(actions.pending(self.actor), [])

    def test_tool_rechecks_current_range_and_current_corpus(self):
        tools = ReaderTools(self.actor, self.session["id"])
        tools.execute("search_lectures", {"query": "结局线索"})
        current = state.update_session(self.actor, self.session, progress=0, strict=True)
        with self.assertRaises(PermissionError):
            tools.execute("read_source", {"source_id": self.chunk["id"]})
        state.update_session(self.actor, current, strict=False)
        save("corpus.json", {"revision": "removed", "chunks": []})
        with self.assertRaises(PermissionError):
            tools.execute("read_source", {"source_id": self.chunk["id"]})

    def test_cancellation_before_commit_prevents_both_writes(self):
        original = service.commit_job

        @contextmanager
        def cancel_before_commit(actor, request_id):
            self.assertTrue(operations.cancel(actor, request_id)["cancel_requested"])
            with original(actor, request_id):
                yield

        answer = {"answer": "迟到回答", "sources": [], "citations": [], "insufficient": True}
        with patch.object(service, "commit_job", cancel_before_commit), patch.object(service, "answer", return_value=answer):
            with self.assertRaises(ValueError):
                service.ask(self.actor, self.session["id"], "结局线索", "cancel-ask")
        self.assertEqual(state.get_session(self.actor, self.session["id"])["history"], [])
        state.update_session(self.actor, self.session, history=[{"role": "user", "content": "讨论"}])
        with patch.object(service, "commit_job", cancel_before_commit), patch.object(service, "complete", return_value={"message": {"content": "迟到草稿"}}):
            with self.assertRaises(ValueError):
                service.make_draft(self.actor, self.session["id"], "note", "cancel-draft")
        self.assertEqual(actions.pending(self.actor), [])

    def test_committing_result_is_not_reported_as_cancelled(self):
        entered, release, cancelling = threading.Event(), threading.Event(), threading.Event()
        original = service.update_session

        def paused_commit(*args, **kwargs):
            entered.set()
            if not release.wait(5):
                raise TimeoutError("测试提交等待超时")
            return original(*args, **kwargs)

        def cancel():
            cancelling.set()
            return operations.cancel(self.actor, "commit-race")

        answer = {"answer": "先完成提交的回答", "sources": [], "citations": [], "insufficient": True}
        with patch.object(service, "update_session", paused_commit), patch.object(service, "answer", return_value=answer), ThreadPoolExecutor(max_workers=2) as pool:
            asking = pool.submit(service.ask, self.actor, self.session["id"], "结局线索", "commit-race")
            try:
                self.assertTrue(entered.wait(5))
                cancellation = pool.submit(cancel)
                self.assertTrue(cancelling.wait(5))
            finally:
                release.set()
            self.assertEqual(asking.result(timeout=5)["answer"], answer["answer"])
            self.assertFalse(cancellation.result(timeout=5)["cancel_requested"])
        self.assertTrue(state.get_session(self.actor, self.session["id"])["history"])

    def test_committed_job_keeps_key_until_its_cleanup(self):
        with operations.job(self.actor, "same-key"):
            with operations.commit_job(self.actor, "same-key"):
                pass
            self.assertFalse(operations.cancel(self.actor, "same-key")["cancel_requested"])
            with self.assertRaises(ValueError):
                with operations.job(self.actor, "same-key"):
                    self.fail("旧任务退出前不能复用请求键")
        with operations.job(self.actor, "same-key") as flag:
            self.assertFalse(flag.is_set())

    def stream_client(self, finish_reason):
        @contextmanager
        def stream(**kwargs):
            self.stream_request = kwargs
            yield iter([SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="阅读笔记是记录思考。"), finish_reason=None)]),
                        SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=None), finish_reason=finish_reason)])])

        sdk = MagicMock()
        sdk.chat.completions.create.side_effect = stream
        return sdk, "fixture-only"

    def test_stream_rejects_truncated_and_missing_finish(self):
        for reason in ("length", None):
            with self.subTest(reason=reason), patch.object(measure, "client", return_value=self.stream_client(reason)), self.assertRaises(ValueError):
                measure.stream_probe()
            self.assertIsNone(load("stream-measure.json"))

    def test_stream_records_completion_and_uses_verified_settings(self):
        with patch.dict(os.environ, {"LLM_MAX_TOKENS": "512", "LLM_REASONING_EFFORT": "none"}), patch.object(measure, "client", return_value=self.stream_client("stop")):
            result = measure.stream_probe()
        self.assertEqual(self.stream_request["max_tokens"], 512)
        self.assertEqual(self.stream_request["reasoning_effort"], "none")
        self.assertEqual(result["finish_reason"], "stop")
        self.assertGreater(result["characters"], 0)


if __name__ == "__main__":
    unittest.main()
