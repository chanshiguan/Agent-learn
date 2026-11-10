# 两位读者，不共用一段对话（3/5：连接接口与业务）

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《两位读者，不共用一段对话（2/5：连接接口与业务）》](0042-reader-sessions-02.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

现在 `app.py` 已有测试身份、创建与列出会话的入口。本节补上读取、删除和提问接口，并创建 `web/index.html` 与 `reader.css`。页面会有读者选择、阅读列表和问题框，但按钮还没有连接动作；下一小节的 JavaScript 会按这里的元素 ID 找到它们。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：增加 session 这个接口或错误出口

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.get("/api/sessions/{identity}")
def session(identity: str, who=Depends(actor)):
    return state.get_session(who, identity)
```

**写完后应当怎样：**路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。

### 第 2 步：增加 remove_session 这个接口或错误出口

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.delete("/api/sessions/{identity}")
def remove_session(identity: str, who=Depends(actor)):
    state.delete_session(who, identity)
    return {"deleted": True}
```

**写完后应当怎样：**路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。

### 第 3 步：增加 ask 这个接口或错误出口

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.post("/api/ask")
def ask(body: Question, request: Request, who=Depends(actor)):
    request.state.trace_id = body.request_id
    return service.ask(who, body.session_id, body.question, body.request_id, body.mode, os.environ.get("RETRIEVAL", "keyword"))
```

**写完后应当怎样：**路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。

### 第 4 步：把新服务接到接下来写出的会话页面

页面文件将跟着本章一步步创建，不靠预置模板。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：页面文件将跟着本章一步步创建，不靠预置模板。
# 预期：完成页面文件后 / 才能显示会话界面。
@app.get("/")
def index():
    return FileResponse(web / "index.html")
```

**写完后应当怎样：**完成页面文件后 / 才能显示会话界面。

### 第 5 步：先写页面结构和控件名称

先约定每个控件的 ID，JavaScript 才知道把事件和结果放在哪里；不引入前端框架。

**写在哪里：**项目根目录下的 `companion/web/index.html`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**标签确定页面结构，id 让后面的 JavaScript 找到同一个控件。label 关联输入框；hidden 只是隐藏显示，不负责服务端权限。

下面 2 段按顺序组成同一处代码。每段最多 25 行；保留空行和缩进，全部写完并保存后再检查。

**连续代码 1/2**

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>名著伴读 · 阅读与思考</title>
    <link rel="stylesheet" href="/static/reader.css" />
  </head>
  <body>
    <h1>一起读《狂人日记》</h1>
    <p id="lab-notice">本机练习：只使用虚构读者。</p>
    <div id="lab-picker">
      <label for="reader">测试读者</label>
      <select id="reader">
        <option value="reader-a">读者 A</option>
        <option value="reader-b">读者 B</option>
      </select>
    </div>
    <main id="workspace">
      <label for="book">作品</label
      ><select id="book">
        <option>狂人日记</option>
      </select>
      <button id="new-session">开始一次阅读</button>
      <button id="refresh">刷新记录</button>
```

**连续代码 2/2**（接在上一段后，不额外增加缩进）

```html
      <div id="sessions"></div>
      <p id="selected">先选择或创建一次阅读。</p>
      <button id="delete-session">删除当前阅读记录</button>
      <form id="ask-form">
        <label for="question">想问什么？</label>
        <textarea id="question" required maxlength="800"></textarea>
        <select id="mode" aria-label="伴读方式">
          <option value="qa">直接解答</option>
        </select>
        <button id="ask">查资料并回答</button>
      </form>
      <article id="result" hidden>
        <p id="answer"></p>
        <div id="sources"></div>
      </article>
    </main>
    <p id="status" role="status"></p>
    <script src="/static/reader.js"></script>
  </body>
</html>
```

**写完后应当怎样：**此时页面能显示表单，交互要等下面的事件函数写完。

### 第 6 步：用少量样式保证输入与阅读清楚

控件有可点面积，长来源可以换行，键盘焦点可见。样式不承担权限校验。

**写在哪里：**项目根目录下的 `companion/web/reader.css`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**选择器指定哪些元素受影响，花括号里是一组显示规则。字号、间距和换行只改变阅读体验，不改变接口行为。

下面 2 段按顺序组成同一处代码。每段最多 25 行；保留空行和缩进，全部写完并保存后再检查。

**连续代码 1/2**

```css
body {
  max-width: 900px;
  margin: 32px auto;
  padding: 0 20px;
  color: #21324b;
  background: #f6f8fb;
  font: 17px/1.8 system-ui;
}
button,
input,
select,
textarea {
  font: inherit;
  padding: 10px;
  margin: 8px 4px;
}
button {
  min-height: 44px;
  cursor: pointer;
}
textarea {
  display: block;
  box-sizing: border-box;
  width: 100%;
  min-height: 110px;
```

**连续代码 2/2**（接在上一段后，不额外增加缩进）

```css
}
article,
.draft {
  background: white;
  padding: 20px;
  border: 1px solid #c5cfdf;
  margin: 16px 0;
}
pre,
.source-text {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
:focus-visible {
  outline: 3px solid #2356c8;
  outline-offset: 3px;
}
[hidden] {
  display: none !important;
}
```

**写完后应当怎样：**手机上表单适应宽度，来源保持换行。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/app.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

控件有可点面积，长来源可以换行，键盘焦点可见。样式不承担权限校验。 手机上表单适应宽度，来源保持换行。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter9)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
