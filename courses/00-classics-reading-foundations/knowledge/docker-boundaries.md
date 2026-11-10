# 镜像、容器与文件挂载

第一次读到容器路径 `/input` 时，可以先问一句：这是主机上的目录，还是程序在容器里看到的目录？把这两个视角分清，许多“文件明明存在却找不到”的问题就有了解释。

## 用同一次读稿任务对照

| 概念 | 本课中的具体对象 | 改变它会发生什么 |
|---|---|---|
| Dockerfile | 构建步骤文件 | 改完还要重新构建，已有镜像不会自动变化 |
| 镜像 | `classics-reader:chapter3` | 包含程序副本与依赖，可创建多个容器 |
| 容器 | 一次读稿程序的运行实例 | 主进程完成后停止，可保留记录或删除 |
| 绑定挂载 | 主机目录与容器路径的对应关系 | 换输入资料时可以保持镜像不变 |

容器以隔离的进程环境运行程序；它和包含完整操作系统的虚拟机不是同一概念。隔离也不代表任何运行配置都天然安全。[Docker 官方概念说明](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)提供了容器与虚拟机的对照。

## 用一张路径表推演

| 你在主机上看到 | 程序在容器里看到 | 容器删除之后 |
|---|---|---|
| `data/input/第一讲.docx` | `/input/第一讲.docx` | 主机原文件保留 |
| `data/output/image.json` | `/output/image.json` | 主机结果保留 |
| 未挂载的容器内部文件 | `/tmp/inside.txt` | 随该容器文件层删除 |

表中“第一讲.docx”是帮助理解路径的简写，实际运行仍使用课程里的完整文件名。输入设为只读，输出单独可写，是为了让读取程序不能意外改掉讲稿。

如果把挂载目标改成 `/books`，读取参数也要跟着改。只改一边，就像告诉程序去一个没有接上资料的位置找文件。

## localhost 也是一个视角问题

第 4 章中，Python 在主机上运行时，`127.0.0.1` 指主机；放进容器后，它指容器自身。课程使用 Docker Desktop for Mac 的宿主访问地址连接主机模型。其他运行环境不能照搬这条网络约定。

## 可以继续读什么

- [Docker：什么是容器](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)（英文，约 8 分钟）：先看概念对照，无需把官方练习再做一遍。
- [指定仓库的部署练习](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/examples/stage-7/05-deploy/README.zh-Hans.md)（中文）：看文件、运行参数和宿主服务怎样衔接。Web 服务部分留到后续主线。
