# 保存结果，并证明没有读错资料

本单元预计 **55—70 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《让 Python 读出第一讲》](0012-read-document.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 运行刚写出的程序

你刚写的 `read_docx.py` 接受两个位置参数：先输入 DOCX，再指定输出 JSON。在练习目录启用虚拟环境后运行：


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：把输入、输出变成终端参数

上一节每换一讲都要改代码。现在让运行命令选择文件，并阻止把输出写回 Word。

**写在哪里：**项目根目录下的 `read_docx.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

```python
# 目的：上一节每换一讲都要改代码。现在让运行命令选择文件，并阻止把输出写回 Word。
# 预期：写完这一步可先运行 python read_docx.py --help，看到两个位置参数；给出错误后缀时会停止。
"""把一份讲稿的正文段落保存为 JSON，保留回查来源所需的信息。"""

import argparse
import hashlib
import json
from pathlib import Path

from docx import Document


parser = argparse.ArgumentParser(description="读取一份 DOCX 讲稿")
parser.add_argument("source", type=Path, help="输入的 .docx 文件")
parser.add_argument("output", type=Path, help="新生成的 .json 文件")
args = parser.parse_args()
if not args.source.is_file() or args.source.suffix.lower() != ".docx":
    parser.error("输入必须是存在的 .docx 文件。先检查路径和引号。")
if args.output.suffix.lower() != ".json":
    parser.error("输出请使用 .json 扩展名，避免误把原讲稿当成输出覆盖。")
```

**写完后应当怎样：**写完这一步可先运行 python read_docx.py --help，看到两个位置参数；给出错误后缀时会停止。

### 第 2 步：整理正文，并保留原段落位置

跳过空段，但不重新编号，后面引用仍能指回 Word 原来的位置。空正文应失败。

**写在哪里：**项目根目录下的 `read_docx.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 目的：跳过空段，但不重新编号，后面引用仍能指回 Word 原来的位置。空正文应失败。
# 预期：用本页的 DOCX 与 JSON 两个路径参数运行，先打印已读取的非空段数 1；此时还没有写出 JSON。
document = Document(args.source)
paragraphs = []
for position, paragraph in enumerate(document.paragraphs, start=1):
    text = paragraph.text.strip()
    if text:
        # 保留 Word 正文中的位置，而不是过滤空段后重新编号，方便回查原文件。
        paragraphs.append({"id": f"p{position:04d}", "text": text})

if not paragraphs:
    parser.error("正文没有读出文字。请检查是否为扫描图片或主要内容在表格中。")


# 先观察中间结果，避免到写入后才发现正文没有读到。
print("已读取的非空段数：", len(paragraphs))
```

**写完后应当怎样：**用本页的 DOCX 与 JSON 两个路径参数运行，先打印已读取的非空段数 1；此时还没有写出 JSON。

### 第 3 步：给结果补上来源卡

只保存正文会丢失出处。文件名、指纹、段落数和字符数一起保存，后续能识别换稿。

**写在哪里：**项目根目录下的 `read_docx.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 目的：只保存正文会丢失出处。文件名、指纹、段落数和字符数一起保存，后续能识别换稿。
# 预期：再次运行，多显示待保存的来源文件名；JSON 仍要等下一步写入。相同输入指纹相同，它不是原著页码。
result = {
    "source_file": args.source.name,
    "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
    "source_kind": "讲解稿",
    "unit": "Word 正文段落，不是原著章回",
    "paragraph_count": len(paragraphs),
    "character_count": sum(len(item["text"]) for item in paragraphs),
    "skipped_table_count": len(document.tables),
    "paragraphs": paragraphs,
}


# 写入之前先核对来源，防止把另一讲的内容保存成第一讲。
print("待保存的来源：", result["source_file"])
```

**写完后应当怎样：**再次运行，多显示待保存的来源文件名；JSON 仍要等下一步写入。相同输入指纹相同，它不是原著页码。

### 第 4 步：写入 JSON，再打印摘要

JSON 是后续程序可读取的中间结果；先保留中文和缩进，方便你人工核查。

**写在哪里：**项目根目录下的 `read_docx.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 目的：JSON 是后续程序可读取的中间结果；先保留中文和缩进，方便你人工核查。
# 预期：第一讲输出 1 段、1302 字，生成 data/output/first.json。
args.output.parent.mkdir(parents=True, exist_ok=True)
# 保存为 UTF-8，并直接保留中文，便于用编辑器逐段核对，不必先读转义字符。
args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"来源：{result['source_file']}")
print(f"正文非空段落：{result['paragraph_count']}；字符数：{result['character_count']}")
print(f"输出：{args.output}")
if document.tables:
    print("注意：本章程序不读取表格；请在记录里说明这项遗漏。")
