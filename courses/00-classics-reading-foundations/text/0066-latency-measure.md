# 先测一个请求，别急着加并发

本单元预计 **55—70 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《活着不等于已经能接待读者》](0065-readiness-failures.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 先分清用户等的是什么

首字延迟是请求发出到第一段实际内容到达的时间；完整耗时是整个回答结束的时间。本课程网页目前等完整回答后显示，不能把模型流式接口的首字测量冒充网页已经支持流式输出。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：写一份小规模请求测量程序

沿用已经验证的模型参数，分别测首个内容片段与正常结束；截断回答不能记成完整响应。

**写在哪里：**项目根目录下的 `companion/measure.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

下面 4 段按顺序组成同一处代码。每段最多 25 行；保留空行和缩进，全部写完并保存后再检查。

**连续代码 1/4**

```python
# 目的：使用明确虚构账号与题目，记录真实状态码和耗时；先测1个，再增加少量并发。
# 预期：报告区分成功、拒绝和失败，不能只看平均速度。
"""第 26 章测量：分别记录模型首个内容片段和应用完整响应，不混淆两者。"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import getpass
import json
import os
import time
import uuid
import httpx
from .files import save
from .models import client


def stream_probe():
    sdk, model = client(timeout=60)
    maximum = int(os.environ.get("LLM_MAX_TOKENS", "900"))
    if not 128 <= maximum <= 4096:
        raise ValueError("LLM_MAX_TOKENS 需要在 128—4096 之间。")
    request = {"model": model, "messages": [{"role": "user", "content": "用一句话解释什么是阅读笔记。"}], "max_tokens": maximum, "temperature": 0, "stream": True}
    effort = os.environ.get("LLM_REASONING_EFFORT", "").strip()
    if effort:
        request["reasoning_effort"] = effort
    start = time.monotonic()
```

**连续代码 2/4**（接在上一段后，不额外增加缩进）

```python
    first, size, finish_reason = None, 0, None
    with sdk:
        with sdk.chat.completions.create(**request) as stream:
            for chunk in stream:
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                finish_reason = choice.finish_reason or finish_reason
                content = choice.delta.content
                if content:
                    if first is None: first = time.monotonic() - start
                    size += len(content)
    if first is None: raise ValueError("没有收到实际内容片段，不能报告首字延迟。")
    # 有首字不代表完整回答；截断和中断必须失败，不能作为完整耗时样本。
    if finish_reason != "stop":
        raise ValueError(f"流式回答未正常完成（{finish_reason}），不记录为完整响应。")
    result = {"model": model, "first_content_seconds": first, "full_seconds": time.monotonic() - start, "characters": size, "finish_reason": finish_reason, "max_tokens": maximum, "reasoning_effort": effort or None, "scope": "模型流式接口；课程网页目前等完整回答后显示"}
    save("stream-measure.json", result)
    return result


def api_probe(url, concurrency, count):
    if not (url.startswith("http://127.0.0.1:") or url.startswith("https://")):
        raise ValueError("仅测试本机 HTTP 或受保护的 HTTPS 地址。")
    token = getpass.getpass("输入专用测试账号的访问令牌（不回显、不保存）：")
```

**连续代码 3/4**（接在上一段后，不额外增加缩进）

```python
    # 本机测量直连，避免系统代理改变延迟或要求额外的 SOCKS 依赖。
    with httpx.Client(trust_env=url.startswith("https://"), base_url=url, headers={"Authorization": "Bearer " + token}, timeout=130) as client:
        sessions = []
        try:
            # 每个请求使用独立会话，避免把乐观锁冲突误当作模型容量问题。
            for _ in range(count):
                response = client.post("/api/sessions", json={"book": "狂人日记"})
                response.raise_for_status(); sessions.append(response.json()["id"])
            def one(identity):
                started = time.monotonic()
                try:
                    response = client.post("/api/ask", json={"session_id": identity, "request_id": uuid.uuid4().hex, "question": "讲稿怎样解释文言文序言？", "mode": "qa"})
                    return {"status": response.status_code, "seconds": time.monotonic() - started}
                except httpx.HTTPError as error:
                    return {"status": type(error).__name__, "seconds": time.monotonic() - started}
            started = time.monotonic()
            with ThreadPoolExecutor(max_workers=concurrency) as pool: records = list(pool.map(one, sessions))
            elapsed = time.monotonic() - started
        finally:
            for identity in sessions: client.delete("/api/sessions/" + identity)
    successful = sorted(r["seconds"] for r in records if r["status"] == 200)
    result = {"concurrency": concurrency, "requests": count, "records": records, "elapsed_seconds": elapsed,
              "successes_per_second": len(successful) / elapsed, "error_ratio": 1 - len(successful) / count,
              "p95_success_seconds": successful[min(len(successful) - 1, int(len(successful) * .95))] if successful else None,
              "scope": "仅此次小样本，不能当作稳定生产 P95"}
```

**连续代码 4/4**（接在上一段后，不额外增加缩进）

```python
    save(f"load-{concurrency}.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["stream", "api"])
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--concurrency", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--count", type=int, choices=range(1, 21), default=4)
    args = parser.parse_args()
    print(json.dumps(stream_probe() if args.mode == "stream" else api_probe(args.url, args.concurrency, args.count), ensure_ascii=False, indent=2))
```

**写完后应当怎样：**只有正常 stop 的流写入完整测量报告；length 或缺少结束原因时明确失败。

## 运行并观察

```bash
# 直接测真实模型的首个内容片段与完整响应；使用当前终端的本地或线上模型配置。
python -m companion.measure stream
```

记录 `data/live/stream-measure.json`。至少在模型刚启动和已经预热后各测一次，另存报告。首次加载模型、下载权重与实际推理是不同开销。某些服务只在最后一次性返回内容，首字接近完整耗时也可能是实际行为。

本次测量沿用 `LLM_MAX_TOKENS` 与已经验证的 `LLM_REASONING_EFFORT`，报告会记录实际值。先收到文字、随后因为输出预算用完而截断，不能算完整回答；程序只在 `finish_reason=stop` 时保存成功报告。遇到 `length`、缺少结束标记或连接中断，保留报错并单独记为失败。以前的成功报告可能仍在磁盘上，不要把旧文件当成本次测量结果。

再在网页测同题完整请求，包含检索、上下文组织和生成。记录机器、内存、模型名称、量化版本、检索模式、输入与输出大小。没有这些条件，单独一个“每秒多少字”无法比较。

## 比较两条路线

若有条件，再用同一题与资料切到线上模型，保留独立结果。生成模型不同会影响输出长度和质量，所以同时人工评分。M1 16 GB 的可用性由这些实测决定，不预先规定能服务多少人。

本地慢时先检查输入长度、模型大小与并发；线上快也要看费用、数据安排和故障策略。选择是基于目标的取舍，不是看哪个名称更新。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 模型首字快就代表页面首字快吗？
2. 能用一次耗时给 M1 定并发上限吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**模型首字快就代表页面首字快吗？**

不代表。页面若等待完整 JSON 才显示，用户体验仍取决于完整请求。本课分别标注两种测量。

**能用一次耗时给 M1 定并发上限吗？**

不能。还需多次运行、负载、内存、错误率和质量约束，下一单元再测。

**通过证据：**冷启动与预热测量、网页完整请求记录，以及明确的设备/模型条件。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
