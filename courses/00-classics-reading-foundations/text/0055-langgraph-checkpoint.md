# 用状态图重现同一个批准流程（1/2：把本节能力连起来）

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《关闭程序后，接着处理同一草稿》](0054-resume-actions.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 现在才引入框架

StateGraph 用节点表示步骤、边表示顺序；checkpointer 把状态保存到磁盘；interrupt 在需要用户决定时暂停；Command(resume=...) 带着确认继续。thread_id 区分任务，这里同时包含租户、读者和动作 ID。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：现在才安装状态图与磁盘检查点

先理解手写批准和持久状态，再观察框架如何组织同一个流程。

**写在哪里：**项目根目录下的 `requirements-graph.txt`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**langgraph 组织状态流转，sqlite 检查点包保存暂停位置。它们接在已有批准事务之上；安装框架不会自动提供身份隔离或确认权限。

```text
# 第 20 章新增：磁盘检查点使暂停流程可以跨进程恢复。
langgraph==1.2.20
langgraph-checkpoint-sqlite==3.1.3
```

**写完后应当怎样：**安装库不改变批准规则。

```bash
# 按刚亲手保存的清单安装本节所需依赖；只安装库，不会自动运行项目。
python -m pip install -r requirements-graph.txt
```

### 第 2 步：为跨进程状态操作准备文件锁

CLI 与 HTTP 可能不是同一进程；线程锁不能协调两个进程。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
import json
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
import json
import fcntl
```

**写完后应当怎样：**macOS/Linux 上使用文件排他锁，不宣称支持原生 Windows。

### 第 3 步：让图写入与后续删除共享一把锁

保护不调用模型的短状态操作；进程异常退出时系统释放锁。

**写在哪里：**项目根目录下的 `companion/state.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：保护不调用模型的短状态操作；进程异常退出时系统释放锁。
# 预期：不会一边报告删除成功，一边又写回旧检查点。
@contextmanager
def personal_data_lock():
    # CLI 与 API 可能是两个进程；用文件锁协调检查点写入和删除，线程锁不够。
    # 这里只保护不调用模型的短操作，进程异常退出时系统也会释放锁。
    with (data_dir() / ".personal-data.lock").open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)
```

**写完后应当怎样：**不会一边报告删除成功，一边又写回旧检查点。

### 第 4 步：先写这个文件需要的导入

图只管理流程暂停与恢复，最终批准仍调用已经测试过的 actions.approve。

**写在哪里：**项目根目录下的 `companion/graph.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：图只管理流程暂停与恢复，最终批准仍调用已经测试过的 actions.approve。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import sqlite3
from typing import TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from .actions import pending, approve
from .files import data_dir, digest, save
from .state import personal_data_lock
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 5 步：写 ReviewState 的状态边界

明确图中保存动作 ID 和结果，不能保存一份绕过权限的任意执行计划。

**写在哪里：**项目根目录下的 `companion/graph.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**TypedDict 说明图状态有哪些键，total=False 允许结果尚未产生时缺少 result。它不是运行时权限检查；恢复时仍须用 action_id 查询当前动作并复查归属。

```python
# 目的：明确图中保存动作 ID 和结果，不能保存一份绕过权限的任意执行计划。
# 预期：重启后可恢复同一批准，旧版本、越权和重复恢复仍受原事务约束。
class ReviewState(TypedDict, total=False):
    action_id: str
    result: dict
```

**写完后应当怎样：**重启后可恢复同一批准，旧版本、越权和重复恢复仍受原事务约束。

### 第 6 步：写 run_review 的状态边界

暂停时给具体预览，恢复时带回确认；线程 ID 包含本人身份，检查点写入与预览同锁。

**写在哪里：**项目根目录下的 `companion/graph.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

下面 2 段按顺序组成同一处代码。每段最多 25 行；保留空行和缩进，全部写完并保存后再检查。

**连续代码 1/2**

