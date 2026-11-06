# 从规则到可验证的扩展

## 单元一：先看一次任务经过哪些部件

你提出“核对 README” → 宿主加载项目规则 → 匹配 Skill 的任务说明 → 模型提出 Read 等工具调用 → 宿主权限检查 → Hook 收到事件 → 工具执行 → 结果回模型 → 模型给出带文件定位的结论。MCP 只是其中一种外部工具连接方式；Plugin 把若干部件一起分发；Subagent 将一项工作放入另一个上下文。

先问“我需要解决什么重复问题”，再选部件：长期约束写规则；重复步骤写 Skill；确定事件触发写 Hook；外部能力用 MCP；需要独立上下文用 Subagent；给别人安装用 Plugin。换一个部件不会自动获得另外几种能力。

## 单元二：规则与 Skill 的完整练习

原五题的文件都在本课 examples：CLAUDE.md、skills/readme-check/SKILL.md、observe_hook.py、readonly_server.py、agents/evidence-reviewer.md。先在新的演示目录中使用，不把教学配置写进你正在工作的真实全局配置。

规则至少交代用途、禁止、验证、交付。下面是本课完整规则：

{{code:../examples/CLAUDE.md}}

Skill 的 description 帮宿主判断适用场景，正文才说明如何完成；references 里放长材料，scripts 里放确定性处理程序。主文件过长会挤占工作上下文。`disable-model-invocation` 限制模型自动触发；`user-invocable` 控制用户是否能直接调用，不能混为一个开关。提示词中列 allowed-tools 也不等于操作系统阻止其他访问。

{{code:../examples/skills/readme-check/SKILL.md}}

演示输入与确定性初筛器如下。这个检查器只识别四个约定标题，还不能理解任意自然语言标题。遇到使用其他标题的 README，需要由 Skill 按内容含义核对。

{{code:../examples/demo-data/README.md}}

{{code:../examples/check_readme.py}}

在项目根运行：

```bash
# 运行 courses/05-claude-code-ecosystem/examples/check_readme.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/05-claude-code-ecosystem/examples/check_readme.py courses/05-claude-code-ecosystem/examples/demo-data/README.md
```

预期 NEEDS_REVIEW：四段正文齐全，但这还不是语义验收。复制输入到 /tmp 后删除“运行示例”整节，再检查应 FAIL 且 missing 包含该项；检查不存在路径应 FAIL，并明确文件不存在。不能把异常误报为“没有问题”。

要在 Claude Code 中验证 Skill：在一次性演示项目创建 `.claude/skills/readme-check/`，把上方完整 SKILL.md 放入；把演示 README 放在该项目根。启动该项目的 Claude Code，输入 `/readme-check`，再测试自然语言“检查 README 完整性”。最后用“写一首诗”验证不会无关触发。宿主是否加载与初筛器是否运行，是两项独立验收；没有安装 CLI 时可先做人工核对。

<details><summary>完整参考输出与验收理由</summary>

| 检查项 | 结论 | 证据 | 建议 |
|---|---|---|---|
| 目的 | 完整 | README.md 第 4 行说明终端问候和教学用途 | 无 |
| 安装 | 完整 | 第 7 行说明 Python 3、无第三方依赖 | 先确认本机 python3 可用 |
| 运行 | 完整 | 第 10 行包含完整命令与预期文本 | 首次运行记录实际输出 |
| 许可证 | 待确认 | 第 13 行明确尚未选定 | 作者确认前不要声称可按某许可发布 |

仅核对文档，命令未实测。删去运行节时该项为缺失，其他项保留原结论；文件不存在时停止，不编造表格证据。不相关请求不套用检查表。以上四种输入及其结论都正确，才完成本题；NEEDS_REVIEW 本身不算全部通过。原 read-summary 保留为迁移例，不能替代本题。

</details>

## 单元三：Hook 从输入、注册到输出

Hook 是宿主在事件发生时调用的程序，不是每轮重新让模型理解一遍规则。我们的观察型 Hook 从标准输入读取 JSON，只记录 checked_at、event、tool_name、observed，不保存工具参数、正文或凭证；返回 0 表示本 Hook 没拦截，其他权限检查仍可能拒绝。

{{code:../examples/observe_hook.py}}

以下配置完整对应这个脚本。在一次性演示目录根放 observe_hook.py，在其 `.claude/settings.json` 放下面内容。`$CLAUDE_PROJECT_DIR` 是宿主传入的项目路径，双引号保护带空格的路径。本教材不替你注册全局 Hook。

{{code:../examples/settings.demo.json}}

先离线检查，不需要登录：

```bash
# 创建本例需要的目录。
mkdir -p /tmp/course5-hook
# 执行本行指定的工具与参数，完成当前小节对应操作。
printf '%s' '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"secret":"虚构不应被记录"}}' | CLAUDE_PROJECT_DIR=/tmp/course5-hook .venv/bin/python courses/05-claude-code-ecosystem/examples/observe_hook.py
# 显示指定文本文件，核对其内容。
cat /tmp/course5-hook/.course-hook-log/events.jsonl
```

先检查日志：每行只应有时间、事件、工具名称和 observed，不应包含 secret。tool_name 应为 Write，checked_at 应为带时区的 ISO 时间。

