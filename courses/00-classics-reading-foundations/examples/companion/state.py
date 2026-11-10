"""SQLite 保存读者状态；查询始终带租户和本人身份。"""
import json
import fcntl
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass

from .files import data_dir, load


@dataclass(frozen=True)
class Actor:
    tenant: str
    user: str
    role: str = "reader"


@contextmanager
def personal_data_lock():
    # CLI 与 API 可能是两个进程；用文件锁协调检查点写入和删除，线程锁不够。
    # 这里只保护不调用模型的短操作，进程异常退出时系统也会释放锁。
    with (data_dir() / ".personal-data.lock").open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


@contextmanager
def connect():
    db = sqlite3.connect(data_dir() / "reading.sqlite3", timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def initialize():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS sessions(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          book TEXT NOT NULL, progress INTEGER NOT NULL DEFAULT 0,
          strict INTEGER NOT NULL DEFAULT 0, phase TEXT NOT NULL DEFAULT 'question',
          history TEXT NOT NULL DEFAULT '[]', revision INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS actions(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          request_key TEXT NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL,
          digest TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1,
          expires REAL NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
          UNIQUE(tenant,owner,request_key));
        CREATE TABLE IF NOT EXISTS notes(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          kind TEXT NOT NULL, body TEXT NOT NULL, created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS feedback(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          category TEXT NOT NULL, trace_id TEXT NOT NULL, created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS users(
          tenant TEXT NOT NULL, username TEXT NOT NULL, role TEXT NOT NULL,
          salt TEXT NOT NULL, password_hash TEXT NOT NULL, disabled INTEGER NOT NULL DEFAULT 0,
          PRIMARY KEY(tenant,username));
        CREATE TABLE IF NOT EXISTS tokens(
          digest TEXT PRIMARY KEY, tenant TEXT NOT NULL, username TEXT NOT NULL, expires REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS families(
          tenant TEXT NOT NULL, parent TEXT NOT NULL, child TEXT NOT NULL,
          PRIMARY KEY(tenant,parent,child));
        CREATE TABLE IF NOT EXISTS quotas(
          tenant TEXT NOT NULL, owner TEXT NOT NULL, day TEXT NOT NULL, count INTEGER NOT NULL,
          PRIMARY KEY(tenant,owner,day));
        """)
        if db.execute("PRAGMA user_version").fetchone()[0] == 0:
            db.execute("PRAGMA user_version=1")


def create_session(actor, book="狂人日记"):
    identity = uuid.uuid4().hex
    with connect() as db:
        db.execute("INSERT INTO sessions(id,tenant,owner,book) VALUES(?,?,?,?)", (identity, actor.tenant, actor.user, book))
    return get_session(actor, identity)


def get_session(actor, identity):
    with connect() as db:
        row = db.execute("SELECT * FROM sessions WHERE id=? AND tenant=? AND owner=?", (identity, actor.tenant, actor.user)).fetchone()
    if row is None:
        raise PermissionError("会话不存在或不属于当前读者。")
    result = dict(row)
    result["history"] = json.loads(result["history"])
    return result


def update_session(actor, session, history=None, progress=None, strict=None, phase=None):
    with connect() as db:
        # 乐观版本检查防止两次并发提问互相覆盖；冲突时由页面提示重新读取。
        cursor = db.execute("""UPDATE sessions SET history=?,progress=?,strict=?,phase=?,revision=revision+1
          WHERE id=? AND tenant=? AND owner=? AND revision=?""",
          (json.dumps(session["history"] if history is None else history, ensure_ascii=False),
           session["progress"] if progress is None else progress,
           session["strict"] if strict is None else int(strict), phase or session["phase"],
           session["id"], actor.tenant, actor.user, session["revision"]))
        if cursor.rowcount != 1:
            raise ValueError("会话已被另一请求修改，请重新读取后再试。")
    return get_session(actor, session["id"])


def delete_session(actor, identity):
    with connect() as db:
        db.execute("DELETE FROM sessions WHERE id=? AND tenant=? AND owner=?", (identity, actor.tenant, actor.user))


def list_sessions(actor):
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT id,book,progress,strict,phase,revision FROM sessions WHERE tenant=? AND owner=?", (actor.tenant, actor.user))]


def family_report(actor, child):
    with connect() as db:
        linked = db.execute("SELECT 1 FROM families WHERE tenant=? AND parent=? AND child=?", (actor.tenant, actor.user, child)).fetchone()
        if actor.role != "parent" or not linked:
            raise PermissionError("没有已确认的家长关联。")
        # 家长仅查看显式进度，不自动读取孩子的私密对话或笔记。
        return [dict(r) for r in db.execute("SELECT book,progress FROM sessions WHERE tenant=? AND owner=?", (actor.tenant, child))]


def erase_personal_data(actor):
    # 同一锁内清除检查点和业务行，防止另一个进程在删除后又写回旧草稿预览。
    with personal_data_lock():
        if (data_dir() / "checkpoints.sqlite3").exists():
            from .graph import erase_threads
            erase_threads(actor)
        with connect() as db:
            db.execute("BEGIN IMMEDIATE")
            preview = load("graph-preview.json")
            if preview and db.execute("SELECT 1 FROM actions WHERE id=? AND tenant=? AND owner=?", (preview.get("id"), actor.tenant, actor.user)).fetchone():
                (data_dir() / "graph-preview.json").unlink()
            # 当日额度不随内容删除重置，避免反复删除绕过限制；下次请求时清理过期计数。
            for table in ("sessions", "actions", "notes", "feedback"):
                db.execute(f"DELETE FROM {table} WHERE tenant=? AND owner=?", (actor.tenant, actor.user))
            db.execute("DELETE FROM tokens WHERE tenant=? AND username=?", (actor.tenant, actor.user))
    return {"deleted": True, "scope": "已删除当前业务库个人内容与会话令牌；账号和当日限额计数保留，备份按留存流程另行处理"}
