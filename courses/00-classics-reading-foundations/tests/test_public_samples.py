"""公开样本的可重复生成、冲突保护与证据一致性检查。"""
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

from docx import Document

COURSE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COURSE / "examples"))
from prepare_samples import MATERIALS, prepare, render_docx


class PublicSamplesTest(unittest.TestCase):
    def test_repeatable_and_clean_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "input"
            first = prepare(output)
            second = prepare(output)
            self.assertEqual(first, second)
            for row in first["documents"]:
                content = (output / row["file"]).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), row["sha256"])
                doc = Document(BytesIO(content))
                self.assertEqual(doc.core_properties.author, "名著伴读课程")
                self.assertEqual(doc.core_properties.last_modified_by, "")
                self.assertEqual(len(doc.paragraphs), 1)
                self.assertEqual(len(doc.paragraphs[0].text), row["character_count"])

    def test_conflict_does_not_partly_write(self):
        rows = json.loads((MATERIALS / "manifest.json").read_text())["documents"]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "input"
            output.mkdir()
            conflict = output / rows[-1]["file"]
            conflict.write_bytes(b"learner edited this file")
            with self.assertRaises(ValueError):
                prepare(output)
            self.assertEqual(conflict.read_bytes(), b"learner edited this file")
            self.assertEqual(list(output.iterdir()), [conflict])
            self.assertFalse((output.parent / "sample-manifest.json").exists())

    def test_quotes_belong_to_expected_material(self):
        manifest = json.loads((MATERIALS / "manifest.json").read_text())
        texts = {row["file"]: render_docx((MATERIALS / row["text"]).read_text())[1]
                 for row in manifest["documents"]}
        for name in ("dev.json", "holdout.json"):
            for case in json.loads((COURSE / "examples/eval" / name).read_text()):
                if case["expected_insufficient"]:
                    self.assertEqual(case["expected_quotes"], [])
                    self.assertIsNone(manifest["page_mapping"])
                    self.assertIsNone(manifest["publisher"])
                else:
                    for quote in case["expected_quotes"]:
                        self.assertTrue(any(quote in text and any(file.startswith(p) for p in case["expected_document_prefixes"])
                                            for file, text in texts.items()), case["id"])
        first = texts[manifest["documents"][0]["file"]]
        self.assertIn("文言文序言提供外部叙述", first[200:1100])
        self.assertNotIn("文言文序言", first[:120])


if __name__ == "__main__":
    unittest.main()
