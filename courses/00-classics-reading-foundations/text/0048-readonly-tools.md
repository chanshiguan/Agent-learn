# 先由程序员调用工具，再交给模型

本单元预计 **45—60 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《检验提示有没有帮助读者思考》](0047-tutor-review.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 工具先是一段普通程序

“让 Agent 查资料”可以拆成三个动作：search_lectures 查询当前范围，read_source 读取本轮已见来源，get_progress 查看当前进度。先证明这些动作独立正确，再让模型决定调用顺序。

工具 schema 告诉模型工具名、用途和参数结构；服务端仍要重新校验，因为 schema 不是执行权限。`ReaderTools` 初始化时绑定 actor 与 session_id，模型参数里没有可任意更改的 tenant 或 owner。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：先写这个文件需要的导入

工具复用检索与状态，身份由服务端传入，模型参数不能另选读者。

**写在哪里：**项目根目录下的 `companion/tools.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：工具复用检索与状态，身份由服务端传入，模型参数不能另选读者。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
from .rag import retrieve, budget
from .state import get_session
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 2 步：把三项只读能力收进一个工具入口

先验证参数，再按工具名分派；read_source 只读取本次见过的来源，不能任意访问资料库。

**写在哪里：**项目根目录下的 `companion/tools.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**self.actor 和 self.session_id 把一组工具绑定到已验证的本人会话。模型只能选择允许的工具与参数，不能通过参数换成别人的身份。

```python
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
```

**写完后应当怎样：**程序员可以调用查询进度、查讲稿和回查来源，未知工具被拒绝。


## 让刚写的代码生效

如果上一节的服务仍在运行，先在那个终端按 Ctrl+C 停止。确认当前终端仍有模型配置，再从项目根目录重启，随后刷新浏览器。没有使用自动重载时，仅保存文件不会更新运行中的 Python 进程。

```bash
# 载入刚写完的接口、业务模块和页面；等终端显示服务启动后再进行下面的交互。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```


## 运行并观察

```bash
# 创建虚构读者的独立练习会话，直接调用工具；预期得到当前范围内讲稿，而不是生成回答。
python -c 'from companion.state import Actor,initialize,create_session; from companion.tools import ReaderTools; initialize(); a=Actor("demo","reader-a"); s=create_session(a); t=ReaderTools(a,s["id"]); print(t.execute("search_lectures",{"query":"文言文序言"}))'
```

打开 `tools.py`，顺着 execute 看：先确认当前会话归属，再验证字段与长度，再执行固定函数。它没有 eval，也不接收任意 shell 命令或文件路径。

## 动手改一个参数

将 query 改成空字符串，应该被拒绝；添加 tenant=other 字段，也应该被拒绝。新建一个工具实例后直接读一个从未检索过的来源，应失败。这样来源工具不能变成“知道 ID 就能随便读”的入口。

只读工具仍可能泄露资料，因此权限检查不能等到写操作才开始。下一单元把这组边界写成可重复测试。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. schema 写了 additionalProperties=false 就够了吗？
2. 为什么身份绑定在工具实例上？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**schema 写了 additionalProperties=false 就够了吗？**

不够。模型和客户端都可能发异常参数，服务端必须再做白名单与类型、范围校验。

**为什么身份绑定在工具实例上？**

身份应来自服务端已经核验的请求上下文，不能由模型通过参数指定要冒充谁。

**通过证据：**三次直接调用的结果：合法查询成功、空问题拒绝、额外身份参数拒绝。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/03-tool-use-and-hello-agent.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter4)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion import state
from companion.tools import ReaderTools
a=state.Actor("demo","reader-a");s=state.create_session(a);t=ReaderTools(a,s["id"])
assert t.execute("get_progress",{})["progress"]==0
hits=t.execute("search_lectures",{"query":"文言文序言"})
assert hits and t.execute("read_source",{"source_id":hits[0]["id"]})["id"]==hits[0]["id"]
print("三个只读工具由程序员直接调用通过")
PY
```

**预期：**工具先由确定的程序调用验证；本节没有让模型选工具。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
