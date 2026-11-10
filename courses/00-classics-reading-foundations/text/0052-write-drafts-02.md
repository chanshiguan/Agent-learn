# 先预览一份笔记，确认后再保存（2/3：连接接口与业务）

本单元预计 **55—70 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《先预览一份笔记，确认后再保存（1/3：保存会话状态）》](0052-write-drafts.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

上一小节已经把前一部分写进项目。这一节继续处理 `companion/app.py`；先回想它接收什么、交给谁，再往下写。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：增加 Draft 接口约定

分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
class Draft(Input):
    session_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    kind: Literal["note", "review_plan"]
```

**写完后应当怎样：**未确认的内容只在草稿列表中，不在正式笔记中。

### 第 2 步：增加 Confirmation 接口约定

分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
class Confirmation(Input):
    revision: int = Field(ge=1)
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    confirmed: bool
```

**写完后应当怎样：**未确认的内容只在草稿列表中，不在正式笔记中。

### 第 3 步：增加 make_draft 接口约定

分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
@app.post("/api/drafts")
def make_draft(body: Draft, who=Depends(actor)):
    return service.make_draft(who, body.session_id, body.kind, body.request_id)
```

**写完后应当怎样：**未确认的内容只在草稿列表中，不在正式笔记中。

### 第 4 步：增加 drafts 接口约定

分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
@app.get("/api/drafts")
def drafts(who=Depends(actor)):
    return actions.pending(who)
```

**写完后应当怎样：**未确认的内容只在草稿列表中，不在正式笔记中。

### 第 5 步：增加 approve 接口约定

分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
@app.post("/api/drafts/{identity}/approve")
def approve(identity: str, body: Confirmation, who=Depends(actor)):
    return actions.approve(who, identity, body.revision, body.digest, body.confirmed)
```

**写完后应当怎样：**未确认的内容只在草稿列表中，不在正式笔记中。

### 第 6 步：增加 notes 接口约定

分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
@app.get("/api/notes")
def notes(who=Depends(actor)):
    return actions.notes(who)
```

**写完后应当怎样：**未确认的内容只在草稿列表中，不在正式笔记中。

### 第 7 步：先把草稿区和正式笔记区分开

读者必须看见尚未保存与已经确认的区别，按钮文案也要明确。

**写在哪里：**项目根目录下的 `companion/web/index.html`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```html
      </article>
```

</details>

**先理解：**标签确定页面结构，id 让后面的 JavaScript 找到同一个控件。label 关联输入框；hidden 只是隐藏显示，不负责服务端权限。

```html
      </article>
      <section>
        <h2>阅读笔记</h2>
        <button id="draft-note">生成笔记草稿</button
        ><button id="draft-plan">生成复习计划草稿</button>
        <div id="drafts"></div>
        <h3>已确认的笔记</h3>
        <div id="notes"></div>
      </section>
```

**写完后应当怎样：**生成后出现在草稿区，批准后才出现在笔记区。

### 第 8 步：在页面展示预览并确认这一版

批准绑定当前看到的 revision 和 digest；响应回来后再次检查视图，防止旧身份内容迟到。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
  $('result').hidden = false;
}

```

</details>

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

下面 3 段按顺序组成同一处代码。每段最多 25 行；保留空行和缩进，全部写完并保存后再检查。

**连续代码 1/3**

```javascript
  $('result').hidden = false;
}

async function refreshNotes() {
  // 每次异步返回都核对视图，防止 A 的迟到私密内容出现在已经切换为 B 的页面。
  const expectedView = viewVersion;
  const drafts = await api('/api/drafts');
  if (viewVersion !== expectedView) return;
  $('drafts').replaceChildren();
  for (const draft of drafts.filter((x) => x.status === 'pending')) {
    const box = document.createElement('div');
    box.className = 'draft';
    const label = document.createElement('p'),
      text = document.createElement('textarea'),
      edit = document.createElement('button'),
      approve = document.createElement('button');
    label.textContent = '待确认草稿 · 版本 ' + draft.revision;
    text.value = draft.body;
    text.setAttribute('aria-label', '编辑草稿内容');
    edit.textContent = '保存修改，重新预览';
    edit.hidden = true;
    text.readOnly = true;
    approve.textContent = '确认保存这一版';
    approve.onclick = async () => {
      const actionView = viewVersion;
```

**连续代码 2/3**（接在上一段后，不额外增加缩进）

```javascript
      try {
        if (text.value !== draft.body)
          throw new Error('内容已编辑，请先保存修改并重新预览。');
        await api('/api/drafts/' + draft.id + '/approve', 'POST', {
          revision: draft.revision,
          digest: draft.digest,
          confirmed: true,
        });
        if (viewVersion !== actionView) return;
        await refreshNotes();
        if (viewVersion === actionView) status('当前草稿已保存。');
      } catch (e) {
        if (viewVersion === actionView) status(e.message);
      }
    };
    box.append(label, text, edit, approve);
    $('drafts').append(box);
  }
  const notes = await api('/api/notes');
  if (viewVersion !== expectedView) return;
  $('notes').replaceChildren();
  for (const note of notes) {
    const paragraph = document.createElement('p');
    paragraph.textContent = note.body;
    $('notes').append(paragraph);
```

**连续代码 3/3**（接在上一段后，不额外增加缩进）

```javascript
  }
}

```

**写完后应当怎样：**点击确认只提交当前预览，正式笔记重新读取。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/app.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

批准绑定当前看到的 revision 和 digest；响应回来后再次检查视图，防止旧身份内容迟到。 点击确认只提交当前预览，正式笔记重新读取。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/03-tool-use-and-hello-agent.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
