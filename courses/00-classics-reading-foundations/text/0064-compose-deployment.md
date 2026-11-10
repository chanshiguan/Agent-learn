# 从单个容器走到一组服务（1/2：把本节能力连起来）

本单元预计 **50—65 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《冻结题集，用真实模型和人工复核》](0063-release-quality.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 先部署到受控的本机端口

Compose 把应用、Qdrant、网络、卷和健康检查写在一个文件里。模型服务仍可以在宿主机或线上；业务代码不因生成路线改变。当前服务只绑定主机 127.0.0.1:8000，不能据此宣称已对外上线。

先回到第 21—24 章运行宿主 `uvicorn` 的终端，按 `Ctrl+C` 停止那个练习服务，确认终端已经返回提示符。Compose 应用也要使用 8000 端口，两者不能同时占用它。模型服务继续运行；不要为释放端口去终止不认识的进程。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：先列出部署所需配置

样例不带密钥，实际值放 .env；UID/GID 对应宿主数据目录所有者。

**写在哪里：**项目根目录下的 `deploy/env.example`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```text
# 复制为项目根目录的 .env 后逐项填写；此文件本身不含凭据。
LLM_MODE=local
LLM_BASE_URL=http://host.docker.internal:11434/v1
# 填写第 4 章已经验证过的真实模型 ID；空值会使就绪检查失败。
LLM_MODEL=
LLM_API_KEY=
# 后续 RAG/Agent 的输出上限；调大后重新测耗时、用量和完整性。
LLM_MAX_TOKENS=900
# 仅填写第 4 章已实际验证的推理选项；不支持的模型留空。
LLM_REASONING_EFFORT=
RETRIEVAL=keyword
MAX_MODEL_JOBS=1
DAILY_JOB_LIMIT=40
ALLOWED_HOSTS=localhost,127.0.0.1
# 填写实际运行电脑上 id -u 与 id -g 的结果，保持挂载目录可写。
APP_UID=1000
APP_GID=1000
# 改线上模型时填写 HTTPS 地址与私密 API key；不要把 .env 打进镜像。
```

**写完后应当怎样：**逐行解释后再启动；用状态、登录、问答和来源核对实际结果。

### 第 2 步：把已写出的服务封装进镜像

依赖、业务代码和启动命令进入镜像，数据与密钥通过运行时提供。

**写在哪里：**项目根目录下的 `deploy/Dockerfile`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```dockerfile
# 与前三章相同，先固定解释器系列；发布时还需记录实际镜像摘要。
FROM python:3.12-slim
WORKDIR /app
COPY requirements*.txt ./
# 本课程在容器内用 CPU 编码，先装 CPU 版，避免 Linux 自动下载不使用的 CUDA 运行库。
RUN python -m pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN python -m pip install --no-cache-dir -r requirements.txt -r requirements-model.txt -r requirements-web.txt -r requirements-rag.txt -r requirements-graph.txt
COPY companion ./companion
COPY eval ./eval
RUN useradd --uid 1000 --create-home reader && mkdir -p data && chown reader:reader data
USER reader
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
# 单 worker 与本课程进程内请求额度一致；扩副本前必须改成共享限流与会话存储。
CMD ["python", "-m", "uvicorn", "companion.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--limit-concurrency", "16", "--no-access-log"]
```

**写完后应当怎样：**逐行解释后再启动；用状态、登录、问答和来源核对实际结果。

### 第 3 步：写明应用、向量库和持久目录的关系

变量替换显式读 .env，应用只绑定回环地址；先跑 keyword 再验证 hybrid。

**写在哪里：**项目根目录下的 `deploy/compose.yaml`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**YAML 用缩进表示归属；先分清服务名、配置键和值。配置文件本身不会执行，运行 Compose 或触发工作流时才会使用它。

下面 2 段按顺序组成同一处代码。每段最多 25 行；保留空行和缩进，全部写完并保存后再检查。

**连续代码 1/2**

```yaml
services:
  app:
    build:
      context: ..
      dockerfile: deploy/Dockerfile
    image: classics-companion:${RELEASE_TAG:-candidate}
    # 绑定目录由宿主用户拥有时，使用对应 UID/GID，避免只能读取却无法保存状态。
    user: '${APP_UID:-1000}:${APP_GID:-1000}'
    env_file: ../.env
    environment:
      APP_MODE: authenticated
      APP_ENV: production
      COURSE_CHAPTER: '29'
      READING_DATA_DIR: /app/data/live
      QDRANT_URL: http://qdrant:6333
      HF_HOME: /app/data/live/hf-cache
    ports:
      - '127.0.0.1:8000:8000'
    volumes:
      - ../data:/app/data
    extra_hosts:
      - 'host.docker.internal:host-gateway'
    depends_on:
      qdrant:
        condition: service_started
```

**连续代码 2/2**（接在上一段后，不额外增加缩进）

```yaml
    healthcheck:
      test:
        [
          'CMD',
          'python',
          '-c',
          "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)",
        ]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
  qdrant:
    image: qdrant/qdrant:v1.15.5
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped
volumes:
  qdrant_data:
```

**写完后应当怎样：**逐行解释后再启动；用状态、登录、问答和来源核对实际结果。

### 第 4 步：为真正对外访问准备 HTTPS 入口

域名与证书条件需要实际环境满足；示例不会替你获得公司上线批准。

**写在哪里：**项目根目录下的 `deploy/Caddyfile.example`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```text
# 由公司运维把域名换成真实域名并配置 DNS、TLS、访问范围后使用。
# Caddy 运行在宿主机时代理本地端口；不要同时向公网开放 8000 或 6333。
reading.example.com {
    encode gzip
    reverse_proxy 127.0.0.1:8000
}
```

**写完后应当怎样：**逐行解释后再启动；用状态、登录、问答和来源核对实际结果。

### 第 5 步：为对外部署增加主机名边界

明确允许的 Host，与 HTTPS、身份校验分别处理不同边界。

**写在哪里：**项目根目录下的 `companion/app.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from fastapi.exceptions import RequestValidationError
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from fastapi.exceptions import RequestValidationError
from starlette.middleware.trustedhost import TrustedHostMiddleware
```

**写完后应当怎样：**意外 Host 被拒绝，实际域名需显式加入配置。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/app.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

明确允许的 Host，与 HTTPS、身份校验分别处理不同边界。 意外 Host 被拒绝，实际域名需显式加入配置。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
