# 让记忆可以被查看、修正和删除

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《两位读者，不共用一段对话（5/5：连接页面交互）》](0042-reader-sessions-05.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 不要从聊天里偷偷推断读到哪里

“我知道结尾”不代表读者愿意开放全部剧情。进度应由读者明确设置。对本课程，进度数字表示你人工定义的阅读范围，不自动对应讲次或原著页码。第 15 章才把它绑定到核对过的片段。

当前会话只保留最近两轮普通问答，防止上下文无限增长；它不是完整聊天归档。页面暂不展示历史列表，数据库中的 history 用于下一轮请求。隐含偏好不自动写成长久记忆。

## 做一次可逆的状态实验

创建两次阅读，分别提问。关闭服务，用编辑器以只读方式查看数据库或运行下面的查询；不要把真实读者对话复制到公开工单。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：给已有会话补充显式进度与伴读状态

旧数据库已经有会话，不能重新建一个空库掩盖升级问题。先查列名，再补缺少的列。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        """)
```

</details>

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
        """)
        columns={row[1] for row in db.execute("PRAGMA table_info(sessions)")}
        for name, definition in {"progress":"INTEGER NOT NULL DEFAULT 0","strict":"INTEGER NOT NULL DEFAULT 0","phase":"TEXT NOT NULL DEFAULT 'question'"}.items():
            if name not in columns:
                db.execute(f"ALTER TABLE sessions ADD COLUMN {name} {definition}")
```

**写完后应当怎样：**旧会话仍存在，新增字段使用默认值。

### 第 2 步：让进度、范围和状态都受版本检查

修改进度也是写操作；与对话一样需要知道页面拿的是哪个版本。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
def update_session(actor, session, history=None):
```

</details>

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
def update_session(actor, session, history=None, progress=None, strict=None, phase=None):
```

**写完后应当怎样：**旧页面写入被拒绝，新页面更新后返回递增 revision。

### 第 3 步：让进度、范围和状态都受版本检查

修改进度也是写操作；与对话一样需要知道页面拿的是哪个版本。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        cursor=db.execute("UPDATE sessions SET history=?,revision=revision+1 WHERE id=? AND tenant=? AND owner=? AND revision=?",
                          (json.dumps(session["history"] if history is None else history,ensure_ascii=False),session["id"],actor.tenant,actor.user,session["revision"]))
```

</details>

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
        # 乐观版本检查防止两次并发提问互相覆盖；冲突时由页面提示重新读取。
        cursor = db.execute("""UPDATE sessions SET history=?,progress=?,strict=?,phase=?,revision=revision+1
          WHERE id=? AND tenant=? AND owner=? AND revision=?""",
          (json.dumps(session["history"] if history is None else history, ensure_ascii=False),
           session["progress"] if progress is None else progress,
           session["strict"] if strict is None else int(strict), phase or session["phase"],
           session["id"], actor.tenant, actor.user, session["revision"]))
```

**写完后应当怎样：**旧页面写入被拒绝，新页面更新后返回递增 revision。

### 第 4 步：让进度、范围和状态都受版本检查

修改进度也是写操作；与对话一样需要知道页面拿的是哪个版本。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
            raise ValueError("会话已改变，请重新读取。")
    return get_session(actor,session["id"])
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
            raise ValueError("会话已被另一请求修改，请重新读取后再试。")
    return get_session(actor, session["id"])
```

**写完后应当怎样：**旧页面写入被拒绝，新页面更新后返回递增 revision。

### 第 5 步：让列表显示可核对的阅读进度

列表展示显式字段，不根据模型回答猜读到哪里。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        return [dict(r) for r in db.execute("SELECT id,book,revision FROM sessions WHERE tenant=? AND owner=?", (actor.tenant,actor.user))]
```

</details>

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
        return [dict(r) for r in db.execute("SELECT id,book,progress,strict,phase,revision FROM sessions WHERE tenant=? AND owner=?", (actor.tenant, actor.user))]
```

**写完后应当怎样：**重新进入页面能看到自己保存的进度。

### 第 6 步：写进度输入与更新入口

请求带上页面读到的 revision；范围改变时清空旧对话，防止后文残留。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**revision 是页面上次读到的会话版本。将它连同新的 progress 和 strict 发送，服务端才能发现另一个请求已改变会话，拒绝用旧页面覆盖新状态。

```python
# 目的：请求带上页面读到的 revision；范围改变时清空旧对话，防止后文残留。
# 预期：旧 revision 返回 409，成功写入返回新版本。
class Progress(Input):
    progress: int = Field(ge=0, le=10000)
    strict: bool
    revision: int = Field(ge=0)
```

**写完后应当怎样：**旧 revision 返回 409，成功写入返回新版本。

### 第 7 步：写进度输入与更新入口

