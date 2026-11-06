# 用最小改动证明问题已解决

## 单元一：看实际代码，再决定怎样改

开发任务先找入口、读相关实现与项目规则，再提出可验证修改。Diff 表示本次改变了什么，测试表示指定条件是否成立；两者必须一起看。通过测试不能自动授权 push、merge 或 deploy。

本课原任务是 README 小改；完整参考包含只读分析、计划、前后文件、diff、验证和撤回。附加空列表 bug 用于迁移，不替代原任务。请先运行临时目录演示：

```bash
# 运行 courses/branch-developer/examples/develop_demo.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/branch-developer/examples/develop_demo.py
```

输出应为修改前退出非零、修改后 PASS、只有 README 内容差异、撤回验证 true。脚本按固定步骤演示修改，没有调用 CLI Agent。独立作业仍需要你实际使用 CLI 完成。

{{code:../examples/develop_demo.py}}

## 单元二：完整参考与人工判断

{{code:../examples/reference-work.json}}

“顺手格式化全仓”不属于改运行说明，应该拒绝扩大范围。真实项目有未提交改动时，不能直接整文件 restore；先找属于本任务的差异，定点撤回。并行工作可用独立工作树减少文件冲突，但账号、网络和外部服务仍共享，需要另外约束。

## 单元三：权限和工具生态

IDE/Surface 是交互入口，Harness 管工具循环，Provider/Router 管模型请求去向，Model/Runtime 执行推理。换 provider 不会自动改变仓库权限。Sandbox 限制文件和网络等访问，Approval 决定遇到某类动作是否需要人确认；项目规则则提供文本约束，三者不能混同。

Claude 的 allow/ask/deny、Codex 权限配置、Copilot 云端环境、Pi 的容器化方式各有不同实现。共同检查是：可读目录、可写目录、可执行命令、网络、凭证和结果交付。云端编码 Agent 还要考虑代码上传与依赖获取；本地客户端也可能连接云模型。

OpenRouter 选择供应商与模型时，要核对实际路由、数据处理与工具调用兼容性。Ollama 的本地模型可以用于低成本实验，但工具结构输出是否稳定要实测。不要一次换模型、框架和权限，再把收益归因于其中一个。

## 单元四：从单文件走向团队

代码审查列具体触发条件、位置、影响和修复方向，不把个人风格喜好包装成 bug。批量改动先挑一个文件试点，建立检查，再分批推进。长期任务写进度、版本和下一项验收，避免新会话根据过时记忆继续。

CLI/IDE 工具、代码搜索与仓库打包、远程执行、评测平台服务不同需求。第三方 Skills 或 prompt 库先读实际步骤与权限，再在 demo 正反例验证；名称流行不代表适合当前任务。

## 课末提交与验收

```bash
# 运行 courses/branch-developer/examples/check_work.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/branch-developer/examples/check_work.py /tmp/developer-work.json
```

必过：范围只有目标文件；检查器没被改弱；实际 diff 与报告一致；测试状态真实；撤回不影响他人改动。空列表迁移题参考为 `return xs[0] if xs else None`，必须用空列表与非空列表验证，并说明接口允许返回 None。两天后只凭报告复现，一周后换一个有复现的 bug。
