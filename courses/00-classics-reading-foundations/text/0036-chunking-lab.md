# 同一份讲稿，三种切法

本单元预计 **35—50 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《资料更新后，不让旧索引混进来》](0035-index-versions.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 块不是越短或越长越好

短块容易落进编码窗口，但“他”“这种看法”可能失去指代对象；长块保留语境，却会带入无关内容并增加成本。先用关键词检索比较切分，再讨论向量窗口，避免两个问题混在一起。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：加入按段落和标题的切分入口

固定字符不是唯一单位；段落由 Word 结构提供，标题模式需要真实标题样式。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    if strategy != "fixed":
        raise ValueError("本阶段只实现固定切分。")
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

**写完后应当怎样：**没有标题样式的文档不会凭空得到多个语义标题。

### 第 2 步：加入按段落和标题的切分入口

固定字符不是唯一单位；段落由 Word 结构提供，标题模式需要真实标题样式。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        raise ValueError("需要 size >= 20 且 0 <= overlap < size。")
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
        raise ValueError("需要 size >= 20 且 0 <= overlap < size。")
    if strategy in {"paragraph", "heading"}:
        # 标题模式的分组由外层处理；没有标题的文档不会凭空长出语义结构。
        return [(0, text)]
```

**写完后应当怎样：**没有标题样式的文档不会凭空得到多个语义标题。

### 第 3 步：把标题下的正文并入同一组

只在读取到真正标题样式时换组；不要把看起来像标题的普通文字悄悄当结构。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
            groups.append([f"p{position:04d}", text])
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
            heading = paragraph.style.name.startswith("Heading") if paragraph.style else False
            if strategy == "heading" and groups and not heading:
                groups[-1][1] += "\n" + text
            else:
                groups.append([f"p{position:04d}", text])
```

**写完后应当怎样：**可以用同一份 DOCX 比较 fixed、paragraph、heading，原文件保持不变。

## 运行并观察

```bash
# 按 Word 段落保留整段；部分样本正文很长，预期不是自然变成精细知识单元。
python -m companion ingest --strategy paragraph
python -m companion evaluate --output chunks-paragraph.json
# 按 Word 标题样式分组；没有真实标题样式的文档不会凭空获得章节结构。
python -m companion ingest --strategy heading
python -m companion evaluate --output chunks-heading.json
# 固定小块形成可重复基线，比较关键句是否因边界被切开。
python -m companion ingest --size 80 --overlap 16
python -m companion evaluate --output chunks-fixed.json
```

在编辑器里比较三份报告的片段数、目标短句命中和正文。此处 evaluate 没加 generate，不受生成模型波动影响。段落或标题分组可能超出编码器窗口，不要直接拿它运行 index 后再怪向量库。

## 公开样本的实际对照

以下结果来自本版五份新编样本，使用相同开发题和词面检索；没有调用生成模型。

| 切分大小 / 重叠 | 块数 | 第一题短句命中 | 第二题短句命中 | 第三题短句命中 |
|---|---:|---|---|---|
| 600 / 60 | 15 | 是 | 是 | 是 |
| 80 / 16 | 106 | 是 | 是 | 是 |
| 96 / 16 | 85 | 是 | 是 | 是 |

第四道题没有页码证据，不计算目标短句命中。表中短句命中也不代表答案完整正确。打开检索片段，看一看解释的前因、限定条件是否同时保留下来；文件命中和证据完整是两回事。具体记录见课程的验证页面。

## 小练习

先从结果里找一条证据被切开或限定条件丢失的片段，把 size 改为 96，其他条件不变再测；若短句都命中，就比较上下文是否完整，不要为了实验编造失败。若出现好转，也检查另一道题是否变差。一次优化应说明收益发生在哪类问题上，而不是只汇报平均值。

做完恢复 80/16，并重新 index。旧的 range 人工标注关联片段 ID，换切分后不会自动套用到新块；第 15 章会利用这一点防止误继承。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 为什么“按标题切”可能完全无效？
2. 重叠能彻底解决断句吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么“按标题切”可能完全无效？**

文件未使用可识别的标题样式，或正文只是一大段。算法不能凭空得知文学结构。

**重叠能彻底解决断句吗？**

不能。它增加连续性机会，也增加重复和成本；需要用失败题验证，必要时改变分段方法。

**通过证据：**三份可对照报告和一个块大小改变的结论，明确收益与退步。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/resources/advanced-rag.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter8)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion.corpus import ingest
assert ingest(strategy="paragraph")["chunks"]==5
assert ingest(strategy="heading")["chunks"]==5
assert ingest(size=80,overlap=16)["chunks"]==106
print("三种切分已观察，恢复80/16供后续实验")
PY
```

**预期：**段落、标题两种模式均为5块；固定模式恢复为106块。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
