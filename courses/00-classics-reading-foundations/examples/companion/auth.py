"""账号由管理员创建，口令只保存派生值，访问令牌只保存摘要。"""
import hashlib
import hmac
import re
import secrets
import time

from .state import Actor, connect


def password_value(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600_000).hex()


def create_user(tenant, username, password, role="reader"):
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}", tenant) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}", username):
        raise ValueError("租户和账号使用 1—40 位字母、数字、下划线或连字符。")
    if not 12 <= len(password) <= 128 or role not in {"reader", "parent", "content_admin"}:
        raise ValueError("口令需要 12—128 字符，并选择有效角色。")
    salt = secrets.token_hex(16)
    with connect() as db:
        db.execute("INSERT INTO users(tenant,username,role,salt,password_hash) VALUES(?,?,?,?,?)",
                   (tenant, username, role, salt, password_value(password, salt)))


def login(tenant, username, password, peer):
    now = time.time()
    # 两个桶分别限制同一来源和同一账号，避免只换用户名或只换地址就无限尝试。
    buckets = [hashlib.sha256(f"peer:{peer}".encode()).hexdigest(), hashlib.sha256(f"user:{tenant}:{username}".encode()).hexdigest()]
    with connect() as db:
        db.execute("CREATE TABLE IF NOT EXISTS login_attempts(bucket TEXT, at REAL)")
        db.execute("BEGIN IMMEDIATE")
        db.execute("DELETE FROM login_attempts WHERE at < ?", (now - 300,))
        for bucket in buckets:
            count = db.execute("SELECT count(*) FROM login_attempts WHERE bucket=?", (bucket,)).fetchone()[0]
            if count >= 10:
                raise PermissionError("暂时无法登录，请稍后再试。")
        for bucket in buckets:
            db.execute("INSERT INTO login_attempts VALUES(?,?)", (bucket, now))
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE tenant=? AND username=?", (tenant, username)).fetchone()
    salt = row["salt"] if row else "0" * 32
    expected = row["password_hash"] if row else "0" * 64
    actual = password_value(password, salt)
    if not row or row["disabled"] or not hmac.compare_digest(actual, expected):
        raise PermissionError("账号或口令不正确。")
    token = secrets.token_urlsafe(32)
    with connect() as db:
        db.execute("INSERT INTO tokens VALUES(?,?,?,?)", (hashlib.sha256(token.encode()).hexdigest(), tenant, username, now + 3600))
    return {"access_token": token, "expires_in": 3600, "role": row["role"]}


def authenticate(token):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with connect() as db:
        row = db.execute("""SELECT u.tenant,u.username,u.role FROM tokens t JOIN users u
          ON t.tenant=u.tenant AND t.username=u.username
          WHERE t.digest=? AND t.expires>? AND u.disabled=0""", (token_hash, time.time())).fetchone()
    if not row:
        raise PermissionError("登录已过期或无效，请重新登录。")
    return Actor(row["tenant"], row["username"], row["role"])


def logout(token):
    with connect() as db:
        db.execute("DELETE FROM tokens WHERE digest=?", (hashlib.sha256(token.encode()).hexdigest(),))


def link_family(tenant, parent, child):
    with connect() as db:
        roles = dict(db.execute("SELECT username,role FROM users WHERE tenant=? AND username IN (?,?)", (tenant, parent, child)).fetchall())
        if roles.get(parent) != "parent" or roles.get(child) != "reader":
            raise ValueError("先创建本租户家长和读者账号。管理员应在线下核对关联关系。")
        db.execute("INSERT OR IGNORE INTO families VALUES(?,?,?)", (tenant, parent, child))
