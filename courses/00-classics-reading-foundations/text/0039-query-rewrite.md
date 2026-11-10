# 检验改写有没有改变原问题

本单元预计 **50—65 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《先混合检索，再单独试重排》](0038-hybrid-rerank.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 好改写必须保留问题的边界

“为什么不赞同”不能被改成“为什么赞同”。作品、人物、否定和读者限定都应保留。本实现只让模型改写一个检索问题，再用原问题组织答案；不会把改写结果当作事实。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：把改写限制为一次检索问题

保留作品、人名、讲次和否定；改写不应直接作答或添事实。

**写在哪里：**项目根目录下的 `companion/rag.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：保留作品、人名、讲次和否定；改写不应直接作答或添事实。
# 预期：空结果和过长结果被拒绝，仍需人工判断含义有没有改变。
def rewrite(question):
    response = complete([{"role": "system", "content": "只把问题改写为一个更清楚的检索问题，保留作品、人物、讲次和否定。不要回答，不增加事实。"},
                         {"role": "user", "content": question}])
    result = (response["message"].get("content") or "").strip()
    if not result or len(result) > 500:
        raise ValueError("改写为空或过长。")
    return result
```

**写完后应当怎样：**空结果和过长结果被拒绝，仍需人工判断含义有没有改变。

### 第 2 步：引入已写好的改写函数

原问题保留用于最后回答，改写只影响找资料。

**写在哪里：**项目根目录下的 `companion/query.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .rag import retrieve, answer, rerank
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .rag import retrieve, answer, rerank, rewrite
```

**写完后应当怎样：**不会把模型的改写悄悄替换成用户原话。

### 第 3 步：增加改写开关

保持可撤销对照，不把一次看似改善自动设成默认。

**写在哪里：**项目根目录下的 `companion/query.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    parser.add_argument("--rerank",action="store_true")
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    parser.add_argument("--rerank",action="store_true")
    parser.add_argument("--rewrite",action="store_true")
```

**写完后应当怎样：**同一个问题可以开关对照。

### 第 4 步：先保存这次真正用于检索的问法

排查答偏时需要知道原问题和实际检索问题分别是什么。

**写在哪里：**项目根目录下的 `companion/query.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    args = parser.parse_args()
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    args = parser.parse_args()
    query=rewrite(args.question) if args.rewrite else args.question
```

**写完后应当怎样：**query 单独保留，不覆盖 args.question。

### 第 5 步：让向量路线也使用检索问法

变量名区分文本和向量，避免下游把数组当问题字符串。

**写在哪里：**项目根目录下的 `companion/query.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        query=embed([args.question])[0]
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
        query_vector=embed([query])[0]
```

**写完后应当怎样：**编码的是改写后的文本，答案仍针对原问题。

### 第 6 步：更新相似度的输入

点积需要两个数值向量，不能与文本逐字相乘。

**写在哪里：**项目根目录下的 `companion/query.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        hits=sorted([{**c,"score":sum(a*b for a,b in zip(v,query))}
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
        hits=sorted([{**c,"score":sum(a*b for a,b in zip(v,query_vector))}
```

**写完后应当怎样：**相似度计算仍使用相同维度。

### 第 7 步：把实际检索问法传下去

只有调用处换了输入，改写实验才真的生效。

**写在哪里：**项目根目录下的 `companion/query.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        hits = retrieve(args.question,args.tenant,args.book,args.method,expand=args.expand)
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
        hits = retrieve(query,args.tenant,args.book,args.method,expand=args.expand)
```

**写完后应当怎样：**检索来源随 query 变化，最后生成仍用原 question。

### 第 8 步：同时留下两种问法

保留比较依据，后续评测可以发现改写中的语义漂移。

**写在哪里：**项目根目录下的 `companion/query.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    result = answer(args.question,hits) if kind == "ask" else {"question":args.question,"hits":hits}
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    result = answer(args.question,hits) if kind == "ask" else {"question":args.question,"query":query,"hits":hits}
```

**写完后应当怎样：**search.json 中两种问法都可见。

### 第 9 步：让批量评测复用已实现的改写与重排

同一题单、同一资料，分别记录各开关，才知道变化来自哪里。

**写在哪里：**项目根目录下的 `companion/evaluation.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .rag import retrieve, answer
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .rag import retrieve, answer, rewrite, rerank
```

**写完后应当怎样：**评测不复制另一套检索算法。

### 第 10 步：把改写和重排加入逐题对照

保留原问题、实际 query、来源、错误与人工评分，不只给平均分。

**写在哪里：**项目根目录下的 `companion/evaluation.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        query = case["question"]
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
        query = rewrite(case["question"]) if rewriting else case["question"]
```

**写完后应当怎样：**每个实验仍可以独立保存成不同文件。

### 第 11 步：把改写和重排加入逐题对照

保留原问题、实际 query、来源、错误与人工评分，不只给平均分。

**写在哪里：**项目根目录下的 `companion/evaluation.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        hits = retrieve(query, case.get("tenant", "demo"), case.get("book", "狂人日记"), method, expand=expand)
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
        hits = retrieve(query, case.get("tenant", "demo"), case.get("book", "狂人日记"), method, expand=expand)
        if reranking:
            hits = rerank(case["question"], hits)
```

**写完后应当怎样：**每个实验仍可以独立保存成不同文件。

### 第 12 步：在评测入口暴露三个独立条件

命令与实际算法选项一致，防止讲义要求的参数实际上未传入。

**写在哪里：**项目根目录下的 `companion/evaluate_cli.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    parser.add_argument("--output",default="evaluation.json")
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    parser.add_argument("--output",default="evaluation.json")
    parser.add_argument("--expand",action="store_true")
    parser.add_argument("--rerank",action="store_true")
    parser.add_argument("--rewrite",action="store_true")
```

**写完后应当怎样：**可以一次只打开一个条件。

### 第 13 步：把条件完整传给评测函数

参数顺序与函数定义对应；理解位置参数后，也可以改成具名参数提高可读性。

**写在哪里：**项目根目录下的 `companion/evaluate_cli.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    print(json.dumps(evaluate(args.cases,args.method,args.generate,output=args.output),ensure_ascii=False,indent=2))
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    print(json.dumps(evaluate(args.cases,args.method,args.generate,args.expand,args.rerank,args.rewrite,args.output),ensure_ascii=False,indent=2))
```

**写完后应当怎样：**报告的 options 与本次命令一致。

## 运行并观察

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


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
