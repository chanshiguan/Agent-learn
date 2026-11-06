# 从一个状态对象，到可恢复的摘要流程

## 开始前：只准备本题需要的环境

你在 ai-learn 根目录执行以下命令。`.venv/bin/python` 是原项目解释器；`courses/.venv-verification/bin/python` 是后续课程独立验证环境。使用完整路径就不需要先 activate，也不重复 cd。`-m pip` 表示让这个解释器运行安装工具；`-r` 表示按文本中的包名安装。安装依赖只在环境缺包时做，不是每次运行前都要做。

```bash
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-verification/bin/python -m pip install -r courses/04-agent-frameworks/examples/requirements-summary.txt
```

本题不需要模型密钥或下载模型；摘要节点使用固定资料，让你先看清控制过程。原五个框架案例仍在完整代码页，各目录自己的 requirements 只装进独立环境。不要将其 openai 版本范围混装进主 `.venv`。

## 单元一：State、Node、Edge 各负责什么

把状态想成随流程传递的表单。本例有 topic（主题）、draft（草稿）、source_ids（来源）、checked（是否通过检查）、status（状态）、published（本地接受标记）。节点拿到表单，返回需要改变的字段；边决定下一个节点。

`TypedDict` 为开发者说明字段形状，并不是运行时安全检查器。`check_sources` 才执行真实检查。草稿被新草稿替换是合理的；消息历史通常需追加，所以原工具循环使用消息 reducer。两个并行节点都覆盖同一字段时，不能指望框架替你决定谁正确，应分别写字段或使用明确的合并规则。

流程为：开始 → 摘录资料 → 检查来源 → 等待人审 → 接受/拒绝 → 结束。无来源直接进入 blocked，不进入人审。图不是多 Agent 的同义词：这整个图可以只有一个生成节点，其余全是普通函数。

## 单元二：先观察暂停，再在另一进程恢复

以下路径请使用新的数据库名，避免与以前练习混淆。

```bash
# 运行 courses/04-agent-frameworks/examples/summary_workflow.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/04-agent-frameworks/examples/summary_workflow.py --db /tmp/course4-review.sqlite --thread first
# 运行 courses/04-agent-frameworks/examples/summary_workflow.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/04-agent-frameworks/examples/summary_workflow.py --db /tmp/course4-review.sqlite --thread first --decision reject
# 运行 courses/04-agent-frameworks/examples/summary_workflow.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/04-agent-frameworks/examples/summary_workflow.py --db /tmp/course4-review.sqlite --thread second
# 运行 courses/04-agent-frameworks/examples/summary_workflow.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/04-agent-frameworks/examples/summary_workflow.py --db /tmp/course4-review.sqlite --thread second --decision accept
# 运行 courses/04-agent-frameworks/examples/summary_workflow.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/04-agent-frameworks/examples/summary_workflow.py --db /tmp/course4-review.sqlite --thread missing --topic unknown
```

第一步应有 awaiting_review、published=false、next 含 review。第二步 rejected、published=false、next=[]。第四步 accepted、published=true；这里没有网络发布，只是本地字段。第五步 blocked，不能出现人审成功。

`thread_id` 是取回哪份执行状态的键；数据库是存状态的地方。只有键但换了数据库，读不回原任务。`Command(resume=...)` 将人的决定传给暂停点。中断节点恢复可能从头再跑，所以不要把付款、发送等副作用写在 interrupt 前。程序还拒绝对已经完成的任务重复批准。

## 单元三：完整答案及代码阅读顺序

先看 `execute` 如何打开 SQLite 与设置 thread，再看 `build` 的边，最后看三个节点。`check_sources` 不只检查 ID 存在，还要求固定摘要等于资料摘录。这是本题可确定评分的条件；接真实模型改写后，要增加人工事实复核，不能沿用“ID 存在就正确”。

{{code:../examples/summary_workflow.py}}

## 单元四：原五题怎样逐一学习

| 原题 | 先看代码哪一层 | 保持不变 | 必测失败 | 应交证据 |
|---|---|---|---|---|
| 01 同任务两个框架 | 工具定义与调用入口 | 同问题、同搜索资料、同模型 | 找不到资料 | 两次工具输入输出与结果，不只运行时间 |
| 02 角色协作 | researcher 的资料怎样给 writer | 相同任务 | 作者拿不到来源 | 各角色产物与交接资料 |
| 03 图式流程 | 条件边、状态、interrupt | 同一 thread | 人工拒绝、缺来源 | 暂停和恢复前后的状态 |
| 04 CodeAct/JSON | 参数调用与代码执行器 | 同计算任务 | 非法表达式 | 被拒路径；Docker 未运行不得写隔离通过 |
| 05 类型化输出 | Schema、output_type、返回 output | 同一问题 | confidence 越界、空 sources | 字段错误确实触发验证 |

执行每题前打开同目录 README 的代码页了解该题入口。本地的路径统一为 `courses/04-agent-frameworks/examples/upstream/题目目录/`，不用猜原仓库的 examples 路径。原题不是本章改造答案；上面的 summary_workflow 才对应“摘要＋来源检查＋跨进程人审”的新增综合要求。

## 单元五：何时选择哪种编排

固定审核顺序用代码边；资料不确定但动作集合明确，可以让模型选择工具。主管把专家当工具时，专家结果回主管整合；handoff 则把后续交互权交给接收者，需要连同目标、已知事实与限制交接。并行任务最好写不同结果字段，合并时指出冲突，不按最后返回者覆盖。

Crew 的角色适合表达分工，Flow 管事件和状态；Pydantic 管结构约束；CodeAct 用程序组合多步动作，但执行权限更大。没有失败证据时，从原 SDK 循环开始就够了。框架比较报告至少写透明度、恢复、类型约束、部署依赖和实际失败，不能用代码行数或角色数量判胜负。

## 课末验收补充

必须做到：缺少来源时阻止继续；用户拒绝后保持拒绝状态；换进程后仍能恢复；使用错误的 thread 不能恢复原任务；重复批准被拒绝。每项保留命令与输出。解释题：为什么 SQLite 不保证外部邮件只发一次？答案：数据库只保存图状态，邮件服务的效果是另一份状态，需幂等键与收据协调。完成这些后再接真实模型，能分清模型错误与流程错误。
