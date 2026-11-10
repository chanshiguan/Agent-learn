# 用副本练习去重与更新

本单元预计 **30—45 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《给每个片段一张来源卡》](0026-corpus-metadata.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 先保护原文件

去重是识别相同内容，不是自动删除原资料。本实验用副本，结束后恢复已知输入。文件字节相同可以确认重复；措辞相近或文件名带“修改”不能据此决定哪个版本正确。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：用内容指纹阻止重复导入

改文件名不等于换正文；先查本批指纹，再决定是否读取并加入快照。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        version = hashlib.sha256(file.read_bytes()).hexdigest()
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
        version = hashlib.sha256(file.read_bytes()).hexdigest()
        if version in seen:
            duplicates.append({"file": file.name, "same_as": seen[version]})
            continue
        seen[version] = file.name
```

**写完后应当怎样：**副本进入 duplicates，不产生第二份相同正文的块；更新原稿会生成新版本。

## 运行并观察

```bash
# 建一个独立实验目录；只复制五份样本，不移动原件。
mkdir -p data/ingest-lab
cp data/input/*.docx data/ingest-lab/
# 给同一文件再取一个名字；预期程序识别为字节重复，而不是第六份新资料。
python -c 'from pathlib import Path; import shutil; p=sorted(Path("data/input").glob("*.docx"))[0]; shutil.copy2(p, "data/ingest-lab/重复副本.docx")'
# 只读取实验副本；输出 duplicates 应指出重复关系。
python -m companion ingest --source data/ingest-lab
# 恢复主线输入快照，后面的检索始终使用已知的五份样本。
python -m companion ingest --source data/input
```

记录两次输出中的 documents、duplicates 和 revision。这里的去重只覆盖当前这次导入，同一作品跨版本的内容取舍仍要审核。revision 是整份资料快照的指纹，不是“质量得分”。

## 更新与删除也要有明确含义

在实验目录里移走一份副本，再导入，表示当前作品的新快照不再包含它；原件和其他作品不会被删除。空目录会报错，不会清空整个知识库。正式撤下整部作品属于管理操作，需要单独审核流程。

把副本的一句话改掉并保存，再导入，观察 version 与片段 ID 变化。修改工具也可能改变 DOCX 字节，即使可见文字没变；指纹变化只能证明文件变了，不能证明文学内容发生了怎样的变化。

## 排错与交付

若重复数为 0，比较两份文件的字节是否真相同；若出现很多片段，不要把它误读为很多文档。记录文档数、片段数、跳过表格数三项。整理完恢复 `data/input` 快照，保持第 7 章输入一致。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 重复副本应该删掉吗？
2. 撤下一份资料后，旧答案还能引用吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**重复副本应该删掉吗？**

本程序只报告并跳过同批字节重复，不删除原件。是否删除由资料管理者判断。

**撤下一份资料后，旧答案还能引用吗？**

旧答案只能作为历史记录；新回答必须使用当前快照。第 10 章会把资料版本与向量索引版本绑定。

**通过证据：**保存去重前后计数及一次修改后的版本变化，并确认主线已恢复五份原样本。

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
a=ingest(); b=ingest()
assert a["revision"]==b["revision"]
print("相同输入重复整理，版本不变")
PY
```

**预期：**重复导入不会凭空增加资料，版本保持一致。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
