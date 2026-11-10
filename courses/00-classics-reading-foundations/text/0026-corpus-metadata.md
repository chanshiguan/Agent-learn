# 给每个片段一张来源卡

本单元预计 **65—80 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《让回答说清依据和不知道的部分》](0025-evidence-boundary.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 为什么先整理，再加检索

如果程序只存文字，找到答案后仍不知道来自哪份文件。本章把第一章的单份读取扩展为小批量资料，不扩大到整个知识库。当前五份《狂人日记》样本足以把流程练清楚。

## 看懂来源卡上的字段

`tenant` 是资料所属空间，先用 `demo`；`book` 是作品；`file` 是讲稿文件名；`kind` 明确写“讲解稿”。`lecture` 来自文件名中的“第几讲”，不是原著章回。`edition` 留空，表示尚未核实原著版本。

`doc_id` 标识某个空间里的一份文件；`version` 是文件字节的 SHA-256 指纹；片段 `id` 还包含切分参数和位置。改了文件或切分方式，引用编号可能变化，因此旧答案要保留它当时的资料版本。

## 运行整理程序


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：让相同资料得到稳定指纹

资料版本变化后需要识别；这里增加哈希，不让文件修改悄悄混进旧结果。

**写在哪里：**项目根目录下的 `companion/files.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import hashlib
```

**写完后应当怎样：**同一内容重复计算得到相同值。

### 第 2 步：写一个通用的指纹函数

字典按键排序后再编码，避免仅因字段排列不同得到不同指纹。

**写在哪里：**项目根目录下的 `companion/files.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：字典按键排序后再编码，避免仅因字段排列不同得到不同指纹。
# 预期：后续用它计算文档和片段身份，不用它代替权限判断。
def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
```

**写完后应当怎样：**后续用它计算文档和片段身份，不用它代替权限判断。

### 第 3 步：先写这个文件需要的导入

把读取一讲扩成整理多讲，仍保留可回查的文件名和段落位置。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：把读取一讲扩成整理多讲，仍保留可回查的文件名和段落位置。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import hashlib
import re
from pathlib import Path
from docx import Document
from .files import digest, load, save
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 4 步：先写固定长度切块

模型窗口有限，先用可计算的长度和重叠建立基线，后面才能比较其他切法。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：模型窗口有限，先用可计算的长度和重叠建立基线，后面才能比较其他切法。
# 预期：600 字块、60 字重叠的下一起点是 540；非法重叠会报错。
def split_text(text, strategy="fixed", size=600, overlap=60):
    if strategy != "fixed":
        raise ValueError("本阶段只实现固定切分。")
    if not 0 <= overlap < size or size < 20:
        raise ValueError("需要 size >= 20 且 0 <= overlap < size。")
    return [(start, text[start:start + size]) for start in range(0, len(text), size - overlap)]
```

**写完后应当怎样：**600 字块、60 字重叠的下一起点是 540；非法重叠会报错。

### 第 5 步：串起读取、切分和来源记录

外层循环负责文件，内层负责段落与块；一次全部成功后才替换 corpus.json。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

下面 2 段按顺序组成同一处代码。每段最多 25 行；保留空行和缩进，全部写完并保存后再检查。

**连续代码 1/2**

```python
# 目的：外层循环负责文件，内层负责段落与块；一次全部成功后才替换 corpus.json。
# 预期：五份原始讲稿不改动；600/60 应得到 15 块，空正文会拒绝。
def ingest(source="data/input", strategy="fixed", size=600, overlap=60, tenant="demo", book="狂人日记"):
    source = Path(source)
    documents, chunks, duplicates, seen = [], [], [], {}
    for file in sorted(source.glob("*.docx")):
        version = hashlib.sha256(file.read_bytes()).hexdigest()
        document = Document(file)
        doc_id = digest([tenant, book, file.name])[:16]
        lecture = re.search(r"第([一二三四五六七八九十]+)讲", file.name)
        groups = []
        for position, paragraph in enumerate(document.paragraphs, 1):
            text = paragraph.text.strip()
            if not text:
                continue
            groups.append([f"p{position:04d}", text])
        if not groups:
            # 整批成功后才发布新快照，避免把扫描件或空文档悄悄当作已完成的导入。
            raise ValueError(f"{file.name} 没有可读正文；本次导入未更新资料快照。")
        documents.append({"doc_id": doc_id, "version": version, "file": file.name,
                          "tenant": tenant, "book": book, "paragraphs": len(groups), "tables_skipped": len(document.tables)})
        for parent, text in groups:
            for start, part in split_text(text, strategy, size, overlap):
                chunk_id = digest([doc_id, version, parent, strategy, size, overlap, start])[:24]
                chunks.append({"id": chunk_id, "doc_id": doc_id, "version": version,
```

**连续代码 2/2**（接在上一段后，不额外增加缩进）

```python
                               "tenant": tenant, "book": book, "file": file.name,
                               "kind": "讲解稿", "lecture": lecture.group(1) if lecture else None,
                               "edition": None, "parent": parent, "start": start,
                               "end": start + len(part), "text": part})
    if not chunks:
        raise ValueError("没有可读正文，请检查输入目录；原文件不会被覆盖。")
    previous = load("corpus.json", {"documents": [], "chunks": []})
    documents += [d for d in previous["documents"] if (d.get("tenant", "demo"), d.get("book", "狂人日记")) != (tenant, book)]
    chunks += [c for c in previous["chunks"] if (c["tenant"], c["book"]) != (tenant, book)]
    result = {"documents": documents, "chunks": chunks, "duplicates": duplicates,
              "strategy": strategy, "size": size, "overlap": overlap}
    result["revision"] = digest(result)
    save("corpus.json", result)
    return {"documents": len(documents), "chunks": len(chunks), "duplicates": duplicates,
            "revision": result["revision"], "tables_skipped": sum(d["tables_skipped"] for d in documents)}
```

**写完后应当怎样：**五份原始讲稿不改动；600/60 应得到 15 块，空正文会拒绝。

### 第 6 步：把切分条件交给运行命令

同一个整理函数接受不同大小；这里不增加检索，也不会连接模型。

**写在哪里：**项目根目录下的 `companion/ingest_cli.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

```python
# 目的：同一个整理函数接受不同大小；这里不增加检索，也不会连接模型。
# 预期：ingest 命令输出文档数、块数与资料版本。
import argparse
import json
from .corpus import ingest


def main():
    parser = argparse.ArgumentParser(description="整理当前作品讲稿")
    parser.add_argument("--source", default="data/input")
    parser.add_argument("--strategy", default="fixed")
    parser.add_argument("--size", type=int, default=600)
    parser.add_argument("--overlap", type=int, default=60)
    parser.add_argument("--tenant", default="demo")
    parser.add_argument("--book", default="狂人日记")
    args = parser.parse_args()
    print(json.dumps(ingest(args.source,args.strategy,args.size,args.overlap,args.tenant,args.book), ensure_ascii=False, indent=2))
```

**写完后应当怎样：**ingest 命令输出文档数、块数与资料版本。

### 第 7 步：给命令入口增加 ingest

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        main()
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        main()
    elif command == "ingest":
        from .ingest_cli import main
        main()
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。

## 运行并观察

```bash
# 每块最多 600 字符、相邻块重叠 60 字符；预期生成 corpus.json，而不改动 DOCX。
python -m companion ingest --size 600 --overlap 60
```

打开 `data/live/corpus.json`，找到corpus.json 中的第一个片段，再回到对应 DOCX 对照。`parent=p0001` 是 Word 段落编号，`start/end` 是清理首尾空白后在这个段落内的字符区间；标题分组模式另有合并规则，后面再学。

## 自己改一次资料标签

先不执行新导入，口头推演：把作品错标为《三国演义》，之后按《狂人日记》筛选会发生什么？问题出在资料层，生成模型无法可靠纠正错误标签。

一个输入目录只放同一作品、同一租户的资料。新增另一作品时建独立输入目录，并在 ingest 中显式写 `--book`。程序替换这一作品当前快照，保留已导入的其他作品与租户。不要把不同作品混在默认目录后都标成《狂人日记》。

如果文档没有读出正文，程序会失败；表格数量会报告为跳过。图片、表格和修订批注不是本读取器已处理的内容，必须留在导入记录里。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 为什么 edition 不直接填一个常见版本？
2. 讲次、Word 段落和原著章回有什么区别？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么 edition 不直接填一个常见版本？**

文件没有证明采用该版本。未知信息保留为空，才能避免错误引用。

**讲次、Word 段落和原著章回有什么区别？**

讲次是课程编排，段落是 DOCX 结构，章回是作品结构；三者不能自动互换。

**通过证据：**能从 corpus.json 的一条片段记录回查 DOCX；列出一个真实未知字段，解释 doc_id 与 version 的区别。

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
from companion.files import load
r=ingest(); assert r["documents"]==5 and r["chunks"]==15
c=load("corpus.json")["chunks"][0]
print(c["file"],c["parent"],c["start"],c["end"])
PY
```

**预期：**5 份讲稿、15 块；每块能追溯文件、段落和字符范围。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
