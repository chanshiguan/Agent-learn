# 目的：把终端已经跑通的 retrieve 和 answer 接到 HTTP，先不引入会话与账号。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field
from .rag import retrieve, answer

app = FastAPI(title="伴读问答：第一次 API")

# 目的：先规定输入格式和长度，未知字段拒绝，减少把任意对象传进业务函数的风险。
# 预期：空问题和多余字段会得到 422。
class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=800)
    book: str = "狂人日记"

# 目的：接口只连接已经写出的检索与回答；模型错误转成清楚的服务错误。
# 预期：POST /api/ask 返回答案与来源；失败时不回传供应商凭据。
@app.post("/api/ask")
def ask(body: Question):
    try:
        return answer(body.question, retrieve(body.question, book=body.book))
    except Exception:
        # 面向读者只说明暂时不可用；调试时从终端分层检查，不展示供应商凭据或路径。
        raise HTTPException(503, "暂时无法完成回答，请检查本地资料与模型服务。")

# 目的：先提供一个最小存活检查，区分进程没启动与业务依赖未准备。
# 预期：GET /healthz 返回 alive；它不承诺模型已经就绪。
@app.get("/healthz")
def health():
    return {"status": "alive"}

# 目的：使用与代码相邻的 web 目录，避免启动目录变化导致找错文件。
# 预期：GET / 返回页面，页面继续调用同源 /api/ask。
@app.get("/")
def index():
    return FileResponse(Path(__file__).with_name("web") / "basic.html")
