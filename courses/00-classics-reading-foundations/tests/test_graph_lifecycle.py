"""两个真实进程同时暂停图和删除个人资料，检查删除后不会重新写回预览。"""
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
sys.path.insert(0, str(EXAMPLES))
from companion import actions, state

GRAPH = """
import os,time
from pathlib import Path
from unittest.mock import patch
from companion import graph,state
root=Path(os.environ['READING_DATA_DIR'])
original=graph.interrupt
def pause(payload):
    (root/'graph-ready').touch()
    deadline=time.monotonic()+20
    while not (root/'release-graph').exists():
        if time.monotonic()>deadline: raise TimeoutError('test synchronization timed out')
        time.sleep(.01)
    return original(payload)
with patch('companion.graph.interrupt',side_effect=pause):
    graph.run_review(state.Actor('demo','reader-a'),os.environ['REVIEW_ACTION'])
"""
ERASE = """
import os
from pathlib import Path
from companion import state
root=Path(os.environ['READING_DATA_DIR'])
(root/'erase-started').touch()
state.erase_personal_data(state.Actor('demo','reader-a'))
(root/'erase-completed').touch()
"""


class GraphDeletionRace(unittest.TestCase):
    def test_deletion_waits_for_checkpoint_and_removes_preview(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"READING_DATA_DIR": directory}):
            root = Path(directory)
            state.initialize()
            actor = state.Actor("demo", "reader-a")
            draft = actions.draft(actor, "note", "合成的私密草稿，不应残留", "race")
            env = {**os.environ, "PYTHONPATH": str(EXAMPLES), "REVIEW_ACTION": draft["id"]}
            processes = []
            try:
                for code, marker in [(GRAPH, "graph-ready"), (ERASE, "erase-started")]:
                    process = subprocess.Popen([sys.executable, "-c", code], env=env,
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    processes.append(process)
                    deadline = time.monotonic() + 20
                    while not (root / marker).exists():
                        if process.poll() is not None or time.monotonic() > deadline:
                            self.fail(f"子进程未到同步点：{marker}")
                        time.sleep(.01)
                time.sleep(.2)
                self.assertFalse((root / "erase-completed").exists())
                (root / "release-graph").touch()
                for process in processes:
                    _, error = process.communicate(timeout=20)
                    self.assertEqual(process.returncode, 0, error)
                self.assertEqual(actions.pending(actor), [])
                self.assertFalse((root / "graph-preview.json").exists())
                with sqlite3.connect(root / "checkpoints.sqlite3") as db:
                    for table in ("checkpoints", "writes"):
                        self.assertEqual(db.execute(f"SELECT count(*) FROM {table}").fetchone()[0], 0)
            finally:
                for process in processes:
                    if process.poll() is None:
                        process.kill()
                    process.communicate()


if __name__ == "__main__":
    unittest.main()
