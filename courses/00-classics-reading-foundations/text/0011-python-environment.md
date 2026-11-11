# 统一使用全局 Python 3.12

本单元预计 **35—50 分钟**，包括环境核对、编写依赖清单、安装库与一次排错；软件下载等待另计。

上一节已经保存了五份讲稿，并记录了电脑能否找到 Python。现在为读取讲稿准备工具：主机统一使用全局 Python 3.12，后续各章继续使用它。无需创建或激活项目虚拟环境。

## 先确认在哪台机器、哪个目录操作

本版安装步骤针对你实际练习的 Mac 和默认 zsh 终端，M1 也按同样步骤操作。下面只配置这台学习电脑，不依赖课程编写时使用的机器。应用和模型先放在同一台电脑上，等学到部署再处理网络连接。

打开终端，进入导学创建的项目。下面假设它在主目录；如果你放在别处，第一行使用自己的实际位置。

```bash
# 进入已经创建的项目，后面的相对文件路径都从这里开始。
cd "$HOME/classics-reader"
# 预期路径末尾是 classics-reader，避免把文件写到别处。
pwd
# 核对导学保存的项目卡、题单和 data 文件夹。
ls
```

## 用 Homebrew 准备软件

Homebrew 的命令是 `brew`。本课程用它安装 Python、Docker Desktop 和 Ollama；本节只需要 Python，另外两个学到时再装。

```bash
# 查看 Homebrew 是否已可用；显示版本号就直接继续，不必重装。
brew --version
```

