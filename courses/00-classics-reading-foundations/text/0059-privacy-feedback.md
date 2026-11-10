# 让反馈与删除都有明确范围

本单元预计 **70—85 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《讲稿里的命令不能控制助手》](0058-untrusted-input.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：创建 feedback 表

只在能力需要时增加这张表，已有会话继续保留。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
          PRIMARY KEY(tenant,parent,child));
```

</details>

**先理解：**建表语句描述需要保存的字段；已有表不会因重复初始化而清空。增加列与修改已有记录是两种操作。

```python
          PRIMARY KEY(tenant,parent,child));
        CREATE TABLE IF NOT EXISTS feedback(
          id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL,
          category TEXT NOT NULL, trace_id TEXT NOT NULL, created REAL NOT NULL);
```

**写完后应当怎样：**重启服务调用 initialize 后新表存在，重复执行不会清空数据。

### 第 2 步：删除时同时核对保存的预览

待确认正文可能存在业务表与图检查点两个位置，删除不能遗漏副本。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .files import data_dir
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .files import data_dir, load
```

**写完后应当怎样：**预览只在属于本人时移除。

### 第 3 步：在同一锁内清理本人内容与检查点

删除与图写入竞争时必须串行，避免刚报告删除成功就由迟到任务写回。

**写在哪里：**项目根目录下的 `companion/state.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
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
```

**写完后应当怎样：**当前业务库内容与令牌清除；账号、备份与额度留存范围明确说明。

### 第 4 步：记录反馈的接收时间

反馈只保存分类、追踪编号和接收时间，不默认复制问题全文。

**写在哪里：**项目根目录下的 `companion/app.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
import os
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
import os
import time
```

**写完后应当怎样：**可以回查反馈发生时间而不扩散私人内容。

### 第 5 步：增加 Feedback 接口

所有入口复用已认证身份；删除说明当前业务库范围，不能声称远端备份同步消失。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**category 限定反馈类型，trace_id 让维护者找到相关请求。这里故意不收集完整对话正文，以减少反馈处理中额外保存的个人内容。

```python
# 目的：所有入口复用已认证身份；删除说明当前业务库范围，不能声称远端备份同步消失。
# 预期：反馈返回回执，删除撤销令牌并清空当前个人内容。
class Feedback(Input):
    category: Literal["答非所问", "证据不符", "内容不适合", "其他"]
    trace_id: str = Field(pattern=r"^[a-f0-9]{32}$")
```

**写完后应当怎样：**反馈返回回执，删除撤销令牌并清空当前个人内容。

### 第 6 步：增加 feedback 接口

所有入口复用已认证身份；删除说明当前业务库范围，不能声称远端备份同步消失。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：所有入口复用已认证身份；删除说明当前业务库范围，不能声称远端备份同步消失。
# 预期：反馈返回回执，删除撤销令牌并清空当前个人内容。
@app.post("/api/feedback")
def feedback(body: Feedback, who=Depends(actor)):
    identity = uuid.uuid4().hex
    with state.connect() as db:
        db.execute("INSERT INTO feedback VALUES(?,?,?,?,?,?)", (identity, who.tenant, who.user, body.category, body.trace_id, time.time()))
    return {"receipt": identity}
```

**写完后应当怎样：**反馈返回回执，删除撤销令牌并清空当前个人内容。

### 第 7 步：增加 erase 接口

所有入口复用已认证身份；删除说明当前业务库范围，不能声称远端备份同步消失。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：所有入口复用已认证身份；删除说明当前业务库范围，不能声称远端备份同步消失。
# 预期：反馈返回回执，删除撤销令牌并清空当前个人内容。
@app.delete("/api/personal-data")
def erase(who=Depends(actor)):
    return state.erase_personal_data(who)
```

**写完后应当怎样：**反馈返回回执，删除撤销令牌并清空当前个人内容。

### 第 8 步：让反馈有分类，不默认收集全文

先提交最少信息，必要的人工调查再按明确授权取得上下文。

**写在哪里：**项目根目录下的 `companion/web/index.html`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```html
        <div id="sources"></div>
```

</details>

**先理解：**标签确定页面结构，id 让后面的 JavaScript 找到同一个控件。label 关联输入框；hidden 只是隐藏显示，不负责服务端权限。

```html
        <div id="sources"></div>
        <label for="category">反馈类型</label
        ><select id="category">
          <option>答非所问</option>
          <option>证据不符</option>
          <option>内容不适合</option>
          <option>其他</option></select
        ><button id="feedback">提交反馈</button>
```

