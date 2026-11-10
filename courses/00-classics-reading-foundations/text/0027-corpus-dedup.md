# 用副本练习去重与更新

本单元预计 **30—45 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 先保护原文件

去重是识别相同内容，不是自动删除原资料。本实验用副本，结束后恢复已知输入。文件字节相同可以确认重复；措辞相近或文件名带“修改”不能据此决定哪个版本正确。

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
