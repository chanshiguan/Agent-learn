# 原练习 README 的必读补充：从向量到可维护资料库

基础概念读完后，按本章的练习编号了解模型、资料库和切分接口，再到[原五题实作](05-original-labs.md)运行对应案例。这里整合了原练习 README 中要求阅读的知识。标为“进一步阅读/大型部署/成熟项目”的工具是比较选项，不要求安装整个目录。

## 练习一：Sentence Transformers 与云端 Embedding

Sentence Transformers 把句子编码成固定维度向量，encode 的输入可以是一批文本；比较时使用同一个模型、相同预处理和距离定义。余弦比较方向，点积也受长度影响；只有归一化后才可把二者的排序视作同一种情况。先记录模型名、维度、句对和得分，再看近义句是否排在无关句前。否定句仍可能很相似，所以 embedding 不是真假判断器。[官方相似度说明](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)

OpenAI text-embedding-3-small 是另一种由服务返回向量的选择。生成模型与 embedding 模型职责不同；不能把 gemma 的聊天文本当向量，也不能把两种 embedding 的文档向量和查询向量混查。更换模型通常需要重新编码全部文档，并建立新索引版本。调用前考虑资料会发送到哪里、批量大小和用量；本课不依赖某个固定价格。

完整本地模型、余弦计算与句对输入已经在原练习 starter.py 中；用 mock test 验证接口，再运行本地模型路径验证语义。如果没有下载模型权重，字符计数实验只能验证基本计算，不能算作 Sentence Transformers 的实际运行结果。

## 练习二与五：Chroma 客户端、Embedding Function 与持久化

EphemeralClient 在内存中；PersistentClient 写指定磁盘目录；HttpClient 连接独立服务。Collection 组织 id、document、embedding 与 metadata。输入文段而未给向量时，由 embedding function 编码；它可能下载权重或访问云服务。查询必须与入库使用相容的编码模型，维度相同也不足以证明语义空间相同。[Chroma Clients](https://docs.trychroma.com/reference/python/client)

原练习五已使用 PersistentClient，并用两个新 Python 进程证明保存后能找回。它的 remember 对完全相同事实去重，recall 取相关文段，再把记忆放进下一次模型输入。这个功能与用户隔离、修改、删除、保存期限是不同验收项；后四项由本课补充实现展示。所以，原例用的是 Chroma 持久存储，不是 Mem0 或临时存储。

原题完整实现：

{{code:../examples/upstream/05-long-term-memory/starter.py}}

原题测试中的 TinyEmbeddingFunction 只用于持久化验证，不下载语义权重；重启后能从同一目录找到记录说明磁盘路径正确，不说明相关性高。跑法与环境见[原五题实作](05-original-labs.md)。本课 [Memory 五步](07-direct-readings.md)继续验证生命周期。

VectorDBBench 是比较检索数据库工作负载的工具。先固定数据量、维度、索引参数、过滤条件和并发，再同时看质量、吞吐、延迟与成本；某排行榜在另一份数据上的第一名不能替你决定部署。当前小练习不需要大型数据库压测。

## 练习三：解析、结构切分与语义切分

解析把 PDF/DOCX/HTML 变成可处理的内容；切分决定检索单元。Unstructured 等解析器可帮助保留标题、表格和位置，扫描版还涉及 OCR；解析错序、页眉混入或表格列丢失，后面再好的 embedding 也会索引错误资料。先抽查解析结果，再研究切分策略。

递归结构切分优先保留段落，过长再按句子或更小分隔符切，chunk_size 控制长度、chunk_overlap 保留邻接背景；长度按字符还是 token 取决于配置，不能只比较参数数字。[LangChain splitters](https://docs.langchain.com/oss/python/integrations/splitters)

SemanticSplitterNodeParser 则比较相邻句子组的向量距离，在变化大的地方切开；buffer_size 影响相邻句的组合范围，breakpoint_percentile_threshold 指距离分布中的分位门槛。它不是“超过95%概率就切”，也不等于 Markdown 标题切分；语言断句和 embedding 质量都会影响结果。先比较原三种简单切法，只有语义断点能改善固定评测时才引入。[Semantic Splitter](https://docs.llamaindex.ai/en/stable/api_reference/node_parsers/semantic_splitter/)

原三种算法、全部输入与完整输出方法在 upstream/03-chunking-comparison/starter.py。本课不把简化算法标成 LlamaIndex 库实现；需要该产品的选修者要另建相容环境，不能因为学了名词就算安装验证通过。

## 练习四：LlamaIndex、LangChain 与受管 Retrieval

LlamaIndex 的 loading 负责读资料，indexing 建立索引，storing 保存可复用状态，querying 组织检索与回答，evaluation 判断结果。Document 是源材料，Node 是带来源的片段，Retriever 返回候选，Response Synthesizer 用证据生成答案。换 Query Engine 不代表重新训练模型。[RAG 工作过程](https://docs.llamaindex.ai/en/stable/understanding/rag/)

LangChain 的 two-step RAG 固定先检索再生成，调用次数比较可控；agentic RAG 把检索变为工具，由模型决定何时调用，灵活但需预算和停止条件。混合做法可固定必须检索，同时让模型决定是否最多再查一次。本课 grounded_rag 直接展示各步骤的实现，没有调用这两个库的 API；原题和第六课综合例给出了完整管线。

受管 Retrieval 把切分、编码、索引生命周期交给服务。顺序是创建 vector store→上传文件并等待索引完成→带过滤条件搜索→核对返回片段→按需要再生成→删除临时资源。上传成功不等于索引完成，存储位置也不再是本机。过滤条件必须来自可信身份；本例 alice 只是固定演示身份。

下面是完整选修代码，接口已对照本项目 OpenAI 3.37.0 源码；默认不联网。使用 --live 会把脚本中的一句虚构资料发送到自己的 OpenAI 账户，可能产生费用；教材核验时没有执行这条云端路径。

{{code:../examples/managed_retrieval.py}}

```bash
# 运行 courses/06-memory-rag/examples/managed_retrieval.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/06-memory-rag/examples/managed_retrieval.py
```

具备账户且决定实测时才在同一命令末尾加 --live。结果须包含真实片段，answer_generated=false 表示尚未调用生成模型；空结果也应如实保存。cleanup_errors 为空才说明本次创建的文件和 store 都已清理；非空时按返回的 ID 在自己的账户内检查，不删除其他资源。无需这项云服务也能用本地完整 RAG 完成本课。

## 扩展教材与本地自测

hello-agents 是扩展教材入口，本课程所需的 embedding、向量库、切分、RAG 和记忆能力已在上述五题与本地章节展开；它不是必须再读的一整套先修课。Mem0/Letta 的选择与边界在直接必读章，不能因为列表有链接就把它们列成必装依赖。

自测及答案：重开后记录不见先查数据库路径和客户端种类；语义相似但否定方向相反不判事实一致；上传已完成却搜索不到先查索引状态；95 分位是相对距离门槛而非正确率。交三份证据：模型与维度记录、跨进程读回结果、同题切分对照，并说明一次失败属于哪个环节。原案例代码与本章新增代码均完整提供。