```python
# 目的：暂停时给具体预览，恢复时带回确认；线程 ID 包含本人身份，检查点写入与预览同锁。
# 预期：重启后可恢复同一批准，旧版本、越权和重复恢复仍受原事务约束。
def run_review(actor, action_id, decision=None):
    def review(state):
        candidates = {a["id"]: a for a in pending(actor)}
        item = candidates.get(state["action_id"])
        if item is None:
            raise PermissionError("当前读者没有此待确认动作。")
        confirmation = interrupt({"id": item["id"], "body": item["body"], "revision": item["revision"], "digest": item["digest"]})
        if not isinstance(confirmation, dict):
            raise ValueError("恢复时必须带回对具体版本的确认。")
        return {"result": approve(actor, item["id"], confirmation.get("revision"), confirmation.get("digest"), confirmation.get("confirmed"))}

    flow = StateGraph(ReviewState)
    flow.add_node("review", review)
    flow.add_edge(START, "review")
    flow.add_edge("review", END)
    # 线程标识包含租户和本人，知道 action_id 也不能恢复另一个人的流程。
    config = {"configurable": {"thread_id": digest([actor.tenant, actor.user, action_id])}}
    with personal_data_lock(), sqlite3.connect(data_dir() / "checkpoints.sqlite3", check_same_thread=False) as db:
        graph = flow.compile(checkpointer=SqliteSaver(db))
        if decision is not None:
            checkpoint = graph.get_state(config)
            if not checkpoint.values:
                raise ValueError("没有可恢复的检查点，请先运行 start。")
```

**连续代码 2/2**（接在上一段后，不额外增加缩进）

```python
            if not checkpoint.next:
                return {"status": "finished", "result": checkpoint.values.get("result")}
        value = Command(resume=decision) if decision is not None else {"action_id": action_id}
        result = graph.invoke(value, config=config)
        # 预览也在同一锁内保存，避免删除完成后 CLI 又把旧正文写回磁盘。
        if "__interrupt__" in result:
            preview = result["__interrupt__"][0].value
            save("graph-preview.json", preview)
            return {"status": "awaiting_confirmation", "preview": preview}
        return {"status": "finished", "result": result.get("result")}
```

**写完后应当怎样：**重启后可恢复同一批准，旧版本、越权和重复恢复仍受原事务约束。

### 第 7 步：写 erase_threads 的状态边界

为删除个人内容准备本人图线程清理，不能只删除业务表却留下检查点副本。

**写在哪里：**项目根目录下的 `companion/graph.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：为删除个人内容准备本人图线程清理，不能只删除业务表却留下检查点副本。
# 预期：重启后可恢复同一批准，旧版本、越权和重复恢复仍受原事务约束。
def erase_threads(actor):
    with sqlite3.connect(data_dir() / "checkpoints.sqlite3", check_same_thread=False) as db:
        saver = SqliteSaver(db)
        for item in pending(actor):
            saver.delete_thread(digest([actor.tenant, actor.user, item["id"]]))
```

**写完后应当怎样：**重启后可恢复同一批准，旧版本、越权和重复恢复仍受原事务约束。

### 第 8 步：把暂停和恢复接回命令行

恢复必须使用已显示的具体预览，不能只传一个“同意”就写入。

**写在哪里：**项目根目录下的 `companion/graph_cli.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

```python
# 目的：恢复必须使用已显示的具体预览，不能只传一个“同意”就写入。
# 预期：不同进程的 start/resume 能完成一次批准。
import argparse
import json
from .files import load
from .graph import run_review
from .state import Actor,initialize


def main():
    parser=argparse.ArgumentParser(description="暂停与恢复同一批准")
    parser.add_argument("operation",choices=["start","resume"])
    parser.add_argument("--user",default="reader-a")
    args=parser.parse_args();initialize();actor=Actor("demo",args.user)
    identity=input("本人草稿 ID：").strip()
    decision=None
    if args.operation=="resume":
        preview=load("graph-preview.json")
        if not preview or preview["id"]!=identity:raise ValueError("请先取得匹配预览。")
        print(json.dumps(preview,ensure_ascii=False,indent=2))
        if input("确认这份预览？输入 YES：")!="YES":
            print("没有批准，保持暂停。")
            return
        decision={"revision":preview["revision"],"digest":preview["digest"],"confirmed":True}
    print(json.dumps(run_review(actor,identity,decision),ensure_ascii=False,indent=2))
```

**写完后应当怎样：**不同进程的 start/resume 能完成一次批准。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/state.py companion/graph.py companion/graph_cli.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

恢复必须使用已显示的具体预览，不能只传一个“同意”就写入。 不同进程的 start/resume 能完成一次批准。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/04-agent-frameworks.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
