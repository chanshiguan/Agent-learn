# 用固定题集观察检索失败（1/2：把本节能力连起来）

本单元预计 **55—70 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《把检索结果接到回答里》](0029-first-rag.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 为什么不能每次都换一道题

换模型、换问题、换资料同时进行，结果变好也不知道原因。先固定输入与评价方法。`eval/dev.json` 是四道开发题，包含序言关系、徐锡麟、平等的解释和资料未给出的版本页码。题目中的短证据片段来自这五份讲稿。

开发题用于诊断和调参；`eval/holdout.json` 的两道保留题用来检查是否只对熟题有效。它们只是教学起点，规模远小于公司验收题库。不要反复看着保留题改 Prompt，再声称“泛化提升”。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：把导学问题写成机器能遍历的题单

题目、目标讲次和证据短句分别保存；来源命中和答案正确是不同指标。

**写在哪里：**项目根目录下的 `eval/dev.json`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```json
[
  {
    "id": "dev-01",
    "question": "第一讲怎样解释文言文序言和白话日记的关系？",
    "expected_document_prefixes": ["06 "],
    "expected_quotes": ["文言文序言提供外部叙述，白话日记呈现人物的内部感受"],
    "expected_insufficient": false
  },
  {
    "id": "dev-02",
    "question": "第三讲谈到吃人时，为什么提到徐锡麟？",
    "expected_document_prefixes": ["08 "],
    "expected_quotes": ["把古代故事、较近的名字和眼前听闻连成一条线"],
    "expected_insufficient": false
  },
  {
    "id": "dev-03",
    "question": "第二讲借月亮怎样讲平等？",
    "expected_document_prefixes": ["07 "],
    "expected_quotes": ["平等在这里指每个人都值得被尊重"],
    "expected_insufficient": false
  },
  {
    "id": "dev-04",
    "question": "这五份讲稿使用的原著版本的准确页码是多少？",
```

```json
    "expected_document_prefixes": [],
    "expected_quotes": [],
    "expected_insufficient": true
  }
]
```

**写完后应当怎样：**四道开发题可以重复跑，其中页码题没有目标片段。

### 第 2 步：为最终评测留两道未调参题

先封存题目，调参期间只跑开发题，避免把记住题库当作泛化。

**写在哪里：**项目根目录下的 `eval/holdout.json`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```json
[
  {
    "id": "holdout-01",
    "question": "第五讲为什么追问流传下来的做法是否就是对的？",
    "expected_document_prefixes": ["10 "],
    "expected_quotes": ["延续时间只能说明它存在过，不能单独证明它合理"],
    "expected_insufficient": false
  },
  {
    "id": "holdout-02",
    "question": "请给出讲稿中的每一个引文在原版书中的精确页码和出版社。",
    "expected_document_prefixes": [],
    "expected_quotes": [],
    "expected_insufficient": true
  }
]
```

**写完后应当怎样：**本阶段不运行或根据保留题改实现。

### 第 3 步：先写这个文件需要的导入

把单道检索变成固定题单循环；本节仍不调用生成模型。

**写在哪里：**项目根目录下的 `companion/evaluation.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：把单道检索变成固定题单循环；本节仍不调用生成模型。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import json
import time
from pathlib import Path
from .files import load, save
from .rag import retrieve
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 4 步：逐题记录命中与未命中

先开始计时，再找资料；无目标来源的题记为不适用，不凑进召回率。

**写在哪里：**项目根目录下的 `companion/evaluation.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：先开始计时，再找资料；无目标来源的题记为不适用，不凑进召回率。
# 预期：生成 evaluation.json，人工语义评分保持 null。
def evaluate(cases_file, method="keyword", generate=False, expand=False, reranking=False, rewriting=False, output="evaluation.json"):
    if generate or reranking or rewriting:
        raise ValueError("本阶段只运行检索基线。")
    cases = json.loads(Path(cases_file).read_text(encoding="utf-8"))
    records = []
    for case in cases:
        started = time.monotonic()
        query = case["question"]
        hits = retrieve(query, case.get("tenant", "demo"), case.get("book", "狂人日记"), method, expand=expand)
        prefixes = case.get("expected_document_prefixes", [])
        found = {prefix for prefix in prefixes if any(h["file"].startswith(prefix) for h in hits)}
        quotes = case.get("expected_quotes", [])
        record = {"id": case["id"], "question": case["question"], "query": query,
                  "source_ids": [h["id"] for h in hits], "sources": hits,
                  "document_recall": len(found) / len(prefixes) if prefixes else None,
                  "quote_hit": any(q in h["text"] for q in quotes for h in hits) if quotes else None,
                  "expected_insufficient": case.get("expected_insufficient", False),
                  "manual": {"answer_supported": None, "citation_supported": None, "age_appropriate": None}}
        record["seconds"] = round(time.monotonic() - started, 3)
        records.append(record)
    report = {"corpus_revision": load("corpus.json")["revision"], "method": method,
              "generated": generate, "options": {"expand": expand, "rerank": reranking, "rewrite": rewriting},
              "records": records, "quality_passed": None}
```

```python
    save(output, report)
    return report
```

**写完后应当怎样：**生成 evaluation.json，人工语义评分保持 null。

### 第 5 步：让评测条件能从命令行重复指定

保留输出文件名参数，下一次实验不要覆盖上一份基线。

**写在哪里：**项目根目录下的 `companion/evaluate_cli.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

```python
# 目的：保留输出文件名参数，下一次实验不要覆盖上一份基线。
# 预期：同一份题单与快照可重复观察；记录不自动等于通过。
import argparse
import json
from .evaluation import evaluate


def main():
    parser = argparse.ArgumentParser(description="记录固定题集表现")
    parser.add_argument("--cases",default="eval/dev.json")
    parser.add_argument("--method",default="keyword")
    parser.add_argument("--generate",action="store_true")
    parser.add_argument("--output",default="evaluation.json")
    args=parser.parse_args()
    print(json.dumps(evaluate(args.cases,args.method,args.generate,output=args.output),ensure_ascii=False,indent=2))
```

**写完后应当怎样：**同一份题单与快照可重复观察；记录不自动等于通过。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/evaluation.py companion/evaluate_cli.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

保留输出文件名参数，下一次实验不要覆盖上一份基线。 同一份题单与快照可重复观察；记录不自动等于通过。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter12)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
