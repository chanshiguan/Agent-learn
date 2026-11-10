"""先固定教学流程，再讨论是否需要 Agent 自主安排教学动作。"""
from .rag import answer, retrieve
from .state import get_session


def teach_turn(actor, session_id, text, method="keyword", direct=False):
    session = get_session(actor, session_id)
    if direct:
        hits = retrieve(text, actor.tenant, session["book"], method, session["progress"] if session["strict"] else None)
        return answer(text, hits, strict=bool(session["strict"]))
    phase = session["phase"]
    if phase == "question":
        result = {"answer": "从刚读到的讲稿中选一句你印象深的内容：你怎样理解它？请先说理由，也可以提出不同看法。", "sources": [], "citations": []}
        changes = {"history": [], "phase": "hint"}
    elif phase == "hint":
        result = {"answer": "先把你的看法和证据分开：是哪几个词让你这样想？它们有没有别的解释？下一步输入你想核对的具体问题。", "sources": [], "citations": []}
        changes = {"history": [{"role": "user", "content": text}], "phase": "explain"}
    else:
        hits = retrieve(text, actor.tenant, session["book"], method, session["progress"] if session["strict"] else None)
        result = answer(text, hits, history=[] if session["strict"] else session["history"], strict=bool(session["strict"]))
        changes = {"history": [], "phase": "question"}
    return {**result, "next_phase": changes["phase"], "state_changes": changes}
