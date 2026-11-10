# 资料更新后，不让旧索引混进来

本单元预计 **30—45 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《启动向量库，重启后继续查》](0034-qdrant-persistence.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 先看两种版本

`corpus.json` 记录资料快照；`index.json` 记录活动集合、编码器名称、权重提交指纹和资料 revision。查询前会核对二者。资料已变而索引未更新时，失败比悄悄返回旧证据更容易发现。

编码器在 `vectors.py` 中通过 `MODEL_REVISION` 指定[模型仓库的固定提交](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2/tree/e8f8c211226b894fcb81acc59f3b34ba3efd5f42)。加载、缓存和索引都使用这个值，不从依赖库的内部字段猜测版本。要升级权重，先明确修改提交值，再重新运行本章对照；不要只换模型文件而保留旧索引。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：给编码结果加版本化缓存

文本和编码器版本都没变时复用向量；新集合完整后再切换指针，保存旧集合供核对。

**写在哪里：**项目根目录下的 `companion/vectors.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    vectors = embed([chunk["text"] for chunk in corpus["chunks"]])
    new_count = len(vectors)
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    cache = load(f"embedding-cache-{identity}.json", {})
    vectors = []
    new_count = 0
    for chunk in corpus["chunks"]:
        key = digest(chunk["text"])
        if key not in cache:
            cache[key] = embed([chunk["text"]])[0]
            new_count += 1
        vectors.append(cache[key])
    save(f"embedding-cache-{identity}.json", cache)
```

**写完后应当怎样：**重复建索引 new_embeddings=0；改正文后只为新文本重新编码。

## 运行并观察

```bash
# 上一节没有保存编码缓存；第一次运行新逻辑会建立缓存，new_embeddings 通常大于0。
python -m companion index
# 不改资料，再运行一次；这次预期 new_embeddings 为0，才证明缓存被复用。
python -m companion index
# 只改重叠长度，制造新的资料快照；这是可恢复的实验，不动原件。
python -m companion ingest --size 80 --overlap 12
# 此时旧索引版本不匹配，预期被拒绝；拒绝正是本实验要验证的行为。
python -m companion search "文言文序言" --method semantic
# 构建完新集合后才发布指针；然后重查，应使用新快照。
python -m companion index
python -m companion search "文言文序言" --method semantic
```

实验完成后，在同一终端恢复 80/16 并重建对应索引。下一单元要在相同资料起点比较切块，不能把本节的 80/12 实验状态带过去：

```bash
# 恢复第9章的小块基线；资料revision会回到这组参数对应的版本。
python -m companion ingest --size 80 --overlap 16
# 让活动索引与恢复后的资料一致，避免下一节查询因版本不符而失败。
python -m companion index
```

缓存键包含实际模型提交版本及文本指纹，不能跨不同权重盲目复用。未变化的文本复用向量，新文本才编码；这里是“增量计算、整份快照发布”，不是逐条在线增删的完整服务。

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


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
