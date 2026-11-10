# 从测试身份切到登录账号（1/3：保存会话状态）

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《用状态图重现同一个批准流程（2/2：把本节能力连起来）》](0055-langgraph-checkpoint-02.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 先确认是谁，再判断能做什么

认证回答“你是谁”，授权回答“你能读写哪些内容”。之前有授权检查但身份可由测试请求头选择，这次换成登录后签发的短期令牌。口令不存明文，令牌在数据库也只存摘要。

先关闭服务。以下使用虚构账号，不录入真实学生姓名；输入口令时终端不回显，避免口令出现在命令历史。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：创建 users 表

只在能力需要时增加这张表，已有会话继续保留。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
          kind TEXT NOT NULL, body TEXT NOT NULL, created REAL NOT NULL);
```

</details>

**先理解：**建表语句描述需要保存的字段；已有表不会因重复初始化而清空。增加列与修改已有记录是两种操作。

```python
          kind TEXT NOT NULL, body TEXT NOT NULL, created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS users(
          tenant TEXT NOT NULL, username TEXT NOT NULL, role TEXT NOT NULL,
          salt TEXT NOT NULL, password_hash TEXT NOT NULL, disabled INTEGER NOT NULL DEFAULT 0,
          PRIMARY KEY(tenant,username));
```

**写完后应当怎样：**重启服务调用 initialize 后新表存在，重复执行不会清空数据。

### 第 2 步：创建 tokens 表

只在能力需要时增加这张表，已有会话继续保留。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
          PRIMARY KEY(tenant,username));
```

</details>

**先理解：**建表语句描述需要保存的字段；已有表不会因重复初始化而清空。增加列与修改已有记录是两种操作。

```python
          PRIMARY KEY(tenant,username));
        CREATE TABLE IF NOT EXISTS tokens(
          digest TEXT PRIMARY KEY, tenant TEXT NOT NULL, username TEXT NOT NULL, expires REAL NOT NULL);
```

**写完后应当怎样：**重启服务调用 initialize 后新表存在，重复执行不会清空数据。

### 第 3 步：创建 families 表

只在能力需要时增加这张表，已有会话继续保留。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
          digest TEXT PRIMARY KEY, tenant TEXT NOT NULL, username TEXT NOT NULL, expires REAL NOT NULL);
```

</details>

**先理解：**建表语句描述需要保存的字段；已有表不会因重复初始化而清空。增加列与修改已有记录是两种操作。

```python
          digest TEXT PRIMARY KEY, tenant TEXT NOT NULL, username TEXT NOT NULL, expires REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS families(
          tenant TEXT NOT NULL, parent TEXT NOT NULL, child TEXT NOT NULL,
          PRIMARY KEY(tenant,parent,child));
```

**写完后应当怎样：**重启服务调用 initialize 后新表存在，重复执行不会清空数据。

### 第 4 步：先写这个文件需要的导入

把本机虚构身份换成登录后得到的身份；口令与令牌都不以明文存入数据库。

**写在哪里：**项目根目录下的 `companion/auth.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：把本机虚构身份换成登录后得到的身份；口令与令牌都不以明文存入数据库。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import hashlib
import hmac
import re
import secrets
import time
from .state import Actor, connect
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 5 步：实现 password_value 的认证职责

用带盐的慢派生计算处理口令，不能直接保存或比较明文口令。

**写在哪里：**项目根目录下的 `companion/auth.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：用带盐的慢派生计算处理口令，不能直接保存或比较明文口令。
# 预期：请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。
def password_value(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600_000).hex()
```

**写完后应当怎样：**请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。

### 第 6 步：实现 create_user 的认证职责

管理员创建账号时检查机构、用户名、角色和口令范围。

**写在哪里：**项目根目录下的 `companion/auth.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
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
```

**写完后应当怎样：**请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。

### 第 7 步：实现 login 的认证职责

限制来源与账号的尝试次数，验证后只发短期随机令牌。

**写在哪里：**项目根目录下的 `companion/auth.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
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
```

**写完后应当怎样：**请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。

### 第 8 步：实现 authenticate 的认证职责

通过令牌摘要、有效期和账号状态重新取得服务端身份。

**写在哪里：**项目根目录下的 `companion/auth.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
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
```

**写完后应当怎样：**请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。

### 第 9 步：实现 logout 的认证职责

退出时删除服务端令牌摘要，而不只是隐藏页面。

**写在哪里：**项目根目录下的 `companion/auth.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：退出时删除服务端令牌摘要，而不只是隐藏页面。
# 预期：请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。
def logout(token):
    with connect() as db:
        db.execute("DELETE FROM tokens WHERE digest=?", (hashlib.sha256(token.encode()).hexdigest(),))
```

**写完后应当怎样：**请求头中的虚构读者不再影响已登录身份；无效或过期令牌被拒绝。

### 第 10 步：从终端创建账号，不把口令放进历史

getpass 交互输入不会把口令写在命令行参数中；结果只显示账号和角色。

**写在哪里：**项目根目录下的 `companion/accounts_cli.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

```python
# 目的：getpass 交互输入不会把口令写在命令行参数中；结果只显示账号和角色。
# 预期：可以创建测试读者，数据库只保存盐与派生值。
import argparse
import getpass
import json
from .auth import create_user
from .state import initialize


def main(kind="create-user"):
    parser=argparse.ArgumentParser(description="管理员创建试用账号")
    parser.add_argument("username")
    parser.add_argument("--tenant",default="demo")
    parser.add_argument("--role",choices=["reader","parent","content_admin"],default="reader")
    args=parser.parse_args();initialize()
    password=getpass.getpass("设置至少12字符的口令（不回显）：")
    if password!=getpass.getpass("再次输入："):raise ValueError("两次口令不同。")
    create_user(args.tenant,args.username,password,args.role)
    print(json.dumps({"created":args.username,"role":args.role},ensure_ascii=False))
```

**写完后应当怎样：**可以创建测试读者，数据库只保存盐与派生值。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/state.py companion/auth.py companion/accounts_cli.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

getpass 交互输入不会把口令写在命令行参数中；结果只显示账号和角色。 可以创建测试读者，数据库只保存盐与派生值。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
