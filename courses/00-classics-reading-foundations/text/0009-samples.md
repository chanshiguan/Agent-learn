# 看清这五份文件究竟是什么

本单元预计 **20—30 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《从五份讲稿开始做伴读助手》](0008-mission.html)继续。


## 先用一套人人都能取得的小样本

公开课程附带五份新编《狂人日记》讲解稿，位于练习目录的 `data/input/`。可编辑的 Markdown 正文在 [公开样本目录](../courses/00-classics-reading-foundations/public-materials/index.html)，不是私人授课资料，也不是原著全文。课程中的问题保持不变，参考证据来自这套新稿。

| 文件 | 主要内容 |
|---|---|
| `06 《狂人日记》第一讲两种叙述声音.docx` | 文言序言、白话日记及叙述者 |
| `07 《狂人日记》第二讲月光与平等.docx` | 象征解读的依据和边界 |
| `08 《狂人日记》第三讲吃人的历史联想.docx` | 文学列举与历史证据的区别 |
| `09 《狂人日记》第四讲不可靠叙述.docx` | 人物感受、推断与社会批判 |
| `10 《狂人日记》第五讲传统与未来.docx` | 为传统提供理由，理解结尾的呼吁 |

打开第一讲，记一处讲解者的解释；再打开第五讲，找一处标明出处的短引句。现在不用抄长段，只记文件名、定位词和内容类别。看到第三讲的“徐锡麟／徐锡林”说明时，留意题目写法与核对文本的差别，不要在导入时悄悄统一。

## 为什么读出一段仍可能正确

Word 的屏幕行数、手动换行和段落数量不是一回事。这批公开样本特意用一个正文段落保存每讲内容，在段内保留换行；因此程序读出 `1` 是预期现象。这个设计用于后面的切块实验，不表示一讲在文学上只有一个意思。

第一章先按文件结构读取，第 11 章再比较不同切法。标题文字写在正文里，也不代表 Word 已使用标题样式；这正是“按标题切分”可能没有效果的原因。

## 只准备阅读材料，程序由你接下来写

在 `classics-reader` 下新建 `data`，再在其中新建 `input`。逐份保存下面五个 Word 文件到 `data/input/`，保持文件名不变。这些链接只有阅读材料，不含程序。可以用 Finder 和编辑器完成，本节不要求你会终端命令。

- [06 《狂人日记》第一讲两种叙述声音.docx](../courses/00-classics-reading-foundations/examples/data/input/06%20《狂人日记》第一讲两种叙述声音.docx)
- [07 《狂人日记》第二讲月光与平等.docx](../courses/00-classics-reading-foundations/examples/data/input/07%20《狂人日记》第二讲月光与平等.docx)
- [08 《狂人日记》第三讲吃人的历史联想.docx](../courses/00-classics-reading-foundations/examples/data/input/08%20《狂人日记》第三讲吃人的历史联想.docx)
- [09 《狂人日记》第四讲不可靠叙述.docx](../courses/00-classics-reading-foundations/examples/data/input/09%20《狂人日记》第四讲不可靠叙述.docx)
- [10 《狂人日记》第五讲传统与未来.docx](../courses/00-classics-reading-foundations/examples/data/input/10%20《狂人日记》第五讲传统与未来.docx)

从上面的公开样本目录也能阅读对应 Markdown。先核对正文；不用下载仓库、代码包或运行任何准备脚本。现在项目里只有 `project-card.md` 和五个输入文件，`read_docx.py`、`requirements.txt`、`Dockerfile` 都还不存在。

## 你的资料检查表

在 `project-card.md` 记下：五份文件是否齐全，第一讲能否打开，哪一处是讲解、哪一处需要回到原著核对。再到公开样本说明找到第一讲的来源记录。

<details><summary>没有看到 data/input 怎么办</summary>

在自己的 classics-reader 内手动新建 data/input，保存五份 DOCX。若浏览器给文件名加了编号，改回上方显示的名字。

</details>

**本单元完成条件：**能找到五份样本，说明它们的性质，并解释“程序读出一段”为什么值得核对却不一定是错误。

## 本单元验收与参考答案

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**这五份是什么？** 课程新编的《狂人日记》讲解稿，文件序号为 06—10；它们既不是私人原讲稿，也不是原著全文。讲解中的观点与标明出处的原著引句要分开。

**为什么各读出一段也可能正确？** 本批 DOCX 用一个段落保存正文，段内换行不会增加段落数。程序按文档结构计数，不按屏幕行数计数。

**通过证据：**五份样本可定位，第一讲可打开，来源清单有对应指纹。项目卡记录一处讲解和一处需回查的引句或转述，位置可自行选择。

</details>

## 资料依据

阅读材料见[公开样本说明](../courses/00-classics-reading-foundations/public-materials/index.html)。[Hello-Agents 第八章](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter8)说明文档进入检索系统的流程；本单元先完成输入识别，不提前建立索引。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
