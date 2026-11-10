# 重排序：把更合适的证据往前排

假设检索找回了 20 段资料，而请求里只准备放 4 段。真正回答问题的那段排在第 12 位，仅仅“找到了”仍不足以让模型看到它。这里的 20 和 4 只是说明流程的示例，不是课程推荐参数。

## 为什么再评一次

第一轮先较快地取候选；第二轮只针对候选，用更细的相关性信号重新评分。Cross-encoder 和 late interaction 等是不同实现路径，不必一开始全部掌握。重排作用于已有候选，无法恢复第一轮根本没取回的证据。[Qdrant：Hybrid Search with Reranking](https://qdrant.tech/documentation/tutorials-basics/reranking-hybrid-search/)

## 本项目可以怎样做对照

给同一问题固定一份候选列表。人工标出哪几段确实解释了问题，再比较重排前后这些片段的位置。这样才能区分“第一轮检索进步”和“第二轮排序进步”。

如果问题指定第一讲，先遵守讲次过滤；不要希望重排模型替你补救所有业务限制。分数高也不是“该观点为真”的证明。

## 得到什么，付出什么

更相关的材料有机会进入有限的请求空间；代价是额外评分与延迟，模型部署或调用也可能带来成本。候选越多，工作量通常越大；具体收益要结合问题集、硬件和实现测量。

## 推荐选读

[Qdrant 官方教程：Hybrid Search with Reranking](https://qdrant.tech/documentation/tutorials-basics/reranking-hybrid-search/)（英文，概念部分约 10 分钟）。先看 Ingestion Stage 和 Retrieval Stage，认清检索与重排的位置；不要因为教程用了特定服务就现在去开通账号。

如果证据根本不在候选里，返回[混合检索](rag-hybrid.html)或[查询改写](rag-query.html)更有帮助。
