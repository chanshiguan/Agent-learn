# Track A 与身份分支事实调研

核查日期：2026-11-03。工作仅涉及公开资料读取，未修改项目课程。原课实时文件在 `/private/tmp/ai-learn-branch-sources/`，主代理另有全套 `/private/tmp/ai-learn-upstream/`。

## 关键版本差异

浏览器搜索缓存的 raw / GitHub 页面并非最新 main。已通过直接下载读取最新 A1、A2、A3、五个 branches 及 agent-paradigms / cli-agents-guide。A1 当前标题为“选一个 CLI agent，安全地完成第一个小任务”，不是旧版8工具比较。教师路线当前是目标、脚手架、学生数据、人工审核为主，旧版长应用列表已改写。CLI guide 为9个CLI而非8个；新增Pi。日常个人Agent目录已含Claude Duet、dots、Meta Muse、Grok Bot、Instinct、Tab、Tomo、Poke，不应只写旧缓存的3个产品。

## A1 原课对应

- 本课目标：区分模型、Provider API、Router、Coding agent、Local runtime；按已有账号与本机条件选入口；在可丢弃仓库完成可恢复小改。
- 核心辨析：Ollama只运行模型；OpenRouter路由模型请求；Harness管理上下文、文件工具与循环。界面、身份、部署位置是不同维度。一个产品可能有CLI/desktop/cloud多个入口。
- CLI-1：只读盘点demo项目→说明用途与真实测试命令→提交小文档改动计划→人工确认→只改README→展示diff→仅当开始前该文件干净时定点恢复。新文件与已跟踪文件恢复方法不同，不要全目录reset。
- CLI-2：设置CLAUDE.md/AGENTS.md/GEMINI.md；四项为用途、禁止事项、验证指令、回报格式；通过触发禁止事项的小请求与diff核对是否真正加载。
- CLI-3：同干净repo、同prompt、同输入，在第二harness串行重跑；记录日期、CLI版本、LLM、provider、登录方式、approval、sandbox、改动、diff，不用一次体验做总排名。
- CLI-4：一次性session使用not-a-real-key与不存在模型，区分登录/API认证/模型不存在/权限失败；不改正式凭证或共享env。
- 全部目录入口：Claude Code、Codex、Gemini CLI、Grok Build、OpenCode、goose、Aider、Pi、Hermes Agent；OpenRouter与Ollama单列非agent。重点边界：Pi无内建权限sandbox；Aider自动commit需要先了解；OpenCode AGENTS.md优先，CLAUDE.md fallback，非OPENCODE.md。
- 本课必读覆盖：Claude Quickstart+permissions、Codex CLI、Gemini认证+sandbox、OpenCode/goose/Aider/Hermes/Grok/Pi官网、OpenRouter FAQ、Ollama。遇整个官网只整合本课对应身份/登录/权限/最小运行/退出，不声称复制全部文档。
- 验收：五身份能讲清，真实只读运行证据、小改diff及恢复证据、所选工具认证和权限能说明。

## A2 原课对应

- 三类内容：Project instructions每次需要；Skill重复流程按需载入；One-off prompt本次任务。不要全部堆到规则文件。
- CLI-5：四字段规则卡；新session重述；负向请求验证禁止项；检查文件状态后定点撤销。
- CLI-6：review-changes只读Skill，读取diff，查秘密/危险命令/坏链接/缺验证，输出PASS或文件+原因；验证运行前后状态未变。注意原例git diff HEAD不含未跟踪文件，授课应说明检查范围。
- CLI-7：盘点→计划→修改→验证，任务例给两份README补测试命令；比较遗漏、恢复和真实验证。独立可验证任务才适合并行，依赖强/同文件修改/成功条件未明时先单agent。
- CLI-8：portable任务卡四字段任务/范围/禁止/成功；迁移时单独记录规则文件、Skill路径、权限、工具名、认证、费用。不同工具专属frontmatter不能盲复制。
- 必读：四厂规则和Skill文档；Agent Skills标准。精选项目含官方plugin、mattpocock/skills、superpowers、awesome-claude-code、Anthropic prompt tutorial、repomix、openwiki。后两者是整理上下文/理解项目辅助，不能替代权限与验证。
- 目录：Codex .agents/skills；Claude .claude/skills；Gemini .gemini/skills或.agents；OpenCode .opencode/.agents/.claude兼容。具体优先级须按产品，不宣称同名冲突规则通用。

