# 第五课：规则、Skill、MCP、Hook 和 Subagent

上一阶段练的是怎样完成一次任务；这一课练的是怎样把规则、重复步骤和外部工具组织成可复用的工作环境。从 B 线进入时，联系第四课的编排与状态理解；从 A 线进入时，沿用 A2 的规则卡和 Skill。先做首次会话，再读各部件的职责，最后在演示项目里逐项验证。

## 本课成果与路线

你会建立一套“规则说明 → 重复任务 → 工具连接 → 事件观察 → 独立检查”的工作方式。A 线核心对应原课 5.1–5.4，5.5–5.8 按需选学；B 线继续学习 5.5–5.7，5.8 SDK 托管选修。全部资料都在项目中。Claude Code 是一种宿主产品，不能因为你安装了 OpenAI Python SDK 就推断已安装或登录 Claude Code。当前 Codex 可用于理解相同概念，但配置与命令不能直接混用。

## 5.1 规则文件：告诉助手如何理解这个项目

CLAUDE.md 是经常需要加载的项目约定，适合放任务范围、关键入口、测试命令、输出要求。不要把整本手册和所有库文档都塞进去：上下文越长不一定越有帮助。较深的领域知识放独立文件，由规则文件给出索引。

用户级、项目级、本地私有级和组织策略的作用范围不同。CLAUDE.local.md 通常适合本机偏好；.claude/rules 可按路径组织更具体规则；@import 引入其他文件。自动记忆是工具写下的长期提示材料，不等于可信业务数据库。

当前官方文档已有 AGENTS.md 支持相关说明，具体行为取决于宿主版本与配置；不要记成“Claude 永远不读 AGENTS.md”。最可靠的检查是让当前会话报告生效规则，并用一个小任务观察是否遵守。提示层要求“只读”仍需执行权限落实。

原练习 1 的完整最小规则卡见 examples/CLAUDE.md。把它放进一个隔离的演示项目测试，别覆盖真实项目现有规则。说明文件本身不执行任何动作。

## 5.2 MCP：把外部能力接入宿主

Host 是用户使用的 Agent 应用；Client 是宿主里面连接服务器的组件；Server 暴露工具、资源或提示模板。Tools 是可执行能力；Resources 是可读取内容；Prompts 是可复用交互模板。MCP 解决连接和能力描述，不负责保证数据真实，也不会自动缩小进程权限。

本地 stdio 通常由宿主启动一个子进程，通过标准输入输出交换协议消息；因此日志不要随便 print 到 stdout，避免污染协议。远程服务使用 HTTP 等传输，需要处理身份认证、网络与版本兼容。本课核对的规范版本为 2026-07-28。Python 示例使用 1.x SDK 的 stdio 接口，由 SDK 处理它支持的协议；示例没有手写最新版传输实现。

examples/readonly_server.py 只暴露 read_note，限制 txt、目录和文件大小。resolve 后再检查目录，能阻止 ../ 和静态符号链接越界；教学目录必须由可信方控制，若攻击者可以并发更换符号链接，路径预检查还存在竞态，不能作为生产文件隔离方案。

