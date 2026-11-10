"""第 13 章起的同源页面和 API；第 21 章切换认证模式。"""
import os
import time
import uuid
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import actions, auth, operations, service, state
from .files import load

MODE = os.environ.get("APP_MODE", "lab")
CHAPTER = int(os.environ.get("COURSE_CHAPTER", "14"))
if MODE not in {"lab", "authenticated"}:
    raise ValueError("APP_MODE 只能是 lab 或 authenticated。")
if os.environ.get("APP_ENV") == "production" and MODE != "authenticated":
    raise ValueError("生产配置禁止使用测试身份。")
state.initialize()
app = FastAPI(title="名著伴读助手", docs_url=None, redoc_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(","))
web = Path(__file__).with_name("web")
app.mount("/static", StaticFiles(directory=web), name="static")


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Login(Input):
    tenant: str = Field(min_length=1, max_length=40)
    username: str = Field(min_length=1, max_length=40)
    password: str = Field(min_length=1, max_length=128)


class NewSession(Input):
    book: str = Field(default="狂人日记", min_length=1, max_length=80)


class Question(Input):
    session_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    question: str = Field(min_length=1, max_length=800)
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    mode: Literal["qa", "tutor", "agent"] = "qa"


class Progress(Input):
    progress: int = Field(ge=0, le=10000)
    strict: bool
    revision: int = Field(ge=0)


class Draft(Input):
    session_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    kind: Literal["note", "review_plan"]


class Confirmation(Input):
    revision: int = Field(ge=1)
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    confirmed: bool


class Revision(Input):
    body: str = Field(min_length=1, max_length=6000)


class Feedback(Input):
    category: Literal["答非所问", "证据不符", "内容不适合", "其他"]
    trace_id: str = Field(pattern=r"^[a-f0-9]{32}$")


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


@app.exception_handler(PermissionError)
def denied(request, error):
    return JSONResponse(status_code=403, content={"detail": str(error)})


@app.exception_handler(ValueError)
def invalid(request, error):
    return JSONResponse(status_code=409, content={"detail": str(error)})


@app.exception_handler(TimeoutError)
def busy(request, error):
    return JSONResponse(status_code=429, content={"detail": "当前请求较多，请稍后再试。"}, headers={"Retry-After": "3"})


@app.exception_handler(Exception)
def unavailable(request, error):
    trace_id = getattr(request.state, "trace_id", uuid.uuid4().hex)
    operations.log_event(trace_id, "failure", status=type(error).__name__)
    # 不把模型供应商的原始响应、密钥或文件路径回传给读者。
    return JSONResponse(status_code=503, content={"detail": "服务暂时不可用，请稍后重试。", "trace_id": trace_id})


@app.get("/")
def index():
    return FileResponse(web / "index.html")


@app.get("/healthz")
def health():
    return {"status": "alive"}


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


@app.get("/api/config")
def config():
    return {"mode": MODE, "chapter": CHAPTER}


@app.post("/api/login")
def login(body: Login, request: Request):
    if MODE != "authenticated":
        raise HTTPException(409, "当前是本机练习模式。")
    return auth.login(body.tenant, body.username, body.password, request.client.host if request.client else "unknown")


@app.post("/api/logout")
def logout(request: Request, who=Depends(actor)):
    auth.logout(request.headers.get("Authorization", "")[7:])
    return {"logged_out": True}


@app.get("/api/books")
def books(who=Depends(actor)):
    return sorted({c["book"] for c in load("corpus.json", {"chunks": []})["chunks"] if c["tenant"] == who.tenant})


@app.get("/api/sessions")
def sessions(who=Depends(actor)):
    return state.list_sessions(who)


@app.post("/api/sessions")
def new_session(body: NewSession, who=Depends(actor)):
    books = {c["book"] for c in load("corpus.json", {"chunks": []})["chunks"] if c["tenant"] == who.tenant}
    if body.book not in books:
        raise HTTPException(404, "没有可用的这部作品资料。")
    return state.create_session(who, body.book)


@app.get("/api/sessions/{identity}")
def session(identity: str, who=Depends(actor)):
    return state.get_session(who, identity)


@app.patch("/api/sessions/{identity}")
def progress(identity: str, body: Progress, who=Depends(actor)):
    current = state.get_session(who, identity)
    # 用页面实际读到的版本比较，才能拒绝后来到达的旧页面更新。
    if current["revision"] != body.revision:
        raise ValueError("阅读记录已更新，请重新打开当前记录后再保存进度。")
    # 进度或模式改变时丢弃旧上下文，避免旧对话把后文带进受限阅读。
    return state.update_session(who, current, history=[], progress=body.progress, strict=body.strict, phase="question")


@app.delete("/api/sessions/{identity}")
def remove_session(identity: str, who=Depends(actor)):
    state.delete_session(who, identity)
    return {"deleted": True}


@app.post("/api/ask")
def ask(body: Question, request: Request, who=Depends(actor)):
    request.state.trace_id = body.request_id
    return service.ask(who, body.session_id, body.question, body.request_id, body.mode, os.environ.get("RETRIEVAL", "keyword"))


@app.post("/api/cancel/{request_id}")
def cancel(request_id: str, who=Depends(actor)):
    return operations.cancel(who, request_id)


@app.get("/api/sources/{source_id}")
def source(source_id: str, session_id: str, who=Depends(actor)):
    return service.source(who, session_id, source_id)


@app.post("/api/drafts")
def make_draft(body: Draft, who=Depends(actor)):
    return service.make_draft(who, body.session_id, body.kind, body.request_id)


@app.get("/api/drafts")
def drafts(who=Depends(actor)):
    return actions.pending(who)


@app.patch("/api/drafts/{identity}")
def revise(identity: str, body: Revision, who=Depends(actor)):
    return actions.revise(who, identity, body.body)


@app.post("/api/drafts/{identity}/approve")
def approve(identity: str, body: Confirmation, who=Depends(actor)):
    return actions.approve(who, identity, body.revision, body.digest, body.confirmed)


@app.get("/api/notes")
def notes(who=Depends(actor)):
    return actions.notes(who)


@app.get("/api/family/{child}")
def family(child: str, who=Depends(actor)):
    return state.family_report(who, child)


@app.post("/api/feedback")
def feedback(body: Feedback, who=Depends(actor)):
    identity = uuid.uuid4().hex
    with state.connect() as db:
        db.execute("INSERT INTO feedback VALUES(?,?,?,?,?,?)", (identity, who.tenant, who.user, body.category, body.trace_id, time.time()))
    return {"receipt": identity}


@app.delete("/api/personal-data")
def erase(who=Depends(actor)):
    return state.erase_personal_data(who)


@app.exception_handler(RequestValidationError)
def bad_input(request, error):
    # 默认校验结果可能带回原始输入；这里只返回位置，避免回显口令和私人问题。
    return JSONResponse(status_code=422, content={"detail": "输入格式不合要求。", "fields": [list(e["loc"]) for e in error.errors()]})


@app.middleware("http")
async def response_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    return response
