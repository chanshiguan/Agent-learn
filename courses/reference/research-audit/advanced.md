# Stage 7 / 7.5 / 8 / Capstone 事实调研

核查日期：2026-11-03。仅调研，不修改课程。原课全文暂存 `/private/tmp/07-multi-agent-production.zh-Hans.md`、`07.5-advanced-agentic-concepts.zh-Hans.md`、`08-agent-interfaces.zh-Hans.md`、`CAPSTONE.zh-Hans.md`。对应 `*-links.json` 保存全部直接外部链接，分别 47、30、27 个去重 URL。不要误称这 104 个链接代表 104 篇文章：有共享链接、整个代码仓库、文档入口和法院文件。

## 阅读状态与使用限制

- 已完整读取三个阶段与结业项目正文（下载的 raw 文件）；以下逐项清单按课文，不按 README 的旧缩写。
- 已打开并针对教学相关章节核对全部必读官方页面：Anthropic Evals / Building Effective Agents；OpenAI Tracing / HITL / Harness Engineering；LangGraph Persistence / Interrupts；Anthropic Computer Use / Browser Use；OpenAI Computer Use / Sandbox guide。
- 官方 SDK Markdown 已保存：`/private/tmp/advanced-source-sdk-tracing.md`、`advanced-source-sdk-hitl.md`、`advanced-source-sdk-sandbox.md`；LangGraph `advanced-source-persistence.md`、`advanced-source-interrupt.md`。
- 已打开并核对补充文章：Anthropic infrastructure-noise、multi-agent-research-system、effective-harnesses-for-long-running-agents、harness-design-long-running-apps、Claude Code workflows。其余直接资源的原课定位已列明，但不能冒称全部逐字精读。开源项目 README 抽取记录将置于 `/private/tmp/advanced-repos/`。
- Anthropic `.md` 直连返回 403；普通 HTML 浏览工具成功。web `find` 对 toolset 名称曾出现假阴性，直接打开正文已确认名称仍有效。
- 原课直接链接可以完整列入资源审计；对整个仓库只覆盖本课用法与边界，不能声称复刻整个项目。这里不是转载原文；讲义应原创解释。

## Stage 7：原结构及必须覆盖的内容

原文件：`stages/07-multi-agent-production.zh-Hans.md`。正式标题「Agent 上线工程：可测、可看、可停、可恢复」。先修 4、5、6；Docker 可后补。故事：研究助理找三个来源、写摘要、批准后发布。

### 主章节清单

1. 定位、目标、环境成本：默认单 Agent；先固定成功条件，再记录过程，再批准/恢复，最后部署。Mock 与真实模型分开，追踪数据须脱敏。
2. 十九术语完整表：Harness、Loop、Workflow Graph、Orchestration、Multi-Agent、Handoff；Eval、Outcome、Trajectory、Grader、Evaluation Harness、Trace、Observability；Guardrail、Human Approval、Checkpoint、Resume、Recovery、Idempotency。Prompt 是交给模型的指令资料，Context 是当步所需信息。不要把十九术语缩成仅 eval/log/retry。
3. Harness / Loop / Graph / Eval 四种职责：执行边界；一轮后继续还是停；分支路线；对结果与过程的验收。不是先后取代的四代技术。节点可为固定程序/工具/等批准，非每个节点都是 Agent。
4. Harness 八组件：编排；工具权限；上下文状态检查点；重试恢复幂等；护栏批准；遥测；评测架构；成本延迟预算。这是原课教学归类，非国际标准。补缓存、批处理、路由、小模型的测量方法；日志权限与保留周期。
5. 三种循环：普通 for、任务内模型工具循环、跨轮/跨会话 Goal→Action→Observation→Adjustment。IBM 的 Loop Engineering 与 Anthropic 对 harness 的划分不同，不硬拼唯一层级。
6. Graph 和多 Agent 何时使用：分支/并行/HITL/恢复用 graph；可独立任务或独立检查才考虑多 Agent。SDK manager 把子 Agent 当工具；handoff 转移当前控制权；模型原生 hosted multi-agent 是第三种服务，不混同。
7. Eval 全要素：input、initial state、success criteria、forbidden actions、optional reference、grader、case metadata。Suite 有版本；Reviewed/Golden/Reference Set 名称不统一，不只是 input，也不是 few-shot/训练集。
8. trial、baseline、regression、development、frozen holdout。Outcome 检查真正产生的结果；Trajectory 检查是否越权、绕过批准、超出预算；不要机械限定所有成功解法都走同一动作序列。概率任务需多次 trials，单次失败不能自动叫退步。
9. Observability：trace/span + log + metrics。记录 task ID、工具/来源、错误类型、时延、token、重试原因；记录多不证明结果正确。
10. Approval / Checkpoint / Resume / Recovery：批准要绑定可审核的具体动作；保存版本化状态；同一 task 恢复；拒绝、超时、损坏状态 fail closed。幂等由外部效果去重，不是仅在内存放 bool；执行成功而状态未写入的故障窗口也须测试。
11. 上线路线：Eval → Observability → Approval/Recovery → Deploy。健康与就绪检查、用量限制、停止开关、版本、回滚。服务能启动不等于上线合格。
12. 产品层级：OpenRouter 模型入口；Pi/OpenCode runtime；Orca/QM 协作环境。不能互替。
13. benchmark：SWE-bench 软件修复；Terminal-Bench 终端/Harbor；OSWorld 桌面；tau2/τ³ 工具用户多轮；GAIA 通用助理。比较 task split、harness commit、grader、环境、模型参数、trials，关注 reward hacking，不抄永久 SOTA。
14. 精选项目按编排、评测观测、harness/deploy、多 Agent 四类理解，详见资源库存。

