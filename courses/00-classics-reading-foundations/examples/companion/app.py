# 目的：在最小 API 的基础上增加会话路由，继续只监听本机；没有账号验证时不得对外开放。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import os
import time
import uuid
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, ConfigDict, Field
from . import service, state, actions, auth, operations
from .files import load

MODE = os.environ.get("APP_MODE","lab")
CHAPTER = int(os.environ.get("COURSE_CHAPTER","21"))
if MODE not in {"lab","authenticated"}:
    raise ValueError("APP_MODE 只能是 lab 或 authenticated。")
if os.environ.get("APP_ENV")=="production" and MODE!="authenticated":
    raise ValueError("生产配置禁止测试身份。")
state.initialize()
app = FastAPI(title="名著伴读助手",docs_url=None,redoc_url=None)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=os.environ.get("ALLOWED_HOSTS","localhost,127.0.0.1,testserver").split(","))
web = Path(__file__).with_name("web")
app.mount("/static",StaticFiles(directory=web),name="static")

# 目的：拒绝未约定字段，作品名由服务端检查是否存在。
# 预期：请求不能随意追加身份参数。
class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")

# 目的：拒绝未约定字段，作品名由服务端检查是否存在。
# 预期：请求不能随意追加身份参数。
class NewSession(Input):
    book: str = Field(default="狂人日记", min_length=1, max_length=80)

# 目的：会话 ID、请求 ID 和问题分别校验；本阶段不接受尚未实现的模式。
# 预期：错误格式在业务代码之前被拒绝。
class Question(Input):
    session_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    question: str = Field(min_length=1, max_length=800)
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    mode: Literal["qa", "tutor", "agent"] = "qa"

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
    bearer = request.headers.get("Authorization", "")
    if not bearer.startswith("Bearer "):
        raise HTTPException(401, "请先登录。")
    return auth.authenticate(bearer[7:])

# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.exception_handler(PermissionError)
def denied(request, error):
    return JSONResponse(status_code=403, content={"detail": str(error)})

# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.exception_handler(ValueError)
def invalid(request, error):
    return JSONResponse(status_code=409, content={"detail": str(error)})

# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.exception_handler(RequestValidationError)
def bad_input(request, error):
    # 默认校验结果可能带回原始输入；这里只返回位置，避免回显口令和私人问题。
    return JSONResponse(status_code=422, content={"detail": "输入格式不合要求。", "fields": [list(e["loc"]) for e in error.errors()]})

# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.get("/healthz")
def health():
    return {"status": "alive"}

# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.get("/api/config")
def config():
    return {"mode": MODE, "chapter": CHAPTER}

# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.get("/api/books")
def books(who=Depends(actor)):
    return sorted({c["book"] for c in load("corpus.json", {"chunks": []})["chunks"] if c["tenant"] == who.tenant})

# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.get("/api/sessions")
def sessions(who=Depends(actor)):
    return state.list_sessions(who)

# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.post("/api/sessions")
def new_session(body: NewSession, who=Depends(actor)):
    books = {c["book"] for c in load("corpus.json", {"chunks": []})["chunks"] if c["tenant"] == who.tenant}
    if body.book not in books:
        raise HTTPException(404, "没有可用的这部作品资料。")
    return state.create_session(who, body.book)

# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.get("/api/sessions/{identity}")
def session(identity: str, who=Depends(actor)):
    return state.get_session(who, identity)

# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.delete("/api/sessions/{identity}")
def remove_session(identity: str, who=Depends(actor)):
    state.delete_session(who, identity)
    return {"deleted": True}

# 目的：沿用刚写出的状态和服务函数；接口只做输入、身份与输出的连接。
# 预期：路径对应一个已经存在的业务行为，不导入后面的审批或账号模块。
@app.post("/api/ask")
def ask(body: Question, request: Request, who=Depends(actor)):
    request.state.trace_id = body.request_id
    return service.ask(who, body.session_id, body.question, body.request_id, body.mode, os.environ.get("RETRIEVAL", "keyword"))

