# 第四课：把 Agent Loop 变成可检查的工作流程

第三课已经把模型、工具和消息历史串成循环。这一课接着解决：步骤变多、需要分支和暂停时，怎样让流程仍然清楚、可检查。按目录先理解五种模式，运行原五题，再做动态分工和交接实验，最后把这些知识用在可恢复的摘要项目中。

## 本课要完成的东西

做一个“检索资料 → 写摘要 → 等待审阅 → 通过或拒绝”的小流程。你要能回答：谁决定下一步，状态放在哪里，失败后从哪里继续，以及为什么这里需要框架。第三课的模型、工具、消息历史、停止条件仍然存在，框架只是替你组织它们。

本课与原 Stage 4 一一对应：五个练习分别比较两个框架、角色分工、图式流程、CodeAct 与 JSON 工具、类型化输出。原例的完整 Python 代码、测试和 requirements 都在 examples/upstream，可以直接对照讲解查看。

## 1. 先分清四件事

**Loop** 是一次任务中反复“请求模型、执行工具、读结果”的循环。**Graph** 描述步骤和连接关系，例如审核通过走结束，审核不通过走修改。**Framework** 提供实现这些结构的类和函数。**多 Agent** 指多个具有独立职责或上下文的 Agent，不等于多调用几次模型。

可以只有一个 Agent，却使用图；也可以没有 Agent，只是固定函数依次执行；多个 Agent 也可以严格按程序写死的顺序工作。判断系统时看两个问题：下一步由程序决定还是由模型决定？各步骤共用一份上下文，还是各角色有自己的上下文？不要根据产品名字判断架构。

## 2. Node、Edge、State 如何配合

Node 是一个处理步骤，接收状态，返回状态更新；Edge 决定后继步骤。State 是运行中的共同记录，例如 query、evidence、draft、approved。它不是数据库的替代品，也不应该把 API key 放进去。

LangGraph 示例的 State.messages 使用 add_messages：节点返回的新消息要按 reducer 合并，而不是覆盖整段历史。普通字段通常是新值覆盖旧值。两个并行节点同时更新一个字段时，必须确定合并规则，否则可能冲突或丢失结果。把“消息追加”和“草稿替换”写成同一种操作会出错。

图从 START 开始，遇到 END 结束。conditional edge 的返回值必须在映射里，例如 tools 或 END；它可以来自确定性检查，也可以来自模型分类。recursion_limit 限制图运行步数，不能直接当作模型调用工具的次数上限；费用和工具计数仍应独立控制。

## 3. 五种协作方式怎样选

| 形状 | 数据如何走 | 适用证据 | 主要失败点 |
|---|---|---|---|
| 顺序 | 调研 → 写作 → 校对 | 后一步确实依赖前一步 | 前面的错误会一路传递 |
| 路由/交接 | 分类后把控制权交给专家 | 需要不同权限或知识范围 | 交接缺背景，或给多了权限 |
| 并行 | 独立子问题同时处理后合并 | 分支基本不依赖彼此 | 最慢分支、限流、答案冲突 |
| 主管—工作者 | 主管拆解、委派、收结果 | 任务边界在运行时才能确定 | 主管遗漏、重复派工、合并失真 |
| 评审/辩论 | 另一角色按标准检查 | 有独立证据与明确验收规则 | 相同模型共同犯错，讨论不产生新事实 |

Manager-as-tools 把专家当工具：专家返回结果，主管保留最终回答权。Handoff 把后续对话控制权转给接收者。二者都不是“把字符串换一个 role”；需要定义输入、输出、允许工具、异常和停止方式。

先做单 Agent 基线。只有评测证明单 Agent 的上下文混乱、权限不易隔离或可并行任务拖慢进度，再增加角色。并行耗时约由最慢分支加整合决定，不会自动变为原来的 1/N。

## 4. 用当前项目环境运行

