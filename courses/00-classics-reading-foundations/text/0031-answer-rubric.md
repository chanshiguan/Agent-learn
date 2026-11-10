# 给模型回答打分，也保留不通过

本单元预计 **50—65 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《用固定题集观察检索失败（2/2：把本节能力连起来）》](0030-retrieval-baseline-02.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 把生成质量与检索质量分开

这次才调用真实模型。评分看三件事：解释是否被证据支持、引用是否支持对应说法、表达是否适合目标读者。年龄适配不是简单地“用词可爱”：不羞辱读者，不替读者强下价值结论，遇到复杂内容可提示家长共同讨论。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：让生成评测成为显式选择

默认检索不产生模型调用；只有 --generate 才把题目和候选资料送给模型。

**写在哪里：**项目根目录下的 `companion/evaluation.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .rag import retrieve
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .rag import retrieve, answer
```

**写完后应当怎样：**能分别保留检索失败、模型结构错误和人工评分。

### 第 2 步：在同一条记录中保留模型结果

出错时只记录错误类型，人工字段仍留空，避免把协议成功当成文学正确。

**写在哪里：**项目根目录下的 `companion/evaluation.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    if generate or reranking or rewriting:
        raise ValueError("本阶段只运行检索基线。")
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

**写完后应当怎样：**每道题都有来源及真实响应或失败类型，等待人工逐项核对。

### 第 3 步：在同一条记录中保留模型结果

出错时只记录错误类型，人工字段仍留空，避免把协议成功当成文学正确。

**写在哪里：**项目根目录下的 `companion/evaluation.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
                  "manual": {"answer_supported": None, "citation_supported": None, "age_appropriate": None}}
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
                  "manual": {"answer_supported": None, "citation_supported": None, "age_appropriate": None}}
        # 检索测试默认不调用生成模型；generate 显式开启后才可能向云端发送讲稿片段。
        if generate:
            try:
                record["response"] = answer(case["question"], hits)
            except Exception as error:
                record["error_type"] = type(error).__name__
```

**写完后应当怎样：**每道题都有来源及真实响应或失败类型，等待人工逐项核对。

### 第 4 步：把人工核对变成明确门槛

三个人工字段必须分别为 true，证据不足行为也要匹配预期；少一项就不能放行。

**写在哪里：**项目根目录下的 `companion/evaluation.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：三个人工字段必须分别为 true，证据不足行为也要匹配预期；少一项就不能放行。
# 预期：未评分的报告会失败，不能用缺省值蒙混过去。
def quality_gate(report_file):
    report = json.loads(Path(report_file).read_text(encoding="utf-8"))
    failures = []
    if not report.get("generated") or not report.get("records"):
        failures.append("没有真实生成记录。")
    for item in report.get("records", []):
        if item.get("error_type") or not item.get("response"):
            failures.append(f"{item['id']} 没有成功响应。")
        if not all(item.get("manual", {}).get(k) is True for k in ("answer_supported", "citation_supported", "age_appropriate")):
            failures.append(f"{item['id']} 缺少逐项人工通过结论。")
        if item.get("response", {}).get("insufficient") is not item.get("expected_insufficient"):
            failures.append(f"{item['id']} 的证据不足行为未达到预期。")
    return {"passed": not failures, "failures": failures,
            "scope": "仅这份题集的记录；不是生产容量、教学效果或公司上线批准"}
```

**写完后应当怎样：**未评分的报告会失败，不能用缺省值蒙混过去。

### 第 5 步：让质量门槛有明确退出码

自动流水线需要知道通过还是失败；失败应退出非零，而不只打印一句提醒。

**写在哪里：**项目根目录下的 `companion/grade_cli.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

```python
# 目的：自动流水线需要知道通过还是失败；失败应退出非零，而不只打印一句提醒。
# 预期：未完成核对时退出码为 2，并说明缺失项。
import argparse
import json
from .evaluation import quality_gate


def main():
    parser=argparse.ArgumentParser(description="检查已人工核对的报告")
    parser.add_argument("report")
    result=quality_gate(parser.parse_args().report)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not result["passed"]:
        raise SystemExit(2)
```

**写完后应当怎样：**未完成核对时退出码为 2，并说明缺失项。

### 第 6 步：给命令入口增加 grade

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        from .evaluate_cli import main
        main()
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        from .evaluate_cli import main
        main()
    elif command == "grade":
        from .grade_cli import main
        main()
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。

## 运行并观察

```bash
# 对开发题执行真实检索和生成；线上路线会发送命中的讲稿片段并产生费用。
python -m companion evaluate --generate --output answer-baseline.json
# 在人工评分尚未填写时检查门槛；预期不通过，提醒缺少证据而不是自动补分。
python -m companion grade data/live/answer-baseline.json
```

用编辑器打开报告。每题 `manual` 的三项默认是 `null`。逐题对照 `sources` 与 `response`，确实符合才填 `true`，不符填 `false`，拿不准保持 `null`，另写理由。JSON 布尔值用小写，不能填字符串 `"true"`。

## 用一条规则统一评分

“这个解释和我的解读不同”不自动算错；它应提供证据并说明解释空间。“片段只说序言，回答却给出未提供的出版社”应判不支持。无答案题的合格输出必须承认不足。引用真实存在但与结论无关，仍判引用不支持。

填写后再运行 grade。程序检查的是这份记录是否满足约定，不能知道评分人是否认真，也不能据此认证教学效果。保留初始报告、人工评阅版和失败原因，不覆盖失败历史。

## 阶段二交付

到这里应有结构化资料、三个查询实验、固定题集和一份真实生成评阅。下一阶段所有检索优化先用同一组题比较，不先追新名词。选读页会解释更复杂的方法，但主线每次只改一个条件。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. null、false 和 true 分别是什么意思？
2. 模型可以给自己打满分吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**null、false 和 true 分别是什么意思？**

null 是未评或无法判断，false 是已评且不通过，true 是已核对通过。缺测不能当通过。

**模型可以给自己打满分吗？**

可以辅助发现问题，但不能替代这里的人工作证。文学依据与年龄表达要由能阅读资料的人核查。

**通过证据：**有人工逐项评阅和失败理由；grade 的结果与报告一致，未实测项仍明确留空。

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
from companion.evaluation import quality_gate
r=quality_gate("data/live/evaluation.json")
assert not r["passed"]
print("没有真实回答和人工评分，正确拒绝通过")
PY
```

**预期：**没有评分就不能宣称质量达标。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
