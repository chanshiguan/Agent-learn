"""验证资料不被误改和失败不伪装成功；这些检查不证明模型效果或学员掌握。"""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from docx import Document


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "中文 讲稿.docx"
        doc = Document()
        doc.add_paragraph("  第一段  ")
        doc.add_paragraph("")
        doc.add_paragraph("第二段")
        doc.add_table(rows=1, cols=1).cell(0, 0).text = "表格内的文字"
        doc.save(self.source)

    def tearDown(self):
        self.temp.cleanup()

    def read(self, source, output):
        return subprocess.run([sys.executable, str(EXAMPLES / "read_docx.py"), str(source), str(output)], capture_output=True, text=True)

    def test_positions_provenance_and_source_unchanged(self):
        before = self.source.read_bytes()
        output = self.root / "new" / "result.json"
        result = self.read(self.source, output)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(output.read_text())
        self.assertEqual(data["paragraphs"], [{"id":"p0001","text":"第一段"},{"id":"p0003","text":"第二段"}])
        self.assertEqual(data["skipped_table_count"], 1)
        self.assertEqual(data["source_sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(before, self.source.read_bytes())

    def test_missing_input_has_no_success_file(self):
        output = self.root / "absent.json"
        result = self.read(self.root / "absent.docx", output)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(output.exists())

    def test_cannot_write_json_over_source_docx(self):
        before = self.source.read_bytes()
        result = self.read(self.source, self.source)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(before, self.source.read_bytes())

    def test_no_text_is_not_success(self):
        empty = self.root / "empty.docx"
        Document().save(empty)
        output = self.root / "empty.json"
        self.assertEqual(self.read(empty, output).returncode, 2)
        self.assertFalse(output.exists())

    def test_cloud_configuration_stops_before_sending(self):
        env = {k:v for k,v in os.environ.items() if not k.startswith("LLM_")}
        env.update(LLM_MODE="cloud", LLM_MODEL="test-only", LLM_BASE_URL="http://example.invalid/v1")
        output = self.root / "model.json"
        result = subprocess.run([sys.executable, str(EXAMPLES / "first_chat.py"), "--output", str(output)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("HTTPS", result.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