### 原课练习一一对应

- 核心 1 Eval：固定案例+评分规则，改一项后指出哪题退步。原入口 examples/stage-7/02-eval。
- 核心 2 Observability：步骤、延迟、token、错误。03-observability。
- 核心 3 Safe execution：暂停批准、持久化 checkpoint、重启 resume、同幂等键只产生一次外部效果。06-safe-execution。
- 核心 4 Deploy：`/health` 与 `/chat` API、错误状态测试；Docker 加分项。05-deploy。
- 选修 A：两名正反 Agent+第三个裁决者，必须有单 Agent baseline 才比较。01-multi-agent-debate。
- 选修 B：Streaming 与 Prompt caching，测实际用量；cache 不是安全或恢复机制。04-sdk-advanced。
- 综合项目「有收据的研究助理」：三来源 URL+抓取时刻；据来源摘要/缺证据承认未知；发布前批准/修改/拒绝；中断恢复；幂等发布；收据含 task ID、outcome、trajectory、工具来源、时间token错误、checkpoint 版本、审批。5 个 development 起步，真实失败持续入版本化 suite。不能把这个综合项目漏掉。

## Stage 7 六份必读：实质知识与 API 事实

### S7-R1 Anthropic Demystifying Evals

URL https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents （现重定向 /research/）。task/trial/grader/transcript/outcome 分开；code/model/human graders 各有成本与局限。Capability tests 找能力边界，regression tests 保护已有能力。Coding 看外部测试；对话看任务完成与对话质量；研究看事实、引用、覆盖；电脑使用看环境状态而非自报。pass@k 是至少一次成功；pass^k 是所有次成功（独立同分布假设下分别 1-(1-p)^k、p^k，实际估计须记录试跑方案）。20–50 是早期经验建议，非硬门槛。实践步骤：早点建、从手动检查/真实失败收题、明确可解题及已知参考、平衡该行动/不该行动、清洁隔离环境、防共享缓存/历史泄漏、校准 grader、读完整轨迹、监测饱和、持续维护。离线评测还需线上监控、用户反馈、A/B、人工抽查互补。

### S7-R2 OpenAI Agents SDK Tracing

URL https://openai.github.io/openai-agents-python/tracing/