再检查宿主是否真正触发了 Hook：注册后，在演示目录内做一次已授权的小编辑，日志应多出一条事件；移除 settings 中这段 Hook 后，再做同样操作，日志应不再增加。离线脚本运行成功和宿主触发成功，要分别验收。

日志统一使用 UTC，便于比较不同机器的记录。event 对应原题的 hook_event_name；工具名称只接受白名单中的值，其他名称记为 other，避免把任意输入写进日志。把 `.course-hook-log/` 加入演示仓库的 `.gitignore`。

## 单元四：MCP 的完整协议往返

Host 是你使用的 Agent 应用；Client 是 Host 为一条连接持有的协议端；Server 暴露工具、资源或提示模板。Tools 让模型请求执行，Resources 提供内容，Prompts 提供模板。stdio 通过子进程标准输入输出交换消息，因此服务端不要把调试打印混入 stdout。

本题固定使用 MCP Python SDK 1.x 的 Client/Server，不把它叫作所有新版规范的手写实现。SDK 负责连接和协议协商。运行：

```bash
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-verification/bin/python -m pip install -r courses/05-claude-code-ecosystem/examples/requirements-mcp.txt
# 运行 courses/05-claude-code-ecosystem/examples/mcp_roundtrip.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/05-claude-code-ecosystem/examples/mcp_roundtrip.py
```

期望发现 read_note，notes.txt 读取成功，`../observe_hook.py` 被拒。不是只直接调用 Python 函数，下面的客户端真正启动 stdio server，列出工具再调用。

{{code:../examples/mcp_roundtrip.py}}

{{code:../examples/readonly_server.py}}

目录判断先 resolve 再检查所属范围，避免 `..` 或符号链接越界；类型只允许 txt，限制文件大小。这个工具函数受限，不代表整个进程完全隔离。真实 Host 的 shell 权限、服务进程身份和网络仍独立配置。接入 Claude CLI 的可复制命令如下；执行前确认路径存在，完成后可移除：

```bash
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude mcp add --transport stdio --scope local course-readonly -- /Users/owen/Documents/ai-learn/courses/.venv-verification/bin/python /Users/owen/Documents/ai-learn/courses/05-claude-code-ecosystem/examples/readonly_server.py
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude mcp list
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude mcp remove course-readonly
```

连接后用 `/mcp` 检查状态，再请求读 notes.txt 与越界文件。账户未登录时先完成本地协议实验，不把未登录误诊为 server 代码失败。

## 单元五：Subagent、并行与 Worktree

{{code:../examples/agents/evidence-reviewer.md}}

把任务交给工作者时要给完整输入：目标、资料路径、允许工具、返回格式、停止条件。只说“检查刚才那个问题”会依赖它没有的历史。让它返回文件位置、证据和未确认项，主流程才能合并。

Subagent 隔离上下文；Worktree 隔离一份 Git 工作目录；消息协调负责交换任务进展。这三者互不替代。两个工作者写同一文件仍可能冲突。原 cookbook 的研究、审查、排错、测试、文档等配方，应理解为“任务职责＋输入输出＋工具范围”的组合，不需要全部安装第三方 agents。原 15 个配方与高级支线仍在本地原课页逐条保留，选择配方时依次判断：是否独立、是否缺证据、是否可并行、谁合并、何时停止。

同一小 bug 高度依赖共享上下文时，用一个工作者更容易定位；不同资料的独立核读才适合并行。并行报告要保留各自证据与冲突，不能把多数赞同当事实验证。

## 单元六：Plugin、SDK 与长期运行

Plugin 是分发包：元数据在 `.claude-plugin/plugin.json`，Skills、agents、hooks 和 MCP 配置放各自目录。Marketplace 是目录，加入目录不等于安装其中全部插件。发布前要写版本、所需权限、兼容宿主、安装验证和卸载方法。先把一个 Skill 安装到第二个干净 demo，再考虑打包。

Agent SDK 提供程序接口管理运行、工具与会话；它并不是公开完整宿主内部源码。读取结果时区分普通消息和最终结果，区分正常结束、轮数限制、错误。保存 session ID 便于续接，但业务任务状态、批准、外部效果仍需要自己记录。费用上限与 max_turns 是不同限制，结束后也应检查实际用量。

长期任务至少要留下这些交接信息：目标、已完成事项及其证据、未完成事项、运行环境，以及下一步做什么、怎样检查结果。压缩上下文会丢信息，不能让新的会话凭一句“继续”猜任务。A3 给出团队交付和收据，学习 SDK 托管是本课选修，不是 A 线核心的登录门槛。

## 本课最终验收

五项分别交证据：规则被读取且范围正确；Skill 正例与反例；Hook 日志不泄露内容；MCP 合法/越界真实往返；只读工作者返回路径与理由。需要 Claude Code 才能验证的项目，若未实际运行，就标为未执行；本地协议测试不能代替宿主中的加载与触发测试。中文步骤和完整配置都已提供。排错按“入口是否触发 → 参数与路径 → 进程/协议 → 业务结果”顺序，避免一看到失败就改提示词。
