# 先在容器里运行一行 Python

本单元预计 **20—30 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《保存结果，并证明没有读错资料》](0013-save-json.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 这次为什么用 Docker

第一章能运行，依赖于你选的 Python 和安装的读取库。把脚本发到另一台机器，对方未必有同样的环境。Docker 镜像可以包含一套运行所需的文件；从镜像创建的容器，才是执行程序的实例。

可以先记住这三个关系：Dockerfile 是构建说明，镜像是构建出的环境，容器是用这个环境运行程序的一次实例。一个镜像可以创建多个容器。容器也有自己的文件位置，宿主机上的讲稿不会自动出现在里面。

## 在 M1 Mac 上准备 Docker Desktop

先运行 `docker --version`。如果已经有客户端，再运行 `docker info`；后者能检查后台服务是否可用。只有版本号并不能证明容器已经能启动。

还没有安装时，可以使用 Docker Desktop 的 Mac Apple Silicon 安装包：打开安装包，将 Docker 拖入“应用程序”，启动 Docker，按安装向导完成必要设置，等待界面显示引擎已运行。请核对安装器支持你的 macOS 版本，不要选 Intel 包。

如果电脑已有 Homebrew，也可以用下面的安装命令；两种方式选一种即可：


使用 Mac 时，安装前核对 [Docker 的系统要求](https://docs.docker.com/desktop/setup/install/mac-install/)：当前支持最新及前两个主要 macOS 版本，M1 选择 Apple silicon 安装包。能安装 Docker 不代表所有模型都能同时装入内存；模型容量到第4章再逐项观察。

## 运行并观察

```bash
# 通过已有的 Homebrew 安装 Docker Desktop；安装完成后还需要启动应用。
brew install --cask docker
# 启动 Docker Desktop 的后台容器服务；等引擎就绪后再做 docker info 检查。
open -a Docker
```

安装完成后，重新打开终端，检查：

```bash
# 检查 Docker 客户端是否可找到；看到版本号还不能证明后台引擎可用。
docker --version
# 向 Docker 引擎查询状态；成功返回服务信息才表示可以继续运行容器。
docker info
```

前者找不到命令时，检查安装和终端路径；后者提示连接不上 daemon 时，先看 Docker Desktop 是否启动。daemon 是负责创建和运行容器的后台服务。它和你输入的 `docker` 客户端不是同一个进程。

软件可从指定资料中的 Docker 入口获取；本课程的概念与练习均在本地讲解，不要求先读完整 Docker 官方手册。

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

安装 Docker 时如果重新开过终端，原来的项目目录和虚拟环境不会自动恢复。先进入项目并启用 `.venv`，再比较两边的 Python：

```bash
# 回到第一章的项目；若当时放在别处，把这一行换成自己的项目路径。
cd "$HOME/classics-reader"
# 恢复主机的项目环境；容器不会因此使用这份环境，下面会观察这个区别。
source .venv/bin/activate
# 查看实际运行的 Python 路径；在主机上应指向本项目 .venv，用于排查包装错环境。
python -c "import sys; print(sys.executable)"
# 观察容器内的 Python 路径；它来自镜像，通常不同于主机的 .venv 路径。
docker run --rm python:3.12-slim python -c "import sys; print(sys.executable)"
```

两次路径通常不同。第一条来自当前主机环境，第二条来自镜像。主机启用了 `.venv`，不代表容器也会使用它。下一单元会显式把程序和资料交给容器。

**本单元完成条件：**运行成功，并解释为何容器执行完会退出。若安装仍未完成，就把 Docker 状态记为待完成，不用跳到第三章假装已经跑过。

## 本单元验收与参考答案

先完成上面的操作，再用自己的话回答。下面是核对思路和结果的参考，不要求背原句。

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么容器打印完就退出？** 本次主进程是一条打印语句，执行完毕后进程结束，容器随之停止。它本来就不是持续运行的服务。

**`--rm` 删除了什么？** 删除本次结束的容器，不删除 Python 镜像。下次仍可从同一镜像创建新容器。

**主机启用 `.venv` 后，容器也会用它吗？** 不会。容器运行镜像里的 Python；可用两次 `sys.executable` 输出看见区别。

**通过证据：**`docker info` 能连接引擎；临时容器打印“容器里的 Python 已启动”；能保留并说明两次解释器路径。仅看到客户端版本号还不够。

</details>

## 资料依据

[awesome-agentic-ai-zh 部署练习](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/examples/stage-7/05-deploy/README.zh-Hans.md)提供 Docker 构建与运行的应用背景。本单元先把它拆成一次单独运行，降低同时学习服务和容器的负担。容器操作须在你的实际学习环境验收；课程编写时的验证范围另列于验证记录。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
