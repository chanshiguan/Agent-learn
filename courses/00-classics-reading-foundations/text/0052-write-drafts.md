# 先预览一份笔记，确认后再保存（1/3：保存会话状态）

本单元预计 **55—70 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《比较固定 RAG 与 Agent，练习及时停止》](0051-agent-stopping.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 先分清草稿和正式笔记

模型产出文字后，读者还没看过它。先保存在 actions 表里，状态是 pending；只有读者核对具体内容、版本和摘要并确认后，才写入 notes。复习计划也遵守相同流程，不自动改日历或阅读进度。

## 写完后检查预览与批准


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：创建 actions 表

只在能力需要时增加这张表，已有会话继续保留。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
          revision INTEGER NOT NULL DEFAULT 0);
```

</details>

**先理解：**建表语句描述需要保存的字段；已有表不会因重复初始化而清空。增加列与修改已有记录是两种操作。

```python
          revision INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS actions(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          request_key TEXT NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL,
          digest TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1,
          expires REAL NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
          UNIQUE(tenant,owner,request_key));
```

**写完后应当怎样：**重启服务调用 initialize 后新表存在，重复执行不会清空数据。

### 第 2 步：创建 notes 表

只在能力需要时增加这张表，已有会话继续保留。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
          UNIQUE(tenant,owner,request_key));
```

</details>

**先理解：**建表语句描述需要保存的字段；已有表不会因重复初始化而清空。增加列与修改已有记录是两种操作。

```python
          UNIQUE(tenant,owner,request_key));
        CREATE TABLE IF NOT EXISTS notes(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          kind TEXT NOT NULL, body TEXT NOT NULL, created REAL NOT NULL);
```

**写完后应当怎样：**重启服务调用 initialize 后新表存在，重复执行不会清空数据。

### 第 3 步：先写这个文件需要的导入

草稿预览与正式笔记分开保存，批准必须绑定本人、内容和版本。

**写在哪里：**项目根目录下的 `companion/actions.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：草稿预览与正式笔记分开保存，批准必须绑定本人、内容和版本。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import time
import uuid
from .files import digest
from .state import connect
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 4 步：写 draft() 的边界

生成草稿不等于保存笔记；请求键防止重复生成同一动作。

**写在哪里：**项目根目录下的 `companion/actions.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
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
```

**写完后应当怎样：**越权、过期或错误摘要不会写入笔记；重复批准返回同一结果。

### 第 5 步：写 pending() 的边界

只列出当前读者的动作，让预览能够回查。

**写在哪里：**项目根目录下的 `companion/actions.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：只列出当前读者的动作，让预览能够回查。
# 预期：越权、过期或错误摘要不会写入笔记；重复批准返回同一结果。
def pending(actor):
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM actions WHERE tenant=? AND owner=? ORDER BY rowid DESC", (actor.tenant, actor.user))]
```

**写完后应当怎样：**越权、过期或错误摘要不会写入笔记；重复批准返回同一结果。

### 第 6 步：写 approve() 的边界

在同一事务内写笔记并标记完成，确认必须匹配当前版本和摘要。

**写在哪里：**项目根目录下的 `companion/actions.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
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
```

**写完后应当怎样：**越权、过期或错误摘要不会写入笔记；重复批准返回同一结果。

### 第 7 步：写 notes() 的边界

只读取已经批准后的正式笔记，不把 pending 草稿混进来。

**写在哪里：**项目根目录下的 `companion/actions.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：只读取已经批准后的正式笔记，不把 pending 草稿混进来。
# 预期：越权、过期或错误摘要不会写入笔记；重复批准返回同一结果。
def notes(actor):
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT id,kind,body,created FROM notes WHERE tenant=? AND owner=?", (actor.tenant, actor.user))]
```

**写完后应当怎样：**越权、过期或错误摘要不会写入笔记；重复批准返回同一结果。

### 第 8 步：复用当前阅读对话生成草稿

模型只生成内容，真正写入由后面的批准接口执行。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .agent import run_agent
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .agent import run_agent
from . import actions
from .models import complete
```

**写完后应当怎样：**生成完成后仍处于待确认状态。

### 第 9 步：根据当前对话整理待确认内容

生成前取本人会话，写草稿时再次检查会话还存在，避免读者删除后又留下内容。

**写在哪里：**项目根目录下的 `companion/service.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：生成前取本人会话，写草稿时再次检查会话还存在，避免读者删除后又留下内容。
# 预期：得到的是待确认草稿，不会自动变成正式笔记。
def make_draft(actor, session_id, kind, request_id):
    existing = next((a for a in actions.pending(actor) if a["request_key"] == request_id), None)
    if existing:
        return existing
    session = get_session(actor, session_id)
    if session["strict"] or not session["history"]:
        raise ValueError("当前没有可整理的普通阅读对话；受限模式下请手动写笔记。")
    task = "一份简短阅读笔记" if kind == "note" else "一份三次复习计划草稿，日期由读者确认"
    response = complete([{"role": "system", "content": f"依据当前对话整理{task}。只写草稿，不声称已经保存或改变进度。不补充对话之外的事实。"}, *session["history"]])
    # 供应商可能已完成响应，但取消后的结果不再写入读者的待确认区。
    body = response["message"].get("content") or ""
    return actions.draft(actor, kind, body, request_id, session_id=session_id)
```

**写完后应当怎样：**得到的是待确认草稿，不会自动变成正式笔记。

### 第 10 步：接入草稿存储模块

接口不自己拼批准 SQL，统一复用事务边界。

**写在哪里：**项目根目录下的 `companion/app.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from . import service, state
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from . import service, state, actions
```

**写完后应当怎样：**页面与命令行以后共用同一批准行为。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/state.py companion/actions.py companion/service.py companion/app.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

接口不自己拼批准 SQL，统一复用事务边界。 页面与命令行以后共用同一批准行为。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/03-tool-use-and-hello-agent.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
