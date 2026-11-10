# 给一次提问一个可以追踪的编号

本单元预计 **35—50 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 用户说“刚才那次很慢”，怎么找

trace_id 把同一次请求的检索、生成、工具与最终结果连起来。它不是学生身份，也不需要放入姓名。页面反馈保存这个编号，开发者才知道应查哪一次运行。

正常模式提问一次，在 Network 响应中记下 trace_id，再查看 `data/live/events.jsonl`。普通问答会记录 retrieve、generate、answer；Agent 还记录工具结果。受限模式没有生成调用，不能给它编造 token 消耗。

```bash
# 只查看最近的结构化事件，预期是耗时、数量和状态，不包含问题正文、口令或完整讲稿。
python -c 'from companion.files import data_dir; p=data_dir()/"events.jsonl"; print("\n".join(p.read_text().splitlines()[-12:]) if p.exists() else "尚无事件，请先在网页提问")'
```

把 trace_id 相同的行放在一起：检索用了多久，生成用了多久，返回了几个来源，有无工具拒绝。时间是各阶段实际墙钟耗时，不能简单把所有嵌套阶段相加当作总耗时。

## 练一次故障定位

停止模型服务，再发一个需要生成的普通问题。预期页面显示通用失败与可追踪编号，日志保存错误类型，不把供应商原始响应回传给学生。恢复服务后重试，用新的 trace 区分。

如果检索很快、生成很慢，先查模型服务与输入长度；若工具反复拒绝，先看参数协议，而不是直接加大并发。日志帮助缩小问题，不替代实际重现。

## 对照完整实现

先读上面标出的函数，再展开文件。配套包已包含它及依赖文件；不需要把后续章节一起学完。注释重点解释为什么这样处理，以及出错时应发生什么。

<details><summary>展开本单元完整源码：companion/operations.py</summary>

{{code:companion/operations.py}}

</details>

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. trace_id 与用户 ID 有什么不同？
2. 为何不把完整问题写进日志方便排查？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**trace_id 与用户 ID 有什么不同？**

trace_id 标记一次请求，用户 ID 标记归属。定位故障通常不需要把个人身份写入每条日志。

**为何不把完整问题写进日志方便排查？**

那会扩大私人内容的存储与传播。默认只记录必要状态；确需内容取证时另走受控、最少化流程。

**通过证据：**一条成功和一条故障请求的事件链，能按阶段解释慢点或失败位置。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
