# Python、pip 与统一环境

主线使用一个全局Python3.12。遇到“库装过了却导入失败”，先核对执行程序的Python和安装库时使用的Python是否一致。

## 四件事分别负责什么

| 工具或位置 | 本课中的作用 |
|---|---|
| Homebrew | 安装Python3.12、Docker Desktop、Ollama等软件 |
| Python解释器 | 执行你写的程序；各章在主机沿用同一个3.12 |
| pip | 按requirements清单给这个解释器安装第三方库 |
| 用户包目录 | 当前账号的3.12共享库位置；换项目目录不会换一套解释器 |

Homebrew不管理pip安装的项目库；`brew upgrade`不会代替依赖清单管理。统一使用`python -m pip`，能明确由当前Python执行安装。参见[Homebrew对语言运行时和包的说明](https://docs.brew.sh/Language-Runtimes-and-Packages)。

## 把安装命令拆开看

主机命令是 `python -m pip install --user --break-system-packages -r requirements.txt`。

`-m pip` 选择当前解释器的pip，`-r` 读取清单，`--user` 指定当前账号的包目录。Homebrew的外部管理标记会限制直接安装；`--break-system-packages` 明确允许本次操作越过该限制。参数定义见[pip文档](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-break-system-packages)。

这条命令不会创建Python环境、读取Word或启动模型。当前账号的其他3.12程序也会使用这些库，因此修改依赖版本后，应重新检查课程程序。课程保留固定版本和发布清单，用于记录实际运行条件。

## Docker为什么仍有自己的Python

主机运行的是macOS软件。Docker本课使用的`python:3.12-slim`包含Linux中的Python3.12及精简系统文件，不能把Mac的安装目录直接拿进去执行。主机与容器运行同一份业务代码，按同一份requirements清单安装适合各自系统的包。

容器里写 `RUN python -m pip install -r requirements.txt`，是在构建镜像时安装；它不使用主机的Homebrew，也不照搬主机用户目录的两个参数。后续Dockerfile和Compose会把容器内的准备步骤固定下来，无需你再手工维护另一份项目代码。

## 测试目录和虚拟环境是一回事吗

不是。课堂测试有时把数据放入临时目录，或让恢复副本使用另一个端口。这些练习仍调用同一个Python，只是把试验数据与正在阅读的记录分开，防止覆盖。

虚拟环境是按项目隔离Python依赖的另一种做法，本课按你的选择不使用它。上游资料若出现venv、uv或Conda安装步骤，理解其目的即可，不必跟着切换路线。

## 可以继续读什么

- [Homebrew的python@3.12条目](https://formulae.brew.sh/formula/python@3.12)：核对全局命令所在位置。
- [Docker官方Python镜像](https://hub.docker.com/_/python)：了解3.12与slim标签。
- [Hello-Agents环境配置](https://github.com/datawhalechina/hello-agents/blob/main/Extra-Chapter/Extra07-%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE.md)：选读依赖管理背景；实际安装沿用本课的全局路线。

读到能解释“谁运行程序、包安装给谁、容器为何另装库”，即可返回主线。
