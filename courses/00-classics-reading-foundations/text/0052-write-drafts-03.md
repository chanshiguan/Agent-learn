# 先预览一份笔记，确认后再保存（3/3：连接页面交互）

本单元预计 **40—55 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《先预览一份笔记，确认后再保存（2/3：连接接口与业务）》](0052-write-drafts-02.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

上一小节已经把前一部分写进项目。这一节继续处理 `companion/web/reader.js`；先回想它接收什么、交给谁，再往下写。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：刷新会话时也刷新本人笔记

先完成列表，再读取草稿；每次 await 后都确认视图没有切换。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
    $('sessions').append(button);
  }
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
    $('sessions').append(button);
  }
  if (config.chapter >= 19) await refreshNotes();
```

**写完后应当怎样：**切换读者后没有旧笔记残留。

### 第 2 步：切换身份时清空草稿和笔记

即使服务器权限正确，页面也需要立即清掉上一位读者的内容。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
  $('selected').textContent = '先选择或创建一次阅读。';
  $('result').hidden = true;
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
  $('selected').textContent = '先选择或创建一次阅读。';
  $('result').hidden = true;
  $('drafts').replaceChildren();
  $('notes').replaceChildren();
```

**写完后应当怎样：**新读者的数据返回前页面保持空白。

### 第 3 步：记录目前已经写出的页面能力

该数字只供界面了解已实现功能，不代替后端权限。

**写在哪里：**项目根目录下的 `companion/app.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
CHAPTER = 14
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
CHAPTER = 19
```

**写完后应当怎样：**本节刷新可以加载草稿。

### 第 4 步：连接生成笔记与复习计划按钮

两种草稿共用同一预览与批准流程，不在模型返回后立即保存为正式记录。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
for (const [button, kind] of [
  ['draft-note', 'note'],
  ['draft-plan', 'review_plan'],
])
  on(button, async () => {
    requireSession();
    const expectedView = viewVersion;
    status('正在整理草稿，尚未保存……');
    await api('/api/drafts', 'POST', {
      session_id: selected.id,
      kind,
      request_id: id(),
    });
    if (viewVersion !== expectedView) return;
    await refreshNotes();
    if (viewVersion === expectedView) status('草稿已生成，请检查后决定是否保存。');
  });
```

**写完后应当怎样：**按钮先生成草稿，再等待读者确认。

## 运行并观察

```bash
# 停止旧服务后重启，让新路由和页面生效；仍使用原会话与资料。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```

先完成一次普通问答，再点“生成笔记草稿”。核对正文，未确认时正式笔记区不应增加记录；点击确认后才增加一条。重复点击同一批准，应返回同一条笔记。受限模式不从旧对话生成草稿，避免引入范围外内容。

本节先做不可编辑的预览；下一单元才增加“修改后重新确认”。终端操作入口在跨进程恢复单元亲手实现。下面的小检查可以先验证写入协议，不依赖模型是否生成好文章。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 为什么修改后必须重新预览？
2. 确认复习计划会自动修改进度吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么修改后必须重新预览？**

旧批准针对旧内容。修改改变了语义和摘要，新版本需要新的明确确认。

**确认复习计划会自动修改进度吗？**

不会。本课程只把确认后的计划作为本人笔记保存，进度由读者单独明确设置。

**通过证据：**一份真实模型草稿、一份修改后确认的笔记和未批准时没有写入的记录。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/03-tool-use-and-hello-agent.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion import state,actions
state.initialize();a=state.Actor("demo","reader-a")
d=actions.draft(a,"note","这是需要本人确认的测试笔记","guided-test")
assert not actions.notes(a)
actions.approve(a,d["id"],d["revision"],d["digest"],True)
assert len(actions.notes(a))==1
print("批准前无正式笔记，批准后1条")
PY
```

**预期：**只检查事务与确认边界；测试正文不是模型生成质量证据。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