Trace 包一次工作，span 包有起止的子操作；trace_id、group_id、parent_id、metadata 区分。自动覆盖 runner/task/turn/agent/generation/function/guardrail/handoff 等。默认 tracing 开启，且 trace_include_sensitive_data 默认 True；纯本地案例要显式关闭外传（`set_tracing_disabled(True)` / env `OPENAI_AGENTS_DISABLE_TRACING=1` / RunConfig）。`with trace(...)` 关联多个 run；`custom_span` 自定义；后台批量导出，可在 trace 结束后 `flush_traces()`。`add_trace_processor` 是增加，仍保留默认 OpenAI exporter；`set_trace_processors` 才替换。脱敏处理器和 exporter 独立时，脱敏异常不会自动阻止其他 exporter，所以脱敏和发送要组合成 fail-closed exporter。不要让“用了 Ollama”误导用户以为 SDK tracing 一定不发云端。

### S7-R3 OpenAI HITL

URL https://openai.github.io/openai-agents-python/human_in_the_loop/

函数工具 `needs_approval=True` 或 async 判断；响应 `result.interruptions` → `state=result.to_state()` → `state.approve(item)` / `state.reject(item)` → `Runner.run(original_agent,state)`。`to_string`/`from_string`、`to_json`/`from_json` 支持存储；恢复原顶层 run，即便审批出自 handoff 或 Agent.as_tool 的内层。审批状态要放受控服务端，不信任客户端上传 RunState；反序列化不是身份认证。全局 sticky approve 对 shell/apply_patch 在相同工具类型名间可跨角色，不适合不同权限执行器；逐 call 批准更明确。shell/apply_patch approval 是 opt-in，只有 callback 并不启用。保存 sdk/agent/tool/schema 版本并校验待办任务；崩溃前后仍需外部幂等。会话 session 保存聊天，RunState 保存执行/批准，不可互替。ComputerTool `on_safety_check` 与此 interruption 流程不同。

### S7-R4 LangGraph Persistence

URL https://docs.langchain.com/oss/python/langgraph/persistence

Checkpointer 保存单 thread graph state；Store 保存跨 thread 应用数据。`builder.compile(checkpointer=...,store=...)`；调用 config `{'configurable':{'thread_id':'...'}}`。`InMemorySaver` / `InMemoryStore` 只在进程存活时有效，不可标注重启恢复；生产使用持久后端。检查点积累有存储/延迟成本，保留策略；子图 checkpoint namespace 与父图不自动完全共享，跨边界数据可用 store。

### S7-R5 LangGraph Interrupts

URL https://docs.langchain.com/oss/python/langgraph/interrupts

`interrupt(JSON可序列化payload)` 暂停；同 thread 使用 `Command(resume=decision)`。恢复会从节点开头重跑，不是恢复 Python 栈到下一行，因此 interrupt 前必须幂等或移去独立节点；放在批准后仍可能“副作用成功、节点失败”，同样要去重。不要宽泛 try/except 吞掉中断；不要按不稳定顺序排列多个 interrupt；不要传函数/文件句柄等不可序列化对象。静态 breakpoint 与动态 interrupt 不同；有检查点、thread ID、可恢复调用才构成持久审批。

### S7-R6 Building Effective Agents

URL https://www.anthropic.com/engineering/building-effective-agents （现 /research/）。Augmented LLM=模型+检索/工具/记忆；workflow 固定代码路径，agent 动态选路径。五模式：chaining+gate；routing；parallel sectioning/voting；orchestrator-worker 动态分解；evaluator-optimizer 有条件反馈循环。真正 agent 适合未知步数、可反馈、可控成本/停止条件的开放任务。框架隐藏细节会增加调试难度；先简单可组合。工具 ACI 需要清楚描述/参数/边界、反馈、实测，不能只调 prompt。客服、编码是案例，原则不等于最新产品清单。

## Stage 7.5：按正文是四个概念，不是 README 的旧「12个」

原文件 `stages/07.5-advanced-agentic-concepts.zh-Hans.md`。先修 Stage 7 的可重跑 cases、停止条件、单 Agent baseline；原课不要求代码、不要求购买 API。新增可执行案例应标教学补充，不改写原课门槛。

### 原结构全清单

