# course-review 1.0.0

用途：只读审查 Git diff 引入的问题。宿主：支持本地 Plugin 的 Claude Code；其他宿主只复用 skills/review-changes/SKILL.md 正文，不能直接假定支持此 Plugin。

权限：读取项目规则、已跟踪文件和 Git diff/status；不需要网络、编辑、提交、推送、评论或发布。Skill 是文本约束，实际权限仍由宿主控制。

安装：在干净的演示仓库中用 `claude --plugin-dir /本机课程目录/examples/team-plugin` 启动；替换为这份 README 所在目录的绝对路径。输入 `/course-review:review-changes`。这里只加载到本次启动，不修改全局 Marketplace。

测试：使用 A2 diff_lab.py 的 broken 副本，预期指出 README.md:7 的缺失程序和 :9 的失效链接；fixed 副本预期无已证实新增问题。两种情况下保存审查前后的 git status --short，必须相同。baseline 副本无 diff，应说明范围为空，不能声称检查了全部文件。

版本：1.0.0。更新前比较 SKILL.md 和清单；在新的 demo 上重跑三种输入，再决定采用。分享时只分享本目录，不包含项目私有规则、账户配置或秘密。

移除：退出本次会话，重新启动时不传 --plugin-dir；新会话确认找不到 course-review:review-changes。若另行安装到持久目录，应使用该宿主的卸载入口并复查。移除后不要把旧会话残留上下文当作仍然安装。
