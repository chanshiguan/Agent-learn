# 先让程序找到相关文字

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《用副本练习去重与更新》](0027-corpus-dedup.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 先不让模型回答

现在有结构化片段，但第 5 章仍由人选资料。RAG 的 R 是 Retrieval，即检索。今天只把“人挑片段”换成“程序按问题找片段”，便于看清失败在哪一步。

`terms()` 把中文拆成相邻双字片段，把英文字母和数字按词处理。`keyword_search()` 按问题与正文共有的词面片段比例排序，最多取五条。它是简单、可解释的词面基线，不是 BM25，也不是语义理解。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：先选对作品，再比较文字

先限制机构和作品，避免排完名才发现搜索了别人的资料。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：先限制机构和作品，避免排完名才发现搜索了别人的资料。
# 预期：不同作品的块在评分前就被排除。
def visible(chunks, tenant, book, progress=None):
    return [c for c in chunks if c["tenant"] == tenant and c["book"] == book]
```

**写完后应当怎样：**不同作品的块在评分前就被排除。

### 第 2 步：写 terms()，让问题找到片段

用中文相邻双字片段和英文数字词建立可解释基线，不把它叫作完整分词器。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：用中文相邻双字片段和英文数字词建立可解释基线，不把它叫作完整分词器。
# 预期：命中只表示词面相关；没有资料的事实不会因此出现。
def terms(text):
    # 中文双字片段是可解释的入门词面基线，不冒称完整分词器或 BM25。
    lower = text.lower()
    words = set(re.findall(r"[a-z0-9]+", lower))
    for run in re.findall(r"[\u4e00-\u9fff]+", lower):
        words.update(run[i:i + 2] for i in range(len(run) - 1))
    return words
```

**写完后应当怎样：**命中只表示词面相关；没有资料的事实不会因此出现。

### 第 3 步：写 keyword_search()，让问题找到片段

计算问题与每块文字的词面交集，按分数排序并保留前五条。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：计算问题与每块文字的词面交集，按分数排序并保留前五条。
# 预期：命中只表示词面相关；没有资料的事实不会因此出现。
def keyword_search(question, chunks, k=5):
    query = terms(question)
    ranked = []
    for chunk in chunks:
        matches = query & terms(chunk["text"])
        if matches:
            ranked.append({**chunk, "score": len(matches) / max(1, len(query))})
    return sorted(ranked, key=lambda c: (-c["score"], c["id"]))[:k]
```

**写完后应当怎样：**命中只表示词面相关；没有资料的事实不会因此出现。

### 第 4 步：把检索与已有回答函数放在同一条调用链

整理模块提供片段，检索负责找片段，回答仍只消费候选列表。

**写在哪里：**项目根目录下的 `companion/rag.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
import json
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
import json
from .corpus import visible, keyword_search
from .files import load
```

**写完后应当怎样：**导入只依赖已经完成的 corpus、files 和 models。

### 第 5 步：写出第一版检索入口

本节只允许关键词方法，显式拒绝尚未实现的其他方法，避免看似生效其实没有执行。

**写在哪里：**项目根目录下的 `companion/rag.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：本节只允许关键词方法，显式拒绝尚未实现的其他方法，避免看似生效其实没有执行。
# 预期：传入问题后返回来源片段列表，不调用生成模型。
def retrieve(question, tenant="demo", book="狂人日记", method="keyword", progress=None, expand=False):
    if method != "keyword" or expand:
        raise ValueError("当前只实现关键词检索，还没有扩展语境。")
    corpus = load("corpus.json")
    if not corpus:
        raise ValueError("请先整理讲稿。")
    allowed = visible(corpus["chunks"], tenant, book, progress)
    return keyword_search(question, allowed)
```

**写完后应当怎样：**传入问题后返回来源片段列表，不调用生成模型。

### 第 6 步：给检索加一个可重复的命令

把同一个问题及命中结果保存起来，下一章可以对照修改前后的检索表现。

**写在哪里：**项目根目录下的 `companion/query.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

```python
# 目的：把同一个问题及命中结果保存起来，下一章可以对照修改前后的检索表现。
# 预期：search.json 只有问题和片段，不会冒充模型答案。
import argparse
import json
from .files import save
from .rag import retrieve


def main(kind="search"):
    parser = argparse.ArgumentParser(description="从讲稿中找资料")
    parser.add_argument("question")
    parser.add_argument("--method", default="keyword")
    parser.add_argument("--tenant", default="demo")
    parser.add_argument("--book", default="狂人日记")
    args = parser.parse_args()
    hits = retrieve(args.question,args.tenant,args.book,args.method)
    result = {"question":args.question,"hits":hits}
    save(kind + ".json",result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
```

**写完后应当怎样：**search.json 只有问题和片段，不会冒充模型答案。

### 第 7 步：给命令入口增加 search

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        from .ingest_cli import main
        main()
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        from .ingest_cli import main
        main()
    elif command == "search":
        from .query import main
        main('search')
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。

## 运行并观察

```bash
# 关键词接近讲稿原词时，观察第一讲相关片段是否靠前；不消耗生成模型 token。
python -m companion search "文言文序言和白话日记"
# 保存原词查询结果；下一次 search 会覆盖工作文件 search.json。
cp data/live/search.json data/live/keyword-literal.json
# 换成同义问法，检查结果是否变差；后面用它判断向量检索有没有帮助。
python -m companion search "开头古雅的文字和后面的记录有什么关系"
# 留下同义问法的候选，后面加向量检索时要用同一道问题比较。
cp data/live/search.json data/live/keyword-paraphrase.json
# 刻意选择当前没有导入的作品；预期 hits 为空，而不是串入另一部书。
python -m companion search "文言文序言" --book "三国演义"
# 留下作品过滤结果，与前两次实验分开核对。
cp data/live/search.json data/live/keyword-wrong-book.json
```

上面三次调用分别留下了原词、同义问法和错误作品的记录。打开它们，先核对 `question`，再看 `hits` 中的文件名和文字。第 9 章比较向量检索时会重用同义问法；不要因为这次没找到理想结果就换题。

## 先过滤，还是先排序

程序先按租户与作品限定可见片段，再排序。若先在所有资料里取前五名，最后才删掉其他作品，可能既泄露候选内容，又把真正相关的本作品片段挤掉。

## 小练习

从第三讲手选一个问题：徐锡麟的例子在讲稿里用来说明什么？先写下你预期命中的文件，再运行 search。只检查检索，不评价生成语言。若找不到，检查原词、切块边界和标签，暂时不要换模型。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 分数 0.8 能理解为答案有 80% 正确吗？
2. 为什么先测 search 再测 ask？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**分数 0.8 能理解为答案有 80% 正确吗？**

不能。它是本算法的词面覆盖比例，只用于排序，没有被校准成可信概率。

**为什么先测 search 再测 ask？**

先确认证据能被找到，才能判断下一步生成是否正确；否则两个故障混在一起。

**通过证据：**保留原词、同义问法和错误作品三种检索结果，能指出一次词面检索的局限。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/06-memory-rag.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter8)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion.rag import retrieve
hits=retrieve("文言文序言和白话日记")
assert hits and any(h["file"].startswith("06 ") for h in hits)
assert retrieve("序言",book="没有导入的作品")==[]
print("找到了第一讲，错误作品没有命中")
PY
```

**预期：**正确作品可查，错误作品不混用资料。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
