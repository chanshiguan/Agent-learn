# 选修实作：Plugin、Dynamic workflows 与 SDK 托管

## 先选一个具体目标

本章分别完成三件事：把 README Skill 打成可加载插件；用脚本检查两份文档并处理工作者失败；让应用托管一个有超时和收据的 SDK 任务。每个单元可独立做。Plugin 包装扩展，workflow 保存编排，SDK 让程序控制运行，三者不是替代关系。

第五课首次会话完成后再做宿主实作。当前机器的 CLI 2.1.81 可以校验插件，但早于 workflow-authoring 所需的 2.1.248。不要在旧版中反复输入不存在的命令。按原安装渠道更新：Homebrew 使用 `brew upgrade --cask claude-code`；原生安装使用 `claude update`，再新开终端检查版本。此教材没有替你升级全局程序。

## 单元一：完整 Plugin

完整目录如下；只有 manifest 放进 `.claude-plugin`，Skill 与它平级：

```text
course-plugin/
  .claude-plugin/plugin.json
  skills/readme-check/SKILL.md
```

{{code:../examples/course-plugin/.claude-plugin/plugin.json}}

{{code:../examples/course-plugin/skills/readme-check/SKILL.md}}

在项目根先校验 manifest，然后用临时项目加载：

```bash
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude plugin validate courses/05-claude-code-ecosystem/examples/course-plugin
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
course5_plugin_demo=$(mktemp -d /tmp/course5-plugin.XXXXXX)
# 将指定文件复制到本例目录，供后续操作。
cp courses/05-claude-code-ecosystem/examples/workflow-inputs/b.md "$course5_plugin_demo/README.md"
# 切换到 $course5_plugin_demo，让后面的相对路径从这里开始计算；已在该目录时可跳过。
cd "$course5_plugin_demo"
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude --plugin-dir /Users/owen/Documents/ai-learn/courses/05-claude-code-ecosystem/examples/course-plugin
```

在 Claude 输入 `/course-readme:readme-check`。应发现缺少运行示例，许可证待确认。`course-readme` 是 plugin name，`readme-check` 是 skill name，所以命令带命名空间。manifest 校验成功只证明包结构可接受，真正加载及内容输出要另外看。

退出后不带 `--plugin-dir` 重新启动，临时插件命令不应继续存在；若仍存在，检查是否曾从其他范围安装过同名插件。这样完成了加载和撤销，不需要发布市场。移交给同伴时复制整个目录，并保留版本号；修改 Skill 后提高版本，再在干净目录重复正反例。

失败参考：把 skills 错放进 `.claude-plugin/skills`，manifest 可能仍合法，但组件不会正确加载。修复是恢复上面的完整目录。只有 manifest 正确不能作为全部通过。

## 单元二：完整 Dynamic workflow

任务固定为两份虚构 README。a 有四节，b 缺运行示例。工作者输出结构化结果，取消或不可恢复错误可返回 null；必须保留失败槽位，不能过滤后声称所有文档已查。

{{code:../examples/workflow-inputs/a.md}}

{{code:../examples/workflow-inputs/b.md}}

{{code:../examples/audit-readmes.js}}

`pipeline` 针对列表中的每项调用工作者；每个 agent 得到完整文件定位和输出 schema。此例至多安排两个工作者。结果只代表结构检查，许可证正文是否允许发布仍要人工判断。脚本中的 return 由宿主包装执行，不是给普通 `node audit-readmes.js` 使用的模块。

先做离线契约练习，只需 Node.js 18+；本机已有 Node 时跳过安装。以下程序提供所需的 agent/pipeline 替身，读取同一输入并执行同一个脚本正文：

```bash
# 运行指定的 JavaScript 离线演示，观察实际输出。
node courses/05-claude-code-ecosystem/examples/workflow_contract.mjs
# 运行指定的 JavaScript 离线演示，观察实际输出。
node courses/05-claude-code-ecosystem/examples/workflow_contract.mjs cancel
```

{{code:../examples/workflow_contract.mjs}}

第一条应返回 NEEDS_REVIEW，a.missing 为空，b.missing 为“运行示例”；第二条应返回 INCOMPLETE，b 的 result 为 null。这个测试验证脚本控制和失败保留，不证明 Claude runtime 或模型已经运行。

