# 让来源和错误都能看见（1/2：把本节能力连起来）

本单元预计 **55—70 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《用一个 API 接住读者的问题》](0040-first-api.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：从表单开始接一条完整页面请求

页面收集问题，fetch 发给自己的 API；先清旧结果，返回后用 textContent 显示，避免执行模型里的 HTML。

**写在哪里：**项目根目录下的 `companion/web/basic.html`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**标签确定页面结构，id 让后面的 JavaScript 找到同一个控件。label 关联输入框；hidden 只是隐藏显示，不负责服务端权限。

下面 5 段按顺序组成同一处代码。每段最多 25 行；保留空行和缩进，全部写完并保存后再检查。

**连续代码 1/5**

```html
<!doctype html>
<html lang="zh-CN">
  <meta charset="utf-8" /><meta
    name="viewport"
    content="width=device-width,initial-scale=1"
  /><title>名著伴读 · 第一次页面问答</title>
  <style>
    body {
      max-width: 760px;
      margin: 48px auto;
      padding: 0 20px;
      font: 17px/1.8 system-ui;
      color: #21324b;
      background: #f6f8fb;
    }
    h1 {
      font-size: 30px;
    }
    textarea {
      box-sizing: border-box;
      width: 100%;
      min-height: 120px;
      padding: 16px;
      font: inherit;
      border: 1px solid #8192a8;
```

**连续代码 2/5**（接在上一段后，不额外增加缩进）

```html
      border-radius: 8px;
    }
    button {
      font: inherit;
      padding: 10px 20px;
      margin-top: 12px;
      border: 0;
      border-radius: 7px;
      background: #2356c8;
      color: white;
      cursor: pointer;
    }
    button:disabled {
      background: #526174;
    }
    pre {
      white-space: pre-wrap;
    }
    article {
      padding: 20px;
      background: white;
      border: 1px solid #dbe2eb;
      border-radius: 10px;
      margin: 20px 0;
    }
```

**连续代码 3/5**（接在上一段后，不额外增加缩进）

```html
    summary {
      cursor: pointer;
    }
    :focus-visible {
      outline: 3px solid #2356c8;
      outline-offset: 3px;
    }
  </style>
  <h1>一起读《狂人日记》</h1>
  <p>提出一个问题，回答下方可以查看用到的讲稿。</p>
  <form id="form">
    <label for="question">你想了解什么？</label
    ><textarea id="question" maxlength="800" required>
这份讲稿怎样解释文言文序言和白话日记？</textarea
    ><button id="submit">查资料并回答</button>
  </form>
  <p id="status" role="status"></p>
  <article id="result" hidden>
    <p id="answer"></p>
    <div id="sources"></div>
  </article>
  <script>
    document.getElementById('form').addEventListener('submit', async (event) => {
      event.preventDefault();
      const button = document.getElementById('submit');
```

**连续代码 4/5**（接在上一段后，不额外增加缩进）

```html
      button.disabled = true;
      document.getElementById('result').hidden = true;
      document.getElementById('status').textContent = '正在查找资料并组织回答……';
      try {
        const response = await fetch('/api/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question: document.getElementById('question').value,
            book: '狂人日记',
          }),
        });
        const result = await response.json();
        if (!response.ok)
          throw new Error(
            typeof result.detail === 'string' ? result.detail : '请求未通过检查',
          );
        // 用 textContent 显示不可信模型输出；其中即使有 HTML，也不会被浏览器执行。
        document.getElementById('answer').textContent = result.answer;
        const list = document.getElementById('sources');
        list.replaceChildren();
        for (const source of result.sources || []) {
          const details = document.createElement('details'),
            summary = document.createElement('summary'),
            text = document.createElement('p');
```

**连续代码 5/5**（接在上一段后，不额外增加缩进）

```html
          summary.textContent = source.file + ' · ' + source.parent;
          text.textContent = source.text;
          details.append(summary, text);
          list.append(details);
        }
        document.getElementById('result').hidden = false;
        document.getElementById('status').textContent = '回答已生成，请对照来源判断。';
      } catch (error) {
        document.getElementById('status').textContent = error.message;
      } finally {
        button.disabled = false;
      }
    });
  </script>
</html>
```

**写完后应当怎样：**页面可以提问并展开来源；模型出错时显示错误，不残留上一次答案。

## 在这里停一下，检查刚写的部分

保存文件，逐段核对标签、括号和元素 ID。网页尚未全部接通，完整交互检查放在本组最后一个小节。

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

页面收集问题，fetch 发给自己的 API；先清旧结果，返回后用 textContent 显示，避免执行模型里的 HTML。 页面可以提问并展开来源；模型出错时显示错误，不残留上一次答案。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
