# 第三课资源记录

核查日期：2026-11-03。页面正文是中文原创教学重组；不逐字复制官方文档。标号供课程内引用。学习任务在本地完成，外部链接仅用于溯源。

## Knowledge

- [S0：Stage 3 原始学习路线](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/03-tool-use-and-hello-agent.zh-Hans.md)
  用途：确定概念、六组练习、天气小项目、反思模式和扩展资料的覆盖范围。采用独立代码重新实现，不沿用可能过时的安装版本和云端价格。
- [S1：Ollama Tool Calling](https://docs.ollama.com/capabilities/tool-calling)
  必修来源。用途：单工具、多工具与多轮工具交互。官方示例主要是 Ollama 原生接口；本课主线使用已安装的 OpenAI-compatible SDK。
- [S2：Anthropic How Tool Use Works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works)
  必修来源。用途：模型和执行程序的分工、client/server tools、循环协议。
- [S3：ReAct 原始论文](https://arxiv.org/abs/2210.03629)
  [论文全文](https://arxiv.org/html/2210.03629v3)。必修来源。用途：交替推理、行动、观察的研究背景和局限；本课实现现代原生工具循环，不复刻论文 benchmark。
- [S4：Ollama OpenAI Compatibility](https://docs.ollama.com/api/openai-compatibility)
  用途：base_url、Chat Completions 兼容字段、接口差异。兼容一部分 API 不意味着供应商所有保证相同。
- [S5：Anthropic Define Tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)
  用途：名称、description、input_schema 与工具设计。
- [S6：Anthropic Handle Tool Calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)
  用途：tool_use_id、user 消息中的 tool_result、紧邻顺序、is_error 与保留原始内容块。
- [S7：OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
  用途：原生函数请求、工具结果关联、strict schema；同时区分 Responses 与 Chat Completions 的结构。
- [S8：Ollama Structured Outputs](https://docs.ollama.com/capabilities/structured-outputs)
  用途：本地结构化输出、JSON 与 JSON Schema 输出控制。
- [S9：JSON Schema Object](https://json-schema.org/understanding-json-schema/reference/object)
  用途：properties、required、additionalProperties 各自约束什么。
- [S10：OpenAI Python SDK](https://github.com/openai/openai-python)
  用途：错误分类、timeout、默认重试。课程显式覆盖重试设置，避免隐藏的重复请求。
- [S11：Gemini Function Calling](https://ai.google.dev/gemini-api/docs/function-calling)
  用途：补充顺序与并行调用的协议差异；本课不依赖 Gemini 服务。
- [S12：Anthropic Strict Tool Use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use)
  用途：区别 schema 约束、严格模式与应用权限检查。
- [S13：Reflexion 原始论文](https://arxiv.org/abs/2303.11366)
  用途：文字反馈与经验记忆，不等同于修改模型权重。
- [S14：Self-Refine 原始论文](https://arxiv.org/abs/2303.17651)
  用途：生成、反馈、修订的模式；不保证每次修改都会更正确。
- [S15：Instructor Ollama集成](https://python.useinstructor.com/integrations/ollama/)
  用途：Pydantic结果模型、JSON模式和本地模型；补充单元13提供完整案例。
- [S15补充：Instructor重试计数](https://python.useinstructor.com/concepts/retrying/)
  用途：区分验证重试与SDK传输重试，避免重复次数相乘。
- [S16：Outlines Ollama适配器](https://dottxt-ai.github.io/outlines/latest/features/models/ollama/)
  用途：from_ollama、输出类型、后端能力边界；补充单元13提供完整案例。
- [S16兼容信息：Outlines包元数据](https://pypi.org/project/outlines/)
  用途：核对1.3.3的Python兼容范围；本课使用Python3.11独立环境。
- [S17：CodeAct原始论文](https://arxiv.org/html/2402.01030v4)
  用途：代码行动、组合与执行反馈的研究背景；本课独立实现受限语法解释器，不运行完整宿主Python。
- [S18：Python AST](https://docs.python.org/3.14/library/ast.html)
  用途：解析和检查语法树，区分解析源码与执行源码。
- [S19：Python concurrent.futures](https://docs.python.org/3.14/library/concurrent.futures.html)
  用途：线程池、Future、并发结果收集与超时边界。
- [S20：Smolagents代码执行隔离](https://huggingface.co/docs/smolagents/en/tutorials/secure_code_execution)
  用途：对照本地解释器与隔离执行环境的边界；本课不安装框架。

## 原路线扩展资料目录（可选，不是本课前置任务）

以下项目保留原路线的扩展方向；没有声称完整整合每个仓库，也不沿用原路线的维护状态、授权状态或星级。

- [Anthropic Courses](https://github.com/anthropics/courses)：观察官方课程的教学组织方式。
- [Anthropic Tool Use Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/tool_use)：对照单工具和多工具应用。
- [Anthropic Quickstarts](https://github.com/anthropics/claude-quickstarts)：比较完整应用的连接方式。
- [Microsoft AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners)：扩展课程路线。
- [ai-agents-from-scratch](https://github.com/pguso/ai-agents-from-scratch)：比较不用框架的循环。
- [react-from-scratch](https://github.com/arunpshankar/react-from-scratch)：比较其他供应商和反思变体。
- [agent-implementation](https://github.com/mattambrogi/agent-implementation)：最小实现的历史参考。
- [GenericAgent](https://github.com/lsdefine/GenericAgent)：小型 Agent 实现的扩展参考。
- [Smolagents](https://github.com/huggingface/smolagents)：比较 CodeAct；代码执行比本课固定函数需要更强隔离。
- [QuantaLogic](https://github.com/quantalogic/quantalogic)：另一个 CodeAct 方向的实现。
- [LangChain ReAct Agent](https://github.com/langchain-ai/react-agent)：比较框架如何封装工具执行和状态。
- [hello-agents](https://github.com/datawhalechina/hello-agents)：中文 Agent 教材扩展。
- [HelloAgents](https://github.com/jjyaoao/HelloAgents)：配套实现扩展，使用时确认对应教材版本。
- [Instructor](https://github.com/567-labs/instructor)：类型模型、验证与受控重试。
- [Outlines](https://github.com/dottxt-ai/outlines)：约束解码方向。

## Wisdom (Communities)

- [Ollama Issues](https://github.com/ollama/ollama/issues)
  用途：拿着版本、最小代码、原始响应定位兼容性问题；issue 中的个案不是所有模型的结论。不要求加入社区。

## Gaps

- 先前列出的流式、工具选择、真正并发、ReAct实验解读、反馈与记忆、Instructor、Outlines和CodeAct知识缺口已补进单元9–15，并有完整案例、测试与课后练习。
- 本课不复制所有扩展项目的全部源码，也不把自己的小实验宣称为论文完整benchmark复现；云服务部署不在此课程任务内。
- 云端真实调用需要用户自己的服务权限与预算；本项目提供完整代码和离线协议测试，未用付费密钥做实测。
