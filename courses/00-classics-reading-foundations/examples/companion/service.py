"""应用层连接资料、会话与模型；页面和命令行可以共用这些行为。"""
import time
from . import actions
from .agent import run_agent
from .corpus import visible
from .files import load
from .models import complete
from .operations import job, log_event
from .rag import answer, retrieve
from .state import get_session, update_session
from .tutor import teach_turn


def ask(actor, session_id, question, request_id, mode="qa", method="keyword"):
    started = time.monotonic()
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
        if flag.is_set():
            raise ValueError("请求已取消，本次结果没有写入阅读对话。")
        if mode == "tutor":
            updated = update_session(actor, session, **result.pop("state_changes"))
        if mode != "tutor":
            history = [] if session["strict"] else (session["history"] + [{"role": "user", "content": question}, {"role": "assistant", "content": result["answer"]}])[-4:]
            updated = update_session(actor, session, history=history)
    for entry in result.get("trace", []):
        log_event(request_id, "tool", seconds=entry.get("seconds"), status=entry.get("status"))
    usage = result.get("usage")
    total_tokens = (sum(u["total_tokens"] for u in usage) if usage and all(u and u.get("total_tokens") is not None for u in usage) else None) if isinstance(usage, list) else (usage or {}).get("total_tokens")
    log_event(request_id, "answer", seconds=round(time.monotonic() - started, 3), status="ok", method=method,
              input_chars=len(question), source_count=len(result.get("sources", [])), tool_count=len(result.get("trace", [])), tokens=total_tokens)
    # 页面接收自己这次写入后的版本，下一次保存进度不必拿旧版本碰运气。
    return {**result, "trace_id": request_id, "session_revision": updated["revision"]}


def source(actor, session_id, source_id):
    session = get_session(actor, session_id)
    corpus = load("corpus.json", {"chunks": []})
    allowed = visible(corpus["chunks"], actor.tenant, session["book"], session["progress"] if session["strict"] else None)
    hit = next((c for c in allowed if c["id"] == source_id), None)
    if hit is None:
        raise PermissionError("当前阅读范围内没有此来源。")
    return hit


def make_draft(actor, session_id, kind, request_id):
    existing = next((a for a in actions.pending(actor) if a["request_key"] == request_id), None)
    if existing:
        return existing
    session = get_session(actor, session_id)
    if session["strict"] or not session["history"]:
        raise ValueError("当前没有可整理的普通阅读对话；受限模式下请手动写笔记。")
    task = "一份简短阅读笔记" if kind == "note" else "一份三次复习计划草稿，日期由读者确认"
    with job(actor, request_id) as flag:
        if flag.is_set():
            raise ValueError("请求已取消。")
        response = complete([{"role": "system", "content": f"依据当前对话整理{task}。只写草稿，不声称已经保存或改变进度。不补充对话之外的事实。"}, *session["history"]])
        # 供应商可能已完成响应，但取消后的结果不再写入读者的待确认区。
        if flag.is_set():
            raise ValueError("请求已取消，本次结果没有保存为草稿。")
        body = response["message"].get("content") or ""
        return actions.draft(actor, kind, body, request_id, session_id=session_id)
