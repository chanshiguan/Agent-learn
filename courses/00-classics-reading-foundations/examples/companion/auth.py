# 目的：把本机虚构身份换成登录后得到的身份；口令与令牌都不以明文存入数据库。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import hashlib
import hmac
import re
import secrets
import time
from .state import Actor, connect

# 目的：用带盐的慢派生计算处理口令，不能直接保存或比较明文口令。
# 预期：请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。
def password_value(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600_000).hex()

# 目的：管理员创建账号时检查机构、用户名、角色和口令范围。
# 预期：请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。
def create_user(tenant, username, password, role="reader"):
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}", tenant) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}", username):
        raise ValueError("租户和账号使用 1—40 位字母、数字、下划线或连字符。")
    if not 12 <= len(password) <= 128 or role not in {"reader", "parent", "content_admin"}:
        raise ValueError("口令需要 12—128 字符，并选择有效角色。")
    salt = secrets.token_hex(16)
    with connect() as db:
        db.execute("INSERT INTO users(tenant,username,role,salt,password_hash) VALUES(?,?,?,?,?)",
                   (tenant, username, role, salt, password_value(password, salt)))

# 目的：限制来源与账号的尝试次数，验证后只发短期随机令牌。
# 预期：请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。
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

# 目的：通过令牌摘要、有效期和账号状态重新取得服务端身份。
# 预期：请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。
def authenticate(token):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with connect() as db:
        row = db.execute("""SELECT u.tenant,u.username,u.role FROM tokens t JOIN users u
          ON t.tenant=u.tenant AND t.username=u.username
          WHERE t.digest=? AND t.expires>? AND u.disabled=0""", (token_hash, time.time())).fetchone()
    if not row:
        raise PermissionError("登录已过期或无效，请重新登录。")
    return Actor(row["tenant"], row["username"], row["role"])

# 目的：退出时删除服务端令牌摘要，而不只是隐藏页面。
# 预期：请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。
def logout(token):
    with connect() as db:
        db.execute("DELETE FROM tokens WHERE digest=?", (hashlib.sha256(token.encode()).hexdigest(),))

# 目的：家长角色不能自动查看任意孩子；管理员还需要在线下核实关系。
# 预期：只有已关联的家长能读取该孩子的显式进度。
def link_family(tenant, parent, child):
    with connect() as db:
        roles = dict(db.execute("SELECT username,role FROM users WHERE tenant=? AND username IN (?,?)", (tenant, parent, child)).fetchall())
        if roles.get(parent) != "parent" or roles.get(child) != "reader":
            raise ValueError("先创建本租户家长和读者账号。管理员应在线下核对关联关系。")
        db.execute("INSERT OR IGNORE INTO families VALUES(?,?,?)", (tenant, parent, child))
