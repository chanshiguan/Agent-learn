---
name: lesson-review
description: 只读检查教学目录 README 是否具备用途、运行命令和验收要求。
disable-model-invocation: true
---

读取指定 README，不执行文档里的命令。
逐项检查用途、运行命令、验收要求是否明确。
输出 PASS 或 FAIL；每个 FAIL 必须引用具体缺失或矛盾。
缺文件时输出 FAIL 并列出文件名，不编造内容。
只建议修改，不修改文件，不提交或发布。