1. 默认不增加复杂度；只有可重现失败才选做法。
2. 四核心：Evaluator-Optimizer/Agent-as-Judge（按 rubric 反馈，judge 也要校准）；Failure Injection/Chaos Eval（隔离制造timeout/坏格式/陈旧资料/不可用工具）；Autonomy Gradients/Trust Layers（按可信权限分配 suggest/propose/execute，不能模型自授）；Model-Harness Fit（每次只删除一个部件，用同 suite 对比）。后三组是编辑/社群名称，不是公认标准。
3. 其他模式选择表：parallel exploration、hierarchical delegation、handoff、plan-act-reflect、dynamic workflows。写清输入输出责任、合并成本、共享上下文问题，而非只列名词。
4. 最小决策记录五项：失败 case/outcome/trajectory；baseline 质量成本时延安全；唯一新增做法；事前接受门槛；停止/撤销办法。
5. Keep/Simplify/Remove 删除测试；模型弱点 workaround 可移除，最小权限/隔离/审计/批准/rollback 的责任不能因模型变强移除。
6. Bitter Lesson 是通用计算/学习长期趋势论述，不是直接提出 agent harness 删除定律。Claude Code 70% planning /80% execution 是特定数据观察，不是推荐比例。
7. Dynamic Workflows：Claude Code 功能，JS orchestration script + 后台 runtime，任务可独立fan out/重跑时用；不等于模型名、不替代任意 workflow engine。运行中一般输入不能像普通对话插入；支持查看/暂停/恢复机制，权限和sandbox仍生效。计划、分阶段、并发/总数/成本受控；不要把最大并发当建议。
8. 案例：Cognition共享背景不足导致结果难合；Anthropic research的来源质量/引用/eval防推测跳跃；Replit事故提醒规则须落到权限门，第三方事件不外推所有产品。
9. benchmark 需固定 task/scaffold/tools/env/timeout/grader，多次测量，基础设施失败与能力失败分开；holdout、确定规则、人工校准。
10. 完整资源 24 项+正文额外引用，按设计context、编排契约、eval韧性、研究模式、中文教材分类。原课完成检查五项应全部映射。

### 必读 OpenAI Harness Engineering 的知识点

URL https://openai.com/index/harness-engineering/

这是单一代码库案例，不是所有团队标准：人的职责转为目标、环境和反馈；agent 需要能运行/观察应用；仓库内版本化文档作为 system of record，短 AGENTS.md 是地图，深资料在 docs；文档也要检查陈旧/缺失。通过架构分层、依赖约束、lint/tests 把口头约定机械化；tool输出帮助定位失败。合并策略与高吞吐相适应但不抄成免review。持续自动清理重复/坏模式，避免 agent 照抄导致熵增。自主性来自完整验证、反馈、恢复设施，不是一句“自己做完”。

### 已读补充文章实质

- Infrastructure Noise：同 benchmark 的硬件资源、限额执行方式、超时能影响分数；进程/容器错误需单列；固定资源、公开配置、多 trials，不把小幅模型差距当稳定能力差。
- Multi-agent Research：lead-worker 压缩宽度搜索的独立context，明确目标/工具/任务边界/返回格式避免重复；搜索从广到窄、来源质量；引用单独核对；多角色token与协调贵，适合可并行开放研究，不适合紧耦合共享状态；生产要持久化、重试、可观测、部署一致性。
- Long-running agents：初始化建立feature清单/启动脚本/进度与git记录；后续每session读交班资料、先验现有状态、一次实现一项、做端到端检查、留下可恢复状态。compaction不是自动可靠跨session记忆。
- Long-running apps：planner/generator/evaluator和可打分审美 rubric 是特定实验；把主观“好看”拆成维度；换更强模型后通过测量删除context reset等过时补丁，保留安全责任。

## Stage 8 全结构与 API 要点

原文件 `stages/08-agent-interfaces.zh-Hans.md`。推荐在 7.5 后，但最低只需理解 Stage 3 工具循环。A 做练习1，B 再做2。全部 4 练习都要保留，3/4属进一步实现。

