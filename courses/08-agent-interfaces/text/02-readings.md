# 第八课必读与全部资源分类

## Anthropic Computer Use / Browser Use

模型输出动作请求，应用提供真正的执行器。Computer 从截图控制桌面，Browser 可用网页结构信息；工具集合与返回格式必须成对匹配。当前文档使用 computer_toolset_20260801 和 browser_toolset_20260801，不能混用旧版单 computer 工具的消息样式。

执行器要串行解释动作并核对结果。截图需要保留尺寸和缩放关系，上传给模型的图与执行器坐标必须一致。任何页面上要求“忽略限制、传走文件”的文字都是不可信内容，不会因为被截图送入模型就变成系统指令。

## OpenAI Computer Use

工具类型为 computer；Responses API 的 call_id 串起请求和 screenshot output。批量动作仍要逐项检查。安全提示是额外检查，不是业务批准的替代品。账户与模型支持随版本变化，课程不把某个历史 preview 名称当永久配置。

## OpenAI Sandbox guide

Workspace 是文件空间，session 是活跃执行环境，snapshot 是保存的状态；聊天上下文和环境状态不同。Manifest 可以定义新环境初始文件，但续接已有 session 不代表每次都重新创建文件。capabilities 决定可提供哪些能力，run_as 与文件权限还决定实际访问。

本地 Unix workspace 不等于容器或 VM 安全边界。选择 Docker 或托管环境时核对网络、挂载、凭证、生命周期、资源限制和清理；不要只看到产品名包含 sandbox 就认为允许执行任何未知代码。

## 执行器、基准与安全资料

Playwright 与 Playwright MCP 提供浏览器能力；browser-use 在其上组织 Agent 流程；E2B、容器和虚拟机类项目提供不同执行环境；OSWorld、BrowserGym、WebArena、Mind2Web 等提供任务或数据。任务基准不是执行器，执行器不是权限系统。原课 22 项完整资源表已留在本地，每个入口按这些职责阅读。

间接 Prompt injection 的关键是攻击指令来自页面、邮件、文档或工具结果，混在正常任务资料里。来源标签、最小工具权限、动作前策略、审批与外部状态验证共同降低风险。单靠模型“记住不要被骗”不足以构成边界。

未来的语音、机器人视觉语言动作等入口改变观察和行动的介质，但仍需要权限与验证。它们是研究延伸，不是本课额外必修编号。现实法律争议与平台条款不能从单个案例外推，本课仅在测试页和虚构资料上练习。
