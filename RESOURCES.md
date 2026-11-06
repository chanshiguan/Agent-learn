# Prompt Engineering 学习资源

## Knowledge

- [Anthropic: Interactive Prompt Engineering Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)
  九章交互式课程与三个附录，从消息结构、清晰指令、角色、数据分隔到 Few-Shot、幻觉、链式 Prompt、工具调用和检索。适合：动手改 Prompt、建立直觉。注意：部分模型名和 API 代码已旧，以概念和练习为主。
- [Anthropic: Chapter 1 — Basic Prompt Structure](https://github.com/anthropics/prompt-eng-interactive-tutorial/blob/master/Anthropic%201P/01_Basic_Prompt_Structure.ipynb)
  讲 `model`、`max_tokens`、`messages`、`system` 和消息角色的基本结构。适合：理解 API “信封”与 Prompt “信件内容”的区别。
- [OpenAI: Prompt Engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)
  当前 OpenAI API 的工程指南，涵盖输出读取、模型选择、指令优先级、消息角色、Prompt 代码版本化、Few-Shot、上下文、当前模型和推理模型。适合：把 Prompt 放进程序和生产流程。
- [Google AI Studio: Prompt Design Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
  系统的策略清单：清晰指令、输入类型、约束、输出格式、Few-Shot、上下文、任务拆分、参数、迭代、Gemini 3 和 Agent 工作流。适合：遇到具体问题时查找对应策略。

## Wisdom (Communities)

- [Anthropic tutorial discussions and issues](https://github.com/anthropics/prompt-eng-interactive-tutorial/issues)
  用于观察其他学习者的常见卡点和教程兼容性问题；不把单个 issue 当成权威结论。

## Gaps

- 第三课的工具调用、错误处理、ReAct 与固定评测资料已补充到 [第三课资源记录](courses/03-tool-use-and-hello-agent/RESOURCES.md)，中文学习入口见 [第三课](courses/03-tool-use-and-hello-agent/index.html)。
- 更完整的生产级 Prompt Injection 防护、持久记忆和长期 Agent 评测留待后续阶段。
# 后续课程资料入口（2026-11-03）

- [双轨完整本地目录](courses/index.html)：原编号对应的后续主线、身份分支、结业与课末练习。
- [原课程来源记录](courses/reference/SOURCES.md)：固定版本、原文与官方资料入口；外部链接只用于核查。
- [本地知识卡](courses/reference/source-readings.html)：必读文章概念与工具用途，配合各课阅读章使用。
- [验证记录](courses/VERIFICATION.md)：区分代码提供、离线测试、真实模型和未运行的外部依赖。

