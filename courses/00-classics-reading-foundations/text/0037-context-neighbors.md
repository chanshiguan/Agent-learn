# 检索小块，再补它旁边的语境

本单元预计 **40—55 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《同一份讲稿，三种切法》](0036-chunking-lab.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 找得准，却读不懂怎么办

小块适合检索，回答可能需要它前后的一两句。`neighbors()` 在同一文档、同一父段落里补左右相邻块。它只能从已经允许的范围中取内容，不能为了补上下文跨作品或跨阅读进度。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：按文档和父段落补相邻块

检索小块容易缺少前因；只补同一父段落附近内容，避免把不相关文档拼在一起。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：检索小块容易缺少前因；只补同一父段落附近内容，避免把不相关文档拼在一起。
# 预期：每个块只出现一次，范围过滤在扩展前已经完成。
def neighbors(hits, chunks):
    selected = {c["id"]: c for c in hits}
    for hit in hits:
        siblings = sorted((c for c in chunks if c["doc_id"] == hit["doc_id"] and c["parent"] == hit["parent"]), key=lambda c: c["start"])
        position = next((i for i, c in enumerate(siblings) if c["id"] == hit["id"]), -1)
        if position >= 0:
            for item in siblings[max(0, position - 1):position + 2]:
                selected[item["id"]] = item
    return list(selected.values())
```

**写完后应当怎样：**每个块只出现一次，范围过滤在扩展前已经完成。

### 第 2 步：让检索可以选择是否补语境

扩展结果仍交给已有字符预算，增加来源不代表无限塞入模型。

**写在哪里：**项目根目录下的 `companion/rag.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .corpus import visible, keyword_search
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .corpus import visible, keyword_search, neighbors
```

**写完后应当怎样：**不开扩展时原基线不变。

### 第 3 步：在返回前按开关补相邻块

保留一个开关，才能用同题对比扩展带来的收益与噪音。

**写在哪里：**项目根目录下的 `companion/rag.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    return hits
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    return neighbors(hits, allowed) if expand else hits
```

**写完后应当怎样：**expand=True 时补充相邻证据，仍受可见范围限制。

### 第 4 步：把语境扩展变成实验开关

对照实验一次只换一个条件，不直接改掉旧基线。

**写在哪里：**项目根目录下的 `companion/query.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    parser.add_argument("--method", default="keyword")
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    parser.add_argument("--method", default="keyword")
    parser.add_argument("--expand",action="store_true")
```

**写完后应当怎样：**命令可以带 --expand，其余条件保持一致。

### 第 5 步：把开关传给检索函数

参数只有传到实际执行位置才生效。

**写在哪里：**项目根目录下的 `companion/query.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        hits = retrieve(args.question,args.tenant,args.book,args.method)
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
        hits = retrieve(args.question,args.tenant,args.book,args.method,expand=args.expand)
```

**写完后应当怎样：**同一问题的扩展结果可与未扩展文件比较。

## 运行并观察

```bash
# 在已恢复的 80/16 快照上比较相邻扩展；方法固定为 keyword，先观察输入变化。
python -m companion evaluate --output context-before.json
python -m companion evaluate --expand --output context-after.json
# 再用真实模型回答一题，核对代词是否有了着落；这个命令会产生模型请求。
python -m companion ask "讲稿怎样解释文言文序言和白话日记？" --expand
```

对比总字符数、来源数和关键句。上下文预算仍为 2400 字符，扩展太多会使后面的整块放不进去。多拿资料不必然更好；重复片段也会浪费预算。

## 亲手检查取舍

找一条带“这”“他”的候选，单看小块解释一次，再看相邻块解释一次。写出新增内容究竟补了人物、论证前提还是时间关系。若没补到，就如实记录，不用硬说有提升。

父子块检索会把小块映射到更大的父块；本实现只补相邻片段。两者相关但不是同一个实现。Contextual Retrieval 等方法见选读，不要求现在生成全库的背景摘要。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 相邻扩展为什么仍要检查权限？
2. 本实现是完整父子块检索吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**相邻扩展为什么仍要检查权限？**

相关上下文也可能在读者允许范围之外。不能以“帮助理解”为由突破资料或进度边界。

**本实现是完整父子块检索吗？**

不是。它补同父段内相邻块；可以作为理解“检索粒度与阅读粒度不同”的第一步。

**通过证据：**一条前后语境对照、预算变化和效果结论；能指出本方法没有解决的问题。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/resources/advanced-rag.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter8)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
