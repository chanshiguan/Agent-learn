# 用同一个程序获得回答

本单元预计 **70—85 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

到这里，你应已完成[本地路线](0020-local-model.html)或[线上路线](0021-cloud-model.html)其中一种，并在当前终端设置了对应模型变量。接下来两条路线共用同一个程序，不需要另一种路线也做一遍。继续使用 `classics-reader/` 和已启用的 `.venv`；如果换过终端，先恢复环境，再按自己所选路线重新设置变量。

## 让读取项目第一次向模型发请求

前几章的程序只读取 Word，还没有访问模型。这节新建 `first_chat.py`，先只发一个公开阅读问题。它成功后会保存模型返回的文字；下一阶段再把第一章保存的讲稿 JSON 接进请求。

下面先写依赖清单与程序，写完再安装客户端并运行。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：只增加模型客户端依赖

继续使用同一个虚拟环境，先保存依赖清单，再安装；本地与线上路线共用客户端。

**写在哪里：**项目根目录下的 `requirements-model.txt`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**这是另一份依赖清单，记录调用兼容接口所需的客户端库。安装它不会下载本地模型权重；模型服务仍由上一单元准备。

```text
# 第 4 章新增的兼容接口客户端；读取讲稿的依赖仍在 requirements.txt 中。
openai==3.37.0
```

**写完后应当怎样：**安装后可以导入 openai，但还没有发送请求。

```bash
# 按刚亲手保存的清单安装本节所需依赖；只安装库，不会自动运行项目。
python -m pip install -r requirements-model.txt
```

### 第 2 步：先读取配置并检查地址

凭据留在环境变量；本地和线上只换配置。先拒绝缺少模型名或云端 HTTPS/密钥的配置。

**写在哪里：**项目根目录下的 `first_chat.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

下面 2 段按顺序组成同一处代码。每段最多 25 行；保留空行和缩进，全部写完并保存后再检查。

**连续代码 1/2**

```python
# 目的：凭据留在环境变量；本地和线上只换配置。先拒绝缺少模型名或云端 HTTPS/密钥的配置。
# 预期：配置不全时在发请求前停止。
"""验证一次真实模型调用；本章不读取或上传讲稿。"""

import argparse
import json
import os
from pathlib import Path
from time import perf_counter
from urllib.parse import urlparse

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, DefaultHttpxClient


parser = argparse.ArgumentParser(description="用相同程序连接本地或兼容接口的线上模型")
parser.add_argument("--question", default="请用两句话说明阅读《狂人日记》时可以留意什么。")
parser.add_argument("--output", type=Path, default=Path("data/output/model-run.json"))
args = parser.parse_args()
mode = os.environ.get("LLM_MODE", "local")
model = os.environ.get("LLM_MODEL", "").strip()
base_url = os.environ.get("LLM_BASE_URL", "http://127.0.0.1:11434/v1").strip()
key = os.environ.get("LLM_API_KEY", "")
if mode not in {"local", "cloud"} or not model:
    parser.error("请设置 LLM_MODE 为 local 或 cloud，并用 LLM_MODEL 指定真实模型名。")
address = urlparse(base_url)
```

**连续代码 2/2**（接在上一段后，不额外增加缩进）

```python
if mode == "cloud" and (address.scheme != "https" or not key):
    parser.error("线上路线需要 HTTPS 服务地址和 LLM_API_KEY。")
if mode == "local":
    if address.hostname not in {"127.0.0.1", "localhost", "host.docker.internal"}:
        parser.error("本章本地路线只连接本机或 Docker 宿主地址。远程服务器连接留到部署阶段。")
    key = "ollama"
```

**写完后应当怎样：**配置不全时在发请求前停止。

### 第 3 步：组装一份明确的模型请求

客户端负责网络，messages 描述任务与问题。明确不附讲稿，避免把常识回答误认为知识库结果。

**写在哪里：**项目根目录下的 `first_chat.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**messages 是按顺序排列的消息列表：system 说明任务约束，user 放本次问题。request 此时只是 Python 字典；创建客户端和字典都还没有发送请求。

```python
# 目的：客户端负责网络，messages 描述任务与问题。明确不附讲稿，避免把常识回答误认为知识库结果。
# 预期：这里只准备客户端与消息，尚未发送。写到下一步的 create 调用后，才发生网络请求。
# 本地请求不经过环境中的联网代理，避免把回环地址交给代理或触发额外 SOCKS 依赖。
client = OpenAI(base_url=base_url, api_key=key, timeout=90.0, max_retries=0,
                http_client=DefaultHttpxClient(trust_env=mode != "local"))
# 初次实验不自动重试：一次运行对应一次请求，出错时先定位，也便于记录实际用量。
request = {
    "model": model,
    "messages": [
        {"role": "system", "content": "请用清楚的中文回答。这次没有提供讲稿，不要声称读过用户的资料。"},
        {"role": "user", "content": args.question},
    ],
    "max_tokens": 256,
}
# 仅在已经核对模型能力后设置此项；基础练习不要求模型支持推理参数。
# 其他模型未必支持同一参数；留空时不发送，避免把本地选项误带到云端。
reasoning_effort = os.environ.get("LLM_REASONING_EFFORT", "").strip()
if reasoning_effort:
    request["reasoning_effort"] = reasoning_effort
```