原练习 4 的步骤是：创建只有虚构资料的目录 → 注册 server → 查看工具列表 → 读合法文件 → 验证越界被拒 → 移除连接。受限 MCP 工具只限制这条通道，不会同时限制宿主自己的 Shell 或 Read。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
/opt/homebrew/bin/python3.11 -m venv courses/05-claude-code-ecosystem/.venv
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/05-claude-code-ecosystem/.venv/bin/python -m pip install -r courses/05-claude-code-ecosystem/examples/requirements-mcp.txt
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude mcp add --transport stdio course-readonly -- /Users/owen/Documents/ai-learn/courses/05-claude-code-ecosystem/.venv/bin/python /Users/owen/Documents/ai-learn/courses/05-claude-code-ecosystem/examples/readonly_server.py
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude mcp list
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude mcp remove course-readonly
```

这些是供学习时运行的命令，制作教材时没有替你注册服务。首次使用 CLI 需完成它自己的登录；CLI 命令与 scope 以已安装版本的 help 为准。

## 5.3 Skill：把重复流程写成操作卡

Skill 有名称、description 和正文。description 帮宿主判断什么时候需要加载；正文规定操作步骤；references 放详解；scripts 放可执行逻辑。这种按需要分层加载资料的方式叫渐进披露：开始只让宿主知道“什么时候用”，执行任务时再读具体步骤。

disable-model-invocation:true 代表不由模型自行触发；user-invocable:false 则涉及用户是否能直接调用。二者不是同一件事，也不是所有宿主都支持全部字段。allowed-tools 表示预批准的工具，不应解释成绝对只允许这些工具。真正限制能力需要宿主的 tools 池、拒绝规则或权限控制。

原练习 2 可以使用 examples/skills/readme-check/SKILL.md。测试一个应该触发的请求和一个不应该触发的请求；再给缺文件、资料内含恶意指令的输入。验收重点是输出有证据、缺资料会停止、不会因为资料中的话扩大权限。原课程 tool-calling-tutor 的完整 Skill、引用文件和 evals 也已保留。

## 5.4 Hook、Plugin 与 Marketplace

Hook 在某个生命周期事件发生时运行确定性程序。观察型 Hook 可以记事件；拦截型 Hook 则可能影响能否执行。先做观察型：examples/observe_hook.py 只记录 UTC 时间、事件类别和工具名称，不记录工具输入和用户资料。它退出成功不等于已经验证工具安全。

```bash
# 执行本行指定的工具与参数，完成当前小节对应操作。
printf '%s' '{"hook_event_name":"PostToolUse","tool_name":"Write","tool_input":{"secret":"fake"}}' | .venv/bin/python courses/05-claude-code-ecosystem/examples/observe_hook.py
```

结果在当前项目的 .course-hook-log/events.jsonl，只应出现 checked_at、event、tool_name 与 observed。把该程序接入 Hook 时使用绝对解释器和程序路径。不要把外部输入拼成 shell 命令。

Plugin 是打包方式，Marketplace 是发现和分发索引。加入市场不等于安装里面所有插件。常见布局是 .claude-plugin/plugin.json 描述插件，skills、agents、hooks 等放在插件根目录的相应位置。安装前知道来源、版本、范围、需要的权限、如何卸载。社区“精选”不等于平台审核，也不等于适合你的项目。

## 5.5 Subagent：隔离上下文，不自动隔离文件

适合把大批文件检查交给独立工作者，只把结论和证据返回主流程。委派说明至少包含目标、可读范围、工具、输出格式、停止条件。examples/agents/evidence-reviewer.md 是完整只读检查者配置；工具名、字段名及模型选项需匹配当前宿主。

如果任务强烈依赖主会话的细节，拆出去会丢上下文。多个工作者共享目录时仍可能修改同一个文件。当前版本支持一定层次的嵌套委派。使用时仍要限制任务总数、嵌套深度和成本，并明确由谁负责最终结果。

## 5.6 并行与 Worktree

独立任务可以并行：一个人检查文档链接，另一个检查类型。但两个工作者修改同一段业务逻辑时，先明确文件归属，或用不同 Git worktree。Worktree 隔离工作目录与分支，不隔离网络账户、凭证或所有系统资源。消息协作、代码隔离、合并审查是三种不同职责。

Dynamic Workflows 用可读脚本组织重复的委派与收集，适合步骤明确、分支可独立的任务。先验证单个任务，再小规模并行；不要把工具支持的最大并发当推荐值。

## 5.7 Loop 与 5.8 SDK

真实循环仍是 context → 模型 → 权限检查 → 工具 → observation → 继续或结束。Claude Agent SDK 让应用管理会话和异步消息流，并不等于把整个 Claude Code 内部实现公开成 Python 函数。ResultMessage 的 subtype、错误、轮数和花费需要检查；一条文本消息不是成功收据。

只有需要把 Agent 嵌入应用、定时调度或自定义审计时再用 SDK。query 适合一次异步任务，持续会话可用相应 client；恢复 session 不等于所有外部动作都能安全重试。原课 SDK 示例完整保留在本地核对页，其 allowed_tools 只表示预批准，不能当强只读安全保证。
