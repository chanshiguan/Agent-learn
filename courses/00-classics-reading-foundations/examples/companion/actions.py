# 目的：草稿预览与正式笔记分开保存，批准必须绑定本人、内容和版本。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import time
import uuid
from .files import digest
from .state import connect

# 目的：生成草稿不等于保存笔记；请求键防止重复生成同一动作。
# 预期：越权、过期或错误摘要不会写入笔记；重复批准返回同一结果。
def draft(actor, kind, body, request_key, session_id=None):
    if kind not in {"note", "review_plan"} or not isinstance(body, str) or not 1 <= len(body.strip()) <= 6000:
        raise ValueError("只接受非空笔记或复习计划，最多 6000 字符。")
    hashed = digest([kind, body])
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        # 草稿生成期间读者可能删除阅读；在同一写事务里复核，避免删除后又留下新草稿。
        if session_id is not None and not db.execute("SELECT 1 FROM sessions WHERE id=? AND tenant=? AND owner=?", (session_id, actor.tenant, actor.user)).fetchone():
            raise PermissionError("阅读记录已删除，不再保存这份草稿。")
        existing = db.execute("SELECT * FROM actions WHERE tenant=? AND owner=? AND request_key=?", (actor.tenant, actor.user, request_key)).fetchone()
        if existing:
            if existing["digest"] != hashed:
                raise ValueError("同一幂等键不能用于不同内容，请生成新的请求键。")
            return dict(existing)
        identity = uuid.uuid4().hex
        db.execute("INSERT INTO actions(id,tenant,owner,request_key,kind,body,digest,expires) VALUES(?,?,?,?,?,?,?,?)",
                   (identity, actor.tenant, actor.user, request_key, kind, body, hashed, time.time() + 900))
        return dict(db.execute("SELECT * FROM actions WHERE id=?", (identity,)).fetchone())

# 目的：只列出当前读者的动作，让预览能够回查。
# 预期：越权、过期或错误摘要不会写入笔记；重复批准返回同一结果。
def pending(actor):
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM actions WHERE tenant=? AND owner=? ORDER BY rowid DESC", (actor.tenant, actor.user))]

# 目的：在同一事务内写笔记并标记完成，确认必须匹配当前版本和摘要。
# 预期：越权、过期或错误摘要不会写入笔记；重复批准返回同一结果。
def approve(actor, identity, revision, expected_digest, confirmed):
    if confirmed is not True:
        raise ValueError("未获得对当前草稿的明确确认。")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM actions WHERE id=? AND tenant=? AND owner=?", (identity, actor.tenant, actor.user)).fetchone()
        if row is None:
            raise PermissionError("草稿不存在或不属于本人。")
        if row["revision"] != revision or row["digest"] != expected_digest:
            raise ValueError("草稿已改变，请重新查看并确认。")
        if row["status"] == "committed":
            return {"id": identity, "status": "committed", "replayed": True}
        if row["expires"] < time.time():
            raise ValueError("确认已过期，请重新生成或修改草稿后确认。")
        # 写入业务记录和标记完成在同一个事务内；中途崩溃时不会只完成一半。
        db.execute("INSERT INTO notes(id,tenant,owner,kind,body,created) VALUES(?,?,?,?,?,?)", (identity, actor.tenant, actor.user, row["kind"], row["body"], time.time()))
        db.execute("UPDATE actions SET status='committed' WHERE id=?", (identity,))
    return {"id": identity, "status": "committed", "replayed": False}

# 目的：只读取已经批准后的正式笔记，不把 pending 草稿混进来。
# 预期：越权、过期或错误摘要不会写入笔记；重复批准返回同一结果。
def notes(actor):
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT id,kind,body,created FROM notes WHERE tenant=? AND owner=?", (actor.tenant, actor.user))]

# 目的：修改正文同时递增版本、更新摘要与有效期；旧确认不能批准新内容。
# 预期：旧 revision/digest 失败，新预览可以确认。
def revise(actor, identity, body):
    if not isinstance(body, str) or not 1 <= len(body.strip()) <= 6000:
        raise ValueError("草稿长度需为 1—6000 字符。")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM actions WHERE id=? AND tenant=? AND owner=? AND status='pending'", (identity, actor.tenant, actor.user)).fetchone()
        if row is None:
            raise PermissionError("没有可修改的本人草稿。")
        db.execute("UPDATE actions SET body=?,digest=?,revision=revision+1,expires=? WHERE id=?",
                   (body, digest([row["kind"], body]), time.time() + 900, identity))
        return dict(db.execute("SELECT * FROM actions WHERE id=?", (identity,)).fetchone())