真实宿主操作：回到项目根，创建独立演示目录并复制文件：

```bash
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
course5_workflow_demo=$(mktemp -d /tmp/course5-workflow.XXXXXX)
# 创建本例需要的目录。
mkdir -p "$course5_workflow_demo/.claude/workflows" "$course5_workflow_demo/inputs"
# 将指定文件复制到本例目录，供后续操作。
cp courses/05-claude-code-ecosystem/examples/audit-readmes.js "$course5_workflow_demo/.claude/workflows/audit-readmes.js"
# 将指定文件复制到本例目录，供后续操作。
cp courses/05-claude-code-ecosystem/examples/workflow-inputs/*.md "$course5_workflow_demo/inputs/"
# 切换到 $course5_workflow_demo，让后面的相对路径从这里开始计算；已在该目录时可跳过。
cd "$course5_workflow_demo"
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude
```

在支持该功能的付费/授权账户中按顺序输入 `/workflow-authoring`、`/reload-skills`、`/audit-readmes`。若 Pro 的功能关闭，在 `/config` 的 Dynamic workflows 项开启。看清任务范围后允许本次运行，用 `/workflows` 查看两个工作者及结果。代码只请求读取两个虚构文件；实际权限仍由宿主执行，不能因为 prompt 写“只读”就当成系统隔离。

运行中可在 `/workflows` 停止，观察已完成与未完成的工作。恢复时根据宿主提示继续；脚本变量不等于任意位置的 Python 栈快照，缓存的工作者结果与重跑规则要核对。修改 b 后重新运行一次完整任务，确认 missing 清空；保留输入版本和前后报告，别把旧缓存当新结果。

通过条件：能够定位脚本、识别两个工作者、保存正常结果与中断结果、解释 INCOMPLETE；读过别人输出不算完成运行。命令不可用时，先检查版本、账户、功能开关及 `.claude/workflows/` 路径。删除演示目录中的脚本并重启后，`/audit-readmes` 不再出现。

## 单元三：SDK 单任务托管

Agent SDK 启动并管理 CLI 子进程。请求、工作目录、会话文件、业务结果各有生命周期。下面采用一个任务一个目录，限制两轮和等待时间，不给模型任何工具；正文由应用作为输入传入。这足以学习消息消费、终止、持久收据和恢复，不需要先搭公网网站。

{{code:../examples/requirements-sdk.txt}}

{{code:../examples/sdk_job.py}}

默认 demo 不需要 SDK 或账户，它只测试终止分类。回到项目根后运行，每次使用新任务目录：

```bash
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
course5_sdk_demo=$(mktemp -d /tmp/course5-sdk.XXXXXX)
# 运行 courses/05-claude-code-ecosystem/examples/sdk_job.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/05-claude-code-ecosystem/examples/sdk_job.py --job-dir "$course5_sdk_demo/ok"
# 运行 courses/05-claude-code-ecosystem/examples/sdk_job.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/05-claude-code-ecosystem/examples/sdk_job.py --job-dir "$course5_sdk_demo/limit" --scenario limit
# 运行 courses/05-claude-code-ecosystem/examples/sdk_job.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/05-claude-code-ecosystem/examples/sdk_job.py --job-dir "$course5_sdk_demo/timeout" --scenario timeout
```

依次应为 NEEDS_REVIEW、FAILED、TIMEOUT；后两条退出码是 1，属于预期失败，不是安装失败。检查各任务的 result.json：失败不得留下一个成功答案，模拟会话不得保存为可恢复的真实 session。

真实 SDK 路径需要 Python 3.11 专用环境。项目的 `courses/.venv-verification` 已有；只有缺少依赖时才运行安装：

```bash
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-verification/bin/python -m pip install -r courses/05-claude-code-ecosystem/examples/requirements-sdk.txt
```

本例使用 Console API 身份，因为任务自己的配置目录没有你的普通 CLI 登录文件。密钥通过终端隐藏输入设置，仅保存在本终端环境，不写入教材或命令历史。Mac zsh 示例：