1. 八词：Agent Interface、Browser Use、Computer Use、Sandbox、Accessibility Tree、Harness、Approval Gate、Prompt Injection。
2. 最小门选择：有正式typed API先API；只读用search/fetch；网页交互browser；跨桌面computer；代码/工作区sandbox。这不是四步逐级升级。
3. Computer loop：截图→模型批次动作→policy/approval→executor顺序执行→新截图→验证/继续/停止。
4. Browser三信号：DOM结构属性、AX角色名称状态、截图像素；JS/canvas/拖拽可能需像素；scraping主要读数据，RPA固定路线，agent动态决策但须验证。
5. Sandbox词表：container共享kernel、VM独立kernel、microVM轻量VM、Firecracker技术、gVisor用户空间kernel、cold start、workspace、session、snapshot。快不代表安全；local workspace实现不等于强隔离。
6. 四检查：隔离、域/文件/动作白名单、批准、验证日志。每个动作执行前都检查；截图和网页指令是不可信资料；重定向后也要验证最终URL，截图坐标动作须核对最新状态。
7. Track A选现成工具、专用profile、长任务停止证据、产品可用性有账号地区限制；Track B executor/framework/sandbox五路线（Anthropic quickstart、browser-use、Playwright MCP、E2B/container、SandboxAgent）。
8. 安全案例：Brave间接注入、BrowseSafe是防御之一、Amazon案件不能说全站禁用；本课不需要复制真实登录/付款/信息发送作为练习。
9. 22项资源按官方文档、executor、sandbox、benchmark/dataset、安全分类；未来voice/VLA三入口，不虚构下一阶段。

### 四个原练习

- 1：只开 example.com，记录title、最终URL、截图；禁止登录下载离域；自己核对证据。
- 2：Python policy checker，https+exact hostname，无用户名密码；read/screenshot ALLOW；login/purchase/delete/send ASK；其余BLOCK。归一化动作；恶意域、file scheme、不认识动作单测。该检查器不是sandbox，更不是网络层完整拦截。
- 3：只读CSV+输出目录+绘图script置于不含host凭据的sandbox，关不需网络，只取图片和log；证明隔离，不只证明脚本能跑。
- 4：observe→propose→policy→approve/execute→verify 完整测试站loop，故意给禁用URL证明阻断。可教学mock模型，但真浏览器执行与mock须分开标注。

### Anthropic Computer / Browser 官方协议

https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool

当前分别 `tools=[{'type':'computer_toolset_20260801'}]` 与 browser_toolset_20260801；不是旧版单工具computer action协议。模型输出 `tool_use` 带 member `name` + `toolset_name='computer'/'browser'` + input。应用提供executor，服务不替你操作。返回每条 `tool_result` 必须同时匹配 tool_use_id 与 toolset_name。多个动作依顺序执行，不是并发；任一失败停止后续执行，但每个未执行请求仍返回is_error结果（详见官方各toolset halt text）。保留assistant整块历史，再紧接user工具结果。computer screenshot/zoom图像，其余动作ack；browser按工具返回结构/文字/图像。截图缩放与坐标变换要一致，不能让旧坐标点击新页面。协议完整性、业务权限与网络隔离是三项不同责任。

### OpenAI Computer 官方协议

https://developers.openai.com/api/docs/guides/tools-computer-use

Responses API `tools=[{'type':'computer'}]`；`computer-use-preview` / `computer_use_preview` 是旧迁移路径。`computer_call` 可有 `actions[]`，status=completed只是模型生成请求完成，不代表环境动作执行完成。处理动作后回 `computer_call_output`，call_id匹配，output为computer_screenshot，image_url base64数据URL，detail original；`previous_response_id` 续接。截图-only请求不改变页面。先检查危险动作与pending safety checks，不自动回ack冒充人批准。模型ID以当日支持为准，不把文档不同示例混配。

### OpenAI Sandbox guide

https://openai.github.io/openai-agents-python/sandbox/guide/

SandboxAgent仍走Runner，继承tools/handoffs/guardrails。Manifest定义新session初始文件；capabilities定义filesystem/shell/compaction/skills；SandboxRunConfig决定client/live session/session_state/snapshot。续接现有session时已有文件状态优先，不能假设每run都重建Manifest。instructions追加，base_instructions替换内建指导，后者慎用；run_as与文件权限；capabilities显式列表会替换默认集合。workspace/snapshot/session/聊天记忆不同。UnixLocal并非VM/container强安全边界；选择Docker/托管provider并核对挂载、网络、secret、生命周期和清理。原课称Beta，当前guide已无可搜索Beta标记，制作时可保守写API快速演进，锁版本并记录验证，不能仅以原课旧状态当实时结论。

