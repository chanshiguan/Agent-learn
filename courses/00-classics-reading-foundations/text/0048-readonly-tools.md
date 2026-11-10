# 先由程序员调用工具，再交给模型

本单元预计 **35—50 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 工具先是一段普通程序

“让 Agent 查资料”可以拆成三个动作：search_lectures 查询当前范围，read_source 读取本轮已见来源，get_progress 查看当前进度。先证明这些动作独立正确，再让模型决定调用顺序。

工具 schema 告诉模型工具名、用途和参数结构；服务端仍要重新校验，因为 schema 不是执行权限。`ReaderTools` 初始化时绑定 actor 与 session_id，模型参数里没有可任意更改的 tenant 或 owner。

```bash
# 创建虚构读者的独立练习会话，直接调用工具；预期得到当前范围内讲稿，而不是生成回答。
python -c 'from companion.state import Actor,initialize,create_session; from companion.tools import ReaderTools; initialize(); a=Actor("demo","reader-a"); s=create_session(a); t=ReaderTools(a,s["id"]); print(t.execute("search_lectures",{"query":"文言文序言"}))'
```

打开 `tools.py`，顺着 execute 看：先确认当前会话归属，再验证字段与长度，再执行固定函数。它没有 eval，也不接收任意 shell 命令或文件路径。

## 动手改一个参数

将 query 改成空字符串，应该被拒绝；添加 tenant=other 字段，也应该被拒绝。新建一个工具实例后直接读一个从未检索过的来源，应失败。这样来源工具不能变成“知道 ID 就能随便读”的入口。

只读工具仍可能泄露资料，因此权限检查不能等到写操作才开始。下一单元把这组边界写成可重复测试。

## 对照完整实现

先读上面标出的函数，再展开文件。配套包已包含它及依赖文件；不需要把后续章节一起学完。注释重点解释为什么这样处理，以及出错时应发生什么。

<details><summary>展开本单元完整源码：companion/tools.py</summary>

{{code:companion/tools.py}}

</details>

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
