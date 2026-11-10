# 把讲稿和问题变成可比较的向量

本单元预计 **50—65 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《给模型回答打分，也保留不通过》](0031-answer-rubric.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 词面找不到时，试着按意思找

第 7 章的同义问法可能漏检。Embedding 模型把文字编码成一组数字，让相近表达有机会靠近。它不是负责写答案的生成模型：无论你选择本地还是线上生成，本章都先用同一个本地 CPU 编码器做比较。

本课使用多语言 MiniLM，沿用指定仓库中小规模向量练习的思路。它的窗口较短，因此先把块减小到 80 个字符、重叠 16 字符。字符数并不保证 token 数，程序会检查实际 tokenizer 长度，超限直接报错，不静默丢掉后半段。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：记录真实编码器和向量客户端的依赖

先写清单再安装，权重首次下载另外耗时；库安装成功不代表权重已可用。

**写在哪里：**项目根目录下的 `requirements-rag.txt`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**sentence-transformers 负责将文本编码成向量，qdrant-client 负责读写向量存储。pip 安装库与首次加载时下载模型权重是两个步骤；安装结束不代表权重已经可用。

```text
# 第 9—10 章新增：真实多语言 Embedding 与 Qdrant 客户端。
sentence-transformers==6.2.0
qdrant-client==1.15.1
```

**写完后应当怎样：**可以导入客户端；首次编码仍需要取得真实模型权重。

```bash
# 按刚亲手保存的清单安装本节所需依赖；只安装库，不会自动运行项目。
python -m pip install -r requirements-rag.txt
```

### 第 2 步：先写这个文件需要的导入

固定编码器提交，避免同名模型后来变化时无法重现；生成模型与编码器职责不同。

**写在哪里：**项目根目录下的 `companion/vectors.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：固定编码器提交，避免同名模型后来变化时无法重现；生成模型与编码器职责不同。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
from functools import lru_cache
from .files import data_dir

MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODEL_REVISION = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 3 步：写 encoder() 并理解输入输出

一次进程只加载一次真实 CPU 编码器，不用字符计数伪造向量。

**写在哪里：**项目根目录下的 `companion/vectors.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：一次进程只加载一次真实 CPU 编码器，不用字符计数伪造向量。
# 预期：文本列表变成等长浮点向量列表，保留输入顺序。
@lru_cache(maxsize=1)
def encoder():
    from sentence_transformers import SentenceTransformer
    # CPU 是两种生成模型路线共同的起点；首次会下载权重，不能当作离线已准备好。
    # 显式指定公开仓库提交，不依赖库的私有配置字段，也不跟随会移动的 main。
    return SentenceTransformer(MODEL, revision=MODEL_REVISION, device="cpu", cache_folder=str(data_dir() / "models"))
```

**写完后应当怎样：**文本列表变成等长浮点向量列表，保留输入顺序。

### 第 4 步：写 embed() 并理解输入输出

先查 token 长度，超窗就停止；归一化后的向量可以用点积比较。

**写在哪里：**项目根目录下的 `companion/vectors.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：先查 token 长度，超窗就停止；归一化后的向量可以用点积比较。
# 预期：文本列表变成等长浮点向量列表，保留输入顺序。
def embed(texts):
    model = encoder()
    lengths = [len(model.tokenizer.encode(t, add_special_tokens=True)) for t in texts]
    if any(length > model.max_seq_length for length in lengths):
        raise ValueError(f"片段超过 Embedding 的 {model.max_seq_length} token 窗口，请减小切块；不静默截断。")
    return model.encode(texts, batch_size=8, normalize_embeddings=True).tolist()
```

**写完后应当怎样：**文本列表变成等长浮点向量列表，保留输入顺序。

### 第 5 步：让直接向量实验读取同一快照

比较方法时保持资料范围相同；只在选择 direct-vector 时加载编码器。

**写在哪里：**项目根目录下的 `companion/query.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .rag import retrieve, answer
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .rag import retrieve, answer
from .files import load
from .corpus import visible
```

**写完后应当怎样：**普通词面检索不会提前加载模型权重。

### 第 6 步：直接比较向量，暂不保存索引

让你看见编码、相似度和排序的完整过程，下一章才引入持久化。

**写在哪里：**项目根目录下的 `companion/query.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    hits = retrieve(args.question,args.tenant,args.book,args.method)
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
    if kind == "direct-vector":
        from .vectors import embed
        chunks=visible(load("corpus.json")["chunks"],args.tenant,args.book)
        vectors=embed([c["text"] for c in chunks])
        query=embed([args.question])[0]
        hits=sorted([{**c,"score":sum(a*b for a,b in zip(v,query))}
                     for c,v in zip(chunks,vectors)],key=lambda c:-c["score"])[:5]
    else:
        hits = retrieve(args.question,args.tenant,args.book,args.method)
```

**写完后应当怎样：**每次都重新编码全部块；慢在哪里可以观察。

### 第 7 步：给命令入口增加 direct-vector

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        from .grade_cli import main
        main()
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        from .grade_cli import main
        main()
    elif command == "direct-vector":
        from .query import main
        main('direct-vector')
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。

## 运行并观察

```bash
# 安装真实文本编码与 Qdrant 客户端；预期装进已激活的虚拟环境，首次下载可能较慢。
python -m pip install -r requirements-rag.txt
# 将当前五份讲稿切成适合入门编码器的小块；片段 ID 和资料 revision 会随参数变化。
python -m companion ingest --size 80 --overlap 16
# 第一次会下载 Embedding 权重；真实编码后，在内存里计算相似度，不需要 Qdrant 服务。
python -m companion direct-vector "开头古雅的文字和后面的记录有什么关系"
```

打开 `data/live/direct-vector.json`，回查前五条。下载等待不算模型推理时间；下载失败先处理网络与缓存，不要拿固定随机数伪装 Embedding。M1 16 GB 也从 CPU 小批量开始，本课不承诺特定速度。

## 看懂计算，但别迷信分数

编码器把向量归一化，内存检索用点积排序，此时与余弦相似度排序一致。分数衡量这套编码器里的接近程度，不表示结论为真的概率。编码器、文本语言、任务与块大小都会影响结果。

若问题太长也可能超限。先用简短、保留人物和否定关系的问题做实验，不要让程序偷偷删除关键限定词。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. Embedding 和生成模型能互换吗？
2. 为何从 600 字改成 80 字？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**Embedding 和生成模型能互换吗？**

职责不同。前者提供可比较的表示，后者根据问题与证据组织文字；生成路线切换不需要同时替换编码器。

**为何从 600 字改成 80 字？**

当前编码器窗口有限。小块降低超限机会，但可能丢上下文；第 11 章会比较这种代价。

**通过证据：**保存真实编码结果、编码器名称和首次/再次运行耗时；能说明本章尚未使用持久向量数据库。

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
from companion.corpus import ingest
r=ingest(size=80,overlap=16)
assert r["chunks"]==106
print("已准备106个小块；真实编码按本页命令执行")
PY
```

**预期：**切块适配编码器窗口；此检查本身没有执行 Embedding。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
