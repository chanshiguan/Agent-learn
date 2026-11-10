# 给一次提问一个可以追踪的编号

本单元预计 **50—65 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《让反馈与删除都有明确范围》](0059-privacy-feedback.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 用户说“刚才那次很慢”，怎么找

trace_id 是一次请求的编号。它不是学生身份，也不需要放入姓名。上一单元的页面反馈已经保存这个编号；现在给服务端日志补上同一个编号，才能从读者的回执找到对应请求。

本节先记录请求进入时的 `request` 和未处理异常时的 `failure`。写完并重启后，再发一次成功请求和一次故障请求，核对编号。下一单元增加普通问答完成时的总耗时，第 26 章再把检索、生成和工具的阶段事件接入同一条日志。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：先写这个文件需要的导入

先只写最少审计日志；并发名额和每日额度放在负载章节实现。

**写在哪里：**项目根目录下的 `companion/operations.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：先只写最少审计日志；并发名额和每日额度放在负载章节实现。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import json
import logging
import threading
from datetime import datetime, timezone
from .files import data_dir

_lock=threading.Lock()
_logger=logging.getLogger("reading-audit")
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 2 步：只允许明确列出的日志字段

日志便于排错，但不应成为另一份聊天、口令或讲稿数据库。

**写在哪里：**项目根目录下的 `companion/operations.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：日志便于排错，但不应成为另一份聊天、口令或讲稿数据库。
# 预期：只保存编号、状态、耗时和用量等白名单字段。
def log_event(trace_id, event, **fields):
    if not _logger.handlers:
        with _lock:
            if not _logger.handlers:
                handler = logging.FileHandler(data_dir() / "events.jsonl", encoding="utf-8")
                handler.setFormatter(logging.Formatter("%(message)s"))
                _logger.addHandler(handler)
                _logger.setLevel(logging.INFO)
                _logger.propagate = False
    # 只写明确允许的数值和状态，不接收请求正文、口令、讲稿或完整模型错误。
    safe = {k: v for k, v in fields.items() if k in {"seconds", "status", "method", "input_chars", "source_count", "tokens", "tool_count"}}
    _logger.info(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "trace_id": trace_id, "event": event, **safe}))
```

**写完后应当怎样：**只保存编号、状态、耗时和用量等白名单字段。

### 第 3 步：把业务结果接到最少日志

使用已有 request_id 串联，不把同一请求拆成无法关联的多条记录。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .models import complete
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .models import complete
from .operations import log_event
```

**写完后应当怎样：**日志不影响业务权限。

### 第 4 步：先记录请求编号与长度

只记录字符数，不记录问题正文；此时还不宣称知道完整耗时。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        raise ValueError("当前只支持问答和固定伴读。")
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
        raise ValueError("当前只支持问答和固定伴读。")
    log_event(request_id,"request",method=method,input_chars=len(question))
```

**写完后应当怎样：**events.jsonl 中能找到同一 request_id。

### 第 5 步：让未处理异常也有追踪编号

页面看到可报告的编号，供应商原始错误仍留在受控排查流程中。

**写在哪里：**项目根目录下的 `companion/app.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from . import service, state, actions, auth
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from . import service, state, actions, auth, operations
```

**写完后应当怎样：**读者不会收到密钥或服务器路径。

### 第 6 步：给不可用错误一个统一出口

公开错误只说明暂时不可用和编号；日志只记异常类型。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：公开错误只说明暂时不可用和编号；日志只记异常类型。
# 预期：服务故障有503和trace_id，不回显原始请求。
@app.exception_handler(Exception)
def unavailable(request, error):
    trace_id = getattr(request.state, "trace_id", uuid.uuid4().hex)
    operations.log_event(trace_id, "failure", status=type(error).__name__)
    # 不把模型供应商的原始响应、密钥或文件路径回传给读者。
    return JSONResponse(status_code=503, content={"detail": "服务暂时不可用，请稍后重试。", "trace_id": trace_id})
```

**写完后应当怎样：**服务故障有503和trace_id，不回显原始请求。


## 让刚写的代码生效

如果上一节的服务仍在运行，先在那个终端按 Ctrl+C 停止。确认当前终端仍有模型配置，再从项目根目录重启，随后刷新浏览器。没有使用自动重载时，仅保存文件不会更新运行中的 Python 进程。

```bash
# 载入刚写完的接口、业务模块和页面；等终端显示服务启动后再进行下面的交互。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```


## 运行并观察

```bash
# 只查看最近的结构化事件；本节预期有请求编号、问题长度或故障类型，不包含问题正文。
python -c 'from companion.files import data_dir; p=data_dir()/"events.jsonl"; print("\n".join(p.read_text().splitlines()[-12:]) if p.exists() else "尚无事件，请先在网页提问")'
```

先在正常模式提问，在 Network 的 `/api/ask` 响应中记下 trace_id，再运行上面的查看命令。应找到同编号的 `request`，包含检索方法和输入字符数；目前成功请求没有完成事件和阶段耗时。不要因为没看到 retrieve、generate 或 answer 就补造日志，它们还没有接入。

## 练一次故障定位

先在运行应用的终端按 `Ctrl+C` 停止 Uvicorn。回想第4章验证过的真实模型 ID，将它记在自己的配置记录中，然后仅为一次应用启动设置一个不存在的演练模型：

```bash
# 这次启动只覆盖模型名；本地和线上都能演练，不需要关闭共享模型服务。
LLM_MODEL=course-model-does-not-exist python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

仍沿用本节前面已经设置的 APP_MODE 和其他变量。在页面发一个能检索到资料、需要生成的普通问题，例如序言与日记的区别。预期模型服务拒绝未知模型，页面显示通用失败与可追踪编号，日志只保存错误类型。若供应商对未知名称自动路由，记录这种实际行为，另用第4章的错误本机地址实验制造连接失败，不能伪造失败。

完成后按 `Ctrl+C`，重用本节前面正常的 Uvicorn 启动命令，恢复真实配置；临时前缀没有改动原终端的 LLM_MODEL。再次提问应恢复成功，用新的 trace 区分。

把故障响应的编号与 `request`、`failure` 两条日志对上，检查 failure 的 status 是否说明异常类型。这个版本能定位“哪次请求失败、报了哪类错”，还不能区分检索慢还是生成慢。保留这次记录，下一单元用同一方式观察成功请求的总耗时；分阶段定位留到第 26 章。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. trace_id 与用户 ID 有什么不同？
2. 为何不把完整问题写进日志方便排查？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**trace_id 与用户 ID 有什么不同？**

trace_id 标记一次请求，用户 ID 标记归属。定位故障通常不需要把个人身份写入每条日志。

**为何不把完整问题写进日志方便排查？**

那会扩大私人内容的存储与传播。默认只记录必要状态；确需内容取证时另走受控、最少化流程。

**通过证据：**成功响应与 request 的编号对应、故障响应与 request/failure 的编号对应，以及日志未包含口令或问题正文的检查。能说明本节还没有记录完成时间和阶段耗时。

</details>

## 下次开始前

下次先不看日志，说明反馈中的 trace_id 怎样找到对应请求，再打开已保存的成功与失败记录核对。能找到编号还不能解释慢在哪里；下一单元会在同一请求开始和完成处计时。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion.operations import log_event
from companion.files import data_dir
log_event("trace-test","check",status="ok",password="must-not-be-logged")
assert "must-not-be-logged" not in (data_dir()/"events.jsonl").read_text()
print("未允许字段不会进入日志")
PY
```

**预期：**日志白名单拒绝口令字段。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
