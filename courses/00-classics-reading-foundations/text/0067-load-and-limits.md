# 小步加负载，检查拒绝与取消（1/2：保存会话状态）

本单元预计 **55—70 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《先测一个请求，别急着加并发》](0066-latency-measure.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 先用专门的测试账号

使用 authenticated 模式，不对真实用户账号做压测。下面最多只允许 4 并发、20 请求，目的是学方法。实际容量试验需要独立环境、预算与负责人安排。模型服务可能仍按失败或取消请求计费。

登录专用账号，在浏览器 Network 的登录响应里取得短期 access_token。只把它输入脚本的隐藏提示，不放进命令历史或报告。测试会创建独立会话，结束后删除这些会话。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：创建 quotas 表

只在能力需要时增加这张表，已有会话继续保留。

**写在哪里：**项目根目录下的 `companion/state.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
          category TEXT NOT NULL, trace_id TEXT NOT NULL, created REAL NOT NULL);
```

</details>

**先理解：**建表语句描述需要保存的字段；已有表不会因重复初始化而清空。增加列与修改已有记录是两种操作。

```python
          category TEXT NOT NULL, trace_id TEXT NOT NULL, created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS quotas(
          tenant TEXT NOT NULL, owner TEXT NOT NULL, day TEXT NOT NULL, count INTEGER NOT NULL,
          PRIMARY KEY(tenant,owner,day));
```

**写完后应当怎样：**重启服务调用 initialize 后新表存在，重复执行不会清空数据。

### 第 2 步：为并发名额和每日额度准备依赖

进程内并发名额与数据库日额度是两种限制；多副本部署时需要共享方案。

**写在哪里：**项目根目录下的 `companion/operations.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
import json
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
import json
import os
import time
from contextlib import contextmanager
from .state import connect
```

**写完后应当怎样：**当前只声明单进程能力，不冒称集群限流。

### 第 3 步：创建明确的并发名额和任务表

名额满了要拒绝，不无限排队；任务键包含机构、本人和请求ID。

**写在哪里：**项目根目录下的 `companion/operations.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**BoundedSemaphore 限制这个 Python 进程同时运行的任务数；_jobs 把具体请求与取消状态关联。多个进程各有自己的名额，因此本课部署固定一个 worker。

```python
# 目的：名额满了要拒绝，不无限排队；任务键包含机构、本人和请求ID。
# 预期：两个读者不能互相取消对方任务。
_slots=threading.BoundedSemaphore(int(os.environ.get("MAX_MODEL_JOBS","1")))
_jobs={}
```

**写完后应当怎样：**两个读者不能互相取消对方任务。

### 第 4 步：实现 job 的资源边界

在 finally 里释放名额，失败和取消也不能泄漏槽位；日额度在数据库事务中更新。

**写在哪里：**项目根目录下的 `companion/operations.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：在 finally 里释放名额，失败和取消也不能泄漏槽位；日额度在数据库事务中更新。
# 预期：取消后不继续工具调用或保存迟到内容；未知请求不会假称已取消。
@contextmanager
def job(actor, request_id):
    key = (actor.tenant, actor.user, request_id)
    with _lock:
        if key in _jobs:
            raise ValueError("请求已经在处理中，请不要重复提交。")
        flag = threading.Event()
        _jobs[key] = flag
    acquired = False
    try:
        acquired = _slots.acquire(timeout=1)
        if not acquired:
            raise TimeoutError("当前请求较多，请稍后再试。")
        day = datetime.now(timezone.utc).date().isoformat()
        with connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM quotas WHERE day < ?", (day,))
            row = db.execute("SELECT count FROM quotas WHERE tenant=? AND owner=? AND day=?", (actor.tenant, actor.user, day)).fetchone()
            count = row[0] if row else 0
            if count >= int(os.environ.get("DAILY_JOB_LIMIT", "40")):
                raise PermissionError("今天的试用请求额度已用完。")
            db.execute("INSERT INTO quotas VALUES(?,?,?,?) ON CONFLICT(tenant,owner,day) DO UPDATE SET count=excluded.count", (actor.tenant, actor.user, day, count + 1))
        yield flag
    finally:
        if acquired:
            _slots.release()
        with _lock:
            _jobs.pop(key, None)
```

**写完后应当怎样：**取消后不继续工具调用或保存迟到内容；未知请求不会假称已取消。

### 第 5 步：让取消与最终提交有明确先后

取消和落库必须共用同一把锁：先取消就不保存，先进入提交则不能再声称已取消。锁里只放短数据库操作。

只写一句 `if flag.is_set()` 还不够：刚检查完，另一个请求可能发来取消，而当前请求已经准备保存。`commit_job` 把“再检查一次”和“保存结果”放进同一个不能被取消插入的短步骤。`yield` 暂时交给 `with commit_job(...)` 里面的代码；里面保存成功后，把任务标为已提交，请求键保留到整个任务退出。这样旧任务还没退出时，同一请求键不能被新任务抢用。取消请求晚到时会明确得到 `false`，而不是收到一个实际上无法兑现的取消成功回执。调用模型仍放在锁外。

**写在哪里：**项目根目录下的 `companion/operations.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：只标记同一身份的当前任务，已发给供应商的请求可能仍运行与计费。
# 预期：取消后不继续工具调用或保存迟到内容；未知请求不会假称已取消。
def cancel(actor, request_id):
    with _lock:
        flag = _jobs.get((actor.tenant, actor.user, request_id))
        if flag is not None:
            flag.set()
    message = "已请求取消；已发送的模型请求仍可能运行和计费，未提交的结果不会保存。" if flag is not None else "任务已提交或不存在，本次没有取消结果。"
    return {"cancel_requested": flag is not None, "message": message}

# 目的：让取消与最终写入有明确先后；检查标记和提交必须是同一个短操作。
# 预期：先取消就不落库；先提交则取消返回 false，不谎称能撤回已保存的结果。
@contextmanager
def commit_job(actor, request_id):
    key = (actor.tenant, actor.user, request_id)
    # 锁内只放数据库提交，不放模型调用；其他请求不必陪着模型等待。
    with _lock:
        flag = _jobs.get(key)
        if flag is None or flag.is_set():
            raise ValueError("请求已取消，本次结果没有保存。")
        yield
        # 保留请求键到 job 退出，避免旧任务清理时误删刚复用同一键的新任务。
        _jobs[key] = None
```

**写完后应当怎样：**取消成功的结果不会落库；已提交或不存在的任务明确返回 cancel_requested=false。

### 第 6 步：让所有模型工作共享同一名额约束

普通问答、伴读、Agent 与草稿都不能各自绕过限制。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .operations import log_event
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .operations import log_event, job, commit_job
```

**写完后应当怎样：**每项工作在统一入口取得并归还资源。

### 第 7 步：在完整业务链前后检查取消与额度

模型调用占用任务名额；最终版本检查与保存由 commit_job 保护，避免取消确认后仍写入。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    if mode not in {"qa","tutor","agent"}:
        raise ValueError("当前只支持问答和固定伴读。")
    started=time.monotonic()
    log_event(request_id,"request",method=method,input_chars=len(question))
    session=get_session(actor,session_id)
    if mode == "tutor":
        result=teach_turn(actor,session_id,question,method)
        updated=update_session(actor,session,**result.pop("state_changes"))
        return {**result,"trace_id":request_id,"session_revision":updated["revision"]}
    if mode == "agent":
        result=run_agent(actor,session_id,question,method)
    else:
        hits=retrieve(question,actor.tenant,session["book"],method,session["progress"] if session["strict"] else None)
        result=answer(question,hits,[] if session["strict"] else session["history"],strict=bool(session["strict"]))
    history=[] if session["strict"] else (session["history"]+[{"role":"user","content":question},{"role":"assistant","content":result["answer"]}])[-4:]
    updated=update_session(actor,session,history=history)
    log_event(request_id,"answer",seconds=round(time.monotonic()-started,3),source_count=len(result.get("sources",[])))
    return {**result,"trace_id":request_id,"session_revision":updated["revision"]}
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

下面 2 段按顺序组成同一处代码。每段最多 25 行；保留空行和缩进，全部写完并保存后再检查。

**连续代码 1/2**

```python
    started = time.monotonic()
    log_event(request_id, "request", method=method, input_chars=len(question))
    session = get_session(actor, session_id)
    with job(actor, request_id) as flag:
        if flag.is_set():
            raise ValueError("请求已取消。")
        if mode == "agent":
            result = run_agent(actor, session_id, question, method, cancelled=flag.is_set)
        elif mode == "tutor":
            result = teach_turn(actor, session_id, question, method)
        else:
            retrieved_at = time.monotonic()
            # 防剧透开启时不带旧对话；每次用当前权限重新检索，不复用过去的来源。
            hits = retrieve(question, actor.tenant, session["book"], method, session["progress"] if session["strict"] else None)
            log_event(request_id, "retrieve", seconds=round(time.monotonic() - retrieved_at, 3), source_count=len(hits), method=method)
            generated_at = time.monotonic()
            result = answer(question, hits, [] if session["strict"] else session["history"], strict=bool(session["strict"]))
            log_event(request_id, "generate", seconds=round(time.monotonic() - generated_at, 3), tokens=(result.get("usage") or {}).get("total_tokens"), status="ok")
        with commit_job(actor, request_id):
            if mode == "tutor":
                updated = update_session(actor, session, **result.pop("state_changes"))
            if mode != "tutor":
                history = [] if session["strict"] else (session["history"] + [{"role": "user", "content": question}, {"role": "assistant", "content": result["answer"]}])[-4:]
                updated = update_session(actor, session, history=history)
    for entry in result.get("trace", []):
        log_event(request_id, "tool", seconds=entry.get("seconds"), status=entry.get("status"))
```

**连续代码 2/2**（接在上一段后，不额外增加缩进）

```python
    usage = result.get("usage")
    total_tokens = (sum(u["total_tokens"] for u in usage) if usage and all(u and u.get("total_tokens") is not None for u in usage) else None) if isinstance(usage, list) else (usage or {}).get("total_tokens")
    log_event(request_id, "answer", seconds=round(time.monotonic() - started, 3), status="ok", method=method,
              input_chars=len(question), source_count=len(result.get("sources", [])), tool_count=len(result.get("trace", [])), tokens=total_tokens)
    # 页面接收自己这次写入后的版本，下一次保存进度不必拿旧版本碰运气。
    return {**result, "trace_id": request_id, "session_revision": updated["revision"]}
```

**写完后应当怎样：**取消后的迟到回答不会写入历史，成功时返回新 revision。

### 第 8 步：草稿生成也遵守取消结果

草稿和问答共用取消与提交边界；进入短提交后再由数据库核对生成时的会话版本。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    response = complete([{"role": "system", "content": f"依据当前对话整理{task}。只写草稿，不声称已经保存或改变进度。不补充对话之外的事实。"}, *session["history"]])
    # 生成期间会话可能改变；保存函数会在事务内核对最初读取的版本。
    body = response["message"].get("content") or ""
    return actions.draft(actor, kind, body, request_id, session_id=session_id, session_revision=session["revision"])
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    with job(actor, request_id) as flag:
        if flag.is_set():
            raise ValueError("请求已取消。")
        response = complete([{"role": "system", "content": f"依据当前对话整理{task}。只写草稿，不声称已经保存或改变进度。不补充对话之外的事实。"}, *session["history"]])
        body = response["message"].get("content") or ""
        # 取消和落库竞争时只允许一个先完成；随后还会在事务内复核会话版本。
        with commit_job(actor, request_id):
            return actions.draft(actor, kind, body, request_id, session_id=session_id, session_revision=session["revision"])
```

**写完后应当怎样：**取消后不新增待确认草稿。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/state.py companion/operations.py companion/service.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

不能只让聊天支持停止，却让笔记继续在后台写入。 取消后不新增待确认草稿。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
