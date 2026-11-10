# 小步加负载，检查拒绝与取消（2/2：连接接口与业务）

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《小步加负载，检查拒绝与取消（1/2：保存会话状态）》](0067-load-and-limits.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

上一小节已经把前一部分写进项目。这一节继续处理 `companion/app.py`；先回想它接收什么、交给谁，再往下写。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：接入 busy 的 HTTP 行为

名额不足返回429，取消接口按本人身份查任务，读者能区分等待与拒绝。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：名额不足返回429，取消接口按本人身份查任务，读者能区分等待与拒绝。
# 预期：忙时可稍后重试，不显示上一次答案。
@app.exception_handler(TimeoutError)
def busy(request, error):
    return JSONResponse(status_code=429, content={"detail": "当前请求较多，请稍后再试。"}, headers={"Retry-After": "3"})
```

**写完后应当怎样：**忙时可稍后重试，不显示上一次答案。

### 第 2 步：接入 cancel 的 HTTP 行为

名额不足返回429，取消接口按本人身份查任务，读者能区分等待与拒绝。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：名额不足返回429，取消接口按本人身份查任务，读者能区分等待与拒绝。
# 预期：忙时可稍后重试，不显示上一次答案。
@app.post("/api/cancel/{request_id}")
def cancel(request_id: str, who=Depends(actor)):
    return operations.cancel(who, request_id)
```

**写完后应当怎样：**忙时可稍后重试，不显示上一次答案。

### 第 3 步：让读者能够发出取消请求

按钮说明停止后续处理，不承诺供应商已经撤销计算。

**写在哪里：**项目根目录下的 `companion/web/index.html`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```html
        <button id="ask">查资料并回答</button>
```

</details>

**先理解：**标签确定页面结构，id 让后面的 JavaScript 找到同一个控件。label 关联输入框；hidden 只是隐藏显示，不负责服务端权限。

```html
        <button id="ask">查资料并回答</button
        ><button type="button" id="cancel" hidden>停止后续处理</button>
```

**写完后应当怎样：**取消请求有明确反馈。

### 第 4 步：单独记录正在处理的请求

一个请求结束时只清理自己的按钮状态，避免迟到结果影响新请求。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
  selected = null,
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
  selected = null,
  activeRequest = null,
```

**写完后应当怎样：**活动请求ID与当前页面视图各自管理。

### 第 5 步：把请求ID、取消按钮和迟到保护连起来

收到返回或错误后同时检查请求和视图，只有当前请求能恢复对应按钮。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
  event.preventDefault();
  const expectedView = viewVersion;
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
  event.preventDefault();
  const expectedView = viewVersion,
    requestId = id();
```

**写完后应当怎样：**旧请求结束不会清掉新请求状态。

### 第 6 步：把请求ID、取消按钮和迟到保护连起来

收到返回或错误后同时检查请求和视图，只有当前请求能恢复对应按钮。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
  try {
    requireSession();
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
  try {
    requireSession();
    activeRequest = requestId;
```

**写完后应当怎样：**旧请求结束不会清掉新请求状态。

### 第 7 步：把请求ID、取消按钮和迟到保护连起来

收到返回或错误后同时检查请求和视图，只有当前请求能恢复对应按钮。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
    $('result').hidden = true;
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
    $('result').hidden = true;
    lastTrace = '';
```

**写完后应当怎样：**旧请求结束不会清掉新请求状态。

### 第 8 步：把请求ID、取消按钮和迟到保护连起来

收到返回或错误后同时检查请求和视图，只有当前请求能恢复对应按钮。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
    $('ask').disabled = true;
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
    $('ask').disabled = true;
    $('cancel').hidden = false;
    status('正在查资料并组织回答……');
```

**写完后应当怎样：**旧请求结束不会清掉新请求状态。

### 第 9 步：把请求ID、取消按钮和迟到保护连起来

收到返回或错误后同时检查请求和视图，只有当前请求能恢复对应按钮。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
      question: $('question').value,
      request_id: id(),
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
      question: $('question').value,
      request_id: requestId,
```

**写完后应当怎样：**旧请求结束不会清掉新请求状态。

### 第 10 步：把请求ID、取消按钮和迟到保护连起来

收到返回或错误后同时检查请求和视图，只有当前请求能恢复对应按钮。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
    status('回答已完成，请核对来源。');
  } catch (error) {
    if (viewVersion === expectedView) status(error.message);
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
    status('回答已完成，可以对照依据。');
  } catch (e) {
    if (viewVersion === expectedView) status(e.message);
```

**写完后应当怎样：**旧请求结束不会清掉新请求状态。

### 第 11 步：把请求ID、取消按钮和迟到保护连起来

收到返回或错误后同时检查请求和视图，只有当前请求能恢复对应按钮。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
    $('ask').disabled = false;
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
    if (activeRequest === requestId) {
      activeRequest = null;
      $('ask').disabled = false;
      $('cancel').hidden = true;
    }
```

**写完后应当怎样：**旧请求结束不会清掉新请求状态。

### 第 12 步：换人时也清理活动请求显示

页面立即清空；旧服务端任务即使稍后返回也不能写到新身份页面。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
  selected = null;
  lastTrace = '';
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
  selected = null;
  lastTrace = '';
  activeRequest = null;
  $('ask').disabled = false;
  $('cancel').hidden = true;
```

**写完后应当怎样：**取消按钮隐藏，提问按钮恢复。

### 第 13 步：连接取消按钮

请求携带的是当前任务ID，后端仍核对本人身份。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
on('cancel', async () => {
  if (activeRequest) {
    const expectedView = viewVersion;
    const result = await api('/api/cancel/' + activeRequest, 'POST');
    if (viewVersion === expectedView) status(result.message);
  }
});
```

**写完后应当怎样：**按钮只影响本人正在处理的请求。

## 运行并观察

```bash
# 单并发、四次请求，建立应用完整耗时基线；提示输入令牌时不回显。
python -m companion.measure api --concurrency 1 --count 4
# 提升到两并发；观察 429/503、成功吞吐与耗时，而不是只看完成数量。
python -m companion.measure api --concurrency 2 --count 4
```

配合 `docker stats --no-stream` 或系统活动监视器记录内存峰值。默认 MAX_MODEL_JOBS=1，等待槽位超过约 1 秒会拒绝；DAILY_JOB_LIMIT=40 是每用户每天的业务尝试次数，不是 token 或金额硬预算。失败也可能消耗额度，避免无限重试。

## 取消和缓存的边界

正在等待时点击停止，确认不再继续工具和状态提交；已经发出的模型请求可能继续。排队过多时明确拒绝，比无限堆积更可控。当前没有跨进程共享队列，也没有答案缓存；多副本前需要重新设计。

若以后加缓存，键至少要包含租户、允许资料范围、作品、资料与模型/Prompt 版本、问题；私人会话相关回答还要考虑本人和上下文。失效与删除也要可验证，不能拿另一个学生的答案直接复用。

小样本的 P95 只用来学习统计，不能写成稳定生产指标。记录错误原因、成功请求分布与质量变化，再逐步扩大经过批准的负载。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 为什么并发越高可能成功吞吐越低？
2. 每日 40 次是否保证费用不超过某金额？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么并发越高可能成功吞吐越低？**

设备竞争、队列、超时与限流会增加失败；不是每个并发请求都能有效推进。

**每日 40 次是否保证费用不超过某金额？**

不保证。每次模型往返和 token 数不同，Agent 也可能调用多轮；还需供应商预算、用量监控与实际费用控制。

**通过证据：**1/2 并发报告、内存记录、一次取消与额度拒绝结果，说明小样本统计的限制。

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
from companion import state
from companion.operations import job,cancel
state.initialize();a=state.Actor("demo","limit-test");b=state.Actor("demo","other")
with job(a,"request-test") as flag:
    assert cancel(b,"request-test")["cancel_requested"] is False
    assert cancel(a,"request-test")["cancel_requested"] is True
    assert flag.is_set()
print("本人取消通过，其他人不能取消")
PY
```

**预期：**取消按身份隔离，任务退出释放并发名额。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
