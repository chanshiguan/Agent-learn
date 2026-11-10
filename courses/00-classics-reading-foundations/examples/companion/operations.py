"""请求边界与最少日志：单进程实验配置，不冒称集群级限流。"""
import json
import logging
import os
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from .files import data_dir, digest
from .state import connect

_slots = threading.BoundedSemaphore(int(os.environ.get("MAX_MODEL_JOBS", "1")))
_jobs, _lock = {}, threading.Lock()
_logger = logging.getLogger("reading-audit")


def log_event(trace_id, event, **fields):
    if not _logger.handlers:
        with _lock:
            if not _logger.handlers:
                handler = logging.FileHandler(data_dir() / "events.jsonl", encoding="utf-8")
                handler.setFormatter(logging.Formatter("%(message)s"))
                _logger.addHandler(handler)
                _logger.setLevel(logging.INFO)
                _logger.propagate = False
    # 只写明确允许的数值和状态，不接收请求正文、口令、讲稿或完整模型错误。
    safe = {k: v for k, v in fields.items() if k in {"seconds", "status", "method", "input_chars", "source_count", "tokens", "tool_count"}}
    _logger.info(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "trace_id": trace_id, "event": event, **safe}))


@contextmanager
def job(actor, request_id):
    key = (actor.tenant, actor.user, request_id)
    with _lock:
        if key in _jobs:
            raise ValueError("请求已经在处理中，请不要重复提交。")
        flag = threading.Event()
        _jobs[key] = flag
    acquired = False
    try:
        acquired = _slots.acquire(timeout=1)
        if not acquired:
            raise TimeoutError("当前请求较多，请稍后再试。")
        day = datetime.now(timezone.utc).date().isoformat()
        with connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM quotas WHERE day < ?", (day,))
            row = db.execute("SELECT count FROM quotas WHERE tenant=? AND owner=? AND day=?", (actor.tenant, actor.user, day)).fetchone()
            count = row[0] if row else 0
            if count >= int(os.environ.get("DAILY_JOB_LIMIT", "40")):
                raise PermissionError("今天的试用请求额度已用完。")
            db.execute("INSERT INTO quotas VALUES(?,?,?,?) ON CONFLICT(tenant,owner,day) DO UPDATE SET count=excluded.count", (actor.tenant, actor.user, day, count + 1))
        yield flag
    finally:
        if acquired:
            _slots.release()
        with _lock:
            _jobs.pop(key, None)


def cancel(actor, request_id):
    with _lock:
        flag = _jobs.get((actor.tenant, actor.user, request_id))
        if flag is not None:
            flag.set()
    return {"cancel_requested": flag is not None, "message": "已发送的模型请求可能仍在运行和计费；停止后不会继续调用工具。"}