**写完后应当怎样：**每次反馈得到回执，不把用户问题塞进 URL。

### 第 9 步：让删除范围在动作前可见

危险动作先确认，服务器完成后清理页面身份。

**写在哪里：**项目根目录下的 `companion/web/index.html`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```html
      </section>
```

</details>

**先理解：**标签确定页面结构，id 让后面的 JavaScript 找到同一个控件。label 关联输入框；hidden 只是隐藏显示，不负责服务端权限。

```html
      </section>
      <button id="erase">删除我的个人阅读内容</button>
```

**写完后应当怎样：**删除后退出，后续访问需重新登录。

### 第 10 步：连接 feedback 动作

操作前后检查当前视图，读者切换后丢弃旧结果。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
on('feedback', async () => {
  if (!lastTrace) throw new Error('请先获得一次回答。');
  const expectedView = viewVersion;
  const result = await api('/api/feedback', 'POST', {
    category: $('category').value,
    trace_id: lastTrace,
  });
  if (viewVersion === expectedView)
    status('反馈已记录，回执 ' + result.receipt.slice(0, 8));
});
```

**写完后应当怎样：**页面提示真实结果，不残留旧身份数据。

### 第 11 步：连接 erase 动作

操作前后检查当前视图，读者切换后丢弃旧结果。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
on('erase', async () => {
  if (!confirm('删除当前业务库中自己的阅读记录、笔记和待确认草稿，并退出登录？'))
    return;
  const expectedView = viewVersion;
  const result = await api('/api/personal-data', 'DELETE');
  if (viewVersion !== expectedView) return;
  token = '';
  reset();
  $('workspace').hidden = true;
  $('login-panel').hidden = false;
  $('logout').hidden = true;
  status(result.scope);
});
```

**写完后应当怎样：**页面提示真实结果，不残留旧身份数据。

## 让刚写的代码生效

如果上一节的服务仍在运行，先在那个终端按 Ctrl+C 停止。确认当前终端仍有模型配置，再从项目根目录重启，随后刷新浏览器。没有使用自动重载时，仅保存文件不会更新运行中的 Python 进程。

```bash
# 载入刚写完的接口、业务模块和页面；等终端显示服务启动后再进行下面的交互。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```


## 先少收，再谈怎样保护

当前账号用虚构标识；反馈只保存类别、请求 trace_id 与归属，不自动收集学生姓名、学校或整段对话。反馈用于人工处理，不能一收到就让模型自动改知识库。

在 authenticated 模式用测试账号提交一次“证据不符”反馈，记下回执。再生成一条测试笔记与一份待确认草稿，最后点“删除我的个人阅读内容”。预期会话、笔记、动作、反馈与令牌被删除，流程检查点中本人的草稿也清除。

账号本身与当日限额计数仍保留，防止反复删除绕过请求额度；旧日期计数在后续请求时清理。删除入口不是完整注销账号；共享讲稿不会删除。重新登录后个人内容应为空。备份里的旧内容不会因在线库删除自动消失，留存与恢复后重放删除清单在第 28 章处理。


验证检查点删除后不能再恢复旧动作；使用临时数据库，不动实际学习笔记。


## 给公司准备一张待确认清单

写清谁负责资料授权、适龄内容审核、家长关联核实、隐私告知、保留时长、删除请求和人工反馈处理。这里是产品与组织决策，不由教程替公司认定法律适用性。

对“吃人”等作品讨论，测试表达是否在文学语境中、是否不必要地渲染、是否提示适当共同讨论。不要简单屏蔽一个词就让整部作品无法学习，也不要声称自动审核已经替代老师或内容负责人。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 删除个人阅读内容等于删除账号吗？
2. 为什么在线删除后还要处理备份？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**删除个人阅读内容等于删除账号吗？**

不是。当前删除会话、笔记、动作、反馈和令牌，保留账号、当日限额计数与共享讲稿；注销账号需要另外的生命周期流程。

**为什么在线删除后还要处理备份？**

旧备份可能保留已删除内容。恢复时需要重放删除清单，备份到期也要按留存安排清除。

**通过证据：**反馈回执、删除前后内容对照与检查点不可恢复结果；公司待确认项有负责角色。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion import state,actions
state.initialize();a=state.Actor("demo","erase-test")
s=state.create_session(a);actions.draft(a,"note","待删除内容","erase-test")
state.erase_personal_data(a)
assert not state.list_sessions(a) and not actions.pending(a)
print("当前个人内容已删除；备份不在本测试范围")
PY
```

**预期：**业务内容删除完成，未把账号和备份一并宣称删除。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
