# CLI-6 完整审查参考（broken 样本）

结论：FAIL。范围为当前 Git diff；没有执行待审 README 中的命令，没有修改文件。

1. README.md:7：新增命令 `python3 missing.py` 引用不存在的程序。基线只有 `run.py`；用户照做会遇到文件不存在。改为从仓库根运行 `python3 run.py`，并写明预期输出“学习记录检查完成”。
2. README.md:9：新增本地链接 `missing-guide.md` 的目标不存在，点击无法打开。提供实际说明文件后链接，或去掉这个无效入口；本练习允许的修改范围只有两份 README，不能擅自创建其他文件。

docs/README.md 缺少命令是基线已有问题，不把它算作这个 diff 新引入的缺陷；在 CLI-7 的独立修改任务中处理。

`git diff --check` 即使通过也只说明没有相应空白错误，不能证明命令或链接正确。审查者不运行文档中的命令，因此 check.py 的运行状态应填“审查阶段未执行”；教师用可信检查器独立验证时应失败。

审查前后 status 应相同，仅 README.md 存在原有待审修改；review-evidence.json 被 .gitignore 排除。没有 HEAD 返回 NEEDS_INFO；没有 diff 返回 PASS（范围为空），同时列出未跟踪文件不在覆盖范围内。
