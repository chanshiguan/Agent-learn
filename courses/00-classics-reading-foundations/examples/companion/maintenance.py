"""备份与恢复实验：保存数据库快照、资料版本及哈希，不复制凭据。"""
import hashlib
import json
import os
import shutil
import sqlite3
from pathlib import Path
from .files import data_dir, load


def backup(destination):
    target = Path(destination)
    target.mkdir(parents=True, exist_ok=False)
    original = data_dir()
    # SQLite backup API 取得一致快照。完整系统备份仍需先停止写入和索引任务，保证多文件版本一致。
    for name in ("reading.sqlite3", "checkpoints.sqlite3"):
        if (original / name).exists():
            with sqlite3.connect(original / name) as source, sqlite3.connect(target / name) as copy:
                source.backup(copy)
    for name in ("corpus.json", "ranges.json", "index.json"):
        if (original / name).exists():
            shutil.copy2(original / name, target / name)
    hashes = {file.name: hashlib.sha256(file.read_bytes()).hexdigest() for file in target.iterdir() if file.is_file()}
    (target / "manifest.json").write_text(json.dumps({"files": hashes, "strategy": "索引可由 corpus 重建；此包不含 Qdrant 卷与模型权重"}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"backup": str(target), "files": list(hashes)}


def restore(source, destination):
    source, target = Path(source), Path(destination)
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    allowed = {"reading.sqlite3", "checkpoints.sqlite3", "corpus.json", "ranges.json", "index.json"}
    if not set(manifest["files"]).issubset(allowed):
        raise ValueError("备份包含未约定的文件名。")
    for name, expected in manifest["files"].items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"备份指纹不符：{name}")
    target.mkdir(parents=True, exist_ok=False)
    for name in manifest["files"]:
        if name != "index.json":
            shutil.copy2(source / name, target / name)
    if (target / "reading.sqlite3").exists():
        with sqlite3.connect(target / "reading.sqlite3") as db:
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("数据库完整性检查失败。")
            # 恢复后重新登录，避免把备份里的旧访问令牌重新激活。
            db.execute("DELETE FROM tokens")
            db.execute("UPDATE actions SET expires=0 WHERE status='pending'")
    return {"restored": str(target), "index_rebuild_required": True, "login_required": True}


def manifest():
    import importlib.metadata
    packages = {}
    for name in ("python-docx", "openai", "fastapi", "qdrant-client", "sentence-transformers", "langgraph"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    from .state import connect
    with connect() as db:
        schema_version = db.execute("PRAGMA user_version").fetchone()[0]
    source_root = Path(__file__).parent
    source_hashes = {str(f.relative_to(source_root)): hashlib.sha256(f.read_bytes()).hexdigest()
                     for f in source_root.rglob("*") if f.is_file() and f.suffix in {".py", ".html", ".js", ".css"}}
    return {"application": "classics-course-v2", "source_hashes": source_hashes,
            "generation_model": os.environ.get("LLM_MODEL"), "generation_route": os.environ.get("LLM_MODE"), "prompt_version": "grounded-v1",
            "corpus_revision": (load("corpus.json") or {}).get("revision"),
            "index": load("index.json"), "packages": packages,
            "schema_version": schema_version}