## Capstone：一份来源，两轨要求

来源 https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/CAPSTONE.zh-Hans.md 。它是独立作品验收，不是标准答案。用户要全代码，可以给示范项目，但必须区分“示范已跑”与“用户已完成真实项目”。

### A

先修 0–2、A1、A2、Stage5核心5.1–5.4、A3；5.5–5.8和8不挡入场（8建议）。真实重复任务，CLI agent为核心，至少1个MCP或自写skill/command，清晰输入到有用成品，别人能按README重跑，至少处理1种失败。交付成品+README+至少一次真实运行证据+150字内反思。五评分维度：问题真实/工具运用/可重现/韧性/文件反思，各四级。只写离线Python脚本不满足CLI agent核心。

### B

先修主线0–8含7.5。二选一：≥2角色协作Agent及编排；或完整检索+生成RAG。两者都需tool use和CLI/API/chat接口；版本化Eval最少5development+3frozen holdout，成功条件/grader/trials/baseline/逐题结果/回归记录；失败分析、架构数据流、README、200字反思。评分：问题、架构、正确性、评测严谨、韧性、接口文档、反思。不能拿holdout逐次调prompt；生成式演示不能被固定模板摘要冒充。已有示例holdout一旦看答案并调参，就需用户补新的保留题。

### 身份选题与展示

研究者文献问答/日志/预处理；开发者review/triage/repo问答/release note；教师出题/评分辅助/教材/问答并守学术边界；知识工作会议行动项/汇整/周报；日常用户资料/行程/重复事务。不是再额外做五个capstone。展示要具体量得的事实，peer review可选，不强制上网站发帖。

## 补充核查记录与资源释义

下面是本次直接读取的 README/官方页面内容与本课的关联，不包含实际安装/运行证明。37 个 README 与索引在 `/private/tmp/advanced-repos/`。Cloudflare 根 README 是指向 `packages/sandbox/README.md` 的短文本，尚需沿该路径读取，不能把 26 字节文件称为已读完整项目文档。

### Stage 7 资源补充