**写完后应当怎样：**这里只准备客户端与消息，尚未发送。写到下一步的 create 调用后，才发生网络请求。

### 第 4 步：发送请求，并区分三类网络错误

地址错误、超时和服务端拒绝需要不同排查步骤；不要直接打印可能带凭据的原始响应。

**写在哪里：**项目根目录下的 `first_chat.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：****request 将字典中的字段作为命名参数传给 create。try 中发生的不同网络错误进入对应 except；非零退出码表示本次失败，不应继续保存成功记录。

```python
# 目的：地址错误、超时和服务端拒绝需要不同排查步骤；不要直接打印可能带凭据的原始响应。
# 预期：能根据错误类型回到地址、负载或服务配置排查。
started = perf_counter()
try:
    response = client.chat.completions.create(**request)
except APITimeoutError:
    parser.exit(2, "请求超时。先检查服务和模型负载，不要连续重复发送。\n")
except APIConnectionError:
    parser.exit(2, "无法连接服务。检查模型是否启动，以及地址、端口和网络。\n")
except APIStatusError as error:
    # 不打印原始响应或凭据；先用状态码区分认证、模型名、额度等问题。
    parser.exit(2, f"服务返回 HTTP {error.status_code}。按教材排错表检查配置。\n")
```

**写完后应当怎样：**能根据错误类型回到地址、负载或服务配置排查。

### 第 5 步：检查模型是否真的完成

返回 HTTP 响应并不代表有完整答案。检查 finish_reason，并记录实际用量与耗时。

**写在哪里：**项目根目录下的 `first_chat.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**choices 是候选回复列表，先判断非空再取第一个。complete 同时检查有可见文字和 finish_reason 为 stop；仅拿到文字可能只是被截断的半个回答。

```python
# 目的：返回 HTTP 响应并不代表有完整答案。检查 finish_reason，并记录实际用量与耗时。
# 预期：空内容或截断会记为未完成，不伪造成功。
if not response.choices:
    parser.exit(2, "接口没有返回候选答案。请检查该服务是否支持本章使用的接口。\n")
choice = response.choices[0]
answer = (choice.message.content or "").strip()
complete = bool(answer) and choice.finish_reason == "stop"
record = {
    "mode": mode, "model": model, "question": args.question,
    "answer": answer, "finish_reason": choice.finish_reason, "complete": complete,
    "elapsed_seconds": round(perf_counter() - started, 3),
    "usage": response.usage.model_dump() if response.usage else None,
    "knowledge_base_used": False,
}
```

**写完后应当怎样：**空内容或截断会记为未完成，不伪造成功。

### 第 6 步：保存这次调用的证据

把结果留下来供后面有资料与无资料的对照；记录里不能含 API key。

**写在哪里：**项目根目录下的 `first_chat.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**记录先落盘，再判断是否以失败退出。这样截断也有可回查的结果；之后做有资料与无资料的比较时，应另存文件，避免覆盖这次记录。

```python
# 目的：把结果留下来供后面有资料与无资料的对照；记录里不能含 API key。
# 预期：data/output/model-run.json 有本次真实答案、用量和完成状态。
args.output.parent.mkdir(parents=True, exist_ok=True)
# 只记实验结果，不保存密钥；这份记录能证明调用过程，不能证明文学解读正确。
args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
print(answer or "本次没有返回可见文字。")
print(f"完整响应：{complete}；耗时：{record['elapsed_seconds']} 秒；记录：{args.output}")
if not complete:
    parser.exit(2, "响应为空或未正常结束，保留记录排查，不将本次标为通过。\n")
```

**写完后应当怎样：**data/output/model-run.json 有本次真实答案、用量和完成状态。

### 第 7 步：复用容器知识封装模型客户端

读取容器的 ENTRYPOINT 与模型程序不同；单独配方让程序职责清楚，环境变量在运行时传入。

**写在哪里：**项目根目录下的 `Dockerfile.model`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**继续使用第3章的镜像配方，只把安装清单和入口脚本换成模型客户端。模型服务在容器外，地址和密钥必须在 docker run 时传入。

```dockerfile
# 这是第 4 章的模型客户端镜像，不包含模型权重或讲稿。
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements-model.txt ./
RUN python -m pip install --no-cache-dir -r requirements-model.txt
COPY first_chat.py ./
# 模型地址和凭据在运行时传入，避免它们随镜像分发。
ENTRYPOINT ["python", "first_chat.py"]
```

**写完后应当怎样：**模型地址指向实际服务，不把密钥写进镜像。

## 运行并观察

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


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