# 目的：页面文件将跟着本章一步步创建，不靠预置模板。
# 预期：完成页面文件后 / 才能显示会话界面。
@app.get("/")
def index():
    return FileResponse(web / "index.html")

# 目的：请求带上页面读到的 revision；范围改变时清空旧对话，防止后文残留。
# 预期：旧 revision 返回 409，成功写入返回新版本。
class Progress(Input):
    progress: int = Field(ge=0, le=10000)
    strict: bool
    revision: int = Field(ge=0)

# 目的：请求带上页面读到的 revision；范围改变时清空旧对话，防止后文残留。
# 预期：旧 revision 返回 409，成功写入返回新版本。
@app.patch("/api/sessions/{identity}")
def progress(identity: str, body: Progress, who=Depends(actor)):
    current = state.get_session(who, identity)
    # 用页面实际读到的版本比较，才能拒绝后来到达的旧页面更新。
    if current["revision"] != body.revision:
        raise ValueError("阅读记录已更新，请重新打开当前记录后再保存进度。")
    # 进度或模式改变时丢弃旧上下文，避免旧对话把后文带进受限阅读。
    return state.update_session(who, current, history=[], progress=body.progress, strict=body.strict, phase="question")

# 目的：接口复用 service.source，不再写一套可能遗漏条件的 SQL 或检索。
# 预期：越界返回403，允许的来源返回正文。
@app.get("/api/sources/{source_id}")
def source(source_id: str, session_id: str, who=Depends(actor)):
    return service.source(who, session_id, source_id)

# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
class Draft(Input):
    session_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    kind: Literal["note", "review_plan"]

# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
class Confirmation(Input):
    revision: int = Field(ge=1)
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    confirmed: bool

# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
@app.post("/api/drafts")
def make_draft(body: Draft, who=Depends(actor)):
    return service.make_draft(who, body.session_id, body.kind, body.request_id)

# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
@app.get("/api/drafts")
def drafts(who=Depends(actor)):
    return actions.pending(who)

# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
@app.post("/api/drafts/{identity}/approve")
def approve(identity: str, body: Confirmation, who=Depends(actor)):
    return actions.approve(who, identity, body.revision, body.digest, body.confirmed)

# 目的：分别验证预览、确认和正式读取，确认请求必须带具体版本与摘要。
# 预期：未确认的内容只在草稿列表中，不在正式笔记中。
@app.get("/api/notes")
def notes(who=Depends(actor)):
    return actions.notes(who)

# 目的：只允许本人修改 pending 状态的内容，已经提交的笔记不通过此入口重写。
# 预期：编辑后需要重新预览。
class Revision(Input):
    body: str = Field(min_length=1, max_length=6000)

# 目的：只允许本人修改 pending 状态的内容，已经提交的笔记不通过此入口重写。
# 预期：编辑后需要重新预览。
@app.patch("/api/drafts/{identity}")
def revise(identity: str, body: Revision, who=Depends(actor)):
    return actions.revise(who, identity, body.body)

# 目的：输入格式、账号校验和令牌撤销分别负责，错误不回显原口令。
# 预期：登录成功取得短期令牌，退出后令牌失效。
class Login(Input):
    tenant: str = Field(min_length=1, max_length=40)
    username: str = Field(min_length=1, max_length=40)
    password: str = Field(min_length=1, max_length=128)

# 目的：输入格式、账号校验和令牌撤销分别负责，错误不回显原口令。
# 预期：登录成功取得短期令牌，退出后令牌失效。
@app.post("/api/login")
def login(body: Login, request: Request):
    if MODE != "authenticated":
        raise HTTPException(409, "当前是本机练习模式。")
    return auth.login(body.tenant, body.username, body.password, request.client.host if request.client else "unknown")

# 目的：输入格式、账号校验和令牌撤销分别负责，错误不回显原口令。
# 预期：登录成功取得短期令牌，退出后令牌失效。
@app.post("/api/logout")
def logout(request: Request, who=Depends(actor)):
    auth.logout(request.headers.get("Authorization", "")[7:])
    return {"logged_out": True}