```

**写完后应当怎样：**第一讲输出 1 段、1302 字，生成 data/output/first.json。

## 运行并观察

```bash
# 读取指定讲稿，将正文与来源保存到第二个参数指定的 JSON；预期显示段落数和字符数。
python read_docx.py \
  "data/input/06 《狂人日记》第一讲两种叙述声音.docx" \
  data/output/first.json
```

反斜杠表示这条命令还没结束，下一行继续；它后面不要加空格。也可以把整条命令写成一行。输出文件夹会由程序创建。

单独下载的第一讲公开样本，预期得到 **1 个非空正文段落，1,302 个字符**。这是资料本身的检查值，与编写电脑的路径和配置无关；它表示去除段落两端空白后的字符数，不是 token 数。换了讲稿版本，数字可能变化，应回查清单而不是强行改到一样。

## 回看数据怎样流动



阅读时沿着“接收路径→读取文档→整理段落→保存结果”走一遍。`argparse` 帮程序接收命令行参数，并生成 `--help`；`json.dumps` 将字典和列表变成可以写入文件的文本。`parser.error` 会说明输入问题并以非零状态结束，后面 Docker 也能观察这个状态。

`source_sha256` 是原文件的内容指纹，用于比较是否读取了同一份输入。它不表示讲稿已经过事实核查。`p0001` 是 Word 正文段落的位置，也不能当作原著第一章。

## 打开文件核对

用编辑器打开 `data/output/first.json`。找到 `source_file`、`paragraph_count` 和 `paragraphs`。`paragraphs` 是列表，里面每个对象有 `id` 和 `text`；你看到的长字符串才是这节读出的正文。

从 Word 开头、中间、结尾各挑一句，在 JSON 里搜索。能找到这三处，比只看“成功”两个字更能说明读取是否符合预期。仍需记住本章范围：程序只读取正文段落，表格数量另外记录，页眉、脚注、文本框和图片中的文字尚未处理。

## 课末练习

用第二讲生成 `data/output/second.json`，不要覆盖第一讲。写下两份文件的字符数，并解释为什么它们各自都可能只有一段。

<details><summary>提示</summary>

命令的第一个参数决定读哪份资料，第二个参数决定结果写到哪里。若只改输入却不改输出，旧结果会被新的 JSON 替换。

</details>

<details><summary>完整参考命令</summary>

```bash
# 读取指定讲稿，将正文与来源保存到第二个参数指定的 JSON；预期显示段落数和字符数。
python read_docx.py \
  "data/input/07 《狂人日记》第二讲月光与平等.docx" \
  data/output/second.json
```

</details>

再试一次不存在的输入，确认程序没有伪造成功结果：

```bash
# 故意使用不存在的输入验证失败行为；预期报错，且不新建 missing.json。
python read_docx.py data/input/not-found.docx data/output/missing.json
# 立即检查上一条程序的退出状态；本节故意输入错误时预期为 2，中间不要执行其他命令。
echo $?
```

`echo $?` 显示紧接着上一条命令的退出状态；预期为 `2`。中间插入另一条命令后，这个值就不再代表读取脚本。回头检查 `missing.json`，在原本不存在的情况下，它不应被创建。

**第 1 章验收：**保留两份 JSON；能对照回源文件；能独立定位一次路径错误；能说明当前读取范围。完成后再进入 Docker，不需要先加向量库。

## 本单元验收与参考答案

先完成上面的操作，再用自己的话回答。下面是核对思路和结果的参考，不要求背原句。

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**两份 JSON 应当是什么结果？** 附带版本的第一讲为 1 段、1,302 字符，第二讲为 1 段、1,306 字符；分别保存为 `first.json` 和 `second.json`。字符数不是 token 数。

**为什么保存来源？** 文件名定位讲稿，SHA-256 判断输入字节是否相同，段落 ID 帮助回到正文位置。它们都不能证明讲稿观点正确，也不是原著页码。

**读不到文件时，合格行为是什么？** 报输入错误，紧接着检查退出码为 2；如果 `missing.json` 原本不存在，就不应新建它。若已有旧记录，要分清旧文件与本次结果。

**通过证据：**两份输出均可打开，在第一讲中选取的开头、中间、结尾三处文字能在 JSON 找到。当前只读正文段落，表格只记数量，页眉、脚注、图片文字等未处理。

</details>

## 资料依据

[Stage 0](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/00-foundations.zh-Hans.md)涵盖 JSON 与文件输出；[Stage 6](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/06-memory-rag.zh-Hans.md)说明资料处理在 RAG 中的位置。完整代码由本课程提供，其验证范围见课程首页的验证记录。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
import runpy,sys
sys.argv=["read_docx.py","data/input/06 《狂人日记》第一讲两种叙述声音.docx","data/output/first.json"]
runpy.run_path("read_docx.py",run_name="__main__")
PY
```

**预期：**产生 first.json；原 DOCX 不变。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
