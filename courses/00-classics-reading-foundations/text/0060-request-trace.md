# 给一次提问一个可以追踪的编号

本单元预计 **50—65 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《让反馈与删除都有明确范围》](0059-privacy-feedback.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 用户说“刚才那次很慢”，怎么找

trace_id 把同一次请求的检索、生成、工具与最终结果连起来。它不是学生身份，也不需要放入姓名。页面反馈保存这个编号，开发者才知道应查哪一次运行。

正常模式提问一次，在 Network 响应中记下 trace_id，再查看 `data/live/events.jsonl`。普通问答会记录 retrieve、generate、answer；Agent 还记录工具结果。受限模式没有生成调用，不能给它编造 token 消耗。


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

## 运行并观察

```bash
# 只查看最近的结构化事件，预期是耗时、数量和状态，不包含问题正文、口令或完整讲稿。
python -c 'from companion.files import data_dir; p=data_dir()/"events.jsonl"; print("\n".join(p.read_text().splitlines()[-12:]) if p.exists() else "尚无事件，请先在网页提问")'
```

把 trace_id 相同的行放在一起：检索用了多久，生成用了多久，返回了几个来源，有无工具拒绝。时间是各阶段实际墙钟耗时，不能简单把所有嵌套阶段相加当作总耗时。

## 练一次故障定位

停止模型服务，再发一个需要生成的普通问题。预期页面显示通用失败与可追踪编号，日志保存错误类型，不把供应商原始响应回传给学生。恢复服务后重试，用新的 trace 区分。

如果检索很快、生成很慢，先查模型服务与输入长度；若工具反复拒绝，先看参数协议，而不是直接加大并发。日志帮助缩小问题，不替代实际重现。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. trace_id 与用户 ID 有什么不同？
2. 为何不把完整问题写进日志方便排查？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**trace_id 与用户 ID 有什么不同？**

trace_id 标记一次请求，用户 ID 标记归属。定位故障通常不需要把个人身份写入每条日志。

**为何不把完整问题写进日志方便排查？**

那会扩大私人内容的存储与传播。默认只记录必要状态；确需内容取证时另走受控、最少化流程。

**通过证据：**一条成功和一条故障请求的事件链，能按阶段解释慢点或失败位置。

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
from companion.operations import log_event
from companion.files import data_dir
log_event("trace-test","check",status="ok",password="must-not-be-logged")
assert "must-not-be-logged" not in (data_dir()/"events.jsonl").read_text()
print("未允许字段不会进入日志")
PY
```

**预期：**日志白名单拒绝口令字段。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