## A3 原课对应

- 核心：MCP接能力，CI定义触发，Observability保留运行证据。只读→最小权限→demo→人工审查→需要时再写入。
- CLI-9：filesystem server只给demo绝对目录；读hello；越界请求拒绝；移除配置确认不可用。GitHub MCP用github/github-mcp-server，不用过时reference github server；read-only + toolset/allowlist。filesystem允许目录并不自动使所有工具只读。
- CLI-10：本人same-repo测试PR上跑只读review；contents:read起步；输出artifact/job summary可避免评论写权限；有评论需求才单独授权。secret进Actions secrets，禁止pull_request_target检出不可信PR代码。完整SHA pin；timeout与concurrency控制。Codex Action新的permission-profile :read-only与legacy sandbox不要混用。
- CLI-11：Task、provider/model、input/output usage、耗时、结果、成本来源；未知字段记未确认。订阅费用不等于按token推算。缓存TTL依供应商；重试/timeout是实设而非prompt承诺。
- CLI-12：团队Skill移植到第二干净repo；交付安装/权限/测试/卸载说明；审查脚本，固定版本，更新看diff；不把项目rules与secrets混进plugin。
- 回归：关闭MCP后目录切换和plugin reload不能重新启动；管理hook拒绝应生效，continue:false还须终止turn；只拒单次tool不一定终止整轮。release notes只是测试线索，不能当已通过证明。
- Playbook4：先看实际agent列表，Explore/Plan/general-purpose与自定义code-reviewer区分；独立任务派遣。其余6方向为范围、并行ownership、review证据、CI受限触发、成本停止、规则drift负向测试。
- 参考项目组：MCP官方/安全/GitHub/reference；Actions secure use、Claude/Codex Actions；Langfuse/Phoenix/Helicone/promptfoo；Claude plugins/official目录/superpowers marketplace；awesome-mcp目录/superpowers完整工作流。
- A3是A核心最后站；Stage8建议但非结业门槛。

## 研究人员

- 术语Source/Claim/Citation/Source Verification/Literature RAG/Reproducibility/Private Data/Human Review。
- 原练习用Attention Is All You Need，3问目标、方法组成、实验及限制，每答案附可定位证据，逐条supported/unsupported。必须在本地讲清论文对应知识，不能只把论文网址交回学员。
- 记录来源版本/DOI/作者/日期/问题/工具/输出/人工判定。跨论文先逐篇主张矩阵，再综合一致、冲突、条件差异；不能先编故事后补引用。
- 文献inbox保存元数据和纳排理由；实验保存数据版本、环境、seed、prompt、模型/工具版本、产物；投稿核claim、图表代码并披露AI使用。
- 必读：Gemini Notebook citation与privacy、Zotero quickstart、PaperQA2 README、DVC命令/管线、Zenodo quickstart。
- 项目全组：Notebook/Zotero/paper-qa；gpt-researcher/STORM/ChatPaper/zotero-gpt；ASReview/DVC/MLflow/Zenodo/repo2docker；flonat-research/AI-Scientist-v2；历史open_deep_research。用途和授权应分开，版本/可重复不等于结论有效，文献筛选仍保留人工纳排。
- 原课称ChatPaper CC BY-NC-ND，AI Scientist自定义授权，open_deep_research封存；这些是源课状态，本轮未逐repo核验，不能标作全部最新已实测。

## 开发者

- 八词覆盖IDE/Surface、Agent/Harness、Provider/Router、Model/Runtime、Sandbox、Approval、Diff/Rollback、Eval/Observability。
- 原练习README一句改清楚：只读计划、文件范围、最小检查、恢复方法→批准→单文件改动→diff+test；test通过不自动授权push/merge/deploy。
- 日常开发看diff与最小测试；PR review用文件行/具体证据；CI最小权限、可信trigger；批量重构先一文件试点并保留分批恢复。
- 必读Claude permissions、Codex security、Copilot cloud agent、Pi permissions/container、OpenRouter provider selection、Ollama。
- 项目覆盖Claude/Codex/Copilot/Cursor；OpenCode/Pi/Aider/goose/OpenHands/Cline；superpowers/repomix/Continue/Roo-Code。模型路由与仓库权限不能混为一谈；已停止维护或授权状态须按核查证据明确，不靠源课旧日期。

