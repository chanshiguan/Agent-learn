# 两位读者，不共用一段对话（5/5：连接页面交互）

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《两位读者，不共用一段对话（4/5：连接页面交互）》](0042-reader-sessions-04.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

上一小节已经把前一部分写进项目。这一节继续处理 `companion/web/reader.js`；先回想它接收什么、交给谁，再往下写。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：写页面函数 on

给按钮统一挂接错误出口，旧身份的迟到错误不覆盖当前提示。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
function on(button, action) {
  $(button).addEventListener('click', () => {
    const expectedToken = token,
      expectedReader = $('reader').value;
    action().catch((e) => {
      if (token === expectedToken && $('reader').value === expectedReader)
        status(e.message);
    });
  });
}
```

**写完后应当怎样：**保存本段后继续下一个函数；事件接好后再刷新浏览器检查整条交互。

### 第 2 步：让表单调用会话问答接口

提交前隐藏旧答案；收到结果后再次检查视图，不能把 A 的回答放到 B 页面。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
$('ask-form').onsubmit = async (event) => {
  event.preventDefault();
  const expectedView = viewVersion;
  try {
    requireSession();
    $('result').hidden = true;
    $('ask').disabled = true;
    const result = await api('/api/ask', 'POST', {
      session_id: selected.id,
      question: $('question').value,
      request_id: id(),
      mode: $('mode').value,
    });
    if (viewVersion !== expectedView) return;
    selected.revision = result.session_revision;
    display(result);
    status('回答已完成，请核对来源。');
  } catch (error) {
    if (viewVersion === expectedView) status(error.message);
  } finally {
    $('ask').disabled = false;
  }
};
```

**写完后应当怎样：**同一个会话可以连续提问，返回的新版本留给下一次更新。

### 第 3 步：连接 new-session 按钮

把刚写出的页面函数接到明确动作，删除必须先确认，刷新不自动新增会话。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
on('new-session', async () => {
  const expectedView = viewVersion;
  const result = await api('/api/sessions', 'POST', { book: $('book').value });
  if (viewVersion !== expectedView) return;
  await refresh();
  if (viewVersion === expectedView) await choose(result.id);
});
```

**写完后应当怎样：**按钮只调用当前已经写出的 API。

### 第 4 步：连接 refresh 按钮

把刚写出的页面函数接到明确动作，删除必须先确认，刷新不自动新增会话。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
on('refresh', refresh);
```

**写完后应当怎样：**按钮只调用当前已经写出的 API。

### 第 5 步：连接 delete-session 按钮

把刚写出的页面函数接到明确动作，删除必须先确认，刷新不自动新增会话。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
on('delete-session', async () => {
  requireSession();
  if (!confirm('删除当前阅读记录？这不会删除讲稿。')) return;
  const expectedView = viewVersion;
  await api('/api/sessions/' + selected.id, 'DELETE');
  if (viewVersion !== expectedView) return;
  reset();
  const refreshedView = viewVersion;
  await refresh();
  if (viewVersion === refreshedView) status('阅读记录已删除。');
});
```

**写完后应当怎样：**按钮只调用当前已经写出的 API。

### 第 6 步：让切换读者立即清除旧页面

服务器按请求发出时的身份返回，浏览器必须自己丢弃切换后才到达的旧结果。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
$('reader').onchange = () => {
  reset();
  const expectedView = viewVersion;
  refresh().catch((e) => {
    if (viewVersion === expectedView) status(e.message);
  });
};
```

**写完后应当怎样：**切成 B 后看不到 A 的笔记或旧答案。

### 第 7 步：最后才启动页面初始化

前面的函数都定义好后，再读取配置和列表；定义函数本身不应提前发请求。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
(async () => {
  config = await api('/api/config');
  await enter();
})().catch((e) => status(e.message));
```

**写完后应当怎样：**刷新页面可创建会话、提问和展开来源。


## 运行并观察

```bash
# 保持测试身份模式，只在本机练习；页面功能由你刚增加的代码提供。
export APP_MODE=lab
# 先使用已验证的词面基线；选择 hybrid 时还要保证 Qdrant 与索引就绪。
export RETRIEVAL=keyword
# 启动带会话的同源页面；数据写到 data/live/reading.sqlite3。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```

选择读者 A，创建《狂人日记》阅读，问一个问题；切到读者 B，应看不到 A 的会话。B 新建记录后，切回 A 检查它仍在。停止并重启服务，再检查持久性。

## 身份来自哪里

本章 `X-Lab-Reader` 只允许两个测试值，且服务限本机。它方便验证隔离，却不是认证系统：知道测试值的人就能选身份。第 21 章才换真实登录。页面功能是在各节实际写入的；显示了按钮仍不等于具备操作权限。

每次查询会话都带 `tenant` 和 `owner`；仅知道会话 ID 不能越过它们。数据库写入还检查 revision，避免两次并发请求用旧状态互相覆盖。冲突会让你重读状态，不静默丢掉一段对话。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 用不同 UUID 是否就实现了权限？
2. 测试身份模式为什么不能上线？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**用不同 UUID 是否就实现了权限？**

没有。ID 不容易猜也不能替代服务端的所属人和租户检查。

**测试身份模式为什么不能上线？**

客户端能够选择身份，没有证明“你是谁”。本章只检验归属逻辑，真实认证在第 21 章接入。

**通过证据：**A/B 两个独立会话和重启后的保留记录；能说明测试身份的限制。

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
a=state.Actor("demo","reader-a");b=state.Actor("demo","reader-b")
s=state.create_session(a)
try:
    state.get_session(b,s["id"])
    raise AssertionError("不应读到另一个人的会话")
except PermissionError:
    print("会话归属检查通过")
PY
```

**预期：**A 能访问自己的会话，B 被拒绝。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from fastapi.testclient import TestClient
from companion.app import app
with TestClient(app) as c:
    assert c.get("/").status_code==200
    r=c.post("/api/sessions",json={"book":"狂人日记"});assert r.status_code==200
    assert c.get("/api/sessions/"+r.json()["id"],headers={"X-Lab-Reader":"reader-b"}).status_code==403
print("页面、创建会话和跨读者拒绝通过")
PY
```

**预期：**路由已接通，身份切换不会读到另一位读者的会话。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
