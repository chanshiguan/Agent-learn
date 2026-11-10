# 工具、权限、批准与恢复

这是独立选读。读懂一个概念就可以返回主线，不要求另装服务或完成额外作业。

## 四个问题分别回答

工具 schema 说明“能请求什么格式”；参数校验判断“这次请求格式是否有效”；授权判断“当前读者是否有权访问”；批准判断“这份具体写入内容是否被同意”。少一层，都不能靠更长的 Prompt 补齐。

## 固定流程与 Agent 的取舍

| 做法 | 优点 | 需要承担的代价 |
|---|---|---|
| 固定 RAG | 路径短、容易比较、成本可预测 | 不灵活决定多次查询 |
| 固定教学状态机 | 节奏清楚，便于内容审核 | 不自动诊断所有学习情况 |
| 工具循环 | 能根据结果选择后续动作 | 多轮耗时、失败、预算与权限控制 |
| 状态图 | 暂停、恢复与分支更清楚 | 新框架和检查点维护，仍要幂等 |

伴读中可以混用：简单问答走固定路径，跨资料核对才用 Agent，写笔记始终走预览批准。没有必要让一个循环管理全部行为。

## MCP 和多 Agent 放在哪里

MCP 提供工具连接协议，不负责证明每个调用都获准。多个 Agent 可以分工，也会增加通信、共享状态和成本。先找到单个 Agent 无法解决的具体瓶颈，再决定是否引入。

主线依据见 [Stage 3](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/03-tool-use-and-hello-agent.zh-Hans.md)。协议选读看 [Hello-Agents 第十章](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter10)；多角色可从 [第六章框架实践](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter6)了解。现在不读也能完成单 Agent 项目。