- OpenAI SDK Testing 当前有 `agents.testing.ScriptedModel`、`assistant_message`、`function_call`。按预设模型响应序列驱动真实SDK派发；`model.calls`查看请求；`model.assert_complete()`检查预设步骤全部消费；`RunConfig(tracing_disabled=True)`保离线。另有流式、故障注入、sandbox测试配方。不能把mock通过写成模型能力通过。
- OpenAI SDK orchestration：LLM自主调度与代码固定调度可混用；manager as_tool回到主Agent综合；handoff换处理者；代码可串联、结构化分类、async并行、有界评估循环。
- Anthropic Develop tests：成功标准具体、可量化、可达、相关；正确性、忠实度、相关性、语气、延迟、成本与隐私各自量；规则、模型和人工评分分层，模糊好坏须rubric校准。
- Anthropic prompt caching：重用稳定前缀，自动缓存或末端 `cache_control={'type':'ephemeral'}`；tools→system→messages顺序影响前缀；不同模型有最小长度阈值；改工具/系统/思考配置可能失效。总输入量是 input_tokens+cache_creation_input_tokens+cache_read_input_tokens，不能只记input_tokens。默认5分钟可刷新，另有1小时，最多4断点；写缓存不是免费，需要重复命中才判断收益。缓存内容不是输出缓存、不是记忆或检查点。
- IBM Loop Engineering 是新兴工程用词，讲目标驱动反复执行、检查、调整；不代表所有prompt engineering都单次，也不应从宣传性对比推断Loop取代Harness。
- Anthropic Managed Agents 文章将 reasoning harness、执行环境、session持久事件解耦；session不等于模型context；可替换组件与持久执行接口帮助模型升级。其context reset例子比较Sonnet4.5与Opus4.5；勿误写成“所有更强模型都无需记忆”。
- Google Agents overview已重定向 `https://aistudio.google.com/docs/agents`，Public Preview；Antigravity默认Gemini3.8 Flash，Linux sandbox；网络默认允许外连，需要额外allowlist。真实接口详细内容见antigravity-agent页，不能用overview推断GUI支持。
- OpenTelemetry GenAI：spans/metrics/events语义约定，含MCP和provider专属字段；规范库与后端服务不同，接入仍要脱敏/采样/版本。
- Pi：极简可扩展harness，extensions/skills/templates/themes、CLI/JSON/RPC/SDK；默认不内置sub-agent/plan mode，不能描述为开箱完整多Agent平台。
- OpenCode：provider可选coding agent，当前README安装入口已v2；教材无需复制全局安装命令，明确所用版本。
- Orca：多个coding agents各在worktree，集中比较/运行；隔离git更改不自动隔离账号/网络或保证合并正确。
- QM：自托管团队harness，个人/房间的memory/files/keychain/permissions/cron/workspace分别作用域；不等同个人CLI。
- promptfoo：配置providers/prompts/tests/assertions批量评测及red-team；配置不代表grader正确，先确定dataset/split与阈值。
- Langfuse：trace、datasets、eval、prompt管理，可自托管；采集器负责数据送出，用户仍负责权限/保留/脱敏，仓库企业目录有不同许可。
- Phoenix：OpenTelemetry追踪+检索/生成eval+版本化datasets/experiments；自托管平台不是模型，不会自动判定业务完成。
- Claude Agent SDK Python：`query`单轮任务、ClaudeSDKClient多轮、有工具/权限/hooks/subagent；Python>=3.10，包内含CLI，可显式cli_path。须有Claude访问，本地Python包不代表免费本地模型。
- DeepSeek Harness：everything-is-plugin、Cordis，developer preview明示破坏性变更；用途为读架构，不能默认稳定生产依赖。
- SandBase：local-first sessions、sandboxed tools、memory、credentials、audit/replay、console；backend可local/Docker/K8s/worker，隔离强度由实际部署决定。
- BentoML：推理API、依赖模型版本打包、容器/批处理/资源调度，部署并不替代审批/评测。
- CrewAI：Crews角色合作，Flows事件驱动控制；多角色是架构选项，商业控制面另算。
- LongHorizon-Harness：跨desktop/terminal长期目标循环、checkpoint/recover、多CLI适配，先看边界与独立eval，README的长任务收益是项目自报。
- Edict：中文角色式规划/审议/派发/执行案例；其三省六部名是项目比喻，不是行业标准；demo可能用预置mock数据。
- benchmark库：SWE-bench问题与测试版本；terminal-bench-1旧版；tau2-bench当前已含τ-bench2.0多语言/语音，不能继续说只是原τ2；OSWorld-Verified与2.0区分。用项目自有case作发布依据。

### Stage 7.5 资源补充

- Constitutional AI（已读原论文摘要）：监督阶段先按原则批评再改写用于fine-tune，RL阶段用AI比较偏好训练偏好模型再RL；不需要人工逐条标有害性，但原则来自人。运行时judge没有训练阶段，不能与CAI画等号。
- CAMEL（已读原论文摘要）：inception prompting给角色与任务约束，通过角色互相对话完成任务并产对话数据；角色倒置、循环、无限客套等须停止条件；是研究框架，非默认可靠生产方案。
- Rigorous Agentic Benchmarks / ABC（已读论文摘要）：任务设置/奖励设计缺陷可造成高估低估，检查说明一致性、参考可解、测试充分、空答案/投机是否获分。论文对特定版本的缺陷不能直接外推今天仓库。
- ReAct/Reflexion 已在第三课本地有完整讲解与例子，后课可本地复习链接；Reflexion改的是反馈记忆/策略，不是在线更新权重。
- DSPy：typed signatures定义输入输出、模块组合、用评测优化prompt/weights；需要训练/开发案例和metric，不能用保留集持续优化。
- Microsoft Agent Framework：现行README为Python/.NET并提及单独Go库；workflows实现编排；新项目不照旧AutoGenAPI直接套。微软官方workflow概念页本次一次超时，不能宣称页面已完整读。
- hello-agents：中文原理、范式、工具/记忆/多Agent的教材，整个书不属于本课必读全量；按概念提供本地解释即可。
- AI Agents for Beginners：多语入门课程集合，概念与供应商演示区分，不把整个教材嵌入本课范围。
- Deep Agents：基于LangGraph的高层harness，planning/subagent/filesystem/context/offload/persistent memory/HITL；默认多能力带来权限面，不是每个任务都要用。
- Cognition文章已读：共享背景+行动隐含设计决定，FlappyBird分工风格不兼容；不是数学证明多Agent永不可用，应与独立检索成功案例比较任务耦合。
- Claude Code expertise已读官方摘要：约40万session，2025-10至2026-04，专业知识影响成功，人定目标、模型执行；统计不是个人学习成绩或固定比例建议。
- Bitter Lesson 原站本次502，未进一步获取全文；目前只按原课引用定位，不应声称本次精读。

