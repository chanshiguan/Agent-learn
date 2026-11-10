# 检验改写有没有改变原问题

本单元预计 **35—50 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 好改写必须保留问题的边界

“为什么不赞同”不能被改成“为什么赞同”。作品、人物、否定和读者限定都应保留。本实现只让模型改写一个检索问题，再用原问题组织答案；不会把改写结果当作事实。

```bash
# 只增加改写，暂不叠加重排；报告会同时保存 question 和 query，便于发现改意。
python -m companion evaluate --method hybrid --rewrite --output retrieval-rewrite.json
# 选择最终准备保留的方案后，才对保留题做一次真实生成；此例先用 hybrid，不预设复杂方案获胜。
python -m companion evaluate --cases eval/holdout.json --method hybrid --generate --output holdout-rag.json
```

先逐题检查 query 是否忠于原意，再看命中。改写输入为空、过长或结构失败时，不把它静默替换成一个“看起来能用”的问题。

在保留题报告上按第 8 章标准人工评分，再执行 grade。保留题失败可以成为下一轮开发题，但之后要补新的保留题；不能持续调到它全对后仍称它未见过。

## 阶段三交付

写一页选择记录：现有失败是什么；试了哪些单项变化；改善了哪类题；额外耗时多少；最后保留哪一种配置。程序默认仍为 keyword，后面网页通过 `RETRIEVAL` 选择。若你选 hybrid，必须维护 Qdrant 与索引一致性。

GraphRAG、HyDE、Multi-query 和 Agentic RAG 都可点开选读。本阶段不要求全部实现，先把“为什么选它”解释清楚。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 改写后命中更高就算成功吗？
2. 最后必须使用 hybrid+rewrite+rerank 吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**改写后命中更高就算成功吗？**

还要确认没改变读者原意。答了一个更容易但不同的问题不是改善。

**最后必须使用 hybrid+rewrite+rerank 吗？**

不必须。按固定题、真实耗时和维护成本选最合适的方案；简单方案通过目标也可以保留。

**通过证据：**人工核对的改写报告、一次保留题评阅和明确的最终检索选择。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/resources/advanced-rag.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter8)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
