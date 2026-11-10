# 保存结果，并证明没有读错资料

本单元预计 **30—45 分钟**。上一节能看到文字，但终端一关，结果不便比较。现在把正文和来源一起保存，供 Docker 实验重复读取。

## 先运行完整程序

附带的 `read_docx.py` 接受两个位置参数：先输入 DOCX，再指定输出 JSON。在练习目录启用虚拟环境后运行：

```bash
# 读取指定讲稿，将正文与来源保存到第二个参数指定的 JSON；预期显示段落数和字符数。
python read_docx.py \
  "data/input/06 《狂人日记》第一讲两种叙述声音.docx" \
  data/output/first.json
```

反斜杠表示这条命令还没结束，下一行继续；它后面不要加空格。也可以把整条命令写成一行。输出文件夹会由程序创建。

课程包附带的第一讲样本，预期得到 **1 个非空正文段落，1,302 个字符**。这是资料本身的检查值，与编写电脑的路径和配置无关；它表示去除段落两端空白后的字符数，不是 token 数。换了讲稿版本，数字可能变化，应回查清单而不是强行改到一样。

## 看懂完整实现

{{code:read_docx.py}}

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
