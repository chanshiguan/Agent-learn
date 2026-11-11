# 用状态图重现同一个批准流程（2/2：把本节能力连起来）

本单元预计 **30—45 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《用状态图重现同一个批准流程（1/2：把本节能力连起来）》](0055-langgraph-checkpoint.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

上一小节已经把前一部分写进项目。这一节继续处理 `companion/__main__.py`；先回想它接收什么、交给谁，再往下写。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：给命令入口增加 graph

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        from .actions_cli import main
        main()
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        from .actions_cli import main
        main()
    elif command == "graph":
        from .graph_cli import main
        main()
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。


## 让刚写的代码生效

如果上一节的服务仍在运行，先在那个终端按 Ctrl+C 停止。确认当前终端仍有模型配置，再从项目根目录重启，随后刷新浏览器。没有使用自动重载时，仅保存文件不会更新运行中的 Python 进程。

```bash
# 载入刚写完的接口、业务模块和页面；等终端显示服务启动后再进行下面的交互。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```


## 运行并观察

```bash
# 安装本课程固定的图框架与 SQLite 检查点依赖；业务数据仍由原来的 actions 表负责。
python -m pip install --user --break-system-packages -r requirements-graph.txt
# 新建一份未确认草稿，记下 ID，避免拿已经提交的动作混淆实验。
python -m companion action draft --text "通过状态图恢复的阅读笔记，请先核对这段具体内容。"
# 输入该 ID，流程暂停并写检查点；命令退出后仍能恢复。
python -m companion graph start
# 在新进程中输入同一 ID，查看预览并输入 YES；预期仅保存一条笔记。
python -m companion graph resume
# 重跑恢复与删除检查；这里检查真实 SQLite 检查点，不需要模型服务。
```

`graph-preview.json` 是命令行单任务练习的预览文件，一次只练一个暂停任务。实际多用户网页使用服务端动作数据；本课没有把这个文件当成多用户消息队列。

## 验证规则没有因迁移而变松

start 后用 action revise 修改草稿，再执行 resume，旧预览应拒绝。重新 start 获取新预览再确认。间隔超过有效期也应拒绝。框架恢复时节点可能重新执行，因此副作用仍在原来的幂等事务里。

对比第 19 章和本章：最终笔记内容、批准版本、重复提交结果应一致。它不是把整个 Agent 循环全部换成框架；本章迁移的是同一审批工作流，先验证等价再扩大范围。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 检查点代替业务数据库了吗？
2. 为什么恢复节点内仍要幂等？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**检查点代替业务数据库了吗？**

没有。检查点负责流程暂停与继续，actions/notes 负责版本、权限、批准和最终副作用。

**为什么恢复节点内仍要幂等？**

恢复可能重新执行节点，网络也可能重试。没有幂等会重复写入，即使框架成功保存了流程状态。

**通过证据：**跨进程恢复、旧预览拒绝、重复恢复单条结果三项证据；能解释手写与框架职责。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/04-agent-frameworks.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion import state,actions
from companion.graph import run_review
a=state.Actor("demo","reader-a");d=actions.draft(a,"note","图流程练习","graph-test")
p=run_review(a,d["id"]);assert p["status"]=="awaiting_confirmation"
r=run_review(a,d["id"],{"revision":d["revision"],"digest":d["digest"],"confirmed":True})
assert r["status"]=="finished"
print("同一批准经过图暂停与恢复成功")
PY
```

**预期：**图复用原批准，不另造第二套写入规则。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