## 教师

- 无需编程前置；先学校核准工具与虚构数据。学习目标→草拟→教师核验→批准使用。
- 八词学习目标、脚手架、Rubric、形成性评价、AI素养、学生数据、人工审核、学术诚信。
- 五条边界：校方政策、避免真实学生数据、教师决策、事实/偏见/年龄/无障碍审核、明确允许与披露。
- 原主练习：15分钟小学高年级影子长短活动，纸笔手电筒，可观察目标、两层非直接答案提示、一题形成性评价、2题exit ticket、3个待核科学事实。
- 额外模板：四级可观察Rubric，不自动评分；3个虚构错误分组、概念缺口、非泄题提示，不推断学生身份能力健康。
- 三类场景：备课教材（课纲/难度/授权），课堂支援（提问/提示/错误整理），行政沟通（核事实语气收件人再批准）。自动化为选数据→最小化→草拟→审查→批准→发布，每步可停。
- 必读UNESCO GenAI、欧盟教师AI伦理、TeachAI toolkit。云产品参考Claude for Teachers、ChatGPT for Teachers、Notebook；课程项目HF agents-course、hello-agents、MS ai-agents-for-beginners；模板anthropics/skills、superpowers、prompts.chat。

## 知识工作者

- 九词Source/ActionItem/KnowledgeBase/PrivateData/HumanReview/AppConnector/MCP/Workflow/ApprovalGate。
- 原练习虚构会议：周五发布说明页；小林整理FAQ未给期限；客服主管9月3日前确认模板；全客户邮件尚未决定。输出Decision|ActionItem|Owner|DueDate|SourceSentence|NeedsConfirmation；未知不补猜；只草稿。
- 一次性聊天→组织核准connector→重复trigger/action；MCP仅自定义/跨client需要才加。
- 常见流程Email分流、会议行动表、周报、产品需求、知识库分类：每项先提供来源和审核；写入前gate，重复事件唯一ID去重，避免写回触发自身。
- 必读ChatGPT Apps、Claude目录、Gemini Connected Apps、Copilot connectors、MCP Registry、Zapier quickstart。
- 全资源：四云连接器；n8n/Make/PowerAutomate/Zapier；Langflow/Dify；Khoj/LobeHub/AnythingLLM；superpowers/MCP registry。自托管不保证本地数据：LLM、embedding、connector都可能外发。

## 日常用户

- 可直接学习，不必前置CLI；九词prompt/source/private data/hallucination/review/connector/CLI/local runtime/approval gate。
- 原练习虚构海报消息，输出Draft/Facts copied/Needs confirmation，不推测具体时间、不发送。
- 四种入口不是等级：chat草拟，connector搜索授权数据，CLI有限目录操作，本地runtime运行模型。只有整条链本地才等于不外发。
- 个人Agent延伸：目标、输入权限、可改范围、需停动作、持续状态与共享会话；产品不等于模型。各产品可用性只作日期明确的参考，不强制购买。
- 必读OpenAI prompt、Claude get-started、ChatGPT Apps、Claude desktop/web connectors、Gemini Privacy Hub、Ollama FAQ；其他直接产品参考看下方自动链接清单。

## 已核读官方资料的实质结论

以下是本轮已打开并读取的官方资料；不是全网站全文审读。

