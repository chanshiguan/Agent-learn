# 两条进阶支线的直接必读知识

## Contextual Retrieval：先补背景，再索引

片段“该服务可在24小时内取消”离开全文会丢掉主语。建索引前可给它附一段简短背景，例如“以下条款适用于虚构周末课程报名，版本v1”；原片段仍原样保存。背景和原文一起用于关键词/向量索引，回答引用仍回到原文位置。背景不是新的政策证据；若模型把条件补错，检索就会被污染，所以抽样核对背景、记录来源版本并在更新时重建受影响索引。

它与 query transformation 的区别在时点：前者处理入库资料，后者处理用户问题。不要把两者同时加入实验后把收益归因于某一个。最小练习把两份同名“该服务”条款标上各自项目，检查问题能否命中正确项目；参考判断是先区分范围，再比较检索，并非背景越长越好。

## Qdrant 与 Weaviate：融合到底合什么

Qdrant 的 hybrid query 可以先执行多路候选查询，再融合或重排；prefetch 是候选阶段，不是最终答案。用 RRF 时只使用名次，适合无法直接比较的分数。Weaviate 的 hybrid search 将关键词与向量信号合并，alpha 控制两者权重；相对分数融合先把每路分数缩放到可比较范围。过滤范围与候选数仍应一致。

下面用同样的三份文档比较差别。完整代码实现了排名融合的计算，没有启动 Qdrant/Weaviate 服务：

{{code:../examples/fusion_comparison.py}}

```bash
# 运行 courses/06-memory-rag/examples/fusion_comparison.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/06-memory-rag/examples/fusion_comparison.py
```

参考结果：相对分数融合 b、a、c；排名融合 a、b、c（a/b 同分时按 ID）。原因是分数融合保留了 b 在词法分数上的大优势，RRF 只知道两路分别第一、第二。不要把 alpha=0.5 解读为某一篇文档有50%概率正确。

## Ragas：把评测拆成可解释的指标

评测记录至少有 question、response、retrieved_contexts 和可选 reference。检索侧问“该来的证据来了吗、噪声多吗”，答案侧问“答了问题吗、断言受证据支持吗”。Faithfulness 不能只数引用 ID 是否存在：引用是真的但不支持断言，也会失败。Judge 的模型、提示和版本要记录，先用人工样本校准；评估模型本身也可能有偏差。

本课的 20 题实验给出了可重跑数据、检索指标、答案及人工复核入口，属于独立实现的透明基线，不是 Ragas 库已经运行。参考练习：给正确摘录加“且全年免费”，引用保持原 ID。ID 检查可能成功，人工忠实度应失败，因为资料没有价格事实。不能用关键词评分把这条断言算成正确。

## Memory overview 与 Add/manage memory

thread 内的 state/checkpoint 保存当前任务进度；跨 thread 的 store 保存获允许复用的信息。namespace 相当于资料所属空间，应由可信身份建立，不能直接相信用户输入“我是另一个人”。semantic search 是在存储中按意义找候选，不代表检索出的事实仍然有效；读回还要核对来源、时间、版本与授权。

本课 MemoryStore 的 SQLite 表提供用户隔离、版本比较、过期、删除与重启读取；summary_workflow 提供 thread 检查点。两者分别处理记忆和执行状态；这里的 preference 表没有实现 LangGraph 的完整 store API。原记忆练习使用 Chroma PersistentClient；Mem0 与 Letta 是后续产品选择。

写入可在回答过程中完成，也可后台提取。后台写入晚到时要防止旧版本覆盖新偏好；删除还需检查缓存和衍生索引。参考判断：用户改为长答后，迟到的短答写入不应覆盖新版。没有同意的敏感推断不保存。

## CoALA 与 Generative Agents：研究模型的边界

CoALA 把语言 Agent 看成记忆、行动空间和决策过程的组合。工作记忆承载当前上下文；长期记忆可分为语义事实、情节经历和程序性方法。外部行动改变环境，内部行动读写记忆、推理或规划。这个分类帮助问“信息存在哪里、由哪一步使用”，不表示给文件夹换三个名称就实现了论文系统。

Generative Agents 的设计将经历保存为记忆流，检索考虑近期性、重要性和相关性，再用反思整理高层认识、用计划组织行为。三种信号的尺度需要处理；近期事件不必最重要，相关叙述也不必真实。反思是由已有经历生成的推断，应保留依据，不能覆盖原始观察。论文研究模拟行为，不能把角色显得可信当事实助理准确率。

自测参考：用户上周说喜欢短答、今天明确改长答，应该优先当前明确选择；不能仅因旧短答被检索得更相似就采用。角色根据多次经历总结偏好时，必须区分观察、推断和待确认。

## Mem0 与 Letta：实现选择和原题

原支线要求完成记忆生命周期，没有要求必须安装 Mem0 或 Letta，更没有规定只能二选一。本课原练习采用 Chroma PersistentClient，补充实现用 SQLite 完成同意、更新、删除、隔离与期限；步骤在[原记忆实验](05-original-labs.md)和本章末尾。Mem0 面向事实提取、合并与记忆检索，适合想复用这些组件的应用；Letta 围绕有状态 Agent 组织可编辑记忆与工具循环。选择取决于需要独立记忆组件还是整套有状态执行方式；两种产品均不是本课必装前提。

验收相同：保存一项明确授权偏好、换问题读回、修改并验证新值、删除再查不到、检查另一个用户不能读到。只看到 add 返回成功不够。Chroma 原例的持久化通过不等于完整生命周期通过，综合任务还须运行本课更新、删除与隔离案例。

## 本章练习与参考答案

提交融合输出、一个引用存在却不支持的反例、记忆旧写入冲突与删除结果。完整代码在本章与实作章，验收是能解释哪一层负责什么：融合决定顺序；证据检查决定能否支持；授权决定能否读取；版本决定能否覆盖。四种责任不能用同一个相似度分数替代。

## 原 Memory 五步的完整对应答案

原题要求先保存短版回答偏好，再改成“先给表格”，同时记录来源、时间和保存期限。下面程序依次写入、结束第一个进程、另起进程读回、修改为表格、在删除前检查另一用户不可见、删除再查。它不是仅仅改了数据库值，grounded_rag 实际根据新偏好输出表格。

{{code:../examples/memory_lifecycle.py}}

```bash
# 运行 courses/06-memory-rag/examples/memory_lifecycle.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/06-memory-rag/examples/memory_lifecycle.py
```

参考：read_from_thread_A.value=先短后长；updated.value=先给表格，version=2；updated_at 是写入时间，expires_at 减 updated_at 为3600秒；display 以表格开头；other_user_before_deletion=null；deleted=null；passed=true。这里用 thread-A/B 标记两个教学会话，没有调用 LangGraph thread API。

此题完整底层代码是本课 memory_store.py 与 grounded_rag.py，完整代码页均可读。旧数据库增加 updated_at 时历史值保持 null，表示未知，不把迁移当天当成历史写入时间。独立作业将有效期改短，再验证到期查不到；若其他用户在删除后才查不到，不能据此证明用户隔离，必须在资料仍存在时检查。
