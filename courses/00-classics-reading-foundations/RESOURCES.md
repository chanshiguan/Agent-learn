# 完整课程的资料来源

本课程以可迁移的新开发环境为起点，不以课程编写电脑上的软件或模型作为学员前置。主线以两个指定仓库为技术依据，DOCX 小样本和教学代码为本课程的实际练习。根据新增的选读要求，知识拓展页另引入官方文档、工程博客与原论文，不增加主线必修任务。

## Knowledge

- [awesome-agentic-ai-zh Stage 0](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/00-foundations.zh-Hans.md)：终端、Python、文件、JSON 与可观察结果；用于导学和第 1 章。
- [awesome-agentic-ai-zh Stage 1](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/01-llm-basics.zh-Hans.md)：本地模型、消息、延迟、用量与连接错误；用于第 4 章。
- [awesome-agentic-ai-zh FastAPI 与 Docker 练习](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/examples/stage-7/05-deploy/README.zh-Hans.md)：Dockerfile、运行参数及宿主 Ollama 连接；先拆为第 2—3 章的纯文件实验，第 13、25 章再引入 Web 与组合部署。
- [Hello-Agents Extra07 环境配置](https://github.com/datawhalechina/hello-agents/blob/main/Extra-Chapter/Extra07-%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE.md)：独立环境和依赖安装；用于第 1 章。
- [Hello-Agents 第七章](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter7)：统一模型客户端、本地与线上服务的配置；用于第 4 章。
- [Hello-Agents 第八章](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter8)：文档进入检索流程的背景；用于第 5—12 章资料、检索、Embedding 和 Qdrant。

## Wisdom

可以通过两个仓库的公开讨论与问题记录了解其他学习者的卡点。参与讨论不是课程验收要求；分享报错时去掉密钥和私人讲稿。不把未经复现的单条讨论当作确定结论。

## 本课程新增的编排

同一组《狂人日记》讲稿贯穿主机读取、容器读取和镜像运行；先对照可确定的 JSON，再观察有波动的模型回答。Docker 入门和 DOCX 程序是围绕既有资料任务拆解出的桥接实验，不声称上游原文已经逐字提供这套伴读课程。

课堂代码固定直接依赖 `python-docx==1.2.0`、`openai==3.37.0`，在独立 Python 3.12 环境做安装检查。镜像使用 `python:3.12-slim`；标签及间接依赖仍可能变化，更严格的可重现发布留到后续阶段。具体验证状态另见验证记录。

## Gaps

- 课程没有本次目标 M1 16 GB 机器的速度和容量实测；不得把其他机器的结果作为保证。
- Docker、默认候选 `qwen2.5:3b` 和付费线上路线仍须按验证记录所列范围在实际学习环境检查。
- 本版采用 macOS 终端命令，没有提供原生 PowerShell 版本。课程内容和目录不依赖特定用户名，移到其他系统时须调整终端与容器网络差异。
- 主线与选读分开：外部拓展文章不是章节验收前置，不以厂商文章中的实验数字保证本项目效果。

## 新增选读来源

查阅日期：2026-11-10。知识拓展每页都标出相关来源和建议阅读段落。方法对比是原理与适用问题的比较，不是使用率或热度排名。

- [Python 3.12 虚拟环境教程](https://docs.python.org/3.12/tutorial/venv.html)：补充解释 Python、pip 与独立环境。
- [Docker 容器概念](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)：对照容器与虚拟机。
- [Ollama 接口兼容说明](https://docs.ollama.com/api/openai-compatibility)：说明兼容范围与本地连接角色。
- [Qdrant Hybrid Search](https://qdrant.tech/articles/hybrid-search/)：词项检索、稠密检索与融合的取舍。
- [Qdrant 重排序教程](https://qdrant.tech/documentation/tutorials-basics/reranking-hybrid-search/)：候选检索与重排各自的位置。
- [Anthropic Contextual Retrieval](https://www.anthropic.com/research/contextual-retrieval)：切块后补充背景的思路，发表于 2024-09-19。
- [HyDE 原论文](https://aclanthology.org/2023.acl-long.99/)：假想文档用于定位真实资料，不能充当引用证据。
- [LlamaIndex 递归检索](https://developers.llamaindex.ai/python/framework/integrations/retrievers/recursive_retriever_nodes/)：小块检索与父块上下文的关系。
- [微软 GraphRAG 文档](https://microsoft.github.io/graphrag/)与[全局搜索工程博客](https://www.microsoft.com/en-us/research/blog/graphrag-improving-global-search-via-dynamic-community-selection/)：结构化索引与全局问题；博客发表于 2024-11-15。
- [LangChain Retrieval](https://docs.langchain.com/oss/python/deepagents/retrieval)：固定检索生成流程、Agentic RAG 与查询增强。原检索文档地址目前会重定向到此页。


## 第 5—29 章新增的主线映射

- [Stage 2 Prompt](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/02-prompt-engineering.zh-Hans.md)：第 5 章的资料与指令分离、输出协议。
- [Stage 6 RAG 与 Memory](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/06-memory-rag.zh-Hans.md)及[进阶 RAG](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/resources/advanced-rag.zh-Hans.md)：第 6—12 章的检索、向量、切分、融合、重排与改写。
- [Stage 3 工具与 Agent](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/03-tool-use-and-hello-agent.zh-Hans.md)、[Hello-Agents 第四章](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter4)：第 17—19 章工具协议、循环、停止与执行边界。
- [Stage 4 框架](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/04-agent-frameworks.zh-Hans.md)：第 20 章从手写批准流程迁移到 LangGraph 检查点。
- [Hello-Agents 第九章](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter9)：第 14—16 章上下文、显式状态与教学流程；伴读教学状态与防剧透策略是本课程场景设计。
- [Stage 7 上线工程](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md)、[Hello-Agents 第十二章](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter12)：第 21—29 章安全边界、评测、观测、部署与恢复原则；公司阈值和批准不由教程代填。

本课程的网页、账号、草稿事务、范围审核、测量与维护脚本为围绕名著任务编写的完整练习实现，不能误称是上游原样代码。单机 SQLite、维护窗口发布、固定教学提示和保守片段展示都是明确教学取舍，不声称已实现多机高可用、个性化能力诊断或绝对防剧透。

## 后半程选读与接口核对

- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)：暂停、恢复和检查点的实际接口。
- [FastAPI 安全教程](https://fastapi.tiangolo.com/tutorial/security/)：认证机制与依赖注入背景。
- [Docker Compose 使用场景](https://docs.docker.com/compose/intro/features-uses/)：多服务配置与单主机部署定位。
- [Hello-Agents 第十章](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter10)：MCP 选读；不作为完成主线的前置。

直接依赖按各 requirements 文件固定，编写环境安装验证详见验证记录。间接依赖和容器摘要在第 27 章由实际发布环境记录；不能只凭一个 requirements 文件声称跨所有系统完全复现。

## 公开阅读材料

五份 DOCX 为课程新编讲解稿，正文、原著核对入口及解释边界见[公开样本说明](public-materials/index.html)。原有六道题保持题干，新的人工参考答案单独保存，不导入检索库。
