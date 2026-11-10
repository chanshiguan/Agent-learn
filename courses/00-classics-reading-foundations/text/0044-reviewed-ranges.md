# 先核对片段属于哪个阅读范围

本单元预计 **35—50 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 讲次不能直接当作剧透边界

第一讲也可能提到结尾。仅按文件名筛选“第一讲”不保证没有后文。先人工核对片段，把“最晚需要读到哪里才能看”标为 range_end；没有核对就保持未知。

从 `corpus.json` 找一条不涉及后文的片段，完整读过，再在编辑器创建 `data/live/ranges.json`。文件是 JSON 对象，键填那条真实片段 ID，值填 `range_end` 和 `reviewed`。不要照抄一个示例 ID，否则标注不会生效。

为了避免手敲 ID，可以运行下面的交互程序。它仍要求你自己阅读并确认，程序不会替你判断剧透。

```bash
# 列出少量片段供人工核对；只显示测试讲稿，先记下准备标注的真实 ID。
python -c 'from companion.files import load; print([(c["id"],c["text"]) for c in load("corpus.json")["chunks"][:5]])'
# 交互输入已核对 ID 和范围，保存标注；只有输入 YES 才标记为已审核。
python -c 'from companion.files import load,save; rows=load("ranges.json",{}); key=input("已核对的片段 ID：").strip(); end=int(input("最晚阅读范围编号：")); rows[key]={"range_end":end,"reviewed":input("已逐字核对且无范围外内容？输入 YES：")=="YES"}; save("ranges.json",rows)'
# 同样参数重新导入，让片段带上标注；若改变切分方式，旧 ID 不会自动套到新片段。
python -m companion ingest --size 80 --overlap 16
```

使用 semantic/hybrid 时还要重新 index，因为过滤用的元数据变了。未标注片段保留在普通检索中，但在受限阅读中排除；没有合格片段就明确不足。

## 改一个条件

把刚才片段的 range_end 从 1 改成 2，再导入。阅读进度为 1 的人不应看到它。不要为了让结果丰富，把全部未知片段批量标为 1；那会让边界失去意义。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 为什么未知范围默认不展示？
2. 换切块后标注为什么可能失效？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么未知范围默认不展示？**

无法证明它不包含后文。保守模式宁可暂时少回答，也不能把未知当作已核对。

**换切块后标注为什么可能失效？**

片段内容与 ID 已变，原审核结论不一定适用；需要重新核对新片段。

**通过证据：**至少两条逐字核对的片段标注，写明范围含义和审核理由，并保留未知片段。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter9)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
