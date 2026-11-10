# 目的：先只保存阅读会话；批准、账号、反馈与限额表都留到对应章节创建。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import json
import fcntl
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from .files import data_dir, load

# 目的：业务函数不从模型文字里推断读者；本章仅有本机虚构身份。
# 预期：每次数据库操作都明确带 tenant 和 user。
@dataclass(frozen=True)
class Actor:
    tenant: str
    user: str
    role: str = "reader"

# 目的：with 内成功才提交；发生错误回滚并关闭连接，避免锁住数据库。
# 预期：一次操作失败不会留下半次修改。
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

# 目的：一行会话属于一个机构和一个读者；history 保存最近对话，revision 用于发现同时修改。
# 预期：数据库中能查询到本节创建的 sessions 表，重复初始化不会清除已有会话。
def initialize():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS sessions(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          book TEXT NOT NULL, history TEXT NOT NULL DEFAULT '[]',
          revision INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS actions(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          request_key TEXT NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL,
          digest TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1,
          expires REAL NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
          UNIQUE(tenant,owner,request_key));
        CREATE TABLE IF NOT EXISTS notes(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          kind TEXT NOT NULL, body TEXT NOT NULL, created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS users(
          tenant TEXT NOT NULL, username TEXT NOT NULL, role TEXT NOT NULL,
          salt TEXT NOT NULL, password_hash TEXT NOT NULL, disabled INTEGER NOT NULL DEFAULT 0,
          PRIMARY KEY(tenant,username));
        CREATE TABLE IF NOT EXISTS tokens(
          digest TEXT PRIMARY KEY, tenant TEXT NOT NULL, username TEXT NOT NULL, expires REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS families(
          tenant TEXT NOT NULL, parent TEXT NOT NULL, child TEXT NOT NULL,
          PRIMARY KEY(tenant,parent,child));
        CREATE TABLE IF NOT EXISTS feedback(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          category TEXT NOT NULL, trace_id TEXT NOT NULL, created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS quotas(
          tenant TEXT NOT NULL, owner TEXT NOT NULL, day TEXT NOT NULL, count INTEGER NOT NULL,
          PRIMARY KEY(tenant,owner,day));
        """)
        columns={row[1] for row in db.execute("PRAGMA table_info(sessions)")}
        for name, definition in {"progress":"INTEGER NOT NULL DEFAULT 0","strict":"INTEGER NOT NULL DEFAULT 0","phase":"TEXT NOT NULL DEFAULT 'question'"}.items():
            if name not in columns:
                db.execute(f"ALTER TABLE sessions ADD COLUMN {name} {definition}")
        if db.execute("PRAGMA user_version").fetchone()[0] == 0:
            db.execute("PRAGMA user_version=1")

# 目的：同时按 id、tenant 和 owner 查询，知道别人的会话 ID 也拿不到正文。
# 预期：会话操作只影响当前读者。
def get_session(actor, identity):
    with connect() as db:
        row = db.execute("SELECT * FROM sessions WHERE id=? AND tenant=? AND owner=?", (identity, actor.tenant, actor.user)).fetchone()
    if row is None:
        raise PermissionError("会话不存在或不属于当前读者。")
    result = dict(row)
    result["history"] = json.loads(result["history"])
    return result

# 目的：由程序生成不可猜的会话 ID，并明确写入归属和作品。
# 预期：会话操作只影响当前读者。
def create_session(actor, book="狂人日记"):
    identity = uuid.uuid4().hex
    with connect() as db:
        db.execute("INSERT INTO sessions(id,tenant,owner,book) VALUES(?,?,?,?)", (identity, actor.tenant, actor.user, book))
    return get_session(actor, identity)

# 目的：删除同样带本人范围，不能只根据任意 ID 操作。
# 预期：会话操作只影响当前读者。
def delete_session(actor, identity):
    with connect() as db:
        db.execute("DELETE FROM sessions WHERE id=? AND tenant=? AND owner=?", (identity, actor.tenant, actor.user))

# 目的：列表不需要返回所有对话正文，先少拿数据再展示。
# 预期：切换读者后列表不会混在一起。
def list_sessions(actor):
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT id,book,progress,strict,phase,revision FROM sessions WHERE tenant=? AND owner=?", (actor.tenant, actor.user))]

# 目的：两个请求读到相同版本，只允许先完成的一次更新成功；另一次重新读取再决定。
# 预期：旧版本写入抛出 ValueError，而不静默覆盖新对话。
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

# 目的：保护不调用模型的短状态操作；进程异常退出时系统释放锁。
# 预期：不会一边报告删除成功，一边又写回旧检查点。
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

# 目的：关联不代表可读私密聊天；查询列仅包含作品和进度。
# 预期：响应中没有 history 或笔记正文。
def family_report(actor, child):
    with connect() as db:
        linked = db.execute("SELECT 1 FROM families WHERE tenant=? AND parent=? AND child=?", (actor.tenant, actor.user, child)).fetchone()
        if actor.role != "parent" or not linked:
            raise PermissionError("没有已确认的家长关联。")
        # 家长仅查看显式进度，不自动读取孩子的私密对话或笔记。
        return [dict(r) for r in db.execute("SELECT book,progress FROM sessions WHERE tenant=? AND owner=?", (actor.tenant, child))]

# 目的：删除与图写入竞争时必须串行，避免刚报告删除成功就由迟到任务写回。
# 预期：当前业务库内容与令牌清除；账号、备份与额度留存范围明确说明。
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