1. Claude Quickstart https://code.claude.com/docs/en/quickstart ：安装、启动项目、认证、问项目、提出改动的入门路径；CLI不等同Web/desktop。
2. Claude permissions https://code.claude.com/docs/en/permissions ：allow/ask/deny为工具权限；规则、模式、管理配置及sandbox是不同机制。路径规则与Shell执行覆盖不同，不能把一句项目规则当OS隔离。
3. Claude memory https://code.claude.com/docs/en/memory ：CLAUDE.md项目约定与auto memory不同；分层、路径规则、按需内容；官方现有AGENTS.md支持章节，源课“Claude只认CLAUDE.md”需标作推荐路径而非排他断言。
4. Claude skills https://code.claude.com/docs/en/skills ：按需程序卡、支持文件、作用域、显式/自动调用及特有frontmatter；legacy commands和skills关系不能推成跨工具统一。
5. Agent Skills spec https://agentskills.io/specification ：至少SKILL.md；name与description必需；name匹配目录且小写字母数字单连字符、1–64；description≤1024。scripts/references/assets可选。allowed-tools实验字段不是所有宿主可执行的权限限制。
6. OpenCode rules https://opencode.ai/docs/rules ：AGENTS.md、项目/全局层级、兼容文件；/init会创建或更新文件，不能称只读。
7. OpenCode skills https://opencode.ai/docs/skills/ ：.opencode/.claude/.agents项目及全局路径；未知frontmatter忽略；permission.skill allow/ask/deny；未发现时查拼写、元数据、重名、权限。
8. Gemini skills https://geminicli.com/docs/cli/using-agent-skills/ ：builtin<extension<user<workspace；.gemini/.agents；/skills list/reload/enable/disable；远程安装和激活有同意步骤。GEMINI.md页面也打开核查。
9. Codex AGENTS https://learn.chatgpt.com/docs/agent-configuration/agents-md 与skills https://learn.chatgpt.com/docs/build-skills ：已打开HTML并定位关键字段；有分层及override机制，技能按需内容；Markdown直读返回unsupported content type，不是页面缺失。
10. Codex security https://learn.chatgpt.com/docs/agent-approvals-security ：sandbox控制访问范围；approval决定越界请求处理；read-only+never用于非交互拒绝越界，不等于全权限；不要混同关闭询问与关闭隔离。
11. Codex Action https://learn.chatgpt.com/docs/github-action 和 https://github.com/openai/codex-action ：已打开，制作完整YAML前仍应定位当前inputs；源课明确permission-profile :read-only。
12. GitHub secure-use https://docs.github.com/en/actions/reference/security/secure-use ：最小GITHUB_TOKEN权限、secrets不明文、日志脱敏非保证、暴露后删除日志与轮换、不可信输入和checkout、第三方Action固定SHA。
13. MCP local https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers ：client启动本地server，Node与filesystem指定目录，权限由client+server实现；官方示例用Claude Desktop不是所有CLI同配置。
14. Claude Actions https://code.claude.com/docs/en/github-actions ：GitHub工作流中的Claude Code，与交互CLI/产品云review不同；可由事件或显式prompt触发，输出和执行权需独立约束。
15. UNESCO https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research?hub=387 ：已读官网摘要，强调人本、隐私、年龄适切、机构验证、教师能力。完整报告PDF本轮未通读，不能标全文覆盖。
16. 欧盟 https://education.ec.europa.eu/focus-topics/digital-education/actions/plan/ethical-guidelines-for-educators-on-using-artificial-intelligence ：已读更新入口，含情境问题、AI/data术语、责任原则、AI Act/GDPR背景；完整指南下载本轮未通读，不做地区法律结论。
17. TeachAI https://www.teachai.org/toolkit ：已读页面，涉及愿景、原则、范本、既有政策、家校沟通与持续反馈；范本不应原样当学校政策，需利益相关方审议；7原则子页未逐条通读。
18. Zotero https://www.zotero.org/support/quick_start_guide ：条目与附件分开，metadata、collection/tag、笔记、检索、引用/参考书目、同步协作；引用管理不等于研究质量审核。
19. PaperQA https://github.com/Future-House/paper-qa ：已读README调用/索引/模型配置。Settings+ask可指定本地paper_directory；Docs.add/query或异步aadd/aquery；检索→证据摘要→带引用回答；evidence_k与最终max_sources不同；默认embedding和各LLM角色可外发，需逐项改配置才是本地。Ollama支持示例不保证小模型质量。完整库未安装实测。
20. DVC https://doc.dvc.org/command-reference ：命令索引已读，涵盖init/add/remote/push/pull/checkout/repro/metrics/experiments；具体pipeline样例应再核get-started，不把命令索引说成读完全部参考。
21. Zenodo https://help.zenodo.org/docs/get-started/quickstart/ ：Upload→描述metadata→存草稿验证→publish取得DOI；发布后不能直接增删改原记录文件，练习用sandbox；版本化另建版本。
22. Notebook citation https://support.google.com/gemininotebook/answer/16179559 ：选择来源、citation悬停/点击回上下文、回答保存为笔记；citation只是验证入口。
23. Notebook privacy https://support.google.com/gemininotebook/answer/17004255 ：个人反馈可能携带prompt/source/output并人工审查，最多保留3年；Workspace/Education反馈内容不人工审查或训练，机构授权仍另外判断。
24. ChatGPT connected apps https://help.openai.com/en/articles/11487775-connectors-in ：当前重定向connected-apps-in-chatgpt；Settings>Plugins连接，provider授权与安装分开；功能依plan/region/workspace/role/model/interface；读写及第三方策略独立。
25. Claude directory https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory ：Customize中Skills/Connectors/Plugins；技能做流程，connector做服务授权；目录技能可启用/禁用，组织策略控制。
26. Gemini connected https://support.google.com/gemini/answer/14959807?co=GENIE.Platform%3DDesktop&hl=en ：工作/学校账号需符合Workspace版、管理员启用和活动设置；@指定app；来源可能旧，逐条核回最新材料。
27. Copilot connectors https://support.microsoft.com/en-us/microsoft-365-copilot/understand-copilot-connectors ：已打开页面，但浏览返回大量导航，核心正文仍需定位，当前笔记不宣称全文审读。
28. MCP Registry https://modelcontextprotocol.io/registry/about ：Preview，集中标准metadata与DNS namespace验证，代码包在npm/PyPI/DockerHub，目录发现不等于安全背书。
29. Zapier https://help.zapier.com/hc/en-us/articles/22234847450893-Zap-workflows-quick-start-guide ：trigger启动、一或多action；草稿配置、样本测试、字段映射、发布后反复运行；每步测试，监控重复/循环。
30. Ollama FAQ https://docs.ollama.com/faq ：localhost API与local/cloud要区分；OLLAMA_NO_CLOUD=1或server.json disable_ollama_cloud:true关闭Ollama云模型及web search；不能控制其他工具的联网。

