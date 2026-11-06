# CLI-9 到 CLI-12：完整交付样例

## CLI-9：原题 filesystem server 路径

第五课的自写只读 server 能练协议与边界；原题还明确给了官方 filesystem 包。两条路径的工具不同：官方包也含写入工具，目录限制不等于只读权限。

只在新 demo 内执行，安装阶段需要网络与 Node.js。先用 `node --version`、`npx --version` 确认存在；只学习原理时不用安装。

```bash
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
COURSE_A3_DEMO=$(mktemp -d /tmp/course-a3-mcp.XXXXXX)
# 创建本例需要的目录。
mkdir "$COURSE_A3_DEMO/allowed"
# 执行本行指定的工具与参数，完成当前小节对应操作。
printf 'hello from A3\n' > "$COURSE_A3_DEMO/allowed/hello.txt"
# 执行本行指定的工具与参数，完成当前小节对应操作。
printf 'outside demo marker\n' > "$COURSE_A3_DEMO/outside.txt"
# 切换到 $COURSE_A3_DEMO，让后面的相对路径从这里开始计算；已在该目录时可跳过。
cd "$COURSE_A3_DEMO"
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude mcp add --transport stdio --scope local course-a3-files -- npx -y @modelcontextprotocol/server-filesystem "$COURSE_A3_DEMO/allowed"
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude mcp get course-a3-files
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude
```

在这个会话明确输入：“只使用 course-a3-files 的列目录和读取工具。先运行 list_allowed_directories 并展示实际范围；仅当范围恰好为演示 allowed 目录才继续。读取 allowed/hello.txt，再请求读取同级 outside.txt。禁止使用 Bash 或宿主 Read 绕过 server；禁止写入。”

参考结果：hello.txt 返回 hello from A3；outside.txt 被这个 server 拒绝，日志能辨认实际工具。如果调用失败后改用宿主 Read 成功，越界测试失败。若 host 支持 Roots，server 可能用客户端给出的目录替换启动参数；所以一定检查实际 allowed directories，看到范围扩大立即停止并修正连接，不能只看命令行参数就判断受限。[官方 filesystem 说明](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)用于溯源，操作步骤已在本页。

退出会话后在同一 demo 目录移除并核对：

```bash
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude mcp remove --scope local course-a3-files
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude mcp list
```

再开新会话确认该工具不再可用。先记录包的实际安装版本和宿主版本；课程未自动注册你的 MCP 配置。连接失败按 Node/包下载→进程→协议版本→实际目录→调用参数顺序检查。

## CLI-10：PR 输入与可信 Skill 必须一起对应

本课完整 [CI 配置](03-workshop.md) 调用 A2 的 review-changes Skill，它审查真实 base/head diff。先把课程所需目录和该 Skill 放到 demo 仓库基线分支；否则 action 找不到 Skill，不能称为完整审查。

测试 PR 的完整参考输入可用 A2 broken 样本，仅修改 README 的运行命令并新增失效链接。预期产物指出两处缺陷；另开 fixed 样本 PR，期待 PASS 加审查范围和未运行项。artifact 存在、内容针对实际差异、基线/PR 文件没有被 action 修改，三项同时满足才通过。脚本仅保存在项目里不算远端跑过。

## CLI-11：未知和未运行字段

下面这份参考收据保持未知；你完成一次真实任务后才填测量。不要把模拟响应补成正式 provider 的 token。

```json
{
  "task": "只读审查 broken 样本 diff",
  "skill_version": "course-review 1.0.0",
  "provider": null,
  "model": null,
  "input_tokens": null,
  "output_tokens": null,
  "seconds": null,
  "cost": null,
  "result": "not_run",
  "artifact": null,
  "stop_rule": "CI job timeout-minutes=10；concurrency 取消同 PR 旧运行"
}
```

发生失败也记录原始分类和产物位置。只在输入输出单价与 usage 明确且口径一致时用本课公式计算；缓存读写、工具与运行环境可能另计。题目要求“有收据”，不是要求一定花钱；没有实际运行就维持 not_run。

## CLI-12：可安装、可撤销的同名 Skill

这是完整 Plugin 清单与安装说明。它复用 A2 review-changes 原文，避免团队安装包和课堂 Skill 各说一套。

{{code:../examples/team-plugin/.claude-plugin/plugin.json}}

{{code:../examples/team-plugin/skills/review-changes/SKILL.md}}

{{code:../examples/team-plugin/README.md}}

从 ai-learn 根目录先运行 `claude plugin validate courses/A3-cli-production/examples/team-plugin` 检查目录。用 A2 diff_lab.py 建一个新的 broken 副本，把输出目录作为第二个 demo，进入后运行 `claude --plugin-dir /Users/owen/Documents/ai-learn/courses/A3-cli-production/examples/team-plugin`。输入 `/course-review:review-changes`，保存答案和前后 status。

完整验收：发现两处缺陷；前后 status 一致；fixed 对照没有误报；退出后不带参数启动，Skill 不再加载。Plugin validate 通过只验证包结构，不能替代这四项宿主测试。其他 CLI 安装时只复制 Skill 到其项目目录，并记录实际版本与触发方式。
