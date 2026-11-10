"""无需模型服务的行为测试；替身只用于协议和边界，不评价真实模型质量。"""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from companion import actions, auth, corpus, maintenance, state
from companion.files import load, save
from companion.rag import answer, retrieve


class CompanionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {"READING_DATA_DIR": self.directory.name, "APP_MODE": "lab", "QDRANT_MODE": "local"})
        self.environment.start()
        state.initialize()
        self.a = state.Actor("demo", "reader-a")
        self.b = state.Actor("demo", "reader-b")
        self.session = state.create_session(self.a)
        self.chunks = [{"id": "one", "tenant": "demo", "book": "狂人日记", "doc_id": "doc", "version": "v1", "file": "06.docx", "parent": "p0001", "start": 0, "end": 12, "text": "讲稿认为文言文是序言。", "range_reviewed": True, "range_end": 1},
                       {"id": "two", "tenant": "other", "book": "狂人日记", "doc_id": "other", "version": "v1", "file": "secret.docx", "parent": "p0001", "start": 0, "end": 9, "text": "文言文私人资料。", "range_reviewed": True, "range_end": 1}]
        save("corpus.json", {"revision": "test-v1", "chunks": self.chunks, "documents": []})

    def tearDown(self):
        from companion.operations import _logger
        for handler in _logger.handlers[:]:
            handler.close(); _logger.removeHandler(handler)
        self.environment.stop()
        self.directory.cleanup()

    def test_source_scope_and_unknown_range(self):
        self.assertEqual([x["id"] for x in retrieve("文言文")], ["one"])
        self.assertEqual(corpus.visible(self.chunks, "demo", "狂人日记", 0), [])
        self.chunks[0]["range_reviewed"] = False
        self.assertEqual(corpus.visible(self.chunks, "demo", "狂人日记", 10), [])

    def test_no_evidence_and_strict_never_generate(self):
        with patch("companion.rag.complete") as model:
            self.assertTrue(answer("页码？", [])["insufficient"])
            self.assertEqual(answer("后来呢？", self.chunks[:1], strict=True)["mode"], "reviewed-excerpts")
            model.assert_not_called()

    def test_fabricated_citation_rejected(self):
        response = {"message": {"content": json.dumps({"answer": "内容", "citations": ["invented"], "insufficient": False})}, "usage": {}, "model": "test-double"}
        with patch("companion.rag.complete", return_value=response), self.assertRaises(ValueError):
            answer("序言？", self.chunks[:1])

    def test_owner_and_optimistic_version(self):
        with self.assertRaises(PermissionError): state.get_session(self.b, self.session["id"])
        state.update_session(self.a, self.session, progress=1)
        with self.assertRaises(ValueError): state.update_session(self.a, self.session, progress=2)

    def test_approval_revision_expiry_and_idempotency(self):
        draft = actions.draft(self.a, "note", "旧内容", "request-1")
        revised = actions.revise(self.a, draft["id"], "新内容")
        with self.assertRaises(ValueError): actions.approve(self.a, draft["id"], draft["revision"], draft["digest"], True)
        with self.assertRaises(PermissionError): actions.approve(self.b, draft["id"], revised["revision"], revised["digest"], True)
        actions.approve(self.a, revised["id"], revised["revision"], revised["digest"], True)
        actions.approve(self.a, revised["id"], revised["revision"], revised["digest"], True)
        self.assertEqual(len(actions.notes(self.a)), 1)
        late = actions.draft(self.a, "note", "过期", "request-2")
        with state.connect() as db: db.execute("UPDATE actions SET expires=0 WHERE id=?", (late["id"],))
        with self.assertRaises(ValueError): actions.approve(self.a, late["id"], late["revision"], late["digest"], True)

    def test_graph_restart_resume_and_erase(self):
        from companion.graph import run_review
        draft = actions.draft(self.a, "note", "图中的笔记", "graph-1")
        paused = run_review(self.a, draft["id"])
        self.assertEqual(paused["status"], "awaiting_confirmation")
        decision = {**paused["preview"], "confirmed": True}
        self.assertEqual(run_review(self.a, draft["id"], decision)["status"], "finished")
        run_review(self.a, draft["id"], decision)
        self.assertEqual(len(actions.notes(self.a)), 1)
        state.erase_personal_data(self.a)
        with self.assertRaises(ValueError): run_review(self.a, draft["id"], decision)

    def test_family_sees_progress_only(self):
        auth.create_user("demo", "parent", "a-long-test-password", "parent")
        auth.create_user("demo", "reader-a", "another-test-password")
        auth.link_family("demo", "parent", "reader-a")
        rows = state.family_report(state.Actor("demo", "parent", "parent"), "reader-a")
        self.assertEqual(set(rows[0]), {"book", "progress"})
        with self.assertRaises(PermissionError): state.family_report(self.b, "reader-a")

    def test_auth_token_revocation(self):
        auth.create_user("demo", "reader", "a-long-test-password")
        token = auth.login("demo", "reader", "a-long-test-password", "local")["access_token"]
        self.assertEqual(auth.authenticate(token).user, "reader")
        auth.logout(token)
        with self.assertRaises(PermissionError): auth.authenticate(token)

    def test_qdrant_persistence_and_filter_contract(self):
        from companion import vectors
        model = MagicMock()
        # 固定向量只检验存储、版本和过滤，不能作为 Embedding 效果报告。
        with patch.object(vectors, "encoder", return_value=model), patch.object(vectors, "embed", side_effect=lambda texts: [[1.0, 0.0] for text in texts]):
            first = vectors.build_index()
            self.assertEqual(vectors.build_index()["new_embeddings"], 0)
            self.assertEqual([x["id"] for x in vectors.semantic_search("文言文", "demo", "狂人日记")], ["one"])
            self.assertEqual(vectors.semantic_search("文言文", "demo", "狂人日记", 0), [])
            changed = load("corpus.json"); changed["revision"] = "new-version"; save("corpus.json", changed)
            with self.assertRaises(ValueError): vectors.semantic_search("文言文", "demo", "狂人日记")
            self.assertEqual(first["count"], 2)

    def test_backup_restore_verifies_hash_and_revokes_tokens(self):
        destination = Path(self.directory.name) / "backup"
        maintenance.backup(destination)
        result = maintenance.restore(destination, Path(self.directory.name) / "restored")
        self.assertTrue(result["index_rebuild_required"])
        (destination / "corpus.json").write_text("tampered")
        with self.assertRaises(ValueError): maintenance.restore(destination, Path(self.directory.name) / "bad")

    def test_api_scope_and_password_not_echoed(self):
        from fastapi.testclient import TestClient
        from companion.app import app
        with TestClient(app) as client:
            self.assertEqual(client.get("/api/books").json(), ["狂人日记"])
            response = client.get("/api/sessions/" + self.session["id"], headers={"X-Lab-Reader": "reader-b"})
            self.assertEqual(response.status_code, 403)
            response = client.post("/api/login", json={"tenant": "demo", "username": "a", "password": "secret", "unexpected": "secret"})
            self.assertEqual(response.status_code, 422)
            self.assertNotIn("secret", response.text)

    def test_erasure_prevents_delayed_draft_and_preserves_limit(self):
        with state.connect() as db:
            db.execute("INSERT INTO quotas VALUES(?,?,?,?)", ("demo", "reader-a", "2099-01-01", 3))
        state.erase_personal_data(self.a)
        with self.assertRaises(PermissionError):
            actions.draft(self.a, "note", "迟到的草稿", "late", session_id=self.session["id"])
        with state.connect() as db:
            self.assertEqual(db.execute("SELECT count FROM quotas").fetchone()[0], 3)
        self.assertEqual(actions.pending(self.a), [])

    def test_agent_protocol_and_budget(self):
        from companion.agent import run_agent
        tool_response = {"message": {"role": "assistant", "content": None, "tool_calls": [{"id": "call1", "type": "function", "function": {"name": "search_lectures", "arguments": '{"query":"文言文"}'}}]}, "usage": {"total_tokens": 10}}
        final = {"message": {"content": json.dumps({"answer": "测试替身回答", "citations": ["one"], "insufficient": False})}, "usage": {"total_tokens": 10}}
        with patch("companion.agent.complete", side_effect=[tool_response, final]):
            result = run_agent(self.a, self.session["id"], "文言文")
            self.assertEqual(result["trace"][0]["tool"], "search_lectures")
            self.assertEqual(result["citations"], ["one"])
        with patch("companion.agent.complete", return_value=tool_response) as model:
            result = run_agent(self.a, self.session["id"], "文言文", max_rounds=1)
            self.assertTrue(result["insufficient"])
            self.assertEqual(model.call_count, 1)

    def test_authenticated_api_does_not_accept_lab_identity(self):
        from fastapi.testclient import TestClient
        from companion.app import app
        with patch("companion.app.MODE", "authenticated"), TestClient(app) as client:
            self.assertEqual(client.get("/api/sessions", headers={"X-Lab-Reader": "reader-a"}).status_code, 401)

    def test_migration_preserves_existing_and_future_notes(self):
        from companion.migrate import migrate
        first = actions.draft(self.a, "note", "迁移前", "before")
        actions.approve(self.a, first["id"], first["revision"], first["digest"], True)
        self.assertEqual(migrate()["note_count"], 1)
        self.assertEqual(migrate()["schema_version"], 2)
        state.initialize()
        second = actions.draft(self.a, "note", "迁移后", "after")
        actions.approve(self.a, second["id"], second["revision"], second["digest"], True)
        self.assertEqual(len(actions.notes(self.a)), 2)
        self.assertEqual(maintenance.manifest()["schema_version"], 2)

    def test_tools_reject_identity_override(self):
        from companion.tools import ReaderTools
        tools = ReaderTools(self.a, self.session["id"])
        with self.assertRaises(ValueError): tools.execute("search_lectures", {"query": "文言文", "tenant": "other"})
        with self.assertRaises(PermissionError): tools.execute("read_source", {"source_id": "two"})


if __name__ == "__main__":
    unittest.main()
