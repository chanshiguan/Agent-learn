# 用一个 API 接住读者的问题

本单元预计 **45—60 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《检验改写有没有改变原问题》](0039-query-rewrite.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 先把已有行为包成服务

前面每次在终端提问。API 让页面也能调用同一套检索与回答。FastAPI 接收请求，Pydantic 校验字段，随后调用已经认识的 `retrieve()` 和 `answer()`。这一步不改变文学回答的质量。

HTTP 可以先理解为一次有约定格式的往返：浏览器发送 JSON，服务返回状态码与 JSON。成功不只是 200，还要有页面能理解的回答和来源。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：写下网页服务需要的依赖

先增加 HTTP 接口，再增加页面；模型凭据仍只由后端读取。

**写在哪里：**项目根目录下的 `requirements-web.txt`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```text
# 第 13 章才安装：页面服务与离线 API 验证，不包含 Embedding 权重。
fastapi==0.162.2
uvicorn==0.54.0
httpx==0.28.1
```

**写完后应当怎样：**安装 FastAPI、Uvicorn 和 HTTP 测试客户端，不安装前端框架。

```bash
# 按刚亲手保存的清单安装本节所需依赖；只安装库，不会自动运行项目。
python -m pip install -r requirements-web.txt
```

### 第 2 步：先写这个文件需要的导入

把终端已经跑通的 retrieve 和 answer 接到 HTTP，先不引入会话与账号。

**写在哪里：**项目根目录下的 `companion/basic_app.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：把终端已经跑通的 retrieve 和 answer 接到 HTTP，先不引入会话与账号。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field
from .rag import retrieve, answer

app = FastAPI(title="伴读问答：第一次 API")
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 3 步：把 Question 接入最小服务

先规定输入格式和长度，未知字段拒绝，减少把任意对象传进业务函数的风险。

**写在哪里：**项目根目录下的 `companion/basic_app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 目的：先规定输入格式和长度，未知字段拒绝，减少把任意对象传进业务函数的风险。
# 预期：空问题和多余字段会得到 422。
class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=800)
    book: str = "狂人日记"
```

**写完后应当怎样：**空问题和多余字段会得到 422。

### 第 4 步：把 ask 接入最小服务

接口只连接已经写出的检索与回答；模型错误转成清楚的服务错误。

**写在哪里：**项目根目录下的 `companion/basic_app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：接口只连接已经写出的检索与回答；模型错误转成清楚的服务错误。
# 预期：POST /api/ask 返回答案与来源；失败时不回传供应商凭据。
@app.post("/api/ask")
def ask(body: Question):
    try:
        return answer(body.question, retrieve(body.question, book=body.book))
    except Exception:
        # 面向读者只说明暂时不可用；调试时从终端分层检查，不展示供应商凭据或路径。
        raise HTTPException(503, "暂时无法完成回答，请检查本地资料与模型服务。")
```

**写完后应当怎样：**POST /api/ask 返回答案与来源；失败时不回传供应商凭据。

### 第 5 步：把 health 接入最小服务

先提供一个最小存活检查，区分进程没启动与业务依赖未准备。

**写在哪里：**项目根目录下的 `companion/basic_app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：先提供一个最小存活检查，区分进程没启动与业务依赖未准备。
# 预期：GET /healthz 返回 alive；它不承诺模型已经就绪。
@app.get("/healthz")
def health():
    return {"status": "alive"}
```

**写完后应当怎样：**GET /healthz 返回 alive；它不承诺模型已经就绪。

## 运行并观察

```bash
# 安装网页服务依赖，复用已有虚拟环境；不需要另学一套前端框架。
python -m pip install -r requirements-web.txt
# 启动本章最小服务，只监听本机；终端会持续运行，用 Ctrl+C 停止。
python -m uvicorn companion.basic_app:app --host 127.0.0.1 --port 8000
```

保持第 4 章模型变量有效，并已完成 ingest。浏览器打开 `http://127.0.0.1:8000/docs`，输入序言关系的问题。当前页面固定使用关键词检索，便于先验证完整请求链。它没有账号，不能直接开放给其他人。

## 看懂一次错误

把问题留空尝试提交，再临时关闭模型服务提交正常问题。前者应由输入校验阻止；后者应显示服务暂不可用，而不是一直转圈或出现上一次答案。恢复模型后重试。

源码里 `response_model` 并不是此例的重点，先看输入模型与 `POST /api/ask`：限制问题长度与未知字段，避免随便接收整个对象。不要把 API key 写进浏览器 JavaScript。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 页面应该直接带 API key 调模型吗？
2. 浏览器收到 200 是否说明答案有据？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**页面应该直接带 API key 调模型吗？**

不应该。服务端持有模型凭据，页面只访问自己的业务 API，避免把密钥交给每个浏览器。

**浏览器收到 200 是否说明答案有据？**

只说明请求成功返回；仍需看引用与人工评测，不能把传输成功当语义正确。

**通过证据：**本机网页成功问答一次，并记录空输入与模型不可用时的界面表现。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

这一节用 FastAPI 自带的 `/docs` 操作：展开 `POST /api/ask` → Try it out → 填 question 和 book → Execute。先观察状态码和 JSON；下一单元才创建阅读页面，当前 `/` 尚未提供页面。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from fastapi.testclient import TestClient
from companion.basic_app import app
with TestClient(app) as c:
    assert c.get("/healthz").status_code==200
    assert c.post("/api/ask",json={"question":""}).status_code==422
print("存活和输入校验通过；正常回答仍需真实模型")
PY
```

**预期：**空输入被拒绝；此检查未调用生成模型。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