```bash
# 从终端读取输入；-s 隐藏密钥输入，值只保存在当前 shell 变量中。
read -s 'course5_key?输入本人的 Anthropic API key：'
# 将本行变量传给随后启动的子进程；不会把它自动写入课程文件。
export ANTHROPIC_API_KEY="$course5_key"
# 执行本行指定的工具与参数，完成当前小节对应操作。
unset course5_key
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
course5_live_job=$(mktemp -d /tmp/course5-live.XXXXXX)
# 运行 courses/05-claude-code-ecosystem/examples/sdk_job.py，按本行参数完成当前案例并核对输出；--live 会进入真实服务路径，需先满足本章环境要求。
courses/.venv-verification/bin/python courses/05-claude-code-ecosystem/examples/sdk_job.py --job-dir "$course5_live_job" --live
```

预期 ResultMessage 正常结束、result.json 含真实 session_id、答案指出缺运行说明。NEEDS_REVIEW 表示还须核对内容；max_turns、预算或认证错误都不能算成功。若已有授权账户但不想 API 调用，可完成离线部分，真实运行保留未执行。

续接前，在同一任务目录的 request.txt 写入新的虚构补充：“新增运行说明：python3 app.py，预期输出 hello。现在还缺什么？”再执行：

```bash
# 运行 courses/05-claude-code-ecosystem/examples/sdk_job.py，按本行参数完成当前案例并核对输出；--live 会进入真实服务路径，需先满足本章环境要求。
courses/.venv-verification/bin/python courses/05-claude-code-ecosystem/examples/sdk_job.py --job-dir "$course5_live_job" --live --resume
# 执行本行指定的工具与参数，完成当前小节对应操作。
unset ANTHROPIC_API_KEY
```

恢复需要同一个业务目录、session_id 和 session-store；仅复制结果 JSON 不保证会话可用。预算是单次调用估计上限，不能当作跨任务严格计费配额。错误记录只保存异常类型，以免把服务响应里的凭证写进日志。

## 单元四：容器中的最小托管

有 Docker 时可运行同一个任务程序；本机没有 Docker 则保留未执行。完整 Dockerfile：

{{code:../examples/Dockerfile.sdk}}

项目根执行：

```bash
# 按指定 Dockerfile 构建本地示例镜像。
docker build -f courses/05-claude-code-ecosystem/examples/Dockerfile.sdk -t course5-sdk courses/05-claude-code-ecosystem/examples
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
course5_container_job=$(mktemp -d /tmp/course5-container.XXXXXX)
# 设置本例文件所需的执行权限。
chmod 777 "$course5_container_job"
# 按本行挂载、网络、用户和资源参数运行隔离案例；这些限制由命令实际落实。
docker run --rm --network none --read-only --tmpfs /tmp:rw,size=64m --cap-drop ALL --security-opt no-new-privileges --memory 512m --cpus 1 --pids-limit 128 -v "$course5_container_job:/job" course5-sdk --job-dir /job
```

chmod 只应用于这一份空的虚构临时目录，便于 UID 10001 写收据；真实多租户部署应按所属 UID 配置。demo 应生成 /job/result.json，证明容器路径可写。真实调用需要网络和 API 身份：去掉 `--network none`，增加 `-e ANTHROPIC_API_KEY`，末尾增加 `--live`，在预先设置自己的环境变量后才执行。这个例子未实现出站域名过滤，不能直接当多租户生产模板。

删除临时容器不等于删除挂载的会话目录；任务保留期结束后由操作者删除对应任务数据。多租户扩展还需身份验证、每租户目录/进程、总预算、并发限制、会话授权、密钥注入和日志保留。这个入门案例用于学习单任务托管；完成上述多租户控制后，才能进一步评估是否适合生产部署。

## 本章练习、参考答案与验收

本章的作业并入本课末尾：Plugin 交加载/撤销证据；workflow 交两份输入与两种状态；SDK 交成功、限制、超时三份收据，并注明是否运行 live/容器。

完整参考答案就是上述实际文件。关键判断：a 结构齐全但许可证待确认；b 缺运行示例；取消结果不能丢；SDK 最终消息缺失、超时或限制都不得标完成。若把 working directory 删掉再只留 session_id，不能承诺恢复。迁移练习增加第三份只有标题、无正文的 README，应该列出空节而不是认为齐全。
