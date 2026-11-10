# Python、pip 与虚拟环境

遇到“刚才装好了库，现在却导入失败”，先别继续安装。要先确认：现在跑程序的 Python，和刚才安装包时用的 Python，是不是同一个。

## 三件事各自负责什么

| 工具 | 负责什么 | 在伴读项目中的例子 |
|---|---|---|
| Python 解释器 | 执行 Python 程序 | 运行 `read_docx.py` |
| pip | 为某个 Python 安装第三方包 | 安装 `python-docx` |
| venv | 为项目准备独立环境 | 把本课程依赖放进 `.venv` |

虚拟环境主要解决项目依赖互相影响的问题。启用它，会让当前终端优先找到该环境的 Python；它不是一台新电脑，也不会让所有终端同时切换。[Python 3.12 官方教程](https://docs.python.org/3.12/tutorial/venv.html)解释了这种隔离方式。

## 把一条命令拆开看

`python -m pip install -r requirements.txt` 可以从左向右读：用当前 `python`，以模块方式运行 `pip`，执行安装，依赖条目从 `requirements.txt` 读取。

这里的 `-m` 解决“让谁来运行 pip”；`-r` 解决“安装清单从哪里来”。命令不会读取 Word，不会创建向量库，也不会下载聊天模型。本课成功后的直接结果是程序能够导入 `docx`。

## 为什么有了虚拟环境还要学 Docker

`.venv` 便于在一台开发电脑上隔离 Python 依赖；Docker 镜像把程序和运行所需的用户态环境一起交付。二者解决的范围不同。我们先用 `.venv` 看清程序怎么工作，再用相同输入验证换进容器后结果是否一致。

假设主机运行成功、容器提示找不到 `docx`。优先检查容器里是否安装了依赖，而不是反复启用主机 `.venv`。这正是第二章临时安装、第三章改为构建时安装的原因。

## 可以继续读什么

- [Python 官方教程：虚拟环境与包](https://docs.python.org/3.12/tutorial/venv.html)（英文，选读约 10 分钟）：先读 12.1 和 12.2；暂时不用研究全部包管理命令。
- [Hello-Agents 环境配置](https://github.com/datawhalechina/hello-agents/blob/main/Extra-Chapter/Extra07-%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE.md)（中文）：把独立环境与本课程的实际操作对照。

读到能解释“包安装给谁”即可回主线。无需再安装一套环境管理工具。
