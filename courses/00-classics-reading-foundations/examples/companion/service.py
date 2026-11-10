# 目的：让 API 与会话问答共用一条业务路径；本节只处理普通问答。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import time
from .corpus import visible
from .files import load
from .rag import retrieve, answer
from .tutor import teach_turn
from .agent import run_agent
from . import actions
from .models import complete
from .operations import log_event, job, commit_job
from .state import get_session, update_session

# 目的：先查归属，再检索当前作品，最后使用版本号保存；身份不能交给模型决定。
# 预期：回答后 history 最多保留两轮，返回新 revision 供下一次更新使用。
def ask(actor, session_id, question, request_id, mode="qa", method="keyword"):
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
    usage = result.get("usage")
    total_tokens = (sum(u["total_tokens"] for u in usage) if usage and all(u and u.get("total_tokens") is not None for u in usage) else None) if isinstance(usage, list) else (usage or {}).get("total_tokens")
    log_event(request_id, "answer", seconds=round(time.monotonic() - started, 3), status="ok", method=method,
              input_chars=len(question), source_count=len(result.get("sources", [])), tool_count=len(result.get("trace", [])), tokens=total_tokens)
    # 页面接收自己这次写入后的版本，下一次保存进度不必拿旧版本碰运气。
    return {**result, "trace_id": request_id, "session_revision": updated["revision"]}

# 目的：读取 ID 仍需带本人会话和当前进度，不能把引用链接当成访问凭证。
# 预期：已失去可见范围的旧引用会被拒绝。
def source(actor, session_id, source_id):
    session = get_session(actor, session_id)
    corpus = load("corpus.json", {"chunks": []})
    allowed = visible(corpus["chunks"], actor.tenant, session["book"], session["progress"] if session["strict"] else None)
    hit = next((c for c in allowed if c["id"] == source_id), None)
    if hit is None:
        raise PermissionError("当前阅读范围内没有此来源。")
    return hit

# 目的：保存时核对本人会话和生成时版本，避免阅读范围改变后又留下旧内容。
# 预期：得到的是待确认草稿，不会自动变成正式笔记。
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
        body = response["message"].get("content") or ""
        # 取消和落库竞争时只允许一个先完成；随后还会在事务内复核会话版本。
        with commit_job(actor, request_id):
            return actions.draft(actor, kind, body, request_id, session_id=session_id, session_revision=session["revision"])