## 未完成独立核读的边界

已完整读原课程8份及2份资源。直接资源目录中的每个项目没有逐仓库完整README/API审读；产品安装、本机CLI认证、CI发布、云端服务均未执行。上述未通读报告必须继续补读才能在最终课程标记“必读材料完整本地覆盖”。不能把下载源课原文等同其所有外链内容已覆盖。

## 后续补读：已进一步核对教育报告、DVC 和 Microsoft 正文

下述更新覆盖前文对应的“入口仅读”状态，但仍不把已读章节标为整个关联文献库全文。

- UNESCO 完整48页报告入口已成功解析：https://unesdoc.unesco.org/in/rest/annotationSVC/DownloadWatermarkedAttachment/attach_import_ab3dfd25-729d-41e8-877f-176076322557?_=386693eng.pdf&from=1&to=48 。正文授权是 CC-BY-SA 3.0 IGO，星号标记图片排除；若改编/全文本地镜像需保留对应授权，不可套MIT。已读目录与重点第3–6章，原文六部分是：生成原理/Prompt/教育模型；争议（数字鸿沟、监管滞后、未经同意使用数据、不透明、信息污染、无现实理解、意见同质化、深伪）；监管与四方责任（政府/供应商/机构/个人）；教育政策框架；具体教学研究用法；未来知识/版权/评价问题。教学应用表本身写“潜在但未被证实”，不能转述成已证实成效。课堂设计要保留独立推理、实物实验、人际讨论与学生自主性；工具可做研究整理、备课、1对1语言艺术练习、项目探究、无障碍，但数据薄弱群体可能被忽略，字幕/翻译也需核验，AI不能诊断特殊教育需求。2023产品及法规叙述仅作历史背景。
- 欧盟2026指南全文已解析政府教育网站托管PDF：https://code.intef.es/wp-content/uploads/2026/03/guidelines-on-the-ethical-use-of-artificial-intelligence-NC0125186ENN_marzo2026.pdf 。官方书目确认版本/DOI：https://op.europa.eu/en/publication-detail/-/publication/f692aa0b-17a7-11f1-8870-01aa75ed71a1/ 。已读p21–36核心问题与场景：人类监督、透明可解释、公平非歧视、社会环境福祉、隐私数据治理、技术稳健安全、问责。每类分别要求教师与学校回答。场景包含个性化学习、形成性反馈、LMS困难识别、作文反馈、学生项目、升学建议、学校预算、RAG教材、创意探究、行政沟通、多来源摘要。实施顺序为盘点数据和目的→校内共议→小群试点→评估学习收益/成本/伦理→定期培训复核；AI素养与数字素养相连。该指南明说不是AI Act执法解释，课程不应写成法律操作指南。
- TeachAI七原则子页已核读：https://www.teachai.org/toolkit-principles 。顺序为目标、合规、知识、平衡、诚信、自主权、评估。对应做法：服务教育目的和公平可及；沿用隐私/安全/采购规则；师生AI素养；列收益风险与措施；明确哪些任务可用AI和披露方式；保留人类决策；持续收集各方反馈并测实际成效。不得用AI文本检测器作为作弊定论；应增加过程性作品、口头解释、课堂独立作答等学习证据。工具包范本仍需本地审议，不能直接复制成学校政策。
- Microsoft connector正文已核读：管理员启用、许可、源系统已有权限共同决定可见范围；可找来源、摘要并引用，非自动获得新权限。排错按源文件能否直开→缩小项目/日期/标题→管理员启用→同步索引延迟。
- DVC补读 https://doc.dvc.org/start ：先Git仓库内dvc init，dvc add为数据生成小.dvc元数据文件，Git跟踪元数据，实际数据进入cache/remote；数据传输与Git提交不同。用版本切换+checkout恢复对应数据；pipeline和metrics另由dvc.yaml定义与repro/metrics比较。DVC保存可重建条件，不验证研究结论。

