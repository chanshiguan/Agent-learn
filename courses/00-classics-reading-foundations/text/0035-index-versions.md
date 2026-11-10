# 资料更新后，不让旧索引混进来

本单元预计 **35—50 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 先看两种版本

`corpus.json` 记录资料快照；`index.json` 记录活动集合、编码器名称、权重提交指纹和资料 revision。查询前会核对二者。资料已变而索引未更新时，失败比悄悄返回旧证据更容易发现。

编码器在 `vectors.py` 中通过 `MODEL_REVISION` 指定[模型仓库的固定提交](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2/tree/e8f8c211226b894fcb81acc59f3b34ba3efd5f42)。加载、缓存和索引都使用这个值，不从依赖库的内部字段猜测版本。要升级权重，先明确修改提交值，再重新运行本章对照；不要只换模型文件而保留旧索引。

```bash
# 相同资料再次建索引；预期 new_embeddings 为 0，复用同一模型版本的文本向量缓存。
python -m companion index
# 只改重叠长度，制造新的资料快照；这是可恢复的实验，不动原件。
python -m companion ingest --size 80 --overlap 12
# 此时旧索引版本不匹配，预期被拒绝；拒绝正是本实验要验证的行为。
python -m companion search "文言文序言" --method semantic
# 构建完新集合后才发布指针；然后重查，应使用新快照。
python -m companion index
python -m companion search "文言文序言" --method semantic
```

实验后用 80/16 重新 ingest 和 index，恢复比较基线。缓存键包含实际模型提交版本及文本指纹，不能跨不同权重盲目复用。未变化的文本复用向量，新文本才编码；这里是“增量计算、整份快照发布”，不是逐条在线增删的完整服务。

## 更新和删除怎样落到索引

在第 6 章的实验目录撤下一份文件后导入，新集合只含新快照；活动指针切过去后，新查询不再用旧文件。旧集合暂留用于回滚，并未物理删除。正式删除必须把保留集合、缓存与备份也列入留存流程。

本实现用 `index.json` 作为单实例活动指针，不是 Qdrant alias。构建期间资料与指针不一致会暂时拒绝查询；第 28 章用维护窗口发布，避免把它说成无中断切换。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. new_embeddings=0 说明没工作吗？
2. 索引更新后旧数据是否已经永久删除？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**new_embeddings=0 说明没工作吗？**

不是。程序复用了已知文本的同版本向量，并检查集合条数；它不意味着本轮没有存储操作。

**索引更新后旧数据是否已经永久删除？**

没有。旧集合和缓存还可能存在；撤下在线使用与永久清除是两件需要分别验收的事。

**通过证据：**版本不匹配的预期失败、更新后的成功查询与缓存复用记录；恢复 80/16 基线。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/06-memory-rag.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter8)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
