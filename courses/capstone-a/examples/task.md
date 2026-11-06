使用 meeting-actions Skill 整理 meeting.txt，仅输出 JSON 草稿。
允许读取：本演示目录的 meeting.txt 与 SKILL.md。
禁止：联网、读取其他资料、发送、创建真实提醒、提交与发布。
成功条件：每条行动有 task/owner/due/source；缺失具体日期标待确认；保留“不发布”；不得声称已执行外部动作。
请把最终 JSON 展示给我，我会另存 draft.json 并运行 validate.py。
