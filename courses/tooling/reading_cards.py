"""按资料职责给出本地阅读要点；链接仅保存在来源审计文件。"""
import re

CARDS = [
    (("building-effective-agents",), "从单次调用开始，按任务需要采用串联、路由、并行、主管—工作者或检查—修改循环。Workflow 由代码安排路径，Agent 根据观察选择下一步。工具应有清楚接口、失败反馈和停止条件；不要先选复杂框架再硬套任务。第四课与第七课阅读章给出完整模式解释。"),
    (("demystifying-evals",), "区分题目、trial、完整轨迹、最终外部结果和 grader。程序、模型、人工评分各有边界；能力测试与回归测试互补。固定版本、隔离环境、多次试跑、人工校准、保留集与线上反馈共同建立可信评测。第七课提供完整流程和案例。"),
    (("harness-engineering",), "把工作目标、可运行环境、代码库文档与反馈设施做成 Agent 可使用的系统。规则文件是地图，架构约束落到 lint/tests，长任务留下版本化进度。案例里的团队经验不等于所有项目的固定做法。第7.5课用单变量删除实验判断设施是否仍值得。"),
    (("multi-agent-research-system",), "并行研究适合彼此独立的搜索方向。主角色明确任务、工具、范围与返回结构，避免重复工作；引用与来源质量需另查。更多角色增加 token、协调和失败方式。特定研究系统的提升与成本不能外推所有任务。"),
    (("dont-build-multi-agents",), "工作细节分散在多个上下文时，合并者可能失去关键约束。对紧密耦合任务，保留一份连续上下文可能更可靠；对独立工作可以实验分工。文章是设计反例与经验，不是证明某个固定比例的任务都不该多 Agent。"),
    (("effective-harnesses", "harness-design-long-running",), "长期工作先建立启动脚本、特性清单、版本记录与进度。接手时先验证现状，一次完成可验收的小目标，留下恢复材料。压缩聊天历史不等于可靠记忆；更强模型出现后，用评测检查哪些修补步骤可以简化。"),
    (("infrastructure-noise",), "资源、超时、限额与并发会改变 benchmark 表现。固定环境，分开记录基础设施错误与模型判断错误，多次试跑后再比较。小幅分数差不能自动解释为稳定模型能力差。"),
    (("contextual-retrieval",), "给片段补简短文档背景，再用于向量和字词索引，减少片段脱离全文后的歧义；可接重排。保留原文与出处，避免背景生成错误传播。缓存降低重复全文处理成本；原实验相对改善不等于任何资料的保证。"),
    (("workflows-agents", "langgraph/overview"), "State 保存输入与中间结果，node 产生更新，edge 决定下一步；reducer 决定追加或覆盖。图既可以固定，也可以包含模型决策。框架不会自动补权限和终止；第四课提供真实 LangGraph 完整例子。"),
    (("langgraph/persistence", "langgraph/interrupts"), "Checkpointer 保存 thread 的执行状态；Store 可保存跨 thread 资料。InMemory 后端不跨进程持久。interrupt 后恢复可能重跑节点开头，副作用必须幂等；同 thread_id 配合恢复命令，不能把一段普通聊天当完整执行状态。"),
    (("langgraph/agentic-rag",), "把检索器变成工具，按问题决定是否查资料，评估候选，必要时改写问题重查，再生成。评分器也会错；循环需要上限与无新证据时的停止策略。先做两步 RAG 基线，再验证动态路线是否值得。"),
    (("deepagents/retrieval", "llamaindex.ai/python/framework/getting_started/concepts"), "索引阶段加载、切片、嵌入、存储；查询阶段检索、可选重排、生成与引用。Document/Node 是资料单位，Retriever 返回证据，Response Synthesizer 生成回答。索引不是训练，权限过滤来自可信身份。第六课覆盖完整管线。"),
    (("trychroma.com",), "Collection 保存 ID、文档、metadata 和向量；add 与 upsert 区别在新增或更新。向量维度和模型需一致；默认嵌入可能下载模型。Client 与 PersistentClient 的持久化范围不同，查询结果需同时保留来源。"),
    (("openai-agents-python/multi_agent", "openai-agents-python/handoffs"), "Manager-as-tools 保留主管的最终回答权；Handoff 转移后续控制权。两者都需要明确传递的历史、结构化输入、权限和停止条件。用代码编排便于确定顺序，用模型编排增加灵活性也增加评测成本。"),
    (("openai-agents-python/tracing",), "Trace 表示任务，span 表示子步骤。默认 exporter 与敏感数据设置需要显式检查；追加 processor 不等于替换原导出器。本地模型调用也可能伴随云端遥测。日志脱敏、访问和保留规则是独立责任。"),
    (("openai-agents-python/human_in_the_loop",), "工具要求批准时产生 interruption，保存 RunState，展示具体动作，人确认后恢复原顶层运行。Session 聊天记录不等于审批状态。审批要验证身份与内容版本；恢复后副作用仍需幂等。"),
    (("openai-agents-python/sandbox",), "区分 workspace 文件、活跃 session、snapshot 与聊天记忆。Manifest 定义新环境文件，续接 session 不会自动重置一切。Capabilities、用户身份、挂载、网络和生命周期共同决定能力；本地工作目录不等于强隔离。"),
    (("tools-computer-use", "computer-use-tool", "browser-use-tool"), "模型提出动作，应用执行并返回新观察。Anthropic toolset 结果匹配 tool_use_id 与 toolset_name；OpenAI computer_call_output 匹配 call_id 并回截图。批次按顺序检查，失败后不继续执行失效动作。第八课提供协议解释、策略和真实浏览器示例。"),
    (("code.claude.com/docs/en/memory",), "项目规则、用户规则、局部规则与自动记忆作用范围不同。主规则保持简短，详细资料按需读取；当前 AGENTS.md 支持受版本和配置影响，不沿用永久不支持的旧说法。规则是输入，权限仍由执行层控制。"),
    (("code.claude.com/docs/en/skills",), "description 帮助识别适用任务，正文定义步骤，references/scripts 按需加载。disable-model-invocation 与 user-invocable 不是同一个字段。allowed-tools 是预批准，不是绝对白名单。用触发正例、反例和缺资料测试验证。"),
    (("code.claude.com/docs/en/hooks",), "Hook 接收生命周期事件，执行确定性程序。先做观察型日志，再考虑阻断；不要将未经验证输入拼 shell。最少记录，避免凭证和原文泄露。第五课给出完整观察型 Python 程序。"),
    (("code.claude.com/docs/en/sub-agents",), "独立上下文适合大批读取和有限任务；任务说明要包含完成工作所需的信息，结果要同时给出结论和证据。隔离上下文不等于隔离共享文件。当前支持的嵌套能力与成本限制随版本演进，保留总任务、深度和预算上限。"),
    (("code.claude.com/docs/en/plugins", "code.claude.com/docs/en/plugin"), "Plugin 打包 Skills、agents、hooks、MCP 等能力，Marketplace 提供发现与分发。加入目录不等于安装所有插件。检查来源、版本、权限、作用域和卸载；第三方精选不是安全认证。"),
    (("code.claude.com/docs/en/agent-sdk",), "SDK 管理异步消息、运行结果与会话；检查 ResultMessage 的错误和终止类型。allowed_tools 是预批准，不是限制全部能力的工具池。托管还需身份、文件隔离、资源、日志和恢复，客户端代码不是整个运行时源码。"),
    (("modelcontextprotocol.io", "code.claude.com/docs/en/mcp"), "Host 使用 Client 连接 Server；Tools、Resources、Prompts 分别是能力、内容、模板。协议解决连接不自动提供最小权限。当前规范与旧初始化式示例要区分版本；第五课固定 Python SDK 1.x stdio 示例，由 SDK 处理协议。"),
    (("crewai",), "Agent 表达角色与能力，Task 描述工作和预期产物，Crew 组织任务；Flow 负责状态和控制路径。角色不是线程，多个角色不保证事实正确。第四课真实例子保留依赖范围，安装在独立环境。"),
    (("pydantic",), "类型约束检查字段、范围与结构，业务验证检查适用规则，证据核对检查事实。output_type/result.output 等接口依版本匹配。结构合法不等于答案可靠，confidence 字段也不是校准概率。"),
    (("smolagents", "codeact"), "代码型行动能把多步工具操作组合成程序，但允许执行的操作更多，也需要更严格的限制。使用受控执行器并限制文件、网络、资源和导入；不能拿任意 exec 当安全实现。第四课保留 Docker CodeAgent 真实例子。"),
    (("qdrant", "weaviate"), "混合检索把字词与语义候选合并，重排再次评估问题与文段。不同产品的分数和融合参数不同，不直接相加不相容分数。先测候选召回再测排序与答案，权限过滤在检索前落实。"),
    (("graphrag", "lightrag"), "图检索使用实体关系或社区摘要回答跨文档问题；构图与更新需要成本，错误关系会传播。GraphRAG 和 LightRAG 是不同项目，不能互换名称。简单单段问题先用基础检索，第六课解释选择证据。"),
    (("mem0", "langmem", "graphiti", "letta", "getzep"), "记忆组件可能抽取偏好、保存经验或建时间关系图。先设计授权、owner、来源、版本、更新冲突、过期、删除与隔离，再选库。测试跨重启和删除后的缓存，不能以添加成功代替全生命周期验证。"),
    (("2310.11511", "2401.15884", "2403.14403"), "Self-RAG 使用训练的反思 token；CRAG 根据检索质量选择补救；Adaptive-RAG 根据问题复杂度选择检索层次。普通 Prompt 或规则分支可以教学，但不等价于原论文模型训练与完整复现。"),
    (("2401.18059", "dspy"), "RAPTOR 通过聚类与摘要递归组织多层索引；DSPy 用模块、示例与指标优化提示/程序。二者不是同一种算法。保留训练/开发/测试边界；简单摘要树不应标成完整 RAPTOR 复现。"),
    (("2309.02427", "2304.03442"), "CoALA 区分工作记忆、长期语义/经历/程序性记忆和行动循环；Generative Agents 用经验流、检索、反思与计划组织角色。研究中的可信行为不等于生产事实正确性或隐私保证。"),
    (("unesco", "teachai", "op.europa.eu"), "教育使用以人的能动性、事实核查、适龄、隐私、公平、可及性、透明和问责为核心。活动与评价对应学习目标，教师审核草稿，保留过程证据，不用 AI 检测器直接判作弊。教师分支给出本地活动与检查流程；外部报告的授权独立于原仓库 MIT。"),
    (("dvc.org", "mlflow", "wandb"), "代码、数据和实验配置分别版本化，关联运行参数、环境与结果。工具能帮助重现记录，但不能证明科学结论正确。先复现小规模 baseline，再做单变量实验，失败记录也保留。"),
    (("playwright", "browser-use", "browsergym", "webarena", "osworld", "mind2web"), "区分浏览器执行器、Agent 编排、测试环境与数据集。动作前策略检查、动作后外部状态验证、截图与收据都必要；旧坐标与新页面不能混用。第八课在受限虚构页给出完整执行案例。"),
    (("e2b", "daytona", "firecracker", "gvisor", "docker", "sandbox"), "比较容器、虚拟机、用户空间隔离和托管运行环境的实际边界。限制挂载、网络、用户、资源、生命周期与输出，不让学习任务接触宿主凭证。环境能启动不等于安全边界已经验证。"),
    (("swe-bench", "terminal-bench", "tau2", "tau-bench", "gaia", "harbor"), "Benchmark 测特定任务分布，比较时固定数据切分、环境、harness、工具、模型参数、超时、grader 和次数。检测评分漏洞与奖励投机，人工抽查外部结果，不把榜单名次直接当业务能力。"),
]


def clean(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'!\[[^]]*\]\([^)]*\)', '', text)
    text = re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'https?://\S+', '（网址见来源记录）', text)
    return text.replace('<', '&lt;').replace('>', '&gt;')


def card(url, info):
    for patterns, body in CARDS:
        if any(pattern in url.lower() for pattern in patterns):
            return body + '\n\n**学习定位**：结合对应课程的中文讲解、完整代码和课后练习阅读。'
    contexts = list(dict.fromkeys(clean(item) for item in info['contexts']))
    context = next((x for x in contexts if len(x) > len(info['title']) + 15), info['title'])
    return ('**原课程中的具体用途与边界**\n\n' + context[:1600] +
            '\n\n这里保留原课程对这项资料用途的介绍，没有逐篇讲解该网站的全部内容。完成课程所需的知识和练习，请看各课的对应表与本地实作章。外部网站或仓库不需要全部读完；介绍中的宣传说法也需要另外验证。')
