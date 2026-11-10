# 启动向量库，重启后继续查

本单元预计 **70—85 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《检验向量有没有帮到你的失败题》](0033-embedding-comparison.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 复用前面学过的 Docker

Qdrant 保存向量和元数据，并按相似度查询。collection 可以先理解为一份有固定向量维度的索引集合。仍沿用第 4 章选定的生成模型；第 9 章使用的本地编码器也不换。这次只把内存里的检索数据搬到服务中。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：准备数据库连接与稳定点 ID

连接需要及时关闭，块 ID 转为 Qdrant 接受的 UUID；这些不改变编码器内容。

**写在哪里：**项目根目录下的 `companion/vectors.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import os
import uuid
from contextlib import closing
```

**写完后应当怎样：**同一块可覆盖写入而不会随机生成重复点。

### 第 2 步：让索引读取资料快照

索引和语料需要共同的版本信息；查询后仍从当前语料取正文。

**写在哪里：**项目根目录下的 `companion/vectors.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .files import data_dir
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .files import data_dir, digest, load, save
from .corpus import visible
```

**写完后应当怎样：**旧载荷不会替代当前资料范围规则。

### 第 3 步：写出可关闭的数据库连接

默认连接真实 Qdrant 服务；本地 SDK 模式只供作者的离线行为检查，不冒充容器。

**写在哪里：**项目根目录下的 `companion/vectors.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：默认连接真实 Qdrant 服务；本地 SDK 模式只供作者的离线行为检查，不冒充容器。
# 预期：离开 with 后关闭客户端，避免本地库被锁住。
def connection():
    from qdrant_client import QdrantClient
    # 离线单元测试可明确选择 local；课程第 10 章默认连接真实 Qdrant 服务。
    if os.environ.get("QDRANT_MODE") == "local":
        return closing(QdrantClient(path=str(data_dir() / "qdrant-local")))
    return closing(QdrantClient(url=os.environ.get("QDRANT_URL", "http://127.0.0.1:6333"),
                        api_key=os.environ.get("QDRANT_API_KEY") or None, timeout=30))
```

**写完后应当怎样：**离开 with 后关闭客户端，避免本地库被锁住。

### 第 4 步：把向量与来源一起写入集合

先建立集合、分批写入，确认条数后再发布活动索引指针；中途失败不能切到半成品。

**写在哪里：**项目根目录下的 `companion/vectors.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：先建立集合、分批写入，确认条数后再发布活动索引指针；中途失败不能切到半成品。
# 预期：index.json 的 count 等于语料块数，集合内保留来源字段。
def build_index():
    from qdrant_client import models
    corpus = load("corpus.json")
    if not corpus:
        raise ValueError("先整理 corpus.json。")
    encoder()
    # 加载时已锁定这个提交；缓存与查询必须使用相同版本，升级需要明确改值并重建。
    revision = MODEL_REVISION
    identity = digest([MODEL, revision])[:12]
    vectors = embed([chunk["text"] for chunk in corpus["chunks"]])
    new_count = len(vectors)
    name = f"reading_{corpus['revision'][:12]}_{identity}"
    with connection() as db:
        if not db.collection_exists(name):
            db.create_collection(name, vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE))
        for start in range(0, len(vectors), 32):
            points = [models.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL, c["id"])), vector=v, payload=c)
                      for c, v in zip(corpus["chunks"][start:start + 32], vectors[start:start + 32])]
            db.upsert(name, points=points, wait=True)
        if db.count(name, exact=True).count != len(vectors):
            raise ValueError("索引条数不符，不切换活动版本。")
    # 新集合完整后才发布指针。旧集合保留用于回滚；清理需要显式维护操作。
    index = {"collection": name, "corpus_revision": corpus["revision"], "model": MODEL,
             "model_revision": revision, "dimension": len(vectors[0]), "count": len(vectors), "new_embeddings": new_count}
    save("index.json", index)
    return index
```

**写完后应当怎样：**index.json 的 count 等于语料块数，集合内保留来源字段。

### 第 5 步：查询持久索引并回查当前正文

先核对资料与编码器版本，再检索当前机构和作品；不让旧索引混进新资料。

**写在哪里：**项目根目录下的 `companion/vectors.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：先核对资料与编码器版本，再检索当前机构和作品；不让旧索引混进新资料。
# 预期：返回仍有文件名、段落与块 ID，可与词面结果比较。
def semantic_search(question, tenant, book, progress=None, k=5):
    from qdrant_client import models
    index, corpus = load("index.json"), load("corpus.json")
    if not index or not corpus or index["corpus_revision"] != corpus["revision"]:
        raise ValueError("活动索引与资料版本不一致，请完成索引构建；不返回旧版证据。")
    if index["model"] != MODEL or index["model_revision"] != MODEL_REVISION:
        raise ValueError("Embedding 版本已变，必须重建索引。")
    required = [models.FieldCondition(key="tenant", match=models.MatchValue(value=tenant)),
                models.FieldCondition(key="book", match=models.MatchValue(value=book))]
    with connection() as db:
        points = db.query_points(index["collection"], query=embed([question])[0],
                                 query_filter=models.Filter(must=required), limit=k, with_payload=True).points
    # 不同存储后端对布尔值和数字的比较可能不同；以当前资料的权限规则再次核对。
    # 正文也从当前快照取得，避免旧索引载荷绕过已修订的阅读范围。
    allowed = {c["id"]: c for c in visible(corpus["chunks"], tenant, book, progress)}
    return [{**allowed[p.payload["id"]], "score": p.score} for p in points if p.payload.get("id") in allowed]
```

**写完后应当怎样：**返回仍有文件名、段落与块 ID，可与词面结果比较。

### 第 6 步：给检索入口增加语义路线

同一个 retrieve 根据 method 选择已经实现的方法；生成侧不需要重写。

**写在哪里：**项目根目录下的 `companion/rag.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    if method != "keyword" or expand:
        raise ValueError("当前只实现关键词检索，还没有扩展语境。")
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    if method not in {"keyword", "semantic"}:
        raise ValueError("未知检索方法。")
```

**写完后应当怎样：**--method semantic 读持久索引，keyword 继续保持原基线。

### 第 7 步：给检索入口增加语义路线

同一个 retrieve 根据 method 选择已经实现的方法；生成侧不需要重写。

**写在哪里：**项目根目录下的 `companion/rag.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        raise ValueError("请先整理讲稿。")
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
        raise ValueError("请先运行 ingest 整理资料。")
```

**写完后应当怎样：**--method semantic 读持久索引，keyword 继续保持原基线。

### 第 8 步：给检索入口增加语义路线

同一个 retrieve 根据 method 选择已经实现的方法；生成侧不需要重写。

**写在哪里：**项目根目录下的 `companion/rag.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    return keyword_search(question, allowed)
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
    lexical = keyword_search(question, allowed)
    if method == "keyword":
        hits = lexical
    else:
        from .vectors import semantic_search
        dense = semantic_search(question, tenant, book, progress)
        hits = dense
    return hits
```

**写完后应当怎样：**--method semantic 读持久索引，keyword 继续保持原基线。

### 第 9 步：给建索引单独一个命令

导入资料与构建向量索引不是同一件事；分开命令便于定位哪一步失败。

**写在哪里：**项目根目录下的 `companion/index_cli.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：导入资料与构建向量索引不是同一件事；分开命令便于定位哪一步失败。
# 预期：index 命令明确完成建索引，查询不偷偷重建。
import json
from .vectors import build_index


def main():
    print(json.dumps(build_index(),ensure_ascii=False,indent=2))
```

**写完后应当怎样：**index 命令明确完成建索引，查询不偷偷重建。

### 第 10 步：给命令入口增加 index

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        main('direct-vector')
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        main('direct-vector')
    elif command == "index":
        from .index_cli import main
        main()
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。

## 运行并观察

```bash
# 创建专用持久卷；容器移除后数据仍留在这个卷中。
docker volume create classics-qdrant
# 仅把服务端口开放给本机；首次下载镜像需要网络，已有同名容器时改用 start。
docker run -d --name classics-qdrant -p 127.0.0.1:6333:6333 -v classics-qdrant:/qdrant/storage qdrant/qdrant:v1.15.5
# 连接本机 Qdrant；正常课程不要设置仅供离线测试的 QDRANT_MODE=local。
export QDRANT_URL=http://127.0.0.1:6333
# 编码当前快照并发布活动索引指针；预期 count 与 corpus 中片段数一致。
python -m companion index
# 按语义查询持久索引；返回的仍是可回查的讲稿片段。
python -m companion search "文言文序言" --method semantic
```

若 connection refused，先看容器是否运行及端口映射；若提示模型窗口超限，检查是否仍用第 9 章的 80/16 小块。向量维度由编码器决定，不要手填一个猜测的维度。

## 证明数据确实持久化

```bash
# 停止再启动同一个练习容器；预期原集合仍在，不需要删除卷或重建资料。
docker stop classics-qdrant
docker start classics-qdrant
# 服务启动完成后重查；若暂时连接失败，先检查容器状态再重试。
python -m companion search "文言文序言" --method semantic
```

记录重启前后的集合名、条数和一条来源 ID。这证明的是本次恢复可用，不证明公司级可用性。卷损坏或主机丢失仍需备份，第 28 章专门演练。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 容器和卷分别保存什么？
2. Qdrant 能替你判断讲稿观点正确吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**容器和卷分别保存什么？**

容器运行 Qdrant 进程，命名卷保存持久数据。删容器不等于删卷，但删除卷会丢失其中索引。

**Qdrant 能替你判断讲稿观点正确吗？**

不能。它负责存储和检索，文学事实与解释仍需来源和评测。

**通过证据：**有真实 Qdrant 容器记录和重启后相同来源的查询结果；未在 Docker 跑过就标待运行。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/06-memory-rag.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter8)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