主环境是 Python 3.14 与 OpenAI 3.37。第四课某些框架要求不同 Python 范围，因此用独立的 Python 3.11 环境。下面命令均在 ai-learn 根目录运行；已经在根目录时不要再 cd。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
/opt/homebrew/bin/python3.11 -m venv courses/04-agent-frameworks/.venv
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/04-agent-frameworks/.venv/bin/python -m pip install -r courses/04-agent-frameworks/examples/upstream/01-same-agent-two-frameworks/requirements.txt
# 运行 courses/04-agent-frameworks/examples/local_runner.py，按本行参数完成当前案例并核对输出。
courses/04-agent-frameworks/.venv/bin/python courses/04-agent-frameworks/examples/local_runner.py
```

创建环境与安装只做一次；换终端不用重复安装。若该机器没有所示 Python 3.11 路径，先安装 Python 3.11 或使用第三课已有解释器的实际基础路径。requirements 固定的是兼容范围，不能叫完整锁文件；安装后用 pip freeze 保存实际解析版本。对不同练习只安装它自己的 requirements；依赖冲突时每题单独环境。

原例默认 qwen2.5:3b。本地 local_runner.py 复用同一张图，显式使用已有 gemma4:e4b、关闭推理输出，并让本机 HTTP 客户端不读取代理环境；不会下载模型。其他原入口可以通过 MODEL=gemma4:e4b 指定模型。更换模型不保证工具协议与推理参数兼容；有错误先看原始响应。本地模型虽然没有按调用收取的 API 费用，运行时仍会占用内存。

## 5. 按原练习读实际代码

**练习 1：同题两个框架。** 01-same-agent-two-frameworks/starter.py 用 LangGraph；starter_crewai.py 用 CrewAI。保持工具、问题和评分不变，只换框架。search 是固定离线字典，不是联网搜索；问不到的键应该返回无记录。检查的是工具选择和结果使用，不能把字典里的演示数据当现实数据。

LangGraph 代码里 bind_tools 让模型知道工具；agent_node 生成新消息；tool_node 核对 name、args，再执行 search 并用同一 tool_call_id 回传；should_continue 看有没有 tool_calls；graph.invoke 开始工作。允许执行哪些工具，仍然要由你的程序规定。

**练习 2：角色分工。** 02-multi-agent-roles 用 CrewAI 的 Agent、Task、Crew。role/goal/backstory 帮模型理解职责，expected_output 说明任务产物，context 把前一个任务结果交给后一个任务。Task 不是线程；只有程序显式配置并行才会并行。如果两个角色拿到的都是同一份错误资料，多加一个角色也无法保证得出正确结论。

**练习 3：真正的暂停。** 03-graph-workflow 先分类，再查资料或直接生成，然后 interrupt 产生待审记录；同一个 thread_id 使用 Command(resume=...) 继续。InMemorySaver 只在当前进程里保留，关程序不等于有磁盘存档。interrupt 所在节点恢复时可能重跑，因此把不可重复动作放在确认后的独立节点，并加幂等键。示例里的 PUBLISHED 只是返回字符串，没有真实发布。

**练习 4：CodeAct 对比。** 04-codeact-vs-json-tool 比较模型输出代码和输出 JSON 工具参数。CodeAct 能组合多步计算，但能执行的操作更多，需要限制的范围也更大。原例使用 Smolagents Docker 执行器，不要为了省配置把它改成 unrestricted exec。Docker 本身也要限制挂载、网络、资源和凭证。先跑离线参数验证，再按原例 README 配置 Docker。

**练习 5：类型化输出。** 05-typed-agent 使用 Pydantic AI 的 output_type 和结果 output；字段校验要求非空 answer、0–1 confidence、非空来源列表。合法 confidence=0.99 不代表正确率 99%；来源字符串存在也不代表资料支持答案。除了检查输出结构，还要确认来源是否存在，以及来源是否支持回答中的每个判断。

## 6. Checkpoint、Handoff 与人工审核各解决什么

Checkpoint 保存运行状态；Handoff 改变接手者；Approval 决定具体动作能否继续。记录一句“已批准”但没有把审批绑定到具体草稿、目标与版本，无法防止草稿改了以后沿用旧批准。恢复前应检查任务 ID、状态版本、操作内容和执行收据。

人工审核不应该只是模型自问自答“我批准了吗”。本课 approve=True/False 是为了演示分支的测试输入；真实系统必须来自可信的人类界面。重复恢复不能重复发送或扣费，第七课会用收据与幂等键解决。

## 7. 最常见的排错顺序

导入失败先检查执行的 Python 路径与 requirements；连接失败检查 Ollama；工具没有调用检查模型能力、工具说明和原始消息；流程不结束检查条件边与上限；恢复后丢数据检查持久化与 thread_id；结果看似正确但没有工具轨迹，仍算未完成工具任务。把失败按这六类记录，比反复修改 Prompt 更容易定位。
