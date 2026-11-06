# 第七课：可测、可看、可停、可恢复

第六课已经能检索资料并回答；这一课要判断它是否可靠，以及出错后怎样停止和恢复。按“评测 → 日志与链路 → 批准和恢复 → 本地部署”完成四个核心练习，再把它们接成研究助理。辩论、流式输出和缓存是选修，可在核心练习之后做。

## 不是先上服务器

本课沿用“有收据的研究助理”：先找资料、生成摘要，展示草稿并等待批准，最后记录结果。准备上线时，除了能启动程序，还要判断任务是否完成、错误出在哪里、什么时候该停，以及中断后怎样恢复。

推荐顺序：Eval → Observability → Approval/Recovery → Deploy。原课六个代码目录全部本地保留；其中四个核心练习和辩论、Streaming/缓存两个选修分开学习。

## 1. 十九个词按职责理解

| 职责 | 术语与含义 |
|---|---|
| 安排执行 | Harness 是运行设施；Loop 是反复决策；Workflow Graph 是路径；Orchestration 是调度；Multi-Agent 是多个角色；Handoff 是控制权交接 |
| 判断正确 | Eval 是评测；Outcome 是实际结果；Trajectory 是行动轨迹；Grader 是评分器；Evaluation Harness 是可重复运行评测的设施 |
| 看见过程 | Trace 是一次任务的完整链；Observability 是通过日志、指标和链路诊断系统 |
| 约束恢复 | Guardrail 是边界检查；Human Approval 是具体动作的人类批准；Checkpoint 是存档；Resume 是继续；Recovery 是故障恢复；Idempotency 是重复请求不重复产生效果 |

Prompt 是指令材料，Context 是本轮可见的信息。Harness 不会取代 Prompt；Eval 也不会替你执行工具，它们解决不同问题。

## 2. Harness 的八项工作

组织流程；控制工具权限；管理上下文、状态和检查点；处理重试、恢复和幂等；检查边界与批准；记录遥测；运行评测；限制成本和延迟。这是教学划分，不是国际标准。

普通 for 循环、一次任务里的工具循环、跨会话长期任务循环要区分。长期任务不能只靠聊天历史无限增长：需要明确目标、已完成事项、下一步、恢复点和终止条件。Graph 适合分支、暂停、恢复，并不要求每个节点都是 Agent。

## 3. 先写可判定的 Eval case

一题应包含输入、初始资料/状态、成功条件、禁止动作、可选参考答案、评分器和版本元数据。例如：“资料缺失时必须说明未知，不调用发送工具”同时检验 outcome 与 trajectory。

Development 用来发现问题并改实现；frozen holdout 在事前冻结，不参与调参。Baseline 是改动前的同口径结果；regression 是原来能做的任务退步。每个 trial 是一次独立试跑；模型有随机性，不能仅凭一次失败断言版本退步。

程序评分适合字段、计算、文件和状态；模型评分适合某些开放质量判断，但必须用人工样本校准；人工评分贵，却能发现评分器盲区。不要让被评模型自己说“完成”就满分。检查轨迹不等于强迫所有正确方案走同一路线，应只约束必要动作与禁止动作。

原核心练习 1 是 examples/upstream/02-eval。保留原题、grader 和结果文件；改一次 Prompt 后把每题差异列出来，不只报平均分。

## 4. Trace 不只是打印回答

为每个任务生成 task ID；为模型、工具、检索、审核建立子步骤。记录开始结束时间、成功/错误类型、重试原因、token、来源和状态版本。延迟用单调时钟测量，日志的现实时间另存，避免系统时间调整影响计算。

不要记录密钥，默认不收集完整用户资料。Trace 可能发往外部平台：OpenAI Agents SDK 默认 tracing 行为需要显式检查，本地模型不保证遥测也留在本地。只做本地实验时关闭外传或配置受控导出器。

原核心练习 2 是 03-observability。先用离线响应测日志结构，再用真实模型测 token/延迟；mock 的耗时和用量只反映模拟测试，不能作为真实模型的指标。

## 5. 批准绑定什么

批准发送时，要让用户确认具体收件人、内容、附件和版本。任何关键字段改变后，都应重新检查。批准输入来自可信用户界面，不能读取模型产生的 approved=true 就放行。

Checkpoint 存任务 ID、状态版本、待执行动作和批准状态；Resume 必须验证它属于当前任务。损坏、过期、拒绝、身份不符时停止。恢复不是把异常吞掉再重试所有动作。

## 6. 最容易漏掉的崩溃窗口

外部动作成功 → 程序还没保存“完成”就崩溃 → 重启读到“未完成” → 又执行一次。这就是幂等键要在真正产生副作用的一端生效的原因。

本课 06-safe-execution 的“副作用”只是写 JSON 收据。它先写 ledger，再保存完成状态；重启发现 ledger 已有相同 key 就不重复追加。不同内容不能复用相同 key。这个文件示例面向顺序执行，并不提供多进程并发事务保证；生产应使用数据库唯一约束、事务或服务端幂等 API。

```bash
# 运行 courses/07-multi-agent-production/examples/upstream/06-safe-execution/starter.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/07-multi-agent-production/examples/upstream/06-safe-execution/starter.py --state /tmp/ai-learn-state.json --ledger /tmp/ai-learn-ledger.json start --action "保存虚构研究摘要收据" --key course7-demo-v1
# 运行 courses/07-multi-agent-production/examples/upstream/06-safe-execution/starter.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/07-multi-agent-production/examples/upstream/06-safe-execution/starter.py --state /tmp/ai-learn-state.json --ledger /tmp/ai-learn-ledger.json resume --decision approve
```

第二条再运行一次，ledger 应只有一条。要测试新动作，换独立状态路径与 key；保留旧收据，用新记录保存这次运行结果。上面只写本地演示文件，不会发布真实摘要。

## 7. 部署、健康检查和回滚

原核心练习 4 在 05-deploy，包含完整 /health、/chat 服务和 Dockerfile。健康检查告诉你进程在，readiness 应反映是否能处理请求；单纯返回 200 不代表模型连接有效。

部署前明确认证、输入大小、并发、超时、费用上限、错误响应、版本与回滚。缺少密钥或模型不可用时，应返回失败信息，不能返回看似正常的答案。保存当前模型、Prompt、工具 Schema 和数据版本，回归时才知道差异来源。教材制作不替你启动公共服务或部署云端。

## 8. 两个选修与成本优化

辩论让正反角色与裁决者交换意见，适合有证据与规则的检查。先保留单 Agent baseline；增加角色也可能只是共同强化错误。Streaming 降低用户看到第一段内容的等待，但完整任务耗时未必降低；不要在参数未组装完成时执行工具。Prompt caching 对重复前缀有帮助，要用实际 usage 验证命中，不能把 cached_tokens 字段的存在当缓存一定生效。

缓存、批处理、路由、小模型都需要对比质量、成本和延迟；提高并发可能触发限流。OpenRouter 是模型入口，Pi/OpenCode 是运行工具，Orca/QM 等是协作环境，不属于同一替代层。

## 9. 基准与作弊式优化

SWE-bench 测软件修复，Terminal-Bench 测终端任务，OSWorld 测桌面操作，tau 系列测交互工具任务，GAIA 测综合助理。比较模型时还要比较任务集、环境、工具、harness、超时、grader 和 trial 数。

Reward hacking 指系统利用评分漏洞得到高分却没有完成真实目标，例如把测试删掉、伪造完成文件。隐藏测试、隔离环境、检查最终外部状态与人工抽查互相补充。不能把排行榜名次直接当自己业务的验收结果。
