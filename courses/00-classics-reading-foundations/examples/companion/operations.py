# 目的：先只写最少审计日志；并发名额和每日额度放在负载章节实现。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import json
import os
import time
from contextlib import contextmanager
from .state import connect
import logging
import threading
from datetime import datetime, timezone
from .files import data_dir

_lock=threading.Lock()
_logger=logging.getLogger("reading-audit")

# 目的：日志便于排错，但不应成为另一份聊天、口令或讲稿数据库。
# 预期：只保存编号、状态、耗时和用量等白名单字段。
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

# 目的：名额满了要拒绝，不无限排队；任务键包含机构、本人和请求ID。
# 预期：两个读者不能互相取消对方任务。
_slots=threading.BoundedSemaphore(int(os.environ.get("MAX_MODEL_JOBS","1")))
_jobs={}

# 目的：在 finally 里释放名额，失败和取消也不能泄漏槽位；日额度在数据库事务中更新。
# 预期：取消后不继续工具调用或保存迟到内容；未知请求不会假称已取消。
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

# 目的：只标记同一身份的当前任务，已发给供应商的请求可能仍运行与计费。
# 预期：取消后不继续工具调用或保存迟到内容；未知请求不会假称已取消。
def cancel(actor, request_id):
    with _lock:
        flag = _jobs.get((actor.tenant, actor.user, request_id))
        if flag is not None:
            flag.set()
    return {"cancel_requested": flag is not None, "message": "已发送的模型请求可能仍在运行和计费；停止后不会继续调用工具。"}
