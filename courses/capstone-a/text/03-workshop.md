# 结业 A 的完整交付样板

## 先做固定示范，再做自己的任务

固定示范输入 meeting.txt，任务是生成行动草稿，不能实际发布。Skill 控制读取、引用、未知项和输出结构。你可以直接让当前 CLI 按以下完整任务卡操作；指定输出为新临时目录，保留运行记录。

{{code:../examples/task.md}}

{{code:../examples/SKILL.md}}

{{code:../examples/meeting.txt}}

## 完整答案与验证

{{code:../examples/reference-draft.json}}

{{code:../examples/validate.py}}

```bash
# 运行 courses/capstone-a/examples/validate.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/capstone-a/examples/validate.py courses/capstone-a/examples/reference-draft.json
# 运行 courses/capstone-a/examples/validate.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/capstone-a/examples/validate.py /tmp/draft.json
```

第一条只查参考产物；第二条查你实际保存的 CLI 产物。固定示范的负责人只能是小林，周五的具体日期待确认，任务保留不发布，预算未确认。改写任务描述需要人工核对语义，不能因包含“不发布”三个字就算正确。

## README 完整写法

作品名：会议资料到行动草稿。输入：本目录 meeting.txt，三条虚构来源 M1–M3。环境：记录实际 CLI 与模型版本，Python 标准库，无额外包。执行：向 CLI 提供 task.md 与 SKILL.md，指定读取 meeting.txt，输出 draft.json；运行 validate.py 加实际文件路径。期待：带来源的行动列表、未知日期与预算、未发送。异常：文件不存在应停止；来源不在 M1–M3 拒绝；负责人不符拒绝。撤销：删除本次草稿即可，不触及原资料。复现：换干净目录，按相同步骤重跑并对照原句。

这段 README 已说明全流程。自己的项目应替换具体输入输出，不能只把作品名改掉。

## 五维自评的四级标准

| 维度 | 未达 | 基本 | 良好 | 优秀 |
|---|---|---|---|---|
| 问题真实度 | 无具体任务 | 有示例 | 能用于自己的重复任务 | 有实测收益与限制 |
| 工具运用 | 只有聊天 | CLI 参与 | Skill/MCP 可复用且边界明确 | 能解释为何不用更多工具 |
| 可复现 | 无步骤 | 本机可跑 | 干净目录可跑 | 别人照 README 能完成 |
| 韧性 | 错误仍报成功 | 有失败提示 | 缺资料/错来源可定位 | 有恢复且无重复效果 |
| 文档反思 | 无证据 | 有操作描述 | 有真实输出和失败分析 | 根据复用记录做一次可证实改进 |

关键事实错误、越权动作或伪造运行记录属于退回项，不能靠其他维度加分抵消。课程参考程序不会替你生成“已掌握”的记录。

## 最终练习

换成一个自己的非敏感重复任务，保留相同结构，提供一次真实成功与一次故意失败、README、自评与150字以内反思。参考答案是本章固定示范，不是要求每个人做同一项目。两天后从干净目录复现，一周后记录一次真实复用和改进。
