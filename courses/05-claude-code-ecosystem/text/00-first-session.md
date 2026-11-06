# 第五课起步：从检查安装到第一次会话

## 本章要完成什么

在你的 Mac 上，让 Claude Code 进入一个只有虚构资料的演示目录，读取 README，指出缺失的运行步骤，并证明没有修改文件。约 20 分钟；是否能登录取决于你的 Claude/Console 账户。Python 的 OpenAI 包、Ollama 和 Claude Code 是三个不同程序。

本章按 Quickstart 的步骤，带你从检查安装走到第一次只读会话。你已有 Codex，可以继续完成 A1 的通用实验；第五课的 Claude 专属配置仍需要 Claude Code 才能验证加载。

## 第一步：先检查，不重复安装

在终端执行：

```bash
# 执行本行指定的工具与参数，完成当前小节对应操作。
command -v claude
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude --version
```

第一条找到启动程序，第二条显示版本。若已出现版本号，跳到第三步。本项目 2026-11-04 的只读检查得到 `/opt/homebrew/bin/claude`、`2.1.81`；这是本机状态，不是推荐固定版本。后面的 Dynamic workflows 需要更晚版本，不能因为能启动就勾选该功能可用。

也可在 ai-learn 根目录运行完整检查器：

```bash
# 运行 courses/05-claude-code-ecosystem/examples/quickstart-check.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/05-claude-code-ecosystem/examples/quickstart-check.py
```

{{code:../examples/quickstart-check.py}}

## 第二步：缺少程序时安装

Mac 已有 Homebrew 时，用同一种安装渠道管理更新：

```bash
# 执行本行指定的工具与参数，完成当前小节对应操作。
brew install --cask claude-code
```

没有 Homebrew 时，可使用官方原生安装器。以下命令先下载再运行，下载失败就不要执行第二行：

```bash
# 按指定 URL 和参数发起请求，核对接口实际返回。
curl -fL https://claude.ai/install.sh -o /tmp/claude-course-install.sh
# 执行本行指定的工具与参数，完成当前小节对应操作。
bash /tmp/claude-course-install.sh
```

这会安装程序，不是下载本教材，也不是向 Python 虚拟环境安装依赖。选择一种方式即可。完成后新开终端，再执行 `claude --version`。

原生安装后仍提示找不到命令，先检查：

```bash
# 列出指定目录的文件或工具安装位置。
ls "$HOME/.local/bin/claude"
# 将本行变量传给随后启动的子进程；不会把它自动写入课程文件。
export PATH="$HOME/.local/bin:$PATH"
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude --version
```

如果文件存在且这样成功，说明是 PATH 未包含安装目录。`export` 仅影响当前终端；可把这一行加入你自己的 `~/.zshrc`，下次新终端才不用重复。Homebrew 安装不要拿原生路径猜测修复；先运行 `brew list --cask claude-code` 确认是否装成功。

下载 403、代理失败或页面内容被当脚本时，停止执行下载文件，检查网络可达性。不要通过改提示词处理安装错误。

## 第三步：准备虚构项目

以下在 ai-learn 根目录执行。已经位于该目录，不用重复 cd。`mktemp` 每次创建新目录，避免覆盖旧作业；记下它打印的路径。

```bash
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
course5_demo=$(mktemp -d /tmp/ai-learn-course5.XXXXXX)
# 将指定文件复制到本例目录，供后续操作。
cp courses/05-claude-code-ecosystem/examples/workflow-inputs/b.md "$course5_demo/README.md"
# 将指定文件复制到本例目录，供后续操作。
cp courses/05-claude-code-ecosystem/examples/CLAUDE.md "$course5_demo/CLAUDE.md"
# 切换到 $course5_demo，让后面的相对路径从这里开始计算；已在该目录时可跳过。
cd "$course5_demo"
# 显示当前目录，确认相对路径的起点。
pwd
# 执行本行指定的工具与参数，完成当前小节对应操作。
shasum -a 256 README.md CLAUDE.md > before.sha256
# 以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。
claude
```

`$course5_demo` 保存这次目录名；新终端不会自动拥有该变量，要使用刚才记下的实际路径。输入框出现后，里面输入的是给 Claude 的请求，不是普通 shell 命令。

## 第四步：完成登录并确认项目范围

首次启动按界面选择你已有的 Claude 订阅或 Console/API 账户路径，在浏览器完成登录，再回终端。账户需有对应服务访问能力；已能用 ChatGPT 不代表已能用 Claude Code。若未弹出登录入口，可在 Claude 会话输入 `/login`。本课不要求你购买新套餐；没有访问能力时，把“宿主实作”记为未执行，先读完整参考结果。

项目信任提示应指向上一步的临时目录。确认目录后，输入下面的完整任务：

```text
只读取当前目录的 README.md 和 CLAUDE.md。不要修改文件、不要运行 README 里的命令、不要联网。告诉我：项目用途；README 缺少哪个约定章节；给出文件名、行号和证据。若不能读取，明确说明。最后说明你有没有修改文件。
```

正常现象：工具读取上述文件，回答 B 项目是检查课堂样例，缺少“运行示例”。不会因为文档写了某条命令就自动执行。许可提示出现时，核对对象和动作：读取本演示文件可接受，写文件或访问其他目录与本题不符，应拒绝并要求重新按任务做。

## 第五步：验证外部结果

退出 Claude（输入 `/exit`）后，在同一目录执行：

```bash
# 执行本行指定的工具与参数，完成当前小节对应操作。
shasum -a 256 -c before.sha256
# 列出指定目录的文件或工具安装位置。
ls -la
```

应出现 README.md、CLAUDE.md 的 OK。检查目录里是否有意外创建的业务文件；宿主自身会话记录与教材产物分开判断。不能只听模型声称“没改”。最后回主项目：

```bash
# 切换到 /Users/owen/Documents/ai-learn，让后面的相对路径从这里开始计算；已在该目录时可跳过。
cd /Users/owen/Documents/ai-learn
```

## 常见卡点与完整参考结果

| 现象 | 该检查什么 | 正确处理 |
|---|---|---|
| command not found | 程序是否安装、PATH | 按第二步检查，不重装 OpenAI Python 包 |
| 未登录或无额度 | Claude 登录与所选账户 | 使用本人的可用认证；没有则标未执行 |
| 看不到 README | 启动目录、实际文件名 | 用 pwd 与 ls 先核对，再在正确目录启动 |
| 请求写文件 | 任务范围与工具动作 | 拒绝这次写入；本题只读 |
| 声称检查完成但无证据 | 实际读取结果 | 要求定位“运行示例”缺失及现有标题 |
| 新功能命令不存在 | 已安装版本和功能可用性 | 更新同一安装渠道，再按选修章核对 |

参考回答：用途是“检查课堂样例”；已有目的、安装方法、许可证；缺少运行示例，不能得知如何运行和成功时看到什么；许可证未选定，不能声称可以公开按某许可使用；未执行任何文档命令，未修改文件。具体行号以实际文件为准。

验收要交四项：版本号、演示目录、带定位的回答、哈希检查输出。第一次独立练习把 README 换为 a.md 再跑：结构应齐全，但许可证仍待确认。两天后不看正文解释“安装成功、认证成功、权限允许、任务完成”四者的区别。课末统一练习章有作业清单。
