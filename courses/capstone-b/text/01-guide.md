# 结业 B：构建并评测一个小型系统

把第三至第八课的能力接起来：工具循环负责执行，检索提供证据，评测判断结果，批准与恢复控制动作。先读完整 RAG 示范及评分边界，再换自己的任务和题集。最终交付要同时包含代码、逐题结果和失败分析。

## 原课要求

完成 B 线含第 7.5 课的自我检查。题目二选一：至少两个有分工和编排的 Agent，或完整检索加生成 RAG。两者都要有 tool use、CLI/API/chat 任一对外接口、明确评测、失败分析和架构说明。

Eval suite 至少五个 development 和三个冻结 holdout，保存版本、成功条件、grader、trial 次数、baseline 与逐题结果。不能把手工试了几个问题当完整评测。

## 示范选 RAG 路线

虚构学习室制度存 documents.json；retrieve 是透明的关键词检索工具；模型实际提出工具请求，程序验证后执行，把结果交回模型生成带来源的答案。CLI 是对外接口。工具最多两次，模型最多四轮，单请求有超时，来源必须来自本次检索。

这里故意先用简单检索，不依赖向量库，便于你看懂失败。它能处理已登记关键词，遇到未收录的同义词会漏检；这是这个基线的限制：它还不具备语义检索能力。以后可用第六课 embedding 替换 retrieve，再保持其他条件不变比较。

## 所有代码与数据

rag_agent.py 包含工具 Schema、检索、真实 Ollama 调用、消息历史、参数验证、终止和引用检查。evaluate.py 读取版本化题集，逐题计时、记成功或错误。没有省略模型接入或评分函数。

```bash
# 运行 courses/capstone-b/examples/rag_agent.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/capstone-b/examples/rag_agent.py "周一几点开放？"
# 运行 courses/capstone-b/examples/rag_agent.py，按本行参数完成当前案例并核对输出；--live 会进入真实服务路径，需先满足本章环境要求。
.venv/bin/python courses/capstone-b/examples/rag_agent.py "周一几点开放？" --live
# 运行 courses/capstone-b/examples/evaluate.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/capstone-b/examples/evaluate.py
# 运行 courses/capstone-b/examples/evaluate.py，按本行参数完成当前案例并核对输出；--live 会进入真实服务路径，需先满足本章环境要求。
.venv/bin/python courses/capstone-b/examples/evaluate.py --live --trials 3
```

第一条是检索摘录基线，没有生成模型；第二条才是完整工具检索加生成。第三条默认 development 基线；第四条真实本地模型进行五题三次，共15次任务，可能较慢。Ollama 需要已运行且有 gemma4:e4b。

## 评分器边界

评分程序会核对来源、检索轨迹和可信摘录。只有确定符合的摘录自动 PASS；结构错误 FAIL；自由改写进入 NEEDS_REVIEW，由人工逐项核对主体、数字、否定、条件和额外事实。待复核不计入自动通过率。

本课提供公开教学 holdout 示例；你读过答案、根据它改过实现后，它就不再是盲测。结业时请另建至少三题冻结保留集，记录冻结时间，不用于调参。公开答案用于学习，不得借此宣称严格盲测成绩。

## 架构与失败分析

CLI → 有界模型循环 → retrieve 工具 → 固定资料 → 证据 → JSON 答案 → 格式/引用检查 → Eval 报告。资料不足拒答；未知工具、错误参数、重复 call ID、超限和截断停止；连接失败报告，不伪造回答。

当前未包含生产身份认证、多租户、持久审计与向量语义召回。因此，它目前适合作为可运行的教学项目，还不是生产服务。真实结业项目根据问题增加必要措施，并用评测证明收益。

## 交付物

程序、架构图或数据流说明、版本化 Eval 报告、运行 README、失败模式及200字内反思。报告分别列 baseline 和候选版本、development 和 holdout、每题每次结果、自动评分与人工核对。最终按问题定义、架构、正确性、评测、韧性、接口文档、反思七维自评。
