# 目的：工具复用检索与状态，身份由服务端传入，模型参数不能另选读者。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
from .rag import retrieve, budget
from .state import get_session

# 目的：先验证参数，再按工具名分派；read_source 只读取本次见过的来源，不能任意访问资料库。
# 预期：程序员可以调用查询进度、查讲稿和回查来源，未知工具被拒绝。
class ReaderTools:
    def __init__(self, actor, session_id, method="keyword"):
        self.actor, self.session_id, self.method = actor, session_id, method
        self.seen = {}

    def execute(self, name, arguments):
        if not isinstance(arguments, dict):
            raise ValueError("工具参数必须为对象。")
        session = get_session(self.actor, self.session_id)
        if name == "get_progress":
            if arguments:
                raise ValueError("读取进度不接受用户身份参数。")
            return {"book": session["book"], "progress": session["progress"], "strict": bool(session["strict"])}
        if name == "search_lectures":
            if set(arguments) != {"query"} or not isinstance(arguments["query"], str) or not 1 <= len(arguments["query"]) <= 500:
                raise ValueError("检索只接受 1—500 字符的 query。")
            hits = budget(retrieve(arguments["query"], self.actor.tenant, session["book"], self.method,
                                   session["progress"] if session["strict"] else None))
            self.seen.update({c["id"]: c for c in hits})
            return hits
        if name == "read_source":
            if set(arguments) != {"source_id"} or not isinstance(arguments["source_id"], str):
                raise ValueError("读取来源只接受 source_id。")
            source = self.seen.get(arguments["source_id"])
            if source is None:
                raise PermissionError("不能读取本次未检索到的来源。")
            return source
        raise ValueError("没有登记这个工具；不会执行模型提供的代码或命令。")

# 目的：JSON Schema 只说明能请求什么；真正的执行权限仍由 ReaderTools 检查。
# 预期：工具参数中没有 tenant 和 user，未知字段禁止。
SCHEMAS = [
    {"type": "function", "function": {"name": "search_lectures", "description": "在当前读者允许范围内查询讲稿。", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "read_source", "description": "读取本次已经检索到的一条来源。", "parameters": {"type": "object", "properties": {"source_id": {"type": "string"}}, "required": ["source_id"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "get_progress", "description": "查看当前会话的显式阅读进度。", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}},
]