# 目的：复用 Actor 与关联检查，不接受页面自己声称的家长角色。
# 预期：未关联或非家长请求被拒绝。
@app.get("/api/family/{child}")
def family(child: str, who=Depends(actor)):
    return state.family_report(who, child)

# 目的：所有入口复用已认证身份；删除说明当前业务库范围，不能声称远端备份同步消失。
# 预期：反馈返回回执，删除撤销令牌并清空当前个人内容。
class Feedback(Input):
    category: Literal["答非所问", "证据不符", "内容不适合", "其他"]
    trace_id: str = Field(pattern=r"^[a-f0-9]{32}$")

# 目的：所有入口复用已认证身份；删除说明当前业务库范围，不能声称远端备份同步消失。
# 预期：反馈返回回执，删除撤销令牌并清空当前个人内容。
@app.post("/api/feedback")
def feedback(body: Feedback, who=Depends(actor)):
    identity = uuid.uuid4().hex
    with state.connect() as db:
        db.execute("INSERT INTO feedback VALUES(?,?,?,?,?,?)", (identity, who.tenant, who.user, body.category, body.trace_id, time.time()))
    return {"receipt": identity}

# 目的：所有入口复用已认证身份；删除说明当前业务库范围，不能声称远端备份同步消失。
# 预期：反馈返回回执，删除撤销令牌并清空当前个人内容。
@app.delete("/api/personal-data")
def erase(who=Depends(actor)):
    return state.erase_personal_data(who)

# 目的：公开错误只说明暂时不可用和编号；日志只记异常类型。
# 预期：服务故障有503和trace_id，不回显原始请求。
@app.exception_handler(Exception)
def unavailable(request, error):
    trace_id = getattr(request.state, "trace_id", uuid.uuid4().hex)
    operations.log_event(trace_id, "failure", status=type(error).__name__)
    # 不把模型供应商的原始响应、密钥或文件路径回传给读者。
    return JSONResponse(status_code=503, content={"detail": "服务暂时不可用，请稍后重试。", "trace_id": trace_id})

# 目的：no-store 避免私人响应进入缓存，CSP 限制页面脚本和资源来源。
# 预期：页面脚本来自自己服务，不能执行模型返回的脚本标签。
@app.middleware("http")
async def response_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    return response

# 目的：资料、状态库、所选索引和生成模型都需要就绪；不通过时先定位依赖，不直接重启一切。
# 预期：healthz 可200而readyz为503；恢复依赖后才返回ready。
@app.get("/readyz")
def ready():
    corpus = load("corpus.json")
    if not corpus:
        raise HTTPException(503, "资料尚未准备好。")
    with state.connect() as db:
        db.execute("SELECT 1 FROM sessions LIMIT 1")
    if os.environ.get("RETRIEVAL", "keyword") != "keyword":
        from .vectors import connection
        current = load("index.json")
        if not current or current["corpus_revision"] != corpus["revision"]:
            raise HTTPException(503, "资料索引待更新。")
        with connection() as db:
            db.get_collection(current["collection"])
    from .models import client
    sdk, model = client(timeout=5)
    with sdk:
        available = {item.id for item in sdk.models.list().data}
    if model not in available:
        raise HTTPException(503, "生成模型尚未就绪。")
    return {"status": "ready", "revision": corpus["revision"][:12]}

# 目的：名额不足返回429，取消接口按本人身份查任务，读者能区分等待与拒绝。
# 预期：忙时可稍后重试，不显示上一次答案。
@app.exception_handler(TimeoutError)
def busy(request, error):
    return JSONResponse(status_code=429, content={"detail": "当前请求较多，请稍后再试。"}, headers={"Retry-After": "3"})

# 目的：名额不足返回429，取消接口按本人身份查任务，读者能区分等待与拒绝。
# 预期：忙时可稍后重试，不显示上一次答案。
@app.post("/api/cancel/{request_id}")
def cancel(request_id: str, who=Depends(actor)):
    return operations.cancel(who, request_id)
