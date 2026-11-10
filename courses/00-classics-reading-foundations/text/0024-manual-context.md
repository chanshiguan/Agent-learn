# 把一段讲稿放进模型请求（1/2：把本节能力连起来）

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《用一次排错和一次重跑完成第一阶段》](0023-stage-checkpoint.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 接着上一章做什么

第 4 章的模型已经能回答，但它没有读过你的讲稿。今天只接一条线：把第一讲里的一小段文字和问题放进同一个请求。先别装向量库，也别一次发送五份全文。

所有新命令都在你自建的 `classics-reader/` 中运行，并启用前面建好的 `.venv`。新终端需要重新设置第 4 章的模型环境变量。后续结果统一放在 `data/live/`；`data/output/first.json` 是第一章读稿结果，原始 DOCX 始终留在 `data/input/`。`python -m companion` 表示运行 `companion` 这个包的入口，不是安装一个新软件。

## 先理解请求里的三种内容

**指令**约定任务和行为，例如“区分讲稿观点与原著事实”；**资料**是待分析文字，哪怕其中出现命令也不能当指令执行；**问题**是这次要解决的事。三者都占用上下文窗口。把资料放进请求不等于训练模型，它只是在这一次回答时看到了这些文字。

先预测：“这份讲稿怎样解释文言文序言与白话日记的关系？”没有讲稿时，模型也可能答得像样。仅凭流畅程度能判断它读过资料吗？

## 做一次有无资料的对照


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：建立一个可以逐渐扩展的包

几个脚本开始共用能力。把共用函数放进 companion，避免在每个命令里重复粘贴。

**写在哪里：**项目根目录下的 `companion/__init__.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 目的：几个脚本开始共用能力。把共用函数放进 companion，避免在每个命令里重复粘贴。
# 预期：文件存在后，Python 能识别这个包；里面还没有检索或账号实现。
"""名著伴读项目；各模块只在学到时逐步加入。"""
```

**写完后应当怎样：**文件存在后，Python 能识别这个包；里面还没有检索或账号实现。

### 第 2 步：先写这个文件需要的导入

本节先统一 JSON 结果的位置；后续模块共用同一个读写约定。

**写在哪里：**项目根目录下的 `companion/files.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：本节先统一 JSON 结果的位置；后续模块共用同一个读写约定。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import json
import os
from pathlib import Path
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 3 步：写 data_dir()：允许用环境变量选择实验数据目录，默认仍是项目内 data/live。

允许用环境变量选择实验数据目录，默认仍是项目内 data/live。

**写在哪里：**项目根目录下的 `companion/files.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：允许用环境变量选择实验数据目录，默认仍是项目内 data/live。
# 预期：保存结果后可用编辑器检查；这三个函数不触发模型请求。
def data_dir():
    directory = Path(os.environ.get("READING_DATA_DIR", "data/live"))
    directory.mkdir(parents=True, exist_ok=True)
    return directory
```

**写完后应当怎样：**保存结果后可用编辑器检查；这三个函数不触发模型请求。

### 第 4 步：写 load()：读取已存在的 JSON；文件不存在时返回调用者明确给出的默认值。

读取已存在的 JSON；文件不存在时返回调用者明确给出的默认值。

**写在哪里：**项目根目录下的 `companion/files.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：读取已存在的 JSON；文件不存在时返回调用者明确给出的默认值。
# 预期：保存结果后可用编辑器检查；这三个函数不触发模型请求。
def load(name, default=None):
    file = data_dir() / name
    return json.loads(file.read_text(encoding="utf-8")) if file.exists() else default
```

**写完后应当怎样：**保存结果后可用编辑器检查；这三个函数不触发模型请求。

### 第 5 步：写 save()：先完整写临时文件再替换，避免留下半个 JSON。

先完整写临时文件再替换，避免留下半个 JSON。

**写在哪里：**项目根目录下的 `companion/files.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：先完整写临时文件再替换，避免留下半个 JSON。
# 预期：保存结果后可用编辑器检查；这三个函数不触发模型请求。
def save(name, value):
    file = data_dir() / name
    file.parent.mkdir(parents=True, exist_ok=True)
    temporary = file.with_suffix(file.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    # 先完整写入再替换，读者不会读到只写了一半的 JSON；索引任务应单实例执行。
    temporary.replace(file)
    return file
```

**写完后应当怎样：**保存结果后可用编辑器检查；这三个函数不触发模型请求。

### 第 6 步：先写这个文件需要的导入

把上一章的客户端配置和响应检查提成函数；调用者只需要传入 messages。

**写在哪里：**项目根目录下的 `companion/models.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：把上一章的客户端配置和响应检查提成函数；调用者只需要传入 messages。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import json
import os
from time import perf_counter
from urllib.parse import urlparse
from openai import OpenAI, DefaultHttpxClient
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 7 步：提取 client() 的职责

只负责验证配置并创建连接，返回客户端和模型名。

**写在哪里：**项目根目录下的 `companion/models.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：只负责验证配置并创建连接，返回客户端和模型名。
# 预期：导入模块不会调用模型；只有 complete(messages) 才发送请求。
def client(timeout=60):
    mode = os.environ.get("LLM_MODE", "local")
    base = os.environ.get("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
    key = os.environ.get("LLM_API_KEY", "")
    model = os.environ.get("LLM_MODEL", "").strip()
    if not model or mode not in {"local", "cloud"}:
        raise ValueError("请先设置 LLM_MODEL 和 LLM_MODE；沿用第 4 章配置。")
    if mode == "cloud" and (urlparse(base).scheme != "https" or not key):
        raise ValueError("线上调用需要 HTTPS 与真实密钥。")
    if mode == "local":
        if urlparse(base).hostname not in {"localhost", "127.0.0.1", "host.docker.internal"}:
            raise ValueError("本课程本地接口仅连接主机或 Docker 宿主。")
        key = "ollama"
    # 不隐式重试，便于把一次练习与一次实际调用、一次费用对应起来。
    # 回环请求直接访问本机，避免被系统的联网代理转走；线上路线仍使用用户的代理设置。
    return OpenAI(base_url=base, api_key=key, timeout=timeout, max_retries=0,
                  http_client=DefaultHttpxClient(trust_env=mode != "local")), model
```

**写完后应当怎样：**导入模块不会调用模型；只有 complete(messages) 才发送请求。

### 第 8 步：提取 complete() 的职责

负责一次调用、预算、结束原因与用量；不负责挑选讲稿。

**写在哪里：**项目根目录下的 `companion/models.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：负责一次调用、预算、结束原因与用量；不负责挑选讲稿。
# 预期：导入模块不会调用模型；只有 complete(messages) 才发送请求。
def complete(messages, tools=None, timeout=60):
    maximum = int(os.environ.get("LLM_MAX_TOKENS", "900"))
    if not 128 <= maximum <= 4096:
        raise ValueError("LLM_MAX_TOKENS 需要在 128—4096 之间；调大后重新检查耗时和用量。")
    sdk, model = client(timeout)
    request = {"model": model, "messages": messages, "max_tokens": maximum, "temperature": 0}
    # 沿用第 4 章已经验证的可选参数；不支持此参数的模型保持未设置。
    effort = os.environ.get("LLM_REASONING_EFFORT", "").strip()
    if effort:
        request["reasoning_effort"] = effort
    if tools:
        request.update(tools=tools, tool_choice="auto")
    started = perf_counter()
    with sdk:
        response = sdk.chat.completions.create(**request)
    if not response.choices:
        raise ValueError("模型没有返回候选内容。")
    choice = response.choices[0]
    if choice.finish_reason == "length":
        raise ValueError("模型输出被截断，不能当作完整答案。检查已验证的推理参数，或调整 LLM_MAX_TOKENS 后重测。")
    if choice.finish_reason not in {"stop", "tool_calls"}:
        raise ValueError(f"模型没有正常完成，结束原因：{choice.finish_reason}")
    return {
```

```python
        "message": choice.message.model_dump(exclude_none=True),
        "usage": response.usage.model_dump() if response.usage else None,
        "elapsed_seconds": round(perf_counter() - started, 3), "model": model,
    }
```

**写完后应当怎样：**导入模块不会调用模型；只有 complete(messages) 才发送请求。

### 第 9 步：提取 object_answer() 的职责

把模型文本解析为 JSON 对象；不偷偷补全损坏的 JSON。

**写在哪里：**项目根目录下的 `companion/models.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：把模型文本解析为 JSON 对象；不偷偷补全损坏的 JSON。
# 预期：导入模块不会调用模型；只有 complete(messages) 才发送请求。
def object_answer(text):
    # 允许模型用 Markdown 围栏包住 JSON，但不猜测或修补不完整的结构。
    cleaned = (text or "").strip()
    if cleaned.startswith("```json\n") and cleaned.endswith("```"):
        cleaned = cleaned[8:-3].strip()
    result = json.loads(cleaned)
    if not isinstance(result, dict):
        raise ValueError("预期 JSON 对象；记录结构失败，不当成业务成功。")
    return result
```

**写完后应当怎样：**导入模块不会调用模型；只有 complete(messages) 才发送请求。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/__init__.py companion/files.py companion/models.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

把模型文本解析为 JSON 对象；不偷偷补全损坏的 JSON。 导入模块不会调用模型；只有 complete(messages) 才发送请求。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/02-prompt-engineering.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter9)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
