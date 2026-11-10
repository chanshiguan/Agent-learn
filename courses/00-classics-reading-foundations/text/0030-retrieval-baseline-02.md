# 用固定题集观察检索失败（2/2：把本节能力连起来）

本单元预计 **30—45 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《用固定题集观察检索失败（1/2：把本节能力连起来）》](0030-retrieval-baseline.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

上一小节已经把前一部分写进项目。这一节继续处理 `companion/__main__.py`；先回想它接收什么、交给谁，再往下写。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：给命令入口增加 evaluate

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        main('ask')
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        main('ask')
    elif command == "evaluate":
        from .evaluate_cli import main
        main()
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。

## 运行并观察

```bash
# 不开生成，仅测固定题的检索结果；预期产生每题候选和命中指标。
python -m companion evaluate --output keyword-baseline.json
```

打开 `data/live/keyword-baseline.json`。`document_recall` 看预期文件是否出现，`quote_hit` 看目标短句是否完整落在候选里。文件命中不表示关键句命中；关键句跨块时，quote_hit 也可能为 false。它们都是诊断信号，不是最终质量分。

## 给失败写一个可行动的名字

挑一题，检查候选是否完整保留论据和限定条件。若失败，可写“相关词不重合”“关键句被切开”或“前五条混入重复内容”，并贴出证据；若当前题全部命中，就如实记录命中情况与上下文观察，不需要编造失败。若无法归因，就写待确认，不要用一个笼统的准确率掩盖问题。

打开导学的 `reading-questions.md`，取出你当时自拟的第 5 题。先在讲稿里人工找到它的依据，再仿照示例追加到 `eval/dev.json`，使用未重复的 ID，例如 `dev-05`。填入对应文件前缀和能支持回答的短句；如果资料本来就没有答案，两个列表留空，并将 `expected_insufficient` 写成 `true`。若原题太宽、暂时无法按这个规则核对，先把它拆成一个能明确找依据的小问题，同时在题单里保留原题。

新增题只使用当前样本，不复制他人的私人问题。保存后用不同文件名再跑一次，保留最初四题的基线：

```bash
# 将导学自拟题纳入同一检索流程；此报告应比原四题基线多出你的新题。
python -m companion evaluate --output keyword-with-my-question.json
```

打开新报告，按 ID 找到新增题，核对它的实际来源和预期短句。之后的检索优化继续用这份已扩充的 `eval/dev.json`，不要为使结果好看而删掉失败题。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 文件命中率高就能交付吗？
2. 为什么保留题不能一直拿来调参？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**文件命中率高就能交付吗？**

不能。命中文件不代表找到了支持结论的那句话，更不代表生成正确。

**为什么保留题不能一直拿来调参？**

一旦依据它持续调整，它就成为开发题。要评估新问题表现，需要另留未参与调参的题。

**通过证据：**有基线报告、一条带片段依据的结果分析和新增的一道有人工依据的开发题。分析可以指出失败原因，也可以说明当前命中了什么、哪些限定条件仍需检查。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter12)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
import json
from pathlib import Path
from companion.evaluation import evaluate
cases=json.loads(Path("eval/dev.json").read_text(encoding="utf-8"))
r=evaluate("eval/dev.json")
assert [item["id"] for item in r["records"]]==[case["id"] for case in cases]
assert r["quality_passed"] is None
print([(x["id"],x["quote_hit"]) for x in r["records"]])
PY
```

**预期：**报告包含当前题单的每道题，包括你新增的问题；短句是否命中看各题实际结果，无目标短句的题为 None。这个检查只确认没有漏跑题目，质量尚未人工确认。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
