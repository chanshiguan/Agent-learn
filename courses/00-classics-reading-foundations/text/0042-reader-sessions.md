# 两位读者，不共用一段对话（1/5：保存会话状态）

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《让来源和错误都能看见（2/2：把本节能力连起来）》](0041-source-page-02.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 从临时页面走到持久会话

会话是一次连续阅读的容器，保存作品、最近对话和进度。它不是知识库，也不是模型重新训练。SQLite 是一个本地数据库文件；适合本课单实例练习，多副本和高并发另需设计。

先用 Ctrl+C 停止第 13 章服务，再启动加入会话的版本。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：先写这个文件需要的导入

先只保存阅读会话；批准、账号、反馈与限额表都留到对应章节创建。

**写在哪里：**项目根目录下的 `companion/state.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：先只保存阅读会话；批准、账号、反馈与限额表都留到对应章节创建。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import json
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from .files import data_dir
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 2 步：把调用者身份变成明确的数据

业务函数不从模型文字里推断读者；本章仅有本机虚构身份。

**写在哪里：**项目根目录下的 `companion/state.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 目的：业务函数不从模型文字里推断读者；本章仅有本机虚构身份。
# 预期：每次数据库操作都明确带 tenant 和 user。
@dataclass(frozen=True)
class Actor:
    tenant: str
    user: str
    role: str = "reader"
```

**写完后应当怎样：**每次数据库操作都明确带 tenant 和 user。

### 第 3 步：用一个连接入口统一提交与回滚

with 内成功才提交；发生错误回滚并关闭连接，避免锁住数据库。

**写在哪里：**项目根目录下的 `companion/state.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
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
```

**写完后应当怎样：**一次操作失败不会留下半次修改。

### 第 4 步：只创建本章需要的会话表

一行会话属于一个机构和一个读者；history 保存最近对话，revision 用于发现同时修改。

**写在哪里：**项目根目录下的 `companion/state.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：一行会话属于一个机构和一个读者；history 保存最近对话，revision 用于发现同时修改。
# 预期：此时库中只有 sessions，不会提前出现账号或审批表。
def initialize():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS sessions(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          book TEXT NOT NULL, history TEXT NOT NULL DEFAULT '[]',
          revision INTEGER NOT NULL DEFAULT 0);
        """)
        if db.execute("PRAGMA user_version").fetchone()[0] == 0:
            db.execute("PRAGMA user_version=1")
```

**写完后应当怎样：**此时库中只有 sessions，不会提前出现账号或审批表。

### 第 5 步：实现 get_session()

同时按 id、tenant 和 owner 查询，知道别人的会话 ID 也拿不到正文。

**写在哪里：**项目根目录下的 `companion/state.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
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
```

**写完后应当怎样：**会话操作只影响当前读者。

### 第 6 步：实现 create_session()

由程序生成不可猜的会话 ID，并明确写入归属和作品。

**写在哪里：**项目根目录下的 `companion/state.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：由程序生成不可猜的会话 ID，并明确写入归属和作品。
# 预期：会话操作只影响当前读者。
def create_session(actor, book="狂人日记"):
    identity = uuid.uuid4().hex
    with connect() as db:
        db.execute("INSERT INTO sessions(id,tenant,owner,book) VALUES(?,?,?,?)", (identity, actor.tenant, actor.user, book))
    return get_session(actor, identity)
```

**写完后应当怎样：**会话操作只影响当前读者。

### 第 7 步：实现 delete_session()

删除同样带本人范围，不能只根据任意 ID 操作。

**写在哪里：**项目根目录下的 `companion/state.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：删除同样带本人范围，不能只根据任意 ID 操作。
# 预期：会话操作只影响当前读者。
def delete_session(actor, identity):
    with connect() as db:
        db.execute("DELETE FROM sessions WHERE id=? AND tenant=? AND owner=?", (identity, actor.tenant, actor.user))
```

**写完后应当怎样：**会话操作只影响当前读者。

### 第 8 步：只列出当前读者自己的会话摘要

列表不需要返回所有对话正文，先少拿数据再展示。

**写在哪里：**项目根目录下的 `companion/state.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：列表不需要返回所有对话正文，先少拿数据再展示。
# 预期：切换读者后列表不会混在一起。
def list_sessions(actor):
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT id,book,revision FROM sessions WHERE tenant=? AND owner=?", (actor.tenant,actor.user))]
```

**写完后应当怎样：**切换读者后列表不会混在一起。

### 第 9 步：用旧版本号防止互相覆盖

两个请求读到相同版本，只允许先完成的一次更新成功；另一次重新读取再决定。

**写在哪里：**项目根目录下的 `companion/state.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：两个请求读到相同版本，只允许先完成的一次更新成功；另一次重新读取再决定。
# 预期：旧版本写入抛出 ValueError，而不静默覆盖新对话。
def update_session(actor, session, history=None):
    with connect() as db:
        cursor=db.execute("UPDATE sessions SET history=?,revision=revision+1 WHERE id=? AND tenant=? AND owner=? AND revision=?",
                          (json.dumps(session["history"] if history is None else history,ensure_ascii=False),session["id"],actor.tenant,actor.user,session["revision"]))
        if cursor.rowcount != 1:
            raise ValueError("会话已改变，请重新读取。")
    return get_session(actor,session["id"])
```

**写完后应当怎样：**旧版本写入抛出 ValueError，而不静默覆盖新对话。

### 第 10 步：先写这个文件需要的导入

让 API 与会话问答共用一条业务路径；本节只处理普通问答。

**写在哪里：**项目根目录下的 `companion/service.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：让 API 与会话问答共用一条业务路径；本节只处理普通问答。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
from .rag import retrieve, answer
from .state import get_session, update_session
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 11 步：把当前会话的最近对话带入回答

先查归属，再检索当前作品，最后使用版本号保存；身份不能交给模型决定。

**写在哪里：**项目根目录下的 `companion/service.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：先查归属，再检索当前作品，最后使用版本号保存；身份不能交给模型决定。
# 预期：回答后 history 最多保留两轮，返回新 revision 供下一次更新使用。
def ask(actor, session_id, question, request_id, mode="qa", method="keyword"):
    if mode != "qa":
        raise ValueError("本阶段只实现普通问答。")
    session=get_session(actor,session_id)
    hits=retrieve(question,actor.tenant,session["book"],method)
    result=answer(question,hits,session["history"])
    history=(session["history"]+[{"role":"user","content":question},{"role":"assistant","content":result["answer"]}])[-4:]
    updated=update_session(actor,session,history=history)
    return {**result,"trace_id":request_id,"session_revision":updated["revision"]}
```

**写完后应当怎样：**回答后 history 最多保留两轮，返回新 revision 供下一次更新使用。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/state.py companion/service.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

先查归属，再检索当前作品，最后使用版本号保存；身份不能交给模型决定。 回答后 history 最多保留两轮，返回新 revision 供下一次更新使用。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter9)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