### Stage 8 资源补充

- Playwright MCP README：AX snapshot工具接口、截图补充；server不是LLM决策循环；CLI+skills与MCP可按token/使用场景选择；origin工具配置不应被当完整安全边界，要控制真实browser网络/profile。
- browser-use：完整browser agent，支持自托管/云浏览器/托管agent不同产品层；托管价格不抄进长效教材，先给本地测试页。
- claude-quickstarts：computer-use等完整示例集合，读container/network/credentials边界而非直接操作真实账户。
- E2B：云端隔离code workspace，JS/Python SDK与API key；开源库许可不代表托管服务免费；结束后取产物并关闭实例。
- Cortex：API specs/Markdown→typed SDK/docs/MCP；gRPC只schema资源，不虚构可调用方法；typed工具通常优于GUI抓取。
- Cua：Spaces、Driver、Lume、SDK/CLI和benchmark多层；计算机执行工具与agent/model分开；backend决定隔离。
- UI-TARS Desktop：桌面控制应用+Agent TARS CLI/WebUI，不把开源GUI模型视作权限沙箱。
- OmniParser：截图→可操作元素结构，为视觉定位服务，不是完整agent。repo/weights各自许可证，不混同。
- Modal Sandbox：生命周期、command、文件、snapshot、network/security设置；默认网络不能假设关闭；GPU/CPU/存储/时间均有资源成本。
- Vercel Sandbox：托管隔离执行，runtime/region/network/生命周期/快照需要配置；不是普通Serverless Function的别名。
- OSWorld2.0当前项目页已打开：长程真实workflow，按binary/partial指标、steps、模型/harness/环境对比。原课108题/500steps/20.6%是该次快照，建议教材重点教比较条件并给日期而非排名。
- WebArena：自托管网站任务与环境状态评估；canonical仓库用于复现原论文，README推荐AgentLab/BrowserGym作新实验；不是随意真人网站爬虫测试。
- Mind2Web：跨网站任务示范数据，离线HTML/动作集与Online-Mind2Web不同；dataset不授权自动化任意当前网站。
- Brave直接链接当前文章为2026-06研究Tabstack/Cotypist，仍支持“云或本地模型均有间接注入面”，不能把此URL当只讲Comet的旧报道。BrowseSafe有开放benchmark+微调检测器，属于一层检测而非权限隔离证明。
- Gemini in Chrome：当前仍渐进开放，要求支持地区/语言/账号/设备；当前页面写13岁或本地区适用年龄，工作/学校成年用户需管理员启用。教材只需要表明可用性不是人人相同，不固化无关资格数字。
- LiveKit Agents：STT/LLM/TTS或实时模型、WebRTC、任务调度和电话集成；语音延迟/打断/同意边界不同于browser。
- OpenAI Voice agents、OpenVLA原课只留未来入口，应定义语音pipeline与视觉语言动作的物理控制边界，不扩写成新阶段或承诺机器人实机。

### 可直接用于完整实现的两项额外协议核对

Anthropic computer 批次未执行项的固定错误文本：`Not executed: an earlier computer action in this turn failed.`；browser有自己的文本，需在实现前从对应页面返回错误小节读取，别复用computer文本。

Dynamic Workflows当前官方表：每parallel()/pipeline()最多4096items，每run总1000agents，超长列表报错而非静默丢弃；是否允许在运行中steer、如何暂停/恢复，以 `/workflows` 视图规则为准。初学者教学应使用2–3子任务和很小预算，不展示满上限运行作为默认。
