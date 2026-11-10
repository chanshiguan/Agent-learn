# 两位读者，不共用一段对话（2/5：连接接口与业务）

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《两位读者，不共用一段对话（1/5：保存会话状态）》](0042-reader-sessions.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

上一小节已经能把会话存进 SQLite，并验证旧版本不能覆盖新对话。本节新建 `companion/app.py`，约定请求格式和本机测试身份，再把“列出会话、创建会话”接到已有状态函数。接口只负责接收和校验，不另写一套存储。下一小节补读取、删除、问答入口和页面结构，之后页面才能使用这些接口。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：先写这个文件需要的导入

在最小 API 的基础上增加会话路由，继续只监听本机；没有账号验证时不得对外开放。

**写在哪里：**项目根目录下的 `companion/app.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：在最小 API 的基础上增加会话路由，继续只监听本机；没有账号验证时不得对外开放。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import os
import uuid
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field
from . import service, state
from .files import load

MODE = "lab"
CHAPTER = 14
state.initialize()
app = FastAPI(title="名著伴读助手",docs_url=None,redoc_url=None)
web = Path(__file__).with_name("web")
app.mount("/static",StaticFiles(directory=web),name="static")
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 2 步：定义 Input 输入约定

拒绝未约定字段，作品名由服务端检查是否存在。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**Input 是后续请求类型共用的基础类。把 extra=forbid 放在这里，继承它的接口都会拒绝多余字段，避免每个接口各写一套规则。

```python
# 目的：拒绝未约定字段，作品名由服务端检查是否存在。
# 预期：请求不能随意追加身份参数。
class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")
```

**写完后应当怎样：**请求不能随意追加身份参数。

### 第 3 步：定义 NewSession 输入约定

拒绝未约定字段，作品名由服务端检查是否存在。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**NewSession 继承刚才的 Input，再声明创建会话需要的 book。默认书名只减少输入，服务端仍要检查这部作品是否存在于资料库。

```python
# 目的：拒绝未约定字段，作品名由服务端检查是否存在。
# 预期：请求不能随意追加身份参数。
class NewSession(Input):
    book: str = Field(default="狂人日记", min_length=1, max_length=80)
```

**写完后应当怎样：**请求不能随意追加身份参数。

### 第 4 步：为一次会话提问规定输入

会话 ID、请求 ID 和问题分别校验；本阶段不接受尚未实现的模式。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**session_id 指已有会话，request_id 区分一次请求，两者不是同一个编号。Literal 只允许当前已经接通的 qa 模式；长度与格式检查先于模型调用。

```python
# 目的：会话 ID、请求 ID 和问题分别校验；本阶段不接受尚未实现的模式。
# 预期：错误格式在业务代码之前被拒绝。
class Question(Input):
    session_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    question: str = Field(min_length=1, max_length=800)
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    mode: Literal["qa"] = "qa"
```

**写完后应当怎样：**错误格式在业务代码之前被拒绝。

### 第 5 步：只允许本机选择两个虚构读者

这是观察数据隔离的练习入口，不能把任意请求头当成真实账号登录。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：这是观察数据隔离的练习入口，不能把任意请求头当成真实账号登录。
# 预期：非本机请求被拒绝，读者只能是 reader-a 或 reader-b。
def actor(request: Request):
    if MODE == "lab":
        if request.client and request.client.host not in {"127.0.0.1", "::1", "testclient"}:
            raise HTTPException(403, "测试身份仅允许本机练习。")
        reader = request.headers.get("X-Lab-Reader", "reader-a")
        if reader not in {"reader-a", "reader-b"}:
            raise HTTPException(400, "无效的测试读者。")
        return state.Actor("demo", reader)
    raise HTTPException(403,"当前只支持本机测试身份。")
```

**写完后应当怎样：**非本机请求被拒绝，读者只能是 reader-a 或 reader-b。

### 第 6 步：增加 denied 这个接口或错误出口

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.exception_handler(PermissionError)
def denied(request, error):
    return JSONResponse(status_code=403, content={"detail": str(error)})
```

**写完后应当怎样：**路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。

### 第 7 步：增加 invalid 这个接口或错误出口

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.exception_handler(ValueError)
def invalid(request, error):
    return JSONResponse(status_code=409, content={"detail": str(error)})
```

**写完后应当怎样：**路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。

### 第 8 步：增加 bad_input 这个接口或错误出口

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.exception_handler(RequestValidationError)
def bad_input(request, error):
    # 默认校验结果可能带回原始输入；这里只返回位置，避免回显口令和私人问题。
    return JSONResponse(status_code=422, content={"detail": "输入格式不合要求。", "fields": [list(e["loc"]) for e in error.errors()]})
```

**写完后应当怎样：**路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。

### 第 9 步：增加 health 这个接口或错误出口

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.get("/healthz")
def health():
    return {"status": "alive"}
```

**写完后应当怎样：**路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。

### 第 10 步：增加 config 这个接口或错误出口

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.get("/api/config")
def config():
    return {"mode": MODE, "chapter": CHAPTER}
```

**写完后应当怎样：**路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。

### 第 11 步：增加 books 这个接口或错误出口

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.get("/api/books")
def books(who=Depends(actor)):
    return sorted({c["book"] for c in load("corpus.json", {"chunks": []})["chunks"] if c["tenant"] == who.tenant})
```

**写完后应当怎样：**路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。

### 第 12 步：增加 sessions 这个接口或错误出口

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.get("/api/sessions")
def sessions(who=Depends(actor)):
    return state.list_sessions(who)
```

**写完后应当怎样：**路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。

### 第 13 步：增加 new_session 这个接口或错误出口

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.post("/api/sessions")
def new_session(body: NewSession, who=Depends(actor)):
    books = {c["book"] for c in load("corpus.json", {"chunks": []})["chunks"] if c["tenant"] == who.tenant}
    if body.book not in books:
        raise HTTPException(404, "没有可用的这部作品资料。")
    return state.create_session(who, body.book)
```

**写完后应当怎样：**路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/app.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。 路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter9)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
