"""统一数据位置与原子写入，让课程换电脑后仍能沿用相对路径。"""
import hashlib
import json
import os
from pathlib import Path


def data_dir():
    directory = Path(os.environ.get("READING_DATA_DIR", "data/live"))
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load(name, default=None):
    file = data_dir() / name
    return json.loads(file.read_text(encoding="utf-8")) if file.exists() else default


def save(name, value):
    file = data_dir() / name
    file.parent.mkdir(parents=True, exist_ok=True)
    temporary = file.with_suffix(file.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    # 先完整写入再替换，读者不会读到只写了一半的 JSON；索引任务应单实例执行。
    temporary.replace(file)
    return file
