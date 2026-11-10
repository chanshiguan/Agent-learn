# 让 Python 读出第一讲

本单元预计 **25—35 分钟**。开始前，你应能启用虚拟环境，并看到“DOCX 读取库可用”。若五份样本尚未准备，先回到导学的资料单元运行准备脚本。

## 先读一小段代码

在练习目录创建 `peek_docx.py`，完整输入下面的代码。这里把路径直接写在代码里，方便你先看清读取过程；下一单元再改用现成的命令行参数。

```python
from pathlib import Path
from docx import Document

# 指定同一份样本，后面改运行环境时才不会把资料差异误当成程序差异。
source = Path("data/input/06 《狂人日记》第一讲两种叙述声音.docx")
document = Document(source)

# 先只观察少量文字，确认读取位置正确，避免把长篇讲稿刷满终端。
print("文件：", source.name)
print("正文段落数量：", len(document.paragraphs))
for position, paragraph in enumerate(document.paragraphs, start=1):
    print("段落位置：", position)
    print("开头文字：", paragraph.text[:80])
```

运行：

```bash
# 运行你刚写的预览程序；本课程第一、第二讲都应显示 1 个正文段落。
python peek_docx.py
```

对于本课程选中的第一讲，预期正文段落数量为 `1`。开头文字应该能在 Word 中找到。显示 80 个字符只限制终端预览，没有截短 `document` 中的内容。

## 把语法和这次任务对上

| 写法 | 在这里有什么用 |
|---|---|
| `Path(...)` | 表示文件位置，后面可以取文件名或检查文件是否存在 |
| `Document(source)` | 让读取库解析 Word 文件，不把 DOCX 当普通文本硬读 |
| `document.paragraphs` | 得到正文段落列表；不会自动包含页眉、脚注和所有表格文字 |
| `enumerate(..., start=1)` | 同时取到位置和段落，方便人从第一段开始核对 |
| `paragraph.text` | 取出当前段落里的文字 |
| `[:80]` | 只拿开头一小段来观察 |

Python 用缩进表示哪些语句属于循环。这里两条循环内的 `print` 都缩进四个空格。代码如果报 `IndentationError`，先检查缩进，别先改文件路径。

## 自己改一个条件

把文件名换成第二讲，再运行一次。先预测段落数是否变化，再用结果验证。随后把预览从 80 个字符改成 120 个字符，确认变化只发生在终端显示。

再故意把文件名中的一个字改错。你应该看到找不到文件的错误。这次排错只检查当前目录、文件名和引号，不去重装读取库。改回正确名称后应恢复。

<details><summary>为什么不能直接使用 open(...).read() 读 DOCX</summary>

DOCX 内部包含结构化的文档部件，并不是按 UTF-8 保存的一整篇纯文本。这里借助读取库取正文段落。你只需要知道这层区别，不必在第一章自己解析 Word 的内部格式。

</details>

**本单元完成条件：**你能读取第一讲和第二讲，找到打印文字在源文件中的位置，并解释预览长度为什么不等于全文长度。

## 本单元验收与参考答案

先完成上面的操作，再用自己的话回答。下面是核对思路和结果的参考，不要求背原句。

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**第一讲和第二讲各有几段？** 本课程附带版本各有 1 个正文段落。需要同时在 Word 中核对预览文字，不能仅凭这个数字判断文件选对了。

**80 改成 120 会改变原文吗？** 不会。`paragraph.text[:120]` 只截取打印时的预览；源 DOCX 和已读入的完整段落不变。

**把文件名写错后先检查什么？** 工作目录、真实文件名与引号。能导入读取库却找不到文件时，重装库不能修正路径。

**通过证据：**保留两讲的运行输出，能在源文件中找到打印的开头文字；改错文件名会失败，改回后恢复。

</details>

## 资料依据

[Stage 0](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/00-foundations.zh-Hans.md)中的文件和程序练习是基础；[Hello-Agents 第八章](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter8)提供文档进入系统的上下文。这里的 DOCX 小程序是为你的讲稿编写的桥接练习，尚未做检索。
