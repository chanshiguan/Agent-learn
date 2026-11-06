# 把一次审查变成可重复技能

原课程 CLI-5–8 的逐题代码、Git diff 审查答案与跨工具卡片见[原题完整实作](04-original-cli.md)；本页用 README 结构检查说明可复用方法。

## 单元一：完整资料与两个层次的检查

本课 sample.md 是正例，empty.md 的运行节为空，另用不存在的文件作第三题。程序先查小节是否存在且非空；人工或 Agent 再查命令能否在给定目录运行、用途是否与实际一致、验收是否可观察。标题齐全只是最低结构条件。

```bash
# 运行 courses/A2-cli-workflow/examples/review.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/A2-cli-workflow/examples/review.py courses/A2-cli-workflow/examples/sample.md
# 运行 courses/A2-cli-workflow/examples/review.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/A2-cli-workflow/examples/review.py courses/A2-cli-workflow/examples/empty.md
# 运行 courses/A2-cli-workflow/examples/review.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/A2-cli-workflow/examples/review.py /tmp/course-a2-missing.md
```

期待 PASS、FAIL（运行小节为空）、FAIL（文件不存在）。失败命令退出非零是正确表现，不是安装出错。

{{code:../examples/review.py}}

## 单元二：Skill 与 Portable Task 的完整区别

Skill 保存长期可复用的方法：读什么、怎样核对、返回什么。Task 保存这次输入和目标。项目规则约束所有相关任务，不应把某次文件名永久写进通用规则。下面两份可直接复用：

{{code:../examples/readme-skill.md}}

{{code:../examples/portable-task.md}}

给 Agent 输入 empty.md 时，完整参考结论是：“FAIL；运行小节没有内容，新使用者不知道执行什么；证据为该小节到下一标题之间为空；未修改文件、未执行文档命令。”给不存在文件则应停止，不自己编造 README。给正例可以返回结构 PASS，但未验证执行的部分必须标清。

## 单元三：盘点、计划、修改、验证怎样交接

盘点输出：哪些文件、当前问题、哪些条件未知。计划输出：仅改变哪些行、用什么验证、失败怎样撤回。修改输出：实际 diff，不只文字承诺。验证输出：实际命令、退出状态、输出、仍有的限制。

例如 empty.md：盘点发现运行节空；计划补具体命令；修改只补这节；验证重跑检查并人工核对路径。若任务只是 review，流程停在发现与建议，不能自动越过授权做修改。Skill 里的方法不提供额外权限。

## 单元四：迁移到第二个 Harness

Portable Task 保持原样；差异卡另写宿主名称、版本、规则目录、Skill 触发方式、模型、权限和会话恢复方式。支持自动发现的宿主可放在其约定目录，不支持时显式把 Skill 当任务说明输入。不能只复制文件就声称成功加载。

两边用相同 sample、empty 与 missing，比较证据与行为。不同模型是额外变量，报告中分开。未具备第二个宿主时可以先填完整安装/触发计划并标未执行；不伪造输出。

## 课末独立练习及评分答案

独立写“资料引用审查”Skill：输入一段答案及带 ID 的资料；检查每条事实是否有来源、来源是否支持；缺资料时停止；只读不改。正例“资料说09:00开放，答案同义复述并引 ID”应支持；反例“资料说09:00，答案说08:00但引同 ID”应失败；无原文不能仅凭 ID 判对。

评分四项分别为通过/退回：目标范围可观察；步骤能照做；正反例能区分；反馈含具体证据。四项全部通过才完成，不用漂亮措辞抵消证据错误。完整答案结构就是上述输入→逐条事实→引用核对→缺项反馈，允许不同措辞，不能把一个通用 JSON 校验器当语义审查。
