# 将只读审查接入团队交付

## 单元一：MCP 连接与撤销

先做第五课 mcp_roundtrip，记录工具清单、合法读取和越界拒绝。CLI 注册需记录 scope=local、确切解释器与 server 路径；完成后 remove，再确认工具不可调用。连接步骤与完整客户端/服务端已在第五课本地实作章，不需要访问外站。

连接成功说明协议可用，不保证服务器可信。服务程序的文件与网络权限独立于工具说明；审核来源、版本与目录后才使用。不要把 server 的只读工具误当宿主全部工具都只读。

## 单元二：真正审查 PR 改动的工作流

下面工作流读取 PR 的 base/head 差异，使用可信基线上的 A2 Skill 调用 Codex Action，产物保存为 artifact。审查对象是该 PR 的实际改动。

{{code:../examples/review-workflow.yml}}

安装步骤：在你控制的 GitHub 演示仓库建 `.github/workflows/lesson-review.yml`，复制完整配置；将 OPENAI_API_KEY 存在该仓库 Actions secrets；先把工作流与 A2 Skill 放进基线分支，再从同仓库新分支提出一个仅改 README 的测试 PR。不要把密钥写入 YAML 或任务文本。云端模型需要对应凭证和额度，与本地 Ollama 是不同路径。

工作流只读 contents，不发 PR 评论。检查 Actions 日志与下载的 lesson-pr-review：必须针对实际改动，含文件/问题/证据，或 PASS 加范围。故意删掉运行说明时应指出问题；无关未改文件不应凭空成为本次缺陷。未运行任何检查时应如实说明。

本教材未向远端安装或触发任务；你可以完整阅读、检查配置，实际集成状态仍单列。主版本 tag 用于教学辨识；正式部署前固定已审查提交并维护更新。失败可能是权限、密钥、模型、Action 或产物路径，先按日志定位，不重复触发收费任务碰运气。

## 单元三：费用、用量和任务收据

{{code:../examples/receipt.py}}

这份最小函数分开 provider、model、token、耗时、费用和结果。unknown 用 null，not_run 不是 pass。正式记录还要包含任务 ID、Skill 版本、输入摘要、产物路径和失败类型，才知道一次运行对应哪份配置。

在项目根运行 `.venv/bin/python courses/A3-cli-production/examples/receipt.py` 输出的是未运行示例，不可计入真实用量统计。缓存读写、模型输入输出和托管运行时间可能有不同计量方式，应读取服务实际 usage 与账单口径，不凭一次耗时猜费用。

## 单元四：团队 Skill 完整交付清单

交付目录至少放 SKILL.md、samples/ 中的正反例、检查程序、README 与版本记录。README 按以下顺序写：解决什么问题；宿主和版本；需要的工具；项目级安装位置；怎样触发；三种样例的期待结果；怎样更新；怎样移除。先在第二个干净 demo 从 README 重做，不靠开发者记忆补步骤。

完整安装演示：使用 [CLI-9–12 完整交付](04-original-delivery.md)的 course-review Plugin，它打包 A2 的 review-changes；让宿主显式加载，在 broken/fixed/baseline 三种 Git diff 样本上验证；退出后不带 `--plugin-dir` 重新启动，确认该插件的 Skill 不再加载。全局安装属于另一个范围，不能因为演示成功就推广到所有项目。

## 课末练习与参考验收

四项原练习分别提交这些结果：CLI-9 是受限连接和撤销证据；CLI-10 是真实 PR diff 的审查产物；CLI-11 是实际收据（未运行字段如实）；CLI-12 是第二个干净目录的安装、测试、卸载记录。

“配置已写好”可以通过配置审查，不能通过远端集成。合理验收分成准备完成、实际执行、独立复现三栏，缺一栏就明确停在那一栏。迁移题：升级 Skill 后让缺运行节样例被误判 PASS，必须发现回归、恢复旧版、记录版本与原因。
