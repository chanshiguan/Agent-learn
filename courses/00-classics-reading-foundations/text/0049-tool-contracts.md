# 让越界请求有可重复的失败结果

本单元预计 **30—45 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 先把失败当作预期行为

工具拒绝越权参数不是系统坏了，是边界生效。把它变成测试，以后改 Prompt、模型或框架时都能重跑。

```bash
# 仅运行工具边界测试；PYTHONPATH 让 Python 找到课程 tests 目录，不改变已安装依赖。
PYTHONPATH=../tests python -m unittest test_companion.CompanionTests.test_tools_reject_identity_override -v
# 再验证来源和未知进度过滤；这两项不调用真实模型，也不等于模型质量测试。
PYTHONPATH=../tests python -m unittest test_companion.CompanionTests.test_source_scope_and_unknown_range -v
```

打开 `../tests/test_companion.py` 对应方法。测试使用临时目录、虚构片段和虚构读者，不访问真实学生数据。断言的是“发生了预期拒绝”，不是文字输出恰好与实现完全一样。

## 补一个自己的反例

复制一种合法调用，把工具名改成 `delete_notes`。它没有登记，预期拒绝，不应猜测你的意图后执行别的函数。再把 query 改为 501 个字符，验证长度边界。

写一张工具契约表：名称、允许参数、身份来源、可读取范围、失败行为。模型看到的描述越清楚，越容易正确选择；但真正的权限仍由程序执行。

这些工具没有写数据库的能力。第 19 章会用独立批准流程处理笔记，而不是在此处悄悄增加一个万能工具。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 未知工具名应怎样处理？
2. 离线测试通过能证明模型会正确用工具吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**未知工具名应怎样处理？**

明确拒绝，并把可处理的错误返回给调用方；不把字符串当代码执行。

**离线测试通过能证明模型会正确用工具吗？**

不能。它证明程序边界；真实模型能否按协议请求工具，要在第 18 章实测。

**通过证据：**两项测试结果、一个自加的越界用例和完整工具契约表。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/03-tool-use-and-hello-agent.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter4)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