## 每份原文的直接外链清单（自动提取，非全部已核读）

### A1-cli-intro.zh-Hans.md
- https://openrouter.ai/docs/faq
- https://github.com/ollama/ollama
- https://code.claude.com/docs/en/quickstart
- https://learn.chatgpt.com/docs/codex/cli
- https://google-gemini.github.io/gemini-cli/
- https://opencode.ai/docs/
- https://block.github.io/goose/
- https://aider.chat/docs/
- https://pi.dev/docs/latest
- https://ollama.com/
- https://code.claude.com/docs/en/permissions
- https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html
- https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html
- https://hermes-agent.nousresearch.com/docs/
- https://github.com/xai-org/grok-build
- https://github.com/anthropics/claude-code
- https://github.com/openai/codex
- https://github.com/google-gemini/gemini-cli
- https://github.com/anomalyco/opencode
- https://github.com/aaif-goose/goose
- https://github.com/Aider-AI/aider
- https://github.com/earendil-works/pi
- https://github.com/NousResearch/hermes-agent

### A2-cli-workflow.zh-Hans.md
- https://learn.chatgpt.com/docs/agent-configuration/agents-md
- https://code.claude.com/docs/en/memory
- https://geminicli.com/docs/cli/gemini-md/
- https://opencode.ai/docs/rules
- https://learn.chatgpt.com/docs/build-skills
- https://code.claude.com/docs/en/skills
- https://geminicli.com/docs/cli/using-agent-skills/
- https://opencode.ai/docs/skills/
- https://agentskills.io/specification
- https://github.com/anthropics/claude-plugins-official
- https://github.com/mattpocock/skills
- https://github.com/obra/superpowers
- https://github.com/hesreallyhim/awesome-claude-code
- https://github.com/anthropics/prompt-eng-interactive-tutorial
- https://github.com/yamadashy/repomix
- https://github.com/langchain-ai/openwiki

