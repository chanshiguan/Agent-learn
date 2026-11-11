# 第一阶段术语与命令速查

这张卡用于做过练习后回忆，不需要开始前背下来。命令在练习目录执行，具体文件参数按对应单元填写。

## 文件与 Python

| 词语 | 本课程中的意思 | 容易混淆的地方 |
|---|---|---|
| 工作目录 | 终端当前所在的文件夹，使用 `pwd` 查看 | 相对路径从这里起算，不一定从脚本文件所在位置起算 |
| 全局Python3.12 | 主机各章共用的解释器 | 用户包目录保存库，不是另一套解释器；容器有自己的包目录 |
| 依赖 | 程序需要的第三方包 | 安装名 `python-docx` 对应导入名 `docx` |
| 正文段落 | Word 文档中实际的段落结构 | 自动换行、讲次和原著章回都不是同一概念 |
| JSON | 可以保存字典、列表等结构的文本格式 | 文件存在不代表内容正确，要回查源文件 |
| 内容指纹 | 根据原文件内容计算的 SHA-256 | 用来识别输入变化，不证明资料事实正确 |

```bash
# 确认终端当前目录；预期路径末尾是 classics-reader，避免在其他目录运行练习。
pwd
# 核对全局解释器版本，预期为3.12，无需执行激活命令。
python --version
# 记录当前解释器路径，用于排查包装给了其他版本的情况。
python -c "import sys; print(sys.executable)"
# 将库装进全局3.12的用户包目录；后一参数允许本次越过Brew外部管理限制。
python -m pip install --user --break-system-packages -r requirements.txt
# 查看读取脚本所需参数；只显示帮助，不读取或改写讲稿。
python read_docx.py --help
```

## Docker

`python:3.12-slim` 是容器内的3.12精简Linux镜像。它不改变主机Python；镜像按同一依赖清单安装自己的库。

| 词语 | 本课程中的意思 |
|---|---|
| Dockerfile | 构建环境的步骤说明 |
| 镜像 | 构建得到的程序和运行环境 |
| 容器 | 从镜像创建、执行程序的实例 |
| 构建输入目录 | `docker build` 最后一个参数指定的目录 |
| 绑定挂载 | 把主机位置接到容器内的某个位置 |
| 只读挂载 | 程序可读取该位置，但不能向其中写入 |
| 退出码 | 主进程结束后的状态；本课正常完成用 0，输入错误用 2 |

```bash
# 向 Docker 引擎查询状态；成功返回服务信息才表示可以继续运行容器。
docker info
# 将当前目录中的构建说明和程序制成镜像；成功后可按 classics-reader:chapter3 运行。
docker build -t classics-reader:chapter3 .
# 确认镜像已构建；预期列表有 chapter3 标签，但仍需运行来验证读取结果。
docker image ls classics-reader
# 把已停止的实验容器也列出来；预期可以观察到 Exited 状态及退出码。
docker ps -a --filter name=reading-lifecycle
# 读取指定实验容器的标准输出与错误；失败程序若没打印内容，日志也可能为空。
docker logs reading-lifecycle
```

后两条只针对对应单元创建的实验容器；容器被 `--rm` 删除后，不能继续查看它的日志。输入目录挂载到 `/input`，输出目录挂载到 `/output`，二者用途分开。

## 模型连接

| 项目 | 本地路线 | 线上兼容接口路线 |
|---|---|---|
| 模型服务在哪里 | 实际学习电脑上的 Ollama | 供应商的 API 服务 |
| Python 在主机运行时的地址 | `http://127.0.0.1:11434/v1` | 控制台给出的 HTTPS 基础地址 |
| Python 在 Mac Docker Desktop 容器中 | `http://host.docker.internal:11434/v1` | 通常使用同一个外部服务地址 |
| 模型名 | 下载后由 `ollama list` 核对 | 由开通的模型列表核对 |
| 凭据 | 本章客户端使用本地占位值 | 从终端安全输入真实 API key |

本章只验证 Chat Completions 兼容接口，兼容不代表所有参数、工具能力与响应质量都相同。生成模型已连接，不表示讲稿已经进入请求。

## 卡住时先分层

找不到命令→检查安装和路径。找不到包→检查当前 Python。找不到文件→检查工作目录、引号和容器挂载。连接失败→检查地址、端口和服务。HTTP 错误→检查服务返回的状态、凭据、模型与参数。回答不合要求→先保留响应，再看消息内容与模型能力。

不要把所有失败都归成“模型不好”。先找到请求在哪一层停下，下一次修改才有方向。

## 资料入口

[awesome-agentic-ai-zh Stage 0](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/00-foundations.zh-Hans.md)、[部署练习](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/examples/stage-7/05-deploy/README.zh-Hans.md)、[Hello-Agents 第七章](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter7)。


## 第 5—29 章速查

| 想做的事 | 入口 | 应看到什么 |
|---|---|---|
| 整理讲稿 | `python -m companion ingest` | 来源、片段与快照 revision |
| 只查证据 | `python -m companion search "问题"` | hits，不调用生成模型 |
| 有据回答 | `python -m companion ask "问题"` | 引用、来源、不足状态 |
| 小规模真实向量 | `python -m companion direct-vector "问题"` | 真实编码后的相似片段 |
| 持久索引 | `python -m companion index` | 集合、权重版本、条数和缓存复用 |
| 评估检索 | `python -m companion evaluate` | 每题候选与命中指标 |
| 评估真实回答 | evaluate 加 `--generate` | 模型响应，人工评分初始为空 |
| 检查人工评阅 | `python -m companion grade 报告路径` | 明确通过范围或失败原因 |
| 创建账号 | `python -m companion create-user 账号` | 隐藏输入口令，不写进命令历史 |
| 批准练习 | `python -m companion action approve` | 具体内容预览与 YES 确认 |
| 图暂停与恢复 | `graph start` / `graph resume` 子命令 | 磁盘检查点与版本核验 |
| 发布清单 | `python -m companion manifest` | 程序、依赖、Prompt 与资料版本 |
| 备份/恢复 | `backup 新目录` / `restore 备份目录 新目录` 子命令 | 哈希检查、恢复后重新登录 |

这些是入口速查，不是一段可以整体粘贴的脚本。运行目录是你从导学开始自建的 `classics-reader/`，具体参数、环境和预期失败按对应章节操作。网站的 examples 是课后代码对照，不是需要下载或进入的练习目录。

## 后半程的几个边界

RAG 找到资料再回答；Agent 决定是否再请求工具。Embedding 模型编码资料，生成模型组织语言；两条生成路线共用检索与业务。

认证证明身份，授权限制可读写范围，批准绑定某份具体内容。事务防止一次操作写一半，幂等防止同一操作重复产生副作用。检查点保存流程位置，不替代这几层规则。

健康检查问进程是否活着，就绪检查问依赖是否准备好。回滚切回版本组合，恢复重建持久数据。RTO 是实际恢复耗时，RPO 是可能损失的数据时间范围。课程检查通过、模型效果通过和公司放行分别记录。
