# 给伴读项目准备独立的 Python 环境

本单元预计 **35—50 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《先留下问题，后面才能判断有没有进步》](0010-baseline.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 先确认在哪台机器、哪个目录操作

整套课程以一台新准备的开发电脑为起点。命令使用 macOS 的终端；你的 M1 Mac 可以作为这台电脑，也可以将本地模型部署在它上面、以后再学习远程连接。本阶段先让客户端和模型位于同一台机器，避免同时处理局域网配置。我们不假设它已经装好任何工具。

沿用导学创建的 `classics-reader`。下面假设它放在主目录；如果你选了别处，只改第一条 cd。macOS 和 Linux 的 shell 可以使用本课命令；Windows 使用 Linux 开发环境，原生 PowerShell 语法不在本版范围内。

```bash
# 进入你自己创建的项目；后面所有相对路径都从这里开始。
cd "$HOME/classics-reader"
# 核对当前位置，预期最后一段为 classics-reader。
pwd
# 此时应只有项目卡、题单和 data 输入目录，还没有程序文件。
ls
```

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
# 在写依赖文件前先启用刚创建的环境；后续安装就进入本项目。
source .venv/bin/activate
```


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：亲手写第一份依赖清单

虚拟环境隔离项目，依赖清单记录本项目需要什么。先不安装模型、网页或向量库。

**写在哪里：**项目根目录下的 `requirements.txt`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**requirements.txt 是普通文本，不是 Python 程序。

```text
# 先只安装读取 Word 所需的库；后续章节遇到新功能时再加依赖。
python-docx==1.2.0
```

**写完后应当怎样：**保存后文件只有注释和一个库名；执行安装命令后可以导入 docx。

```bash
# 按刚亲手保存的清单安装本节所需依赖；只安装库，不会自动运行项目。
python -m pip install -r requirements.txt
```

### 第 2 步：把练习数据与凭据留在电脑上

自己的阅读资料、模型密钥和生成结果不应该随代码提交；这是项目起步就能处理的边界。

**写在哪里：**项目根目录下的 `.gitignore`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```text
.venv/
__pycache__/
*.pyc
.env
.env.*
data/
```

**写完后应当怎样：**Git 只跟踪你之后创建的程序；忽略规则不能删除已经提交过的历史。

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

**重新打开终端，正确恢复顺序是什么？** 进入 `classics-reader/` → 启用 `.venv` → 检查 Python 版本和 `sys.executable` → 导入 `Document`。包已经装好时，不用重建环境。

**通过证据：**版本为 Python 3.12.x；解释器路径包含当前项目的 `.venv`；导入检查输出“DOCX 读取库可用”。路径中的用户名和磁盘位置可以不同。若出现 `No module named docx`，先核对解释器，再在同一环境安装依赖。

</details>

## 资料依据

[Hello-Agents 环境配置](https://github.com/datawhalechina/hello-agents/blob/main/Extra-Chapter/Extra07-%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE.md)介绍独立环境与依赖管理；[Stage 0](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/00-foundations.zh-Hans.md)提供 Python 和终端前置。本项目将它们用于 DOCX 读取任务。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from docx import Document
print("读取库可以使用")
PY
```

**预期：**打印“读取库可以使用”，还没有读取讲稿。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