请求带上页面读到的 revision；范围改变时清空旧对话，防止后文残留。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：请求带上页面读到的 revision；范围改变时清空旧对话，防止后文残留。
# 预期：旧 revision 返回 409，成功写入返回新版本。
@app.patch("/api/sessions/{identity}")
def progress(identity: str, body: Progress, who=Depends(actor)):
    current = state.get_session(who, identity)
    # 用页面实际读到的版本比较，才能拒绝后来到达的旧页面更新。
    if current["revision"] != body.revision:
        raise ValueError("阅读记录已更新，请重新打开当前记录后再保存进度。")
    # 进度或模式改变时丢弃旧上下文，避免旧对话把后文带进受限阅读。
    return state.update_session(who, current, history=[], progress=body.progress, strict=body.strict, phase="question")
```

**写完后应当怎样：**旧 revision 返回 409，成功写入返回新版本。

### 第 8 步：让读者明确填写进度

进度来自读者确认，当前 checkbox 先保存选择，下一章才连接真正过滤。

**写在哪里：**项目根目录下的 `companion/web/index.html`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```html
      <p id="selected">先选择或创建一次阅读。</p>
```

</details>

**先理解：**标签确定页面结构，id 让后面的 JavaScript 找到同一个控件。label 关联输入框；hidden 只是隐藏显示，不负责服务端权限。

```html
      <p id="selected">先选择或创建一次阅读。</p>
      <label for="progress">已核对的阅读进度编号</label>
      <input id="progress" type="number" min="0" max="10000" value="0" />
      <label><input id="strict" type="checkbox" />只看核对范围（下一章接入过滤）</label>
      <button id="save-progress">保存范围</button>
```

**写完后应当怎样：**可以保存数字并刷新回查；本节不宣称已经防剧透。

### 第 9 步：选择会话时恢复明确的进度字段

不把页面旧值留给新会话；来源必须是当前选中会话。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
    '当前阅读：' + selected.book + ' · ' + identity.slice(0, 6);
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
    '当前阅读：' + selected.book + ' · ' + identity.slice(0, 6);
  $('progress').value = selected.progress;
  $('strict').checked = Boolean(selected.strict);
```

**写完后应当怎样：**切换会话后进度显示跟着会话变化。

### 第 10 步：把页面读到的版本随进度提交

缺少这个版本，服务器无法识别迟到的旧页面更新。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
on('save-progress', async () => {
  requireSession();
  const expectedView = ++viewVersion;
  const current = await api('/api/sessions/' + selected.id, 'PATCH', {
    progress: Number($('progress').value),
    strict: $('strict').checked,
    revision: selected.revision,
  });
  if (viewVersion !== expectedView) return;
  selected = current;
  $('result').hidden = true;
  status('阅读范围已更新，旧上下文已清空。');
});
```

**写完后应当怎样：**两个旧页面同时改进度时，后一次应提示重新读取。


## 让刚写的代码生效

如果上一节的服务仍在运行，先在那个终端按 Ctrl+C 停止。确认当前终端仍有模型配置，再从项目根目录重启，随后刷新浏览器。没有使用自动重载时，仅保存文件不会更新运行中的 Python 进程。

```bash
# 载入刚写完的接口、业务模块和页面；等终端显示服务启动后再进行下面的交互。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```


## 运行并观察

```bash
# 仅查看测试账号的会话概况，不打印私人对话正文；预期各条记录有独立 ID 与 revision。
python -c 'from companion.state import Actor,list_sessions; print(list_sessions(Actor("demo","reader-a")))'
```

重启后删除其中一次阅读，再刷新列表。另一条应保留。删除会话不删除原始讲稿，也不自动删除已保存笔记；这些是不同对象，后面提供更完整的个人数据删除入口。

## 思考一次并发修改

同一页面的两个标签页都读到 revision=0，分别写入不同进度。页面保存时会一并发送这个版本号。第一次写完 revision=1，第二次带旧版本应失败，并保留第一次的进度。若允许覆盖，就可能把新进度退回旧值。看到冲突提示后，在阅读列表中重新打开当前记录，再决定要不要修改；不要自动重试覆盖别人刚保存的值。

普通提问也会更新会话版本，接口会把新版本返回页面。因此在同一页面提问后保存进度仍能成功；跨标签页的旧记录则需要重新打开。

把“能存下来”与“存得有边界”一起验收：谁能看、能改哪一项、什么时候清掉、是否会带入下一轮模型请求。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 最近对话与知识库是什么关系？
2. 删会话为什么不删讲稿？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**最近对话与知识库是什么关系？**

对话是某位读者的短期上下文，知识库是有来源的资料。两者归属、更新和删除规则不同。

**删会话为什么不删讲稿？**

讲稿属于资料库，可能服务多个读者；删除某人的阅读记录不应影响公共学习材料。

**通过证据：**删除单条会话前后列表、另一条记录保留的证据，以及对 revision 冲突的解释。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter9)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion import state
state.initialize()
a=state.Actor("demo","reader-a");s=state.create_session(a)
u=state.update_session(a,s,progress=3)
try:
    state.update_session(a,s,progress=1)
    raise AssertionError("旧版本不应覆盖")
except ValueError:
    print("旧版本被拒绝，当前进度",u["progress"])
PY
```

**预期：**旧版本拒绝，进度保持3。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
