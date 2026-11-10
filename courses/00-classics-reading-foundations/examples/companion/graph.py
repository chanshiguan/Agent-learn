# 目的：图只管理流程暂停与恢复，最终批准仍调用已经测试过的 actions.approve。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import sqlite3
from typing import TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from .actions import pending, approve
from .files import data_dir, digest, save
from .state import personal_data_lock

# 目的：明确图中保存动作 ID 和结果，不能保存一份绕过权限的任意执行计划。
# 预期：重启后可恢复同一批准，旧版本、越权和重复恢复仍受原事务约束。
class ReviewState(TypedDict, total=False):
    action_id: str
    result: dict

# 目的：暂停时给具体预览，恢复时带回确认；线程 ID 包含本人身份，检查点写入与预览同锁。
# 预期：重启后可恢复同一批准，旧版本、越权和重复恢复仍受原事务约束。
def run_review(actor, action_id, decision=None):
    def review(state):
        candidates = {a["id"]: a for a in pending(actor)}
        item = candidates.get(state["action_id"])
        if item is None:
            raise PermissionError("当前读者没有此待确认动作。")
        confirmation = interrupt({"id": item["id"], "body": item["body"], "revision": item["revision"], "digest": item["digest"]})
        if not isinstance(confirmation, dict):
            raise ValueError("恢复时必须带回对具体版本的确认。")
        return {"result": approve(actor, item["id"], confirmation.get("revision"), confirmation.get("digest"), confirmation.get("confirmed"))}

    flow = StateGraph(ReviewState)
    flow.add_node("review", review)
    flow.add_edge(START, "review")
    flow.add_edge("review", END)
    # 线程标识包含租户和本人，知道 action_id 也不能恢复另一个人的流程。
    config = {"configurable": {"thread_id": digest([actor.tenant, actor.user, action_id])}}
    with personal_data_lock(), sqlite3.connect(data_dir() / "checkpoints.sqlite3", check_same_thread=False) as db:
        graph = flow.compile(checkpointer=SqliteSaver(db))
        if decision is not None:
            checkpoint = graph.get_state(config)
            if not checkpoint.values:
                raise ValueError("没有可恢复的检查点，请先运行 start。")
            if not checkpoint.next:
                return {"status": "finished", "result": checkpoint.values.get("result")}
        value = Command(resume=decision) if decision is not None else {"action_id": action_id}
        result = graph.invoke(value, config=config)
        # 预览也在同一锁内保存，避免删除完成后 CLI 又把旧正文写回磁盘。
        if "__interrupt__" in result:
            preview = result["__interrupt__"][0].value
            save("graph-preview.json", preview)
            return {"status": "awaiting_confirmation", "preview": preview}
        return {"status": "finished", "result": result.get("result")}

# 目的：为删除个人内容准备本人图线程清理，不能只删除业务表却留下检查点副本。
# 预期：重启后可恢复同一批准，旧版本、越权和重复恢复仍受原事务约束。
def erase_threads(actor):
    with sqlite3.connect(data_dir() / "checkpoints.sqlite3", check_same_thread=False) as db:
        saver = SqliteSaver(db)
        for item in pending(actor):
            saver.delete_thread(digest([actor.tenant, actor.user, item["id"]]))
