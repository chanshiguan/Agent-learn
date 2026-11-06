# 带证据、会拒答、能遗忘的助手

## 单元一：先把资料和答案分开

RAG 是在回答时取出相关资料，再根据资料回答。模型参数中的知识、这次检索资料和用户偏好是三件事。报名政策属于知识库；“喜欢先短后长”属于记忆；本次问题与工具结果属于工作上下文。把用户偏好写进政策库会混淆适用对象，把整段聊天永久保存也不等于设计了记忆。

完整例子内置三类虚构公共资料：课程时间、报名条件、退款规则及例外，并加两个用户的私人编号。每段都有稳定 ID、owner 和 text。真实导入还应记录来源路径、文档版本、段落位置和更新时间，不能只存一段匿名文字。

## 单元二：不用下载权重先看向量怎样排名

向量是一个数字列表。示例把每个中文字或英文数字词的出现次数放进列表，余弦相似度比较方向。这是可手算的字符统计基线，不是语义 embedding；“报读”与“报名”的关系不会自动学出来。真实 embedding 模型是通过训练把文本映射到向量，改变模型后通常必须重建库，不能混合维度或只换查询端。

```bash
# 运行 courses/06-memory-rag/examples/grounded_rag.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/06-memory-rag/examples/grounded_rag.py
# 运行 courses/06-memory-rag/examples/grounded_rag.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/06-memory-rag/examples/grounded_rag.py --compare
# 运行 courses/06-memory-rag/examples/grounded_rag.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/06-memory-rag/examples/grounded_rag.py 'Bob私人预约编号' --user alice
# 运行 courses/06-memory-rag/examples/grounded_rag.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/06-memory-rag/examples/grounded_rag.py '火星天气'
```

默认不调用模型。第一条输出候选、逐条引用与摘录；第二条为八题分别输出纯向量与融合的排名指标；后两条应拒答。注意“召回了片段”不保证片段回答了问题，字符重合可能只是噪声；这也是要看逐题结果而非只看总分的原因。

如果本机已有支持 embedding 的 Ollama 模型，可传 `--embedding-model` 加它的确切名称；`ollama list` 只列已装模型，不保证它们都支持 embedding。选用新权重时才需要下载。以下使用一个明确的可选模型路径：

```bash
# 下载本行指定的模型；已有且未更新时无需重复下载。
ollama pull nomic-embed-text
# 运行 courses/06-memory-rag/examples/grounded_rag.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/06-memory-rag/examples/grounded_rag.py --embedding-model nomic-embed-text --compare
```

下载需要网络与磁盘；没有执行不影响先理解控制流程，但不能把字符基线的结果写成语义模型实验结果。真实模型和字符基线各自设数据版本与指标，不混在一张“改进”表中。代码的字符相似度门槛0.12、真实 embedding 门槛0.25只是教学起点，换数据或模型必须用正反例重新校准，不能当通用拒答保证。

## 单元三：检索前过滤，生成时保留引用

先由可信调用者确定用户，再只在该用户可见的集合里排名；不是先返回全部内容再让模型“别看私人部分”。这个 CLI 的 user 是课堂固定选择，生产服务必须从认证会话获取身份，不能相信请求正文自报 alice。

`retrieve` 返回整条 `{id, owner, text}`，不会丢掉 ID。`generate` 的默认模式逐条摘录并引用，所以可以追到原文。`--live` 才调用现有 gemma4:e4b；程序检查 JSON 和引用范围，然后把答案标为 NEEDS_REVIEW。人工逐句看：哪个来源支持这个数字或条件？有没有把“不退款”改成“退款”？有没有漏掉主办方取消的例外？

```bash
# 运行 courses/06-memory-rag/examples/grounded_rag.py，按本行参数完成当前案例并核对输出；--live 会进入真实服务路径，需先满足本章环境要求。
.venv/bin/python courses/06-memory-rag/examples/grounded_rag.py '主办方取消课程退款' --live
```

完整代码如下。`run` 读记忆、检索、生成；`compare` 只测排名；CLI 在临时数据库保存偏好、重开读取、最后删除。正式持久化时换成你指定的数据库路径，不能再用自动清除的临时目录。

{{code:../examples/grounded_rag.py}}

## 单元四：Memory 的完整生命周期

同一用户的偏好键是 answer_style。写入前要求明确同意；值限制为“先短后长”“分步解释”“先给表格”三种；source 表示为什么保存；expires 表示有效期；version 防止旧任务覆盖新设置。读取用 owner＋name；更新带 expected_version；删除后再读必须 None；另一个用户应读不到。

{{code:../examples/memory_store.py}}

并发写入用 SQLite 写事务保护“读版本→比较→更新”。这不是完整身份系统，删除也只删除本程序数据库中的记录；若以后增加缓存、向量索引或备份，应在删除流程中一并处理。语义记忆保存事实与偏好，经历记忆保存发生过什么，程序性记忆保存如何做；不要把某次失败的推测自动提升为永久规则。

## 单元五：把原五题连接起来

原 01-embeddings 观察同义、反义和无关句；02-vector-db 把片段和 ID 放进 Chroma；03-chunking-comparison 比较固定长度、段落与标题；04-full-rag-pipeline 跑检索生成；05-long-term-memory 观察保存与读取记忆。保留这些代码作为分解实验。本章 grounded_rag 是带逐条引用的综合参考实现，不能用原 04 丢 ID 的实现验收“逐条引用”。

切分时让退款条件和例外尽量保持在可一起召回的范围。overlap 是重复窗口，不是越大越好；太大会增加相同证据多次出现。标题切分依据结构，语义切分依据内容变化，二者不能仅改名字就当同一实验。

Chroma 的操作顺序为创建 client → collection → add 文段、ID、metadata → query → 同时取 ids/documents/metadatas。持久客户端必须指定目录；临时客户端重启丢失。更改资料用更新或 upsert，并测试旧内容是否还会命中。LlamaIndex 的 Document、Node、Index、Retriever、Response Synthesizer 则把同一流程拆成不同职责；Query Engine 组合检索与生成，不是训练一个新模型。

## 单元六：八题验收与人工评分

运行 compare 后保存输出，人工填写每题：期待证据、实际候选、是否漏例外、回答是否支持、耗时。有关退款的例外题需要普通规则和例外共同出现；陌生问题与其他用户私密资料不能生成答案。Recall@k 的分母是已标注的所有相关片段，不是返回 k；无答案题用拒答正确性单列，不计算虚构的 recall=1。

机器必过：未知引用拒绝、越权读取拒绝、记忆重开成功、旧版本更新拒绝、删除后 None。人工必过：回答没有错数字、错否定或漏关键例外；每条事实有支持；无证据不猜。任何一条关键事实错误即返回修改，不让格式分抵消。

独立作业：换成你自己编写的三份资料，先保持纯检索不变，验证八类问题；然后只增加混合检索或重排一项。参考不是要求分数一定上升，而是能解释哪题为什么变了。接着读[进阶检索与长期记忆](04-advanced.md)，了解怎样按失败原因选择改法，再做[20 题 A/B/C 实验](06-abc-experiment.md)。选择依据和完整步骤都在项目中。
