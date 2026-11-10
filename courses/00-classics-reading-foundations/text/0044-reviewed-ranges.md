# 先核对片段属于哪个阅读范围

本单元预计 **35—50 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《让记忆可以被查看、修正和删除》](0043-explicit-progress.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 讲次不能直接当作剧透边界

第一讲也可能提到结尾。仅按文件名筛选“第一讲”不保证没有后文。先人工核对片段，把“最晚需要读到哪里才能看”标为 range_end；没有核对就保持未知。

从 `corpus.json` 找一条不涉及后文的片段，完整读过，再在编辑器创建 `data/live/ranges.json`。文件是 JSON 对象，键填那条真实片段 ID，值填 `range_end` 和 `reviewed`。不要照抄一个示例 ID，否则标注不会生效。

为了避免手敲 ID，可以运行下面的交互程序。它仍要求你自己阅读并确认，程序不会替你判断剧透。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：把人工核对范围加入片段来源卡

范围来自你对片段的核对；缺少记录时保持未知，不能让模型猜一个看似完整的值。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    documents, chunks, duplicates, seen = [], [], [], {}
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    documents, chunks, duplicates, seen = [], [], [], {}
    annotations = load("ranges.json", {})
```

**写完后应当怎样：**重新导入后，每块都有 range_end 和 range_reviewed；未知不自动通过。

### 第 2 步：把人工核对范围加入片段来源卡

范围来自你对片段的核对；缺少记录时保持未知，不能让模型猜一个看似完整的值。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
                chunk_id = digest([doc_id, version, parent, strategy, size, overlap, start])[:24]
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
                chunk_id = digest([doc_id, version, parent, strategy, size, overlap, start])[:24]
                review = annotations.get(chunk_id, {})
                if review.get("reviewed") is True and (type(review.get("range_end")) is not int or review["range_end"] < 0):
                    raise ValueError("已审核的阅读范围必须是非负整数，不能用 true/false 代替。")
```

**写完后应当怎样：**重新导入后，每块都有 range_end 和 range_reviewed；未知不自动通过。

### 第 3 步：把人工核对范围加入片段来源卡

范围来自你对片段的核对；缺少记录时保持未知，不能让模型猜一个看似完整的值。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
                               "end": start + len(part), "text": part})
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
                               "end": start + len(part), "text": part,
                               "range_end": review.get("range_end"),
                               "range_reviewed": review.get("reviewed") is True})
```

**写完后应当怎样：**重新导入后，每块都有 range_end 和 range_reviewed；未知不自动通过。


## 让刚写的代码生效

如果上一节的服务仍在运行，先在那个终端按 Ctrl+C 停止。确认当前终端仍有模型配置，再从项目根目录重启，随后刷新浏览器。没有使用自动重载时，仅保存文件不会更新运行中的 Python 进程。

```bash
# 载入刚写完的接口、业务模块和页面；等终端显示服务启动后再进行下面的交互。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```


## 运行并观察

```bash
# 列出少量片段供人工核对；只显示测试讲稿，先记下准备标注的真实 ID。
python -c 'from companion.files import load; print([(c["id"],c["text"]) for c in load("corpus.json")["chunks"][:5]])'
# 交互输入已核对 ID 和范围，保存标注；只有输入 YES 才标记为已审核。
python -c 'from companion.files import load,save; rows=load("ranges.json",{}); key=input("已核对的片段 ID：").strip(); end=int(input("最晚阅读范围编号：")); rows[key]={"range_end":end,"reviewed":input("已逐字核对且无范围外内容？输入 YES：")=="YES"}; save("ranges.json",rows)'
# 同样参数重新导入，让片段带上标注；若改变切分方式，旧 ID 不会自动套到新片段。
python -m companion ingest --size 80 --overlap 16
```

本节先把核对记录写进语料，下一单元才把范围条件接入检索与回答。使用 semantic/hybrid 时还要重新 index，因为过滤用的元数据变了。未标注片段保留在普通检索中，但在受限阅读中排除；没有合格片段就明确不足。

## 改一个条件

把刚才片段的 range_end 从 1 改成 2，再导入。下一单元接入过滤后，再验证阅读进度为 1 的人看不到它。不要为了让结果丰富，把全部未知片段批量标为 1；那会让边界失去意义。

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

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion.corpus import ingest
from companion.files import load
annotations = load("ranges.json", {})
ingest(size=80, overlap=16)
chunks = load("corpus.json")["chunks"]
for chunk in chunks:
    review = annotations.get(chunk["id"], {})
    assert chunk["range_reviewed"] == (review.get("reviewed") is True)
    assert chunk["range_end"] == review.get("range_end")
print("标注与片段一致，已核对数：", sum(c["range_reviewed"] for c in chunks))
PY
```

**预期：**已标注片段保留核对结果，未标注片段保持未知。按前文完成至少两条标注后，打印的已核对数应至少为2；没有标注时为0。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
