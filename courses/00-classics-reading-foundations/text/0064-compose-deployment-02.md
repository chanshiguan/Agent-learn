# 从单个容器走到一组服务（2/2：连接接口与业务）

本单元预计 **35—50 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《从单个容器走到一组服务（1/2：把本节能力连起来）》](0064-compose-deployment.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

上一小节已经把前一部分写进项目。这一节继续处理 `companion/app.py`；先回想它接收什么、交给谁，再往下写。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：只接受配置的主机名

不要在生产环境随意用通配符掩盖路由配置错误。

**写在哪里：**项目根目录下的 `companion/app.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
app = FastAPI(title="名著伴读助手",docs_url=None,redoc_url=None)
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
app = FastAPI(title="名著伴读助手",docs_url=None,redoc_url=None)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=os.environ.get("ALLOWED_HOSTS","localhost,127.0.0.1,testserver").split(","))
```

**写完后应当怎样：**本机和测试客户端仍可访问，其他 Host 需明确配置。

### 第 2 步：让浏览器按文本与同源边界处理内容

no-store 避免私人响应进入缓存，CSP 限制页面脚本和资源来源。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```python
# 目的：no-store 避免私人响应进入缓存，CSP 限制页面脚本和资源来源。
# 预期：页面脚本来自自己服务，不能执行模型返回的脚本标签。
@app.middleware("http")
async def response_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    return response
```

**写完后应当怎样：**页面脚本来自自己服务，不能执行模型返回的脚本标签。

## 运行并观察

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

运行前在编辑器完成 `.env`，空模型 ID 会使就绪检查失败。默认本地地址使用 host.docker.internal；它指宿主机，不是应用容器自己。在 Docker Desktop for Mac 中，先用下面的检查确认容器能否访问该地址。Linux 的 host-gateway 只提供宿主地址，并不保证绑定在回环地址上的服务可达；本课没有提供远程模型服务器的网络配置步骤。若检查失败，保留主机上的本地调用结果，先用已经验证的线上路线完成本章。需要坚持本地路线时，应先完成仅允许应用宿主访问的模型服务网络配置，再回来重试；不要把这项尚未完成的工作记成部署通过。

模型地址有问题时，先在项目根目录运行下面这条诊断。它只读取模型列表，不生成回答，也不打印密钥。线上路线不需要执行它。

```bash
# 从应用容器检查到宿主 Ollama 的实际连通性；预期返回 HTTP 200。
docker compose --env-file .env -f deploy/compose.yaml run --rm app python -c 'import httpx; r=httpx.get("http://host.docker.internal:11434/api/tags", timeout=10, trust_env=False); r.raise_for_status(); print("宿主模型列表可达：", r.status_code)'
```

如果主机调用成功而这里失败，故障在容器到宿主的网络路径；重复安装 Python 库不能解决。Mac 安装与宿主访问机制可按 [Docker 官方说明](https://docs.docker.com/desktop/features/networking/)核对。

这些命令都在 `classics-reader/` 中执行。`--env-file .env` 明确指定 Compose 替换 UID、GID 和镜像标签时读取哪个文件；配置中的 `env_file: ../.env` 负责给容器内程序传值，两者作用不同。省略前者时，工作目录与 Compose 文件目录的差异可能让用户编号回到默认值，造成数据目录不可写。具体查找规则可选读 [Docker 官方说明](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/)。

Compose 的 Qdrant 使用新命名卷，与第 10 章单独启动的卷不同。选择 hybrid 前需在这套服务里重建索引：

```bash
# 在同一挂载数据与 Compose 网络内构建索引；首次可能下载 CPU 编码器权重。
docker compose --env-file .env -f deploy/compose.yaml run --rm app python -m companion index
```

成功后再把 `.env` 的 RETRIEVAL 改为 hybrid，重新执行上面的 `up -d` 命令使环境配置生效。登录使用 reading.sqlite3 中已有账号；若全新安装，按下面的命令创建测试读者，账号已存在时跳过：

```bash
# 在相同挂载数据库中创建测试读者；交互输入两次至少 12 字符的口令，口令不放进命令历史。
docker compose --env-file .env -f deploy/compose.yaml run --rm app python -m companion create-user student-a
```

Dockerfile 默认使用 UID=1000 的非 root 账号；Compose 可以按 `.env` 中的 `APP_UID`、`APP_GID` 使用你自己的宿主用户编号。将上面两个命令的结果填入即可，通常不需要改变数据目录的所有者。使用普通开发账号运行，不要填写 root 的 0。若仍不可写，核对挂载目录是否属于当前用户，不要给整个项目开放 777 权限。

镜像先安装 CPU 版 PyTorch，再安装其余依赖，因为本课程的编码器明确使用 CPU。这样不会为 Linux 镜像下载用不到的 CUDA 运行库；它也没有把 Mac 的 Metal 加速能力搬进 Linux 容器。


## 对外代理是另一项需要验证的部署工作

到这里应用仍只在本机端口可用，`Caddyfile.example` 只是给部署负责人看的样例。真正接入域名时还要配置 DNS、TLS、访问范围和可信代理，不能把保存样例当成已经完成 HTTPS 部署。

第21章的登录保护按账号和来源地址计数。经过 Docker 与反向代理后，应用看到的来源可能只是代理地址；同一校园网络的读者也可能共享地址。当前阈值是每个来源5分钟10次登录尝试，成功登录同样计数，不适合直接假定为公司容量。

上线前需要部署负责人验证：从两个独立网络登录时，应用能否区分来源；可信代理只包含实际代理地址；伪造的转发头不能冒充其他来源；同一网络多账号正常登录不会被错误阻断。若尚未完成，在第29章 `known_blockers` 中记录“代理来源与登录限额未验证”。不要用信任任意来源的设置来跳过这一检查。

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


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