若提示找不到命令，先按 [Homebrew 官方入口](https://brew.sh/)安装。当前官方支持的 macOS 起点为15，安装前在“关于本机”核对系统要求。安装命令如下；已有 brew 的电脑跳过这一段：

```bash
# 下载并运行 Homebrew 官方安装器；阅读它列出的改动，按提示完成初次安装。
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

安装器结束后会给出 **Next steps**，执行其中为你的机器生成的 `brew shellenv` 配置，再运行 `brew --version`。这一步让终端找到 brew；不要略过它直接输入下一条命令。如果中途重开终端，先重新进入项目目录。

## 让全课的 python 都指向 3.12

如果你已经把全局 Python 配好了，先执行本节末的版本检查，通过后直接进入“现在动手写”。尚未配置时按下面两步完成：

```bash
# 安装3.12系列，不使用会随默认版本变化的 brew install python。
brew install python@3.12
# 让当前终端先找到3.12的 python/python3 命令；不会覆盖 macOS 自带文件。
export PATH="$(brew --prefix python@3.12)/libexec/bin:$PATH"
```

`PATH` 是终端查找命令的目录列表，把3.12目录放在最前面，后面的 `python` 就会选中它。为了重开终端仍然生效，用文本编辑器打开 `~/.zshrc`（不存在就新建），把上面的 `export PATH=...` **整行原样**写到末尾并保存；已有相同行时不重复添加。`~` 表示你的用户主目录，这个文件不放在练习项目里。[Homebrew 的3.12说明](https://formulae.brew.sh/formula/python@3.12)给出了这一命令目录。

现在核对实际选择：

```bash
# 预期显示 Python 3.12.x；最后一位补丁版本可以不同。
python --version
# 查看解释器路径，并确认没有处于项目虚拟环境；预期版本为(3, 12)，最后一项为True。
python -c "import sys; print(sys.executable); print(sys.version_info[:2]); print(sys.prefix == sys.base_prefix)"
# 确认 pip 属于同一个解释器；输出末尾应标明 python 3.12。
python -m pip --version
```

若版本不对，先用 `type -a python` 查看是否有旧别名或环境管理工具接管了命令，修正终端配置后再检查。若最后一项是 `False`，当前终端仍在旧虚拟环境中，重新打开不自动激活它的终端再继续。不要在版本没对齐时安装依赖。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：亲手写第一份依赖清单

全课沿用同一个全局 Python 3.12。依赖清单记录项目需要的库，学到哪项功能再安装对应依赖。

**写在哪里：**项目根目录下的 `requirements.txt`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**requirements.txt 是普通文本，不是 Python 程序。

```text
# 先只安装读取 Word 所需的库；后续章节遇到新功能时再加依赖。
python-docx==1.2.0
```

**写完后应当怎样：**保存后文件只有注释和一个库名；执行安装命令后可以导入 docx。

```bash
# 用当前全局3.12安装读取库到当前账号的包目录；两个参数的作用见下文，不会自动运行项目。
python -m pip install --user --break-system-packages -r requirements.txt
```

### 第 2 步：把练习数据与凭据留在电脑上

自己的阅读资料、模型密钥和生成结果不应该随代码提交；这是项目起步就能处理的边界。

**写在哪里：**项目根目录下的 `.gitignore`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**每一行是一种 Git 忽略规则。末尾的 / 表示目录，* 表示任意匹配文字；这些规则只影响 Git 是否纳入文件，不会阻止 Python 读取资料。

```text
__pycache__/
*.pyc
.env
.env.*
data/
```

**写完后应当怎样：**Git 只跟踪你之后创建的程序；忽略规则不能删除已经提交过的历史。

## 为什么安装命令多了两个参数

`brew` 管理解释器和应用；程序里导入的 Python 库仍由同一解释器的 pip 按清单安装。比如本节用 `python-docx` 读取 Word，不能用一个不对应本课程版本的 Brew 软件包来替换它。

Homebrew 的 Python 会标记为外部管理，直接 pip 安装可能出现 `externally-managed-environment`。按你选定的“全局3.12、不建虚拟环境”方式，本课主机安装命令统一带两个参数：

- `--user`：把库装入当前账号的 Python 用户包目录，供这一账号的全局3.12使用。
- `--break-system-packages`：明确允许**这次命令**越过外部管理限制；它不创建新环境，也不需要永久改 pip 配置。

这些库会被同一账号的其他3.12程序共享，因此本课继续用固定依赖清单。不要用 `sudo pip` 或删掉管理标记来解决报错。安装机制见 [Homebrew说明](https://docs.brew.sh/Language-Runtimes-and-Packages)与 [pip参数文档](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-break-system-packages)。

```bash
# 查看库实际装到哪里；这是全局3.12的用户包目录，不是新的解释器。
python -m site --user-site
# 真正导入读取库；成功后显示提示与库的位置，下一节就用它读讲稿。
python -c "import docx; print('读取库可以使用'); print(docx.__file__)"
```

## 重新打开终端时怎么办

下次继续时，进入 `classics-reader`，核对 `python --version` 为3.12即可。已写入 `~/.zshrc` 的路径设置会随新终端生效，无需重装库或执行激活命令。模型地址等变量到第4章再设置，它们与 Python 解释器的选择是两回事。

关闭终端，重新打开，进入项目后重新执行版本、pip与docx导入检查。把解释器路径、用户包目录和检查结果记入 `project-card.md`。以后出现“库明明装过却找不到”，先对照这两个位置，再决定是否重新安装。

<details><summary>遇到 No module named docx</summary>

先核对 `python --version`、`python -m pip --version` 是否都对应3.12，再用 `python -m pip show python-docx` 查看是否已装。确实缺少时，在项目根目录重跑上面带 `--user --break-system-packages` 的清单安装命令；不要另装一套 Python。

</details>

## 本单元验收与参考答案

<details class="answer-key"><summary>先回答，再展开核对</summary>

**为什么用 python -m pip？** 让当前选定的 Python 运行 pip，避免单独的 pip 命令碰巧对应另一版本。

**--user 是另一套环境吗？** 不是。解释器仍是同一个全局3.12，只指定第三方库存放在当前账号的包目录，不创建项目虚拟环境。

**为什么需要 --break-system-packages？** Homebrew Python 的外部管理标记默认会阻止此类安装。本课选择全局解释器，用该参数允许本次用户目录安装；它不负责选择Python版本。

**通过证据：**新终端中版本仍为3.12；`sys.prefix == sys.base_prefix` 为True；pip显示python3.12；docx可以导入，并已记录实际路径。下一节继续用同一个解释器写读取程序。

</details>

## 资料依据

[Stage 0](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/00-foundations.zh-Hans.md)与[Hello-Agents环境配置](https://github.com/datawhalechina/hello-agents/blob/main/Extra-Chapter/Extra07-%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE.md)提供终端与依赖管理背景。本课程按你的选择使用全局3.12；上游的虚拟环境步骤无需照做。关于解释器、包目录和容器的区别，可选读[Python、pip与统一环境](../courses/00-classics-reading-foundations/knowledge/python-environments.html)。

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
