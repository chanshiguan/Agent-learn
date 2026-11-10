# 给伴读项目准备独立的 Python 环境

本单元预计 **20—30 分钟**，首次下载 Python 的等待时间另计。第 1 章共 **75—110 分钟**。你已经会编程，这里只补运行当前脚本需要的 Python 工具。

## 先确认在哪台机器、哪个目录操作

整套课程以一台新准备的开发电脑为起点。命令使用 macOS 的终端；你的 M1 Mac 可以作为这台电脑，也可以将本地模型部署在它上面、以后再学习远程连接。本阶段先让客户端和模型位于同一台机器，避免同时处理局域网配置。我们不假设它已经装好任何工具。

将课程包解压到主目录，文件夹命名为 `classics-companion-course`。若你选择其他位置，调整下面这条 `cd`，之后仍使用相同相对路径。Windows 学员可以在 Linux 开发环境中沿用文件和 Python 代码，但本版没有提供原生 PowerShell 命令；不要把两种终端语法混用。

```bash
# 进入本课程的练习目录，让后续相对路径指向同一批文件；成功时通常没有输出。
cd "$HOME/classics-companion-course/courses/00-classics-reading-foundations/examples"
# 确认终端当前目录；预期路径末尾是 examples，避免在其他目录运行练习。
pwd
# 列出当前目录的文件；应能找到 read_docx.py 和 requirements.txt。
ls
```

预期能看到 `read_docx.py`、`requirements.txt`、`Dockerfile` 等文件。`cd` 改变当前目录；相对路径 `data/input` 会从这个目录开始找。不要把代码粘进终端后，期待终端自动为你创建 `.py` 文件。

## 选择 Python 3.12

这套新课程以 Python 3.12 为练习环境，与后面容器中的版本一致。已有其他项目的虚拟环境继续保留。

```bash
# 确认 Python 3.12 已可调用；预期显示 Python 3.12.x。
python3.12 --version
```

若提示找不到命令，先安装 Python 3.12。新 Mac 可以从 Python 的 macOS 安装入口选择 3.12 系列安装包，按安装向导完成后重开终端；再次运行 `python3.12 --version`。已有 Homebrew 时，也可以运行 `brew install python@3.12`。这些安装方式选一种，不要求你先掌握包管理器。

如果你已经使用 `uv`，还有下面这条可选路径。它不是课程的前置要求：

```bash
# 通过已有的 uv 准备 Python 3.12；下载完成后才能创建指定版本的环境。
uv python install 3.12
# 用 Python 3.12 建立项目专用环境，并放入 pip；这样后面的 python -m pip 才能运行。
uv venv --python 3.12 --seed .venv
```

如果 `python3.12` 已经能运行，使用 Python 自带方式即可，不必两种都做：

```bash
# 使用 Python 自带的 venv 创建项目独立环境；预期生成 .venv，不会修改其他项目。
python3.12 -m venv .venv
```

[`venv` 虚拟环境](../courses/00-classics-reading-foundations/knowledge/python-environments.html)创建项目自己的包目录；`.venv` 是目录名。它不会把这台电脑所有 Python 都切换成 3.12。创建完后，在当前终端启用它：

```bash
# 让当前终端优先使用项目环境的 Python 和依赖；随后检查解释器路径。
source .venv/bin/activate
# 确认启用环境后的 Python 版本；本课程预期为 3.12.x。
python --version
# 按清单将 DOCX 读取依赖装入当前 Python 环境；成功后可导入 docx，不会下载模型。
python -m pip install -r requirements.txt
# 同时核对解释器位置和读取库；预期路径在 .venv 中，并显示“DOCX 读取库可用”。
python -c "import sys; from docx import Document; print(sys.executable); print('DOCX 读取库可用')"
```

预期第一条版本输出为 Python 3.12，最后的解释器路径位于本练习目录的 `.venv` 中。`python -m pip` 使用当前 Python 安装包，减少“包装到另一个 Python 里”的混乱。安装名是 `python-docx`，导入名是 `docx`；不要另装名为 `docx` 的旧包。

## 重新打开终端时怎么办

虚拟环境只对当前终端生效。下次继续时，先 `cd` 到练习目录，再运行 `source .venv/bin/activate`。不用每次重建环境或重装依赖。运行 `deactivate` 可以退出，但不会删除目录。

<details><summary>遇到 No module named docx</summary>

先运行 `python -c "import sys; print(sys.executable)"`。如果路径不在本项目的 `.venv`，重新启用环境；如果在，再运行 `python -m pip install -r requirements.txt`。先核对解释器，能避免在错误环境里反复安装。

</details>

**动手验收：**关闭终端，重新打开，再独立完成进入目录、启用环境和导入检查。把解释器路径记到项目卡。能够恢复工作环境，比只看到一次安装成功更有用。

## 本单元验收与参考答案

先完成上面的操作，再用自己的话回答。下面是核对思路和结果的参考，不要求背原句。

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**`python -m pip install -r requirements.txt` 在做什么？** 用当前 Python 的 pip，读取依赖清单并安装其中列出的包。本课安装的是 DOCX 读取库；它不会读取讲稿或安装模型。

**重新打开终端，正确恢复顺序是什么？** 进入 `examples/` → 启用 `.venv` → 检查 Python 版本和 `sys.executable` → 导入 `Document`。包已经装好时，不用重建环境。

**通过证据：**版本为 Python 3.12.x；解释器路径包含当前项目的 `.venv`；导入检查输出“DOCX 读取库可用”。路径中的用户名和磁盘位置可以不同。若出现 `No module named docx`，先核对解释器，再在同一环境安装依赖。

</details>

## 资料依据

[Hello-Agents 环境配置](https://github.com/datawhalechina/hello-agents/blob/main/Extra-Chapter/Extra07-%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE.md)介绍独立环境与依赖管理；[Stage 0](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/00-foundations.zh-Hans.md)提供 Python 和终端前置。本项目将它们用于 DOCX 读取任务。
