# CLI-5 到 CLI-8：逐题实作与完整参考

这四题分别练规则、Git diff 审查、分阶段修改、跨工具迁移。后续的 [README 结构检查](03-workshop.md)是补充实验，不能替代 CLI-6 的改动审查。所有命令从 ai-learn 根目录开始；本章创建临时副本，不改学习项目的 Git 状态。

## CLI-5：项目规则

先建立原始双 README 仓库：

```bash
# 运行 courses/A2-cli-workflow/examples/diff_lab.py，按本行参数完成当前案例并核对输出。
python3 courses/A2-cli-workflow/examples/diff_lab.py --mode baseline
```

输出 directory 是本次演示目录。进入该目录后用 `git status --short` 确认干净；按当前宿主选 AGENTS.md（Codex）或 CLAUDE.md（Claude Code），写入下面完整规则。不要同时开两个修改同一目录的会话。

{{code:../examples/project-rules.md}}

给 Agent 的验证输入：“先说明这个仓库用途、禁止事项、验证命令与交付格式，列出读取的规则路径，不修改文件。”参考答案应准确复述这四项，验证必须包括 git diff --check 与 python3 check.py。只回答“我会遵守规则”不算有证据。规则文件由你主动添加造成的 status 变化先记录，之后比较 Agent 是否另改了文件。

## CLI-6：审查真正的 Git diff

```bash
# 运行 courses/A2-cli-workflow/examples/diff_lab.py，按本行参数完成当前案例并核对输出。
python3 courses/A2-cli-workflow/examples/diff_lab.py --mode broken
```

它产生含两个缺陷的 README 改动与真实 diff。进入输出 directory 后，把以下 Skill 安装到项目 `.agents/skills/review-changes/SKILL.md`（Codex）或 `.claude/skills/review-changes/SKILL.md`（Claude Code）。Skill 文件复制完再保存 status 基线。显式要求“读取这个 Skill，审查当前 Git diff”；Claude Code 可输入 `/review-changes`。若宿主未发现 Skill，显式读完整路径，不假定安装等于加载。

{{code:../examples/SKILL.md}}

<details><summary>做完再核对完整答案</summary>

{{code:../examples/diff-reference.md}}

</details>

验收：准确指出两个新增缺陷，有文件、行号、影响与证据；不将未改文件的旧问题算新增问题；审查前后 status 一致；不执行 README 的可疑命令。仅运行 `git diff --check` 然后声称“无问题”失败。

## CLI-7：两份文件的四步交接

新建另一个 baseline 副本，避免继承上一题的坏改动，按这张任务卡分两轮输入：

{{code:../examples/portable-diff-task.md}}

完整参考过程：盘点发现两份文件运行节都待补；计划只修改这两节、统一从仓库根运行；批准后两份文件都替换为下面 AFTER 内容；验证检查器 PASS 且 diff 仅涉及两份 README，未处理项为“未测试其他宿主”。

下面脚本包含两份原始文件、完整目标文件、检查器与 Git 操作；`--mode fixed` 自动构造参考结果，**不算 Agent 已执行**。独立作业应从 baseline 手动交给 CLI 执行。检查器从 baseline 起就存在，不能为通过作业改弱它。

{{code:../examples/diff_lab.py}}

```bash
# 运行 courses/A2-cli-workflow/examples/diff_lab.py，按本行参数完成当前案例并核对输出。
python3 courses/A2-cli-workflow/examples/diff_lab.py --mode fixed
```

参考：diff_check_exit=0、check_exit=0，两份 README 都在 status 中。如果只改一份，check.py 非零并指出另一份。恢复时仅在这个干净演示副本确认没有别人改动后执行 `git restore -- README.md docs/README.md`；之后 diff 应为空，check.py 回到失败，因为原始基线本来尚未补命令。撤回成功不等于任务完成。

## CLI-8：同一任务，分别记录环境

使用上面同一任务卡，在两个新建 baseline 副本操作。模型/provider 不同必须记录，不把效果差别全部归因于 Harness。第二工具不可用时保留“未执行”，不要填虚构截图或耗时。

| 字段 | 第一份完整参考填写方式 | 第二份完整参考填写方式 |
|---|---|---|
| 核心任务 | portable-diff-task 原文，修改两份 README | 同一原文和相同 baseline |
| 宿主、版本 | 当前实际版本输出；本参考未执行 | 第二宿主实际版本；本参考未执行 |
| Provider/model | 读取会话实际显示，取不到写未知 | 同样记录，不能照抄第一列 |
| 规则/Skill 位置 | Codex：AGENTS.md、.agents/skills/review-changes | Claude：CLAUDE.md、.claude/skills/review-changes |
| 权限与登录 | 记录实际目录读写范围、命令审批和登录方式 | 记录该宿主设置，不照搬配置键 |
| 触发 | 显式读取 Skill 并只读审查 | /review-changes 或显式路径 |
| 结果证据 | 两份 README diff、两个检查结果、是否越界 | 保留同样字段 |
| 时间/费用 | 以实际记录填写，未知不写零 | 以实际记录填写，订阅/API 分开 |
| 完成状态 | 未执行（示范卡不伪装实测） | 未执行（无账号时亦如此） |

可核验的参考内容是任务、允许范围与成果；账号和运行测量只能由实际执行产生。验收两边都用相同任务条件；如只完成一边，知识与准备可以完成，跨工具实操仍未完成。
