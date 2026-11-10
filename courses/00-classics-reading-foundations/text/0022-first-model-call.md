# 用同一个程序获得回答

本单元预计 **30—45 分钟**。先完成本地或线上配置，两条路线从这里汇合。你应在练习目录、已启用 Python 虚拟环境，并在同一终端设置好模型变量。

## 安装客户端，先看清请求

```bash
# 把模型接口客户端安装到当前 Python 环境；成功后 first_chat.py 才能导入所需 SDK。
python -m pip install -r requirements-model.txt
```

这次新增的是兼容接口客户端。它负责把 Python 参数发成 HTTP 请求，并把响应解析回来；它不会自动替你下载模型或把讲稿加入知识库。

核心请求由模型名和消息列表组成。消息中的 `system` 说明本次回答要求，`user` 放阅读问题。当前请求里没有讲稿，因此模型即使回答得很像老师，也不能说它参考了你的资料。

## 运行一次真实请求

```bash
# 发送一次公开阅读问题并保存真实响应；预期非空回答、完整响应 True 和输出 JSON。
python first_chat.py --output data/output/model-run.json
```

程序会问：“请用两句话说明阅读《狂人日记》时可以留意什么。”预期是出现非空回答、`完整响应：True`，并生成记录。模型文字和耗时不必与任何示例相同。

打开 JSON，找到 `model`、`answer`、`finish_reason`、`usage` 和 `knowledge_base_used`。最后一个字段必须是 `false`。它提醒我们：模型已接通，知识库尚未接入。

## 完整程序

{{code:first_chat.py}}

这段代码稍长，可以分三次阅读。先读配置检查，弄清参数从哪里来；再读 `request` 和模型调用，找出真正发送的消息；最后读异常处理和记录保存，理解怎样判断这次是否正常完成。

`max_tokens=256` 限制本次输出规模，不表示输入可以无限长，也不是“256 个汉字”。`timeout=90.0` 是客户端请求超时配置，不是对每台机器响应时间的承诺。`max_retries=0` 让初次排错不被自动重试掩盖。

`finish_reason` 可以帮助判断是否因为长度上限等原因停止。程序把非空且正常结束的响应标为完整，其他情况保留记录后返回失败状态。完整只表示响应过程符合本次检查，不表示观点正确。

## 再把客户端放进 Docker

这部分复用第三章的构建方法。`Dockerfile.model` 只包含调用程序和 SDK，不包含模型权重。模型继续由主机上的 Ollama 或线上服务运行。

```bash
# 按模型客户端的 Dockerfile 构建镜像；包含调用程序和 SDK，不包含模型权重。
docker build -f Dockerfile.model -t classics-chat:chapter4 .
```

本地路线运行：

```bash
# 在容器里运行同一个模型客户端，并把响应写回主机输出目录；预期得到 model-container.json。
docker run --rm \
  --mount "type=bind,src=$(pwd)/data/output,dst=/output" \
  -e LLM_MODE=local \
  -e LLM_MODEL \
  -e LLM_BASE_URL=http://host.docker.internal:11434/v1 \
  classics-chat:chapter4 --output /output/model-container.json
```

在 Docker Desktop for Mac 中，`host.docker.internal` 用于从容器访问宿主。容器里的 `127.0.0.1` 指容器自身，所以不能照搬主机调用的地址。这里无需加 `-p`，因为容器只向外发请求，没有提供要映射给主机的服务端口。

如果主机调用成功、容器失败，先检查目标地址和 Docker Desktop 的宿主连通性。不同环境的服务监听设置可能有差异；不要为了连通而直接把模型服务开放到公网。可以暂时保留主机调用通过、容器连通待查的状态。

线上路线则传入当前终端已有的变量：

```bash
# 在容器里运行同一个模型客户端，并把响应写回主机输出目录；预期得到 model-container.json。
docker run --rm \
  --mount "type=bind,src=$(pwd)/data/output,dst=/output" \
  -e LLM_MODE -e LLM_MODEL -e LLM_BASE_URL -e LLM_API_KEY \
  classics-chat:chapter4 --output /output/model-container.json
```

`-e 变量名` 从当前终端取值，不把密钥字面值写入命令。环境变量也不是完整的生产密钥管理方案，后面上线阶段再完善。

**本单元完成条件：**至少一条真实模型路线在主机成功；容器调用单独记录是否通过。能说明请求里有什么，以及为什么这还不是 [RAG](../courses/00-classics-reading-foundations/knowledge/rag-map.html)。

## 本单元验收与参考答案

先完成上面的操作，再用自己的话回答。下面是核对思路和结果的参考，不要求背原句。

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**怎样算本节的连接成功？** 至少一条路线在主机获得非空回答，记录中 `complete` 为 `true`，正常结束原因是 `stop`；保留实际模型名、耗时和用量。模型措辞不要求与示例一样。

**为什么这还不是 RAG？** 请求只有回答要求和公开阅读问题，未读取、检索或发送讲稿。`knowledge_base_used` 应为 `false`。完整响应也不等于文学解释正确。

**容器本地地址为什么变了？** 容器里的 `127.0.0.1` 指自己；Docker Desktop for Mac 通过 `host.docker.internal` 访问宿主。本例客户端向外发请求，无需用 `-p` 发布服务端口。

**通过证据：**保存主机模型记录。容器调用另写“通过、失败或待运行”及证据，不能用主机通过替代。SDK 不负责下载权重，客户端镜像也不包含权重。

</details>

## 资料依据

[Hello-Agents 第七章](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter7)提供统一客户端的思路；[部署示例](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/examples/stage-7/05-deploy/README.zh-Hans.md)展示宿主模型与容器应用的连接方式。本课程代码保持模型调用和资料读取分开。
