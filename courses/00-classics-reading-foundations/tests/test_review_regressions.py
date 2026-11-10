"""复现课程审查中的边界问题，不以模型替身验证文学回答质量。"""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from companion import state, actions, corpus, service, operations, vectors
from companion.files import save, load


class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"READING_DATA_DIR": self.directory.name, "APP_MODE": "lab"})
        self.env.start()
        state.initialize()
        self.actor = state.Actor("demo", "reader-a")
        self.session = state.create_session(self.actor)

    def tearDown(self):
        for handler in operations._logger.handlers[:]:
            handler.close()
            operations._logger.removeHandler(handler)
        self.env.stop()
        self.directory.cleanup()

    def test_progress_rejects_stale_page_revision(self):
        from fastapi.testclient import TestClient
        from companion.app import app
        with TestClient(app) as api:
            path = f"/api/sessions/{self.session['id']}"
            first = api.patch(path, json={"progress": 3, "strict": False, "revision": 0})
            self.assertEqual(first.status_code, 200)
            second = api.patch(path, json={"progress": 1, "strict": False, "revision": 0})
            self.assertEqual(second.status_code, 409)
            self.assertEqual(api.get(path).json()["progress"], 3)

    def test_local_client_does_not_inherit_network_proxy(self):
        from companion.models import client
        with patch.dict(os.environ, {"LLM_MODE": "local", "LLM_MODEL": "test-model",
                                     "LLM_BASE_URL": "http://127.0.0.1:11434/v1",
                                     "ALL_PROXY": "socks5://127.0.0.1:1", "NO_PROXY": ""}):
            sdk, model = client()
            try:
                self.assertEqual(model, "test-model")
                self.assertFalse(sdk._client.trust_env)
            finally:
                sdk.close()

    def test_cancelled_generation_does_not_leave_a_draft(self):
        state.update_session(self.actor, self.session, history=[{"role": "user", "content": "测试讨论"}])
        def delayed_model(messages):
            operations.cancel(self.actor, "cancelled-draft")
            return {"message": {"content": "不应保存的迟到结果"}}
        with patch("companion.service.complete", side_effect=delayed_model):
            with self.assertRaises(ValueError):
                service.make_draft(self.actor, self.session["id"], "note", "cancelled-draft")
        self.assertEqual(actions.pending(self.actor), [])

    def test_mixed_empty_document_preserves_previous_snapshot(self):
        from docx import Document
        root = Path(self.directory.name) / "input"
        root.mkdir()
        doc = Document()
        doc.add_paragraph("这是一份正常的测试文本。")
        doc.save(root / "01-good.docx")
        previous = {"revision": "old", "documents": [], "chunks": []}
        save("corpus.json", previous)
        Document().save(root / "02-empty.docx")
        with self.assertRaises(ValueError):
            corpus.ingest(root)
        self.assertEqual(load("corpus.json"), previous)

    def test_ask_returns_revision_for_next_progress_write(self):
        from fastapi.testclient import TestClient
        from companion.app import app
        save("corpus.json", {"revision": "empty", "chunks": [], "documents": []})
        with TestClient(app) as api:
            result = api.post("/api/ask", json={"session_id": self.session["id"],
                              "question": "没有资料时如何回答", "request_id": "a" * 32})
            self.assertEqual(result.status_code, 200)
            body = result.json()
            self.assertTrue(body["insufficient"])
            saved = api.patch(f"/api/sessions/{self.session['id']}",
                             json={"progress": 2, "strict": False, "revision": body["session_revision"]})
            self.assertEqual(saved.status_code, 200)

    def test_semantic_results_recheck_current_reading_scope(self):
        from contextlib import contextmanager
        from types import SimpleNamespace
        from unittest.mock import MagicMock
        chunk = {"id": "malformed", "tenant": "demo", "book": "狂人日记",
                 "range_reviewed": True, "range_end": True, "text": "不应显示的未核对范围"}
        save("corpus.json", {"revision": "r1", "chunks": [chunk]})
        save("index.json", {"corpus_revision": "r1", "model": vectors.MODEL,
                            "model_revision": vectors.MODEL_REVISION, "collection": "test"})
        model = MagicMock()
        db = MagicMock()
        db.query_points.return_value.points = [SimpleNamespace(payload=chunk, score=1.0)]
        @contextmanager
        def database():
            yield db
        with patch.object(vectors, "encoder", return_value=model), patch.object(vectors, "embed", return_value=[[1.0]]), patch.object(vectors, "connection", database):
            self.assertEqual(vectors.semantic_search("测试问题", "demo", "狂人日记", progress=1), [])

    def test_ingest_rejects_boolean_review_range(self):
        from docx import Document
        root = Path(self.directory.name) / "input"
        root.mkdir()
        doc = Document()
        doc.add_paragraph("范围需要经过人工核对。")
        doc.save(root / "06-test.docx")
        corpus.ingest(root)
        previous = load("corpus.json")
        save("ranges.json", {previous["chunks"][0]["id"]: {"reviewed": True, "range_end": True}})
        with self.assertRaises(ValueError):
            corpus.ingest(root)
        self.assertEqual(load("corpus.json"), previous)

    def test_encoder_loads_explicit_public_revision(self):
        # 不下载权重；核对真实加载器收到固定 revision，防止再次退回私有字段或浮动 main。
        import types
        from unittest.mock import MagicMock
        factory = MagicMock()
        vectors.encoder.cache_clear()
        try:
            with patch.dict(sys.modules, {"sentence_transformers": types.SimpleNamespace(SentenceTransformer=factory)}):
                vectors.encoder()
                self.assertEqual(factory.call_args.kwargs["revision"], vectors.MODEL_REVISION)
                self.assertEqual(factory.call_args.args[0], vectors.MODEL)
        finally:
            vectors.encoder.cache_clear()


if __name__ == "__main__":
    unittest.main()
