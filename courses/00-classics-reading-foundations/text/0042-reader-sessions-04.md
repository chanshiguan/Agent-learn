# 两位读者，不共用一段对话（4/5：连接页面交互）

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《两位读者，不共用一段对话（3/5：连接接口与业务）》](0042-reader-sessions-03.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

上一小节已经把前一部分写进项目。这一节继续处理 `companion/web/reader.js`；先回想它接收什么、交给谁，再往下写。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：先约定页面状态与两个小工具

selected 只表示当前选中的会话；viewVersion 用于识别迟到响应。token 此时为空，登录章节才赋值。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
const $ = (id) => document.getElementById(id);
let token = '',
  config = {},
  selected = null,
  lastTrace = '',
  viewVersion = 0;
const id = () => crypto.randomUUID().replaceAll('-', '');
const status = (message) => {
  $('status').textContent = message;
};
```

**写完后应当怎样：**变量只留在当前页面内存，刷新不会把别人身份带进来。

### 第 2 步：把重复的 HTTP 请求写成一个函数

同源 API 统一 JSON 编解码和错误处理；本机练习发送虚构读者头，后续登录复用同一入口。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
async function api(path, method = 'GET', body) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = 'Bearer ' + token;
  if (config.mode === 'lab') headers['X-Lab-Reader'] = $('reader').value;
  const response = await fetch(path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok)
    throw new Error(
      typeof result.detail === 'string'
        ? result.detail
        : '请求未完成，请检查输入或重新登录。',
    );
  return result;
}
```

**写完后应当怎样：**接口错误会变成可显示的 Error，不继续当成功数据处理。

### 第 3 步：写页面函数 refresh

取回本人的会话列表，逐个创建选择按钮；响应回来时检查视图是否仍相同。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
async function refresh() {
  const expectedView = viewVersion;
  const sessions = await api('/api/sessions');
  if (viewVersion !== expectedView) return;
  $('sessions').replaceChildren();
  for (const session of sessions) {
    const button = document.createElement('button');
    button.textContent = session.book + ' · ' + session.id.slice(0, 6);
    button.onclick = () => choose(session.id).catch((e) => status(e.message));
    $('sessions').append(button);
  }
}
```

**写完后应当怎样：**保存本段后继续下一个函数；事件接好后再刷新浏览器检查整条交互。

### 第 4 步：写页面函数 choose

选择前清旧答案，返回后才赋给 selected，迟到的旧选择不能覆盖新选择。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
async function choose(identity) {
  const expectedView = ++viewVersion;
  selected = null;
  $('result').hidden = true;
  const session = await api('/api/sessions/' + identity);
  if (viewVersion !== expectedView) return;
  selected = session;
  $('selected').textContent =
    '当前阅读：' + selected.book + ' · ' + identity.slice(0, 6);
  $('result').hidden = true;
  lastTrace = '';
  status('已打开阅读记录，可以继续提问。');
}
```

**写完后应当怎样：**保存本段后继续下一个函数；事件接好后再刷新浏览器检查整条交互。

### 第 5 步：写页面函数 reset

切换读者时立即清空旧会话和旧答案，并增加视图代次。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
function reset() {
  viewVersion++;
  selected = null;
  lastTrace = '';
  $('sessions').replaceChildren();
  $('selected').textContent = '先选择或创建一次阅读。';
  $('result').hidden = true;
}
```

**写完后应当怎样：**保存本段后继续下一个函数；事件接好后再刷新浏览器检查整条交互。

### 第 6 步：写页面函数 requireSession

没有会话就停止，避免把问题写到不明确的阅读记录里。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
function requireSession() {
  if (!selected) throw new Error('请先创建或选择一次阅读。');
}
```

**写完后应当怎样：**保存本段后继续下一个函数；事件接好后再刷新浏览器检查整条交互。

### 第 7 步：写页面函数 enter

先加载作品，再加载会话，不把两个不同身份的异步结果拼在一起。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
async function enter() {
  const expectedView = viewVersion;
  $('workspace').hidden = false;
  const books = await api('/api/books');
  if (viewVersion !== expectedView) return;
  $('book').replaceChildren();
  for (const book of books) {
    const option = document.createElement('option');
    option.textContent = book;
    $('book').append(option);
  }
  await refresh();
}
```

**写完后应当怎样：**保存本段后继续下一个函数；事件接好后再刷新浏览器检查整条交互。

### 第 8 步：写页面函数 display

用 textContent 展示模型与讲稿内容，不把不可信输出当成 HTML 执行。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
function display(result) {
  $('answer').textContent = result.answer;
  lastTrace = result.trace_id || '';
  $('sources').replaceChildren();
  for (const source of result.sources || []) {
    const details = document.createElement('details'),
      summary = document.createElement('summary'),
      text = document.createElement('p');
    summary.textContent =
      source.file +
      ' · ' +
      source.parent +
      ' · 片段 ' +
      source.start +
      '—' +
      source.end;
    text.className = 'source-text';
    text.textContent = source.text;
    details.append(summary, text);
    $('sources').append(details);
  }
  if (!(result.sources || []).length)
    $('sources').textContent = '本次没有给出可引用片段。';
  $('result').hidden = false;
}
```

**写完后应当怎样：**保存本段后继续下一个函数；事件接好后再刷新浏览器检查整条交互。

## 在这里停一下，检查刚写的部分

保存文件，逐段核对标签、括号和元素 ID。网页尚未全部接通，完整交互检查放在本组最后一个小节。

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

用 textContent 展示模型与讲稿内容，不把不可信输出当成 HTML 执行。 保存本段后继续下一个函数；事件接好后再刷新浏览器检查整条交互。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter9)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
