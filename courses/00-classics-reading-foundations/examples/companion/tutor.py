# 目的：先写固定三阶段伴读，观察教学效果后再决定是否需要 Agent 自主安排。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
from .rag import answer, retrieve
from .state import get_session

# 目的：先邀请读者表达，再追问证据，最后用已实现的有据回答核对；阶段更新交给服务层保存。
# 预期：前两步是明确教学话术，不冒充模型思考或文学评分。
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
