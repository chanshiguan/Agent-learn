# 让结果、轨迹和恢复都有证据

## 单元一：先定义一条完整评测题

题目不是一句输入。至少包括初始资料/状态、用户输入、成功条件、禁止动作、评分方式、版本与必要参考答案。同一句“继续”在 waiting 与 completed 状态有不同正确行为。任务 outcome 是最终结果；trajectory 是过程中采取了什么动作。结果正确但越权读取，也不能通过。

规则评分适合格式、字段、数值与状态；人工评分适合语义与开放任务；模型评分需要用人工样本校准。三者可以组合，但不要用模型赞同替代来源核对。机器无法判断时返回待复核，而不是默认成功。[结业 B 的评分示例](../../capstone-b/text/03-workshop.md)展示了这个区别。

一题多次 trial 用来观察波动。开发集用于改进，保留集只在固定方案后检验。看过并根据其答案改系统的题，应归回开发集。pass@k 衡量多次至少一次成功，连续可靠性关注多次都成功，不能把两种指标互换宣传。

## 单元二：一份可恢复研究摘要

案例使用固定的可信演示资料，生成可核查摘录，保存草稿和用于检查内容是否变化的哈希值，等待用户决定，最后写本地账本和运行收据。不发送邮件，不发布内容。每次执行下面的命令，都会启动一个新进程。

```bash
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/07-multi-agent-production/examples/production_case.py /tmp/course7-case-1
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/07-multi-agent-production/examples/production_case.py /tmp/course7-case-1 --decision approve
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/07-multi-agent-production/examples/production_case.py /tmp/course7-case-1 --decision approve
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/07-multi-agent-production/examples/production_case.py /tmp/course7-case-2
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/07-multi-agent-production/examples/production_case.py /tmp/course7-case-2 --decision reject
```

第一次 waiting；第二次 completed，账本一条；第三次仍一条；拒绝的任务 cancelled，账本没有它的执行记录。若你在等待期间修改 draft.json，恢复必须拒绝。请按[综合题完整答案](06-complete-project.md)用 revise 创建第二版，旧版取消，新版重新批准；该章也给出三份来源和五类评测的完整参考。

{{code:../examples/production_case.py}}

它复用原课 06-safe-execution 的完整状态与账本实现，完整源码页可直接查看。那份实现先检查幂等键和动作是否匹配，再协调账本与状态：如果效果已经写入而状态没更新，恢复只补状态，不重复效果。它是顺序执行示例，不宣称多进程并发事务；并发部署需要数据库唯一键、事务或可靠队列。

## 单元三：什么才是有用的日志

Trace 对应一项任务，span 对应某个模型/检索/工具步骤。应能回答：在哪里开始，调用什么，耗时多少，结果状态是什么，哪一步失败。关联 task_id、模型/提示/数据版本，才可重现。用量未知用 null，固定摘录明确无模型调用。

不要记录凭证、完整私人资料和不必要的模型内容。使用 OpenAI tracing、OpenTelemetry、Langfuse 或 Phoenix 时，采集、导出、存储和展示是不同层；本地推理也可能配置云端日志。先决定是否导出、脱敏内容、谁能访问与保留多久。增加一个本地 processor 不一定移除默认 exporter，需明确配置实际链路。

观测能证明发生过哪些步骤，不能仅凭“没有异常”证明业务结果正确。第一个排错动作是找同一任务 ID 的失败步骤，而不是重新运行覆盖证据。

## 单元四：批准、检查点、会话与幂等

批准应绑定用户、具体动作和版本。草稿改变后以前的批准失效；拒绝是终止决定，不是临时警告。OpenAI Agents SDK 的 interruption 与 RunState 用于保存和恢复批准上下文；普通聊天 Session 只保存会话，不自动代替审批状态。

LangGraph Checkpointer 按 thread 保存图的运行状态，Store 则用于跨会话数据。`interrupt` 恢复时节点可能重跑，副作用应拆出去并用幂等控制。SQLite 写成功和外部服务发送成功不是同一事务，所以需要外部收据协调。重试只用于可重试错误，参数错误和用户拒绝不该反复尝试。

## 单元五：本地服务与部署契约

原 05-deploy 例子提供 `/health` 与 `/chat`。health 只应证明进程与必要依赖状态，不能靠它判断所有模型任务都正确。chat 对输入做字段与长度检查，给出超时、模型不可用和错误响应，不能把内部栈、密钥返回调用者。

先运行原目录 test.py；再按 README 在本机启动服务，验证正常输入、空请求、错误字段和模型停止四类。生产还需身份校验、每用户权限、并发/队列、重试和幂等、配置与密钥分离、数据保留、回滚。Dockerfile 打包依赖不自动实现这些业务控制。

缓存稳定前缀可以减少重复计算，但缓存不是输出缓存、不是数据库记忆或检查点。流式响应便于及时显示，不代表半截输出可当最终答案；收齐结束状态再验收。模型或工具版本改变后要重新跑固定题集，缓存命中与费用应读实际 usage，不按字符估算。

## 本课最终评分表

| 项目 | 通过证据 | 必须退回的情况 |
|---|---|---|
| 五类评测题 | 正常、无资料、非法工具、预算、拒绝均有预期与实测 | 仅打印总分，没有逐题结果 |
| 可观测性 | 能用 task_id 定位一处故障 | 把凭证或无关原文写进日志 |
| 批准恢复 | 换进程恢复、拒绝、重复恢复、草稿变更四项输出 | 改了草稿仍沿用旧批准 |
| 本地接口 | 正常和异常请求都有明确状态 | 模型失败却返回成功文本 |
| 解释 | 分清结果、轨迹、状态与外部效果 | 将 mock 通过称为真实模型可靠 |

综合参考的完整草稿、状态、账本、收据就在你运行的任务目录。独立作业换一份资料，保留相同验证。可读文件本身就是结果，不能以聊天里写“已完成”替代它。
