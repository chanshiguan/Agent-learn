# 上下文增强：切块后别丢掉来龙去脉

这五份公开讲稿各是一长段。以后切成小块时，有些块可能从“他”“这种想法”开始。单独看时对象不清楚，检索和回答都可能受影响。切得更小，并不自动意味着更准确。

## 两种不同思路

| 方法 | 主要做法 | 成本与限制 |
|---|---|---|
| 父子块检索 | 用小块定位，命中后带回所属的大段或相邻上下文 | 生成请求会变长；父块太大仍可能混入无关内容 |
| Contextual Retrieval | 索引前给片段补充简短的背景说明，再用于检索表示 | 增加预处理；模型生成的说明需要核对 |

父子块的例子可看 [LlamaIndex 的递归检索说明](https://developers.llamaindex.ai/python/framework/integrations/retrievers/recursive_retriever_nodes/)中“Smaller Child Chunks Referring to Bigger Parent Chunk”一节：用小块命中，再沿引用取回更大的块，为回答提供上下文。

Anthropic 提出的 Contextual Retrieval 把针对片段的说明加到片段前，再构建 Embedding 和 BM25 索引。它与“检索后多带几段原文”发生在不同位置。[Anthropic 工程文章](https://www.anthropic.com/research/contextual-retrieval)

## 本项目先做哪一步

本课程建议先保留文件名、讲次、段落位置这些可确定的信息，再试不同切法。若仍出现“找到了句子但看不懂主语”的问题，再比较父子块或上下文说明。这是针对现有资料形态的教学判断。

背景说明应该与原文分开保存。比如“本片段来自第四讲”来自来源元数据；“本片段证明某种唯一解释”则是需要核查的判断。不要把后者混进原文后，继续当作逐字引用。

## 推荐选读

[Anthropic：Introducing Contextual Retrieval](https://www.anthropic.com/research/contextual-retrieval)（2024-09-19，英文，约 12 分钟）。先看切块丢失上下文的例子和预处理流程。文章里的实验提升只对应其测试条件，不是这五份讲稿的保证，也不意味着必须购买同一家模型。

思考题：如果能用可靠的讲次和标题补齐对象，是否需要每个块都再调用模型？参考思路是先测确定性元数据方案，确有不足再增加生成步骤。
