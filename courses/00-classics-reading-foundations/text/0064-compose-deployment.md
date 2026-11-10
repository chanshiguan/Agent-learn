# 从单个容器走到一组服务

本单元预计 **45—60 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 先部署到受控的本机端口

Compose 把应用、Qdrant、网络、卷和健康检查写在一个文件里。模型服务仍可以在宿主机或线上；业务代码不因生成路线改变。当前服务只绑定主机 127.0.0.1:8000，不能据此宣称已对外上线。

先回到第 21—24 章运行宿主 `uvicorn` 的终端，按 `Ctrl+C` 停止那个练习服务，确认终端已经返回提示符。Compose 应用也要使用 8000 端口，两者不能同时占用它。模型服务继续运行；不要为释放端口去终止不认识的进程。

```bash
# 复制无凭据的配置样例；只在 .env 尚不存在时执行，避免覆盖自己的配置。
cp -n deploy/env.example .env
# 创建持久数据目录；容器将挂载它，原始资料与状态不会打进镜像。
mkdir -p data/live
# 查看当前宿主用户与组的数字 ID；将两个结果分别填入 .env 的 APP_UID、APP_GID。
id -u
id -g
# 在编辑器填完 .env 的真实模型 ID、地址和路线后构建；本命令不把 .env COPY 进镜像。
docker compose --env-file .env -f deploy/compose.yaml build
# 启动应用和向量库，先测试 keyword 路线，减少首次排错变量。
docker compose --env-file .env -f deploy/compose.yaml up -d
# 查看服务状态，检查应用进程是否存活。
docker compose --env-file .env -f deploy/compose.yaml ps
```

运行前在编辑器完成 `.env`，空模型 ID 会使就绪检查失败。默认本地地址使用 host.docker.internal；它指宿主机，不是应用容器自己。若宿主模型只接受回环连接且 Docker 无法访问，按第 4 章模型服务说明配置受保护的可达地址，或先选择线上路线；不要为了连通随意向公网开放模型端口。

这些命令都在 `examples/` 中执行。`--env-file .env` 明确指定 Compose 替换 UID、GID 和镜像标签时读取哪个文件；配置中的 `env_file: ../.env` 负责给容器内程序传值，两者作用不同。省略前者时，工作目录与 Compose 文件目录的差异可能让用户编号回到默认值，造成数据目录不可写。

Compose 的 Qdrant 使用新命名卷，与第 10 章单独启动的卷不同。选择 hybrid 前需在这套服务里重建索引：

```bash
# 在同一挂载数据与 Compose 网络内构建索引；首次可能下载 CPU 编码器权重。
docker compose --env-file .env -f deploy/compose.yaml run --rm app python -m companion index
```

成功后再把 `.env` 的 RETRIEVAL 改为 hybrid，执行 up -d 使环境配置生效。登录使用 reading.sqlite3 中已有账号；若全新安装，运行 `docker compose --env-file .env -f deploy/compose.yaml run --rm app python -m companion create-user`，创建管理员安排的测试账号。

Dockerfile 默认使用 UID=1000 的非 root 账号；Compose 可以按 `.env` 中的 `APP_UID`、`APP_GID` 使用你自己的宿主用户编号。将上面两个命令的结果填入即可，通常不需要改变数据目录的所有者。使用普通开发账号运行，不要填写 root 的 0。若仍不可写，核对挂载目录是否属于当前用户，不要给整个项目开放 777 权限。

镜像先安装 CPU 版 PyTorch，再安装其余依赖，因为本课程的编码器明确使用 CPU。这样不会为 Linux 镜像下载用不到的 CUDA 运行库；它也没有把 Mac 的 Metal 加速能力搬进 Linux 容器。

## 对照完整实现

先读上面标出的函数，再展开文件。配套包已包含它及依赖文件；不需要把后续章节一起学完。注释重点解释为什么这样处理，以及出错时应发生什么。

<details><summary>展开本单元完整源码：deploy/compose.yaml</summary>

{{code:deploy/compose.yaml}}

</details>

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 为什么 Dockerfile 不 COPY data 和 .env？
2. 容器里的 localhost 指宿主机吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么 Dockerfile 不 COPY data 和 .env？**

资料、运行状态和凭据不属于不可变程序镜像；通过受控挂载或环境注入，才能独立更新与保护。

**容器里的 localhost 指宿主机吗？**

通常指容器自己。访问 Compose 服务用服务名，访问宿主模型需要已验证的宿主地址。

**通过证据：**Compose 状态、实际登录和一次有据问答；所选向量路线有新服务上的索引验证。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
