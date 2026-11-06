# 2026-11-04 补齐时核对的官方来源

这些链接用于来源审计；学习步骤、完整示例和答案已经写进本地课程，不要求学习者打开外站。主课和第六课两条直接支线共 98 个来源条目在 required-readings.json 中分别注明知识点、精确章节、实例与验收；同一来源可在不同课程出现。

- [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart)：核对安装、首次会话和登录。
- [Claude Code setup](https://code.claude.com/docs/en/setup)：核对原生安装、Homebrew、PATH 与更新渠道。
- [Create a plugin](https://code.claude.com/docs/en/plugins/create)：核对目录、manifest、--plugin-dir 和临时加载。
- [Dynamic workflows](https://code.claude.com/docs/en/workflows)：核对 meta、agent/pipeline、schema、null、保存与加载、版本要求。教学脚本为两份虚构文件的独立案例。
- [Agent SDK Python](https://code.claude.com/docs/en/agent-sdk/python)：核对 ClaudeAgentOptions、tools、strict_mcp_config、ResultMessage、resume 和预算。
- [Hosting Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)：核对子进程、工作目录与会话存储责任；本地单任务示例不冒称多租户生产平台。
- [LangGraph Workflows and Agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)：核对动态工作者与 reducer；实际安装版本 1.2.19。
- [Agents SDK Orchestration](https://openai.github.io/openai-agents-python/multi_agent/)：核对主管工具与 handoff，安装 0.24.0 源码及真实 Runner 进一步验证。
- [Ollama EmbeddingGemma](https://ollama.com/library/embeddinggemma)：核对下载、/api/embed、模型体积与最低 Ollama 版本；本轮未下载权重。
- [Qdrant Hybrid Queries](https://qdrant.tech/documentation/search/hybrid-queries/)：核对多路候选与融合责任。
- [Weaviate Hybrid Search](https://docs.weaviate.io/weaviate/concepts/search/hybrid-search)：核对相对分数融合、排名融合和 alpha；本地程序仅演示数学，不声称启动数据库。

其他直接阅读继续依据项目内已有核读记录、冻结原课程与相关章节，未把本次重新访问少量页面说成重新逐字读完所有来源。


## 本轮全量 review 追加

- GitHub API 核对上游 HEAD 与固定提交一致。原练习 README 的必读/学习资源也纳入清单，147条关联并非147篇去重文章。
- Chroma 原例源码与官方客户端文档确认 PersistentClient 已持久化；更正此前将它误写为临时存储/Mem0 的描述。
- [Chroma Clients](https://docs.trychroma.com/reference/python/client)、[Sentence Transformers 相似度](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)、[LangChain Splitters](https://docs.langchain.com/oss/python/integrations/splitters)、[LlamaIndex Semantic Splitter](https://docs.llamaindex.ai/en/stable/api_reference/node_parsers/semantic_splitter/)、[RAG 工作过程](https://docs.llamaindex.ai/en/stable/understanding/rag/)。
- [Anthropic Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)、[FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)、[Docker 端口发布](https://docs.docker.com/engine/network/port-publishing/)。
- [官方 filesystem MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)：核对客户端 Roots 会改变实际允许目录，补入操作验收。
- [Attention Is All You Need v7](https://arxiv.org/html/1706.03762v7)：有限短摘录与三问定位，不重新分发全文。
- OpenAI 受管 Retrieval 案例首先核对本机 openai 3.37.0 的 VectorStores/Files 源码签名；未进行云端调用。
