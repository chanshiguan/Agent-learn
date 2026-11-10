# 用状态图重现同一个批准流程

本单元预计 **40—60 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 现在才引入框架

StateGraph 用节点表示步骤、边表示顺序；checkpointer 把状态保存到磁盘；interrupt 在需要用户决定时暂停；Command(resume=...) 带着确认继续。thread_id 区分任务，这里同时包含租户、读者和动作 ID。

```bash
# 安装本课程固定的图框架与 SQLite 检查点依赖；业务数据仍由原来的 actions 表负责。
python -m pip install -r requirements-graph.txt
# 新建一份未确认草稿，记下 ID，避免拿已经提交的动作混淆实验。
python -m companion action draft --text "通过状态图恢复的阅读笔记，请先核对这段具体内容。"
# 输入该 ID，流程暂停并写检查点；命令退出后仍能恢复。
python -m companion graph start
# 在新进程中输入同一 ID，查看预览并输入 YES；预期仅保存一条笔记。
python -m companion graph resume
# 重跑恢复与删除检查；这里检查真实 SQLite 检查点，不需要模型服务。
PYTHONPATH=../tests python -m unittest test_companion.CompanionTests.test_graph_restart_resume_and_erase -v
```

`graph-preview.json` 是命令行单任务练习的预览文件，一次只练一个暂停任务。实际多用户网页使用服务端动作数据；本课没有把这个文件当成多用户消息队列。

## 验证规则没有因迁移而变松

start 后用 action revise 修改草稿，再执行 resume，旧预览应拒绝。重新 start 获取新预览再确认。间隔超过有效期也应拒绝。框架恢复时节点可能重新执行，因此副作用仍在原来的幂等事务里。

对比第 19 章和本章：最终笔记内容、批准版本、重复提交结果应一致。它不是把整个 Agent 循环全部换成框架；本章迁移的是同一审批工作流，先验证等价再扩大范围。

## 对照完整实现

先读上面标出的函数，再展开文件。配套包已包含它及依赖文件；不需要把后续章节一起学完。注释重点解释为什么这样处理，以及出错时应发生什么。

<details><summary>展开本单元完整源码：companion/graph.py</summary>

{{code:companion/graph.py}}

</details>

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
