"""第 13 章的最小 API：先把已有问答接到浏览器，不同时引入账号与会话。"""
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field
from .rag import retrieve, answer

app = FastAPI(title="伴读问答：第 13 章")


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=800)
    book: str = "狂人日记"


@app.get("/")
def index():
    return FileResponse(Path(__file__).with_name("web") / "basic.html")


@app.post("/api/ask")
def ask(body: Question):
    try:
        return answer(body.question, retrieve(body.question, book=body.book))
    except Exception:
        # 面向读者只说明暂时不可用；调试时从终端分层检查，不展示供应商凭据或路径。
        raise HTTPException(503, "暂时无法完成回答，请检查本地资料与模型服务。")


@app.get("/healthz")
def health():
    return {"status": "alive"}
