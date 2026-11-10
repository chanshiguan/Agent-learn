# 先混合检索，再单独试重排

本单元预计 **40—55 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 为什么不直接把分数相加

词面分数与向量分数来源不同、尺度不同。本课用 RRF：根据每条结果在两个列表里的名次累加 `1/(60+名次)`。它让在两边都靠前的片段更有机会入选，不需要假定两种分数可直接比较。

先确认 Qdrant 正常、资料为 80/16 且索引版本一致。

```bash
# 固定题集与资料，分别保存词面、语义和融合结果；这三步不调用生成模型。
python -m companion evaluate --method keyword --output retrieval-keyword.json
python -m companion evaluate --method semantic --output retrieval-semantic.json
python -m companion evaluate --method hybrid --output retrieval-hybrid.json
# 再单独增加重排；本实现让真实生成模型排序候选，因此有额外耗时和调用费用。
python -m companion evaluate --method hybrid --rerank --output retrieval-rerank.json
```

重排器只能重新排序已有候选，不能找回根本没检索到的关键段落。本课程是 LLM 重排，不冒称 Cross-Encoder；两种做法的成本和模型要求不同，选读页有比较。

## 判断是否值得留下

选精确人名和同义问法各一题，检查排名、关键句、总耗时。若融合没改善，不需要为了“技术完整”强行启用。重排返回新增 ID、漏掉 ID 或重复 ID 时程序拒绝，避免模型用排序任务偷偷引入新证据。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. RRF 混合的是语义吗？
2. 重排能救回没有进候选的证据吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**RRF 混合的是语义吗？**

直接混合的是候选名次。语义信息来自向量检索，精确词面来自关键词检索。

**重排能救回没有进候选的证据吗？**

不能。应先改善召回或扩大合理候选，再评估重排是否有帮助。

**通过证据：**四份报告，至少一条保留或放弃某项优化的逐题理由；明确重排增加了真实模型调用。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/resources/advanced-rag.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter8)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
