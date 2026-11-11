# 先在容器里运行一行 Python

本单元预计 **20—30 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《保存结果，并证明没有读错资料》](0013-save-json.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 这次为什么用 Docker

第一章能运行，依赖于你选的 Python 和安装的读取库。把脚本发到另一台机器，对方未必有同样的环境。Docker 镜像可以包含一套运行所需的文件；从镜像创建的容器，才是执行程序的实例。

可以先记住这三个关系：Dockerfile 是构建说明，镜像是构建出的环境，容器是用这个环境运行程序的一次实例。一个镜像可以创建多个容器。容器也有自己的文件位置，宿主机上的讲稿不会自动出现在里面。

## 用 Brew 安装 Docker Desktop

沿用第1章准备的 Homebrew。已有 Docker 时先运行 `docker --version` 和 `docker info`，两项都成功就跳过安装；只显示版本号还不能证明后台引擎已运行。

```bash
# 安装 Docker Desktop，包含客户端与 Mac 上运行容器所需的后台引擎。
brew install --cask docker-desktop
# 打开后台引擎；按首次启动提示完成设置，等待它就绪。
open -a Docker
```

`--cask` 表示安装桌面应用。这里选择完整的 Docker Desktop；只安装名为 docker 的命令行工具，不一定已经具备可运行的引擎。包名以 [Homebrew 官方条目](https://formulae.brew.sh/cask/docker-desktop)为准。

```bash
# 确认终端找得到 Docker 客户端。
docker --version
# 查询后台引擎；成功返回服务信息后才继续本节。
docker info
```

`docker info` 若提示无法连接 daemon，先检查 Docker Desktop 是否启动。daemon 指后台负责创建和运行容器的服务。它不是 Python 虚拟环境，也不会改变主机的全局 Python。安装前还应满足 [Docker 的 Mac 系统要求](https://docs.docker.com/desktop/setup/install/mac-install/)。

## 先读懂 python:3.12-slim

这个名字写在 `docker run` 后，指的是一个**容器镜像**，不是需要在 Mac 上另装的 Python 软件。

| 名字的一部分 | 含义 |
|---|---|
| `python` | Docker 官方 Python 镜像 |
| `3.12` | 容器里使用Python3.12系列，与主机选择一致 |
| `slim` | 镜像的Linux系统内容经过精简，不是另一门语言或另一种Python环境管理工具 |

日常写代码和运行练习继续使用主机的全局3.12。学Docker时，用容器验证同一份程序能否换个运行位置继续工作。容器里的解释器和库由镜像提供，不会直接使用Mac上的安装目录；两边沿用同一份代码与依赖清单。补丁版本可能不同，后面的发布清单会记录实际版本。[镜像说明](https://hub.docker.com/_/python)列出了各标签含义。

## 第一条容器命令

```bash
# 创建临时容器运行一句 Python；预期打印启动提示，退出后只删除容器，保留镜像。
docker run --rm python:3.12-slim python -c "print('容器里的 Python 已启动')"
```

如果本机没有这个镜像，Docker 会先下载，下载结束才执行 Python。网络失败时不要把下载错误当成 Python 程序错误。

| 命令部分 | 在本次操作中的作用 |
|---|---|
| `docker run` | 创建容器并启动其中的程序 |
| `--rm` | 程序退出后删除这次容器；镜像仍保留 |
| `python:3.12-slim` | 指定 Python 3.12 的精简镜像标签 |
| 后面的 `python -c ...` | 交给容器执行的程序与参数 |

预期看到一行“容器里的 Python 已启动”。程序打印完就退出，容器随之结束。没有窗口一直开着，是这次任务完成后的正常现象。

## 对照主机与容器

如果安装后重开了终端，先回到项目目录。无需激活任何环境，直接比较两边的解释器：

```bash
# 回到已有项目；放在其他位置时使用自己的实际路径。
cd "$HOME/classics-reader"
# 主机应显示3.12，以及全局解释器位置。
python -c "import sys; print(sys.version); print(sys.executable)"
# 容器也应显示3.12，但路径属于镜像中的Linux文件系统。
docker run --rm python:3.12-slim python -c "import sys; print(sys.version); print(sys.executable)"
```

版本系列一致、路径不同是预期结果。Mac里的读取库不会自动进容器，所以下一节先演示在容器内安装它，再读同一份讲稿；第3章把安装步骤写进Dockerfile，以后由构建完成。

**本单元完成条件：**运行成功，并解释为何容器执行完会退出。若安装仍未完成，就把 Docker 状态记为待完成，不用跳到第三章假装已经跑过。

## 本单元验收与参考答案

先完成上面的操作，再用自己的话回答。下面是核对思路和结果的参考，不要求背原句。

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么容器打印完就退出？** 本次主进程是一条打印语句，执行完毕后进程结束，容器随之停止。它本来就不是持续运行的服务。

**`--rm` 删除了什么？** 删除本次结束的容器，不删除 Python 镜像。下次仍可从同一镜像创建新容器。

**slim 是另一个Python版本吗？** 不是。它表示精简的Linux镜像；主机和容器都选3.12系列，但各自有解释器和依赖目录。

**为什么容器还要安装读取库？** 容器不会直接使用Mac的用户包目录。相同的依赖清单告诉两个运行位置需要哪些库，Dockerfile负责镜像内的安装。

**通过证据：**`docker info` 能连接引擎；临时容器打印“容器里的 Python 已启动”；能保留并说明两次解释器路径。仅看到客户端版本号还不够。

</details>

## 资料依据

[awesome-agentic-ai-zh 部署练习](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/examples/stage-7/05-deploy/README.zh-Hans.md)提供 Docker 构建与运行的应用背景。本单元先把它拆成一次单独运行，降低同时学习服务和容器的负担。容器操作须在你的实际学习环境验收；课程编写时的验证范围另列于验证记录。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