### A3-cli-production.zh-Hans.md
- https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers
- https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- https://code.claude.com/docs/en/github-actions
- https://learn.chatgpt.com/docs/github-action
- https://github.com/github/github-mcp-server
- https://github.com/modelcontextprotocol/servers
- https://github.com/anthropics/claude-code-action
- https://github.com/openai/codex-action
- https://github.com/langfuse/langfuse
- https://github.com/Arize-ai/phoenix
- https://github.com/Helicone/helicone
- https://github.com/promptfoo/promptfoo
- https://code.claude.com/docs/en/plugins
- https://github.com/anthropics/claude-plugins-official
- https://github.com/anthropics/claude-code/releases/tag/v2.1.296
- https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices
- https://docs.github.com/en/actions/reference/security/secure-use
- https://github.com/obra/superpowers-marketplace
- https://github.com/wong2/awesome-mcp-servers
- https://github.com/obra/superpowers

### agent-paradigms.zh-Hans.md
- https://opencode.ai/docs/
- https://pi.dev/docs/latest
- https://openrouter.ai/docs/faq
- https://ollama.com/
- https://aider.chat/docs/
- https://block.github.io/goose/
- https://github.com/NousResearch/hermes-agent
- https://github.com/openclaw/openclaw
- https://github.com/anomalyco/opencode
- https://github.com/earendil-works/pi
- https://github.com/Aider-AI/aider
- https://github.com/aaif-goose/goose
- https://github.com/continuedev/continue
- https://github.com/ollama/ollama
- https://github.com/langchain-ai/langgraph
- https://github.com/crewAIInc/crewAI
- https://github.com/microsoft/agent-framework

### cli-agents-guide.zh-Hans.md
- https://openrouter.ai/docs/faq
- https://ollama.com/
- https://github.com/openai/codex/releases/tag/rust-v0.163.0-alpha.5
- https://github.com/google-gemini/gemini-cli/releases/tag/v0.65.0-nightly.20261010.g9b6e0265d
- https://code.claude.com/docs/en/overview
- https://github.com/anthropics/claude-code
- https://learn.chatgpt.com/docs/codex/cli
- https://github.com/openai/codex
- https://google-gemini.github.io/gemini-cli/
- https://github.com/google-gemini/gemini-cli
- https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/02-authentication.md
- https://github.com/xai-org/grok-build
- https://opencode.ai/docs/providers/
- https://github.com/anomalyco/opencode
- https://block.github.io/goose/
- https://github.com/aaif-goose/goose
- https://aider.chat/docs/
- https://github.com/Aider-AI/aider
- https://pi.dev/docs/latest/providers
- https://github.com/earendil-works/pi
- https://hermes-agent.nousresearch.com/docs/integrations/providers/
- https://github.com/NousResearch/hermes-agent
- http://localhost:11434/v1`
- https://code.claude.com/docs/en/permissions
- https://opencode.ai/docs/
- https://hermes-agent.nousresearch.com/docs/
- https://pi.dev/docs/latest

### for-developer.zh-Hans.md
- https://code.claude.com/docs/en/overview
- https://github.com/openai/codex
- https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent
- https://github.com/anomalyco/opencode
- https://github.com/cline/cline
- https://code.claude.com/docs/en/permissions
- https://learn.chatgpt.com/docs/agent-approvals-security
- https://github.com/earendil-works/pi#permissions--containerization
- https://openrouter.ai/docs/guides/routing/provider-selection
- https://docs.ollama.com/
- https://cursor.com/docs
- https://github.com/earendil-works/pi
- https://github.com/Aider-AI/aider
- https://github.com/aaif-goose/goose
- https://github.com/OpenHands/OpenHands
- https://github.com/obra/superpowers
- https://github.com/yamadashy/repomix
- https://github.com/continuedev/continue
- https://github.com/RooCodeInc/Roo-Code

### for-everyday-users.zh-Hans.md
- https://support.claude.com/en/articles/17631495-get-started-with-claude-duet
- https://help.openai.com/en/articles/10032626-how-do-i-prompt-chatgpt-effectively
- https://support.claude.com/en/articles/8114491-get-started-with-claude
- https://help.openai.com/en/articles/11487775-connectors-in
- https://support.claude.com/en/articles/11725091-when-to-use-desktop-and-web-connectors
- https://support.google.com/gemini/answer/13594961?hl=en
- https://docs.ollama.com/faq
- https://claude.ai
- https://chatgpt.com
- https://gemini.google.com
- https://perplexity.ai
- https://learn.chatgpt.com/docs/dots
- https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/
- https://docs.x.ai/grok-bot/overview
- https://instinct.com/
- https://tab.bot/
- https://www.tomo.ai/about
- https://poke.com/
- https://github.com/anthropics/claude-code
- https://github.com/openai/codex
- https://github.com/anomalyco/opencode
- https://github.com/google-gemini/gemini-cli
- https://github.com/ollama/ollama
- https://lmstudio.ai/
- https://github.com/f/prompts.chat
- https://claude.com/resources/articles/claude-duet
- https://learn.chatgpt.com/docs/whats-new/devday-2026
- https://about.fb.com/news/2026/09/introducing-muse-small-business/
- https://x.ai/news/team-bots
- https://docs.x.ai/build/overview
- https://instinct.com/terms
- https://instinct.com/privacy-policy
- https://tab.bot/terms
- https://tab.bot/security
- https://www.tomo.ai/privacy
- https://cognition.com/blog/interaction
- https://poke.com/pricing
- https://poke.com/privacy
- https://geminicli.com/docs/reference/tools/
- https://geminicli.com/docs/cli/sandbox/
- https://opencode.ai/docs/agents/
- https://opencode.ai/docs/providers/
- https://docs.ollama.com/cloud
- https://lmstudio.ai/docs/app/offline
- https://lmstudio.ai/app-privacy

### for-knowledge-worker.zh-Hans.md
- https://help.openai.com/en/articles/11487775-connectors-in
- https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory
- https://support.google.com/gemini/answer/14959807?co=GENIE.Platform%3DDesktop&hl=en
- https://support.microsoft.com/en-us/microsoft-365-copilot/understand-copilot-connectors
- https://modelcontextprotocol.io/registry/about
- https://help.zapier.com/hc/en-us/articles/22234847450893-Zap-workflows-quick-start-guide
- https://github.com/n8n-io/n8n
- https://academy.make.com/courses/FoundationC01?pc=workflow
- https://learn.microsoft.com/en-us/training/powerplatform/power-automate
- https://github.com/langflow-ai/langflow
- https://github.com/langgenius/dify
- https://github.com/khoj-ai/khoj
- https://github.com/lobehub/lobehub
- https://github.com/Mintplex-Labs/anything-llm
- https://github.com/obra/superpowers

### for-researcher.zh-Hans.md
- https://arxiv.org/abs/1706.03762
- https://notebooklm.google.com/
- https://www.zotero.org/
- https://github.com/Future-House/paper-qa
- https://support.google.com/gemininotebook/answer/16179559
- https://support.google.com/gemininotebook/answer/17004255
- https://www.zotero.org/support/quick_start_guide
- https://doc.dvc.org/command-reference
- https://help.zenodo.org/docs/get-started/quickstart/
- https://github.com/assafelovic/gpt-researcher
- https://github.com/stanford-oval/storm
- https://github.com/kaixindelele/ChatPaper
- https://github.com/MuiseDestiny/zotero-gpt
- https://github.com/asreview/asreview
- https://github.com/treeverse/dvc
- https://github.com/mlflow/mlflow
- https://zenodo.org/
- https://github.com/jupyterhub/repo2docker
- https://github.com/flonat/flonat-research
- https://github.com/SakanaAI/AI-Scientist-v2
- https://github.com/langchain-ai/open_deep_research

### for-teacher.zh-Hans.md
- https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research?hub=387
- https://education.ec.europa.eu/focus-topics/digital-education/actions/plan/ethical-guidelines-for-educators-on-using-artificial-intelligence
- https://www.teachai.org/toolkit
- https://www.anthropic.com/news/claude-for-teachers
- https://openai.com/index/chatgpt-for-teachers/
- https://support.google.com/gemininotebook/answer/16337734?hl=en
- https://github.com/huggingface/agents-course
- https://github.com/datawhalechina/hello-agents
- https://github.com/microsoft/ai-agents-for-beginners
- https://github.com/anthropics/skills
- https://github.com/obra/superpowers
- https://github.com/f/prompts.chat
