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
if mode == "cloud" and (address.scheme != "https" or not key):
    parser.error("线上路线需要 HTTPS 服务地址和 LLM_API_KEY。")
if mode == "local":
    if address.hostname not in {"127.0.0.1", "localhost", "host.docker.internal"}:
        parser.error("本章本地路线只连接本机或 Docker 宿主地址。远程服务器连接留到部署阶段。")
    key = "ollama"

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
args.output.parent.mkdir(parents=True, exist_ok=True)
# 只记实验结果，不保存密钥；这份记录能证明调用过程，不能证明文学解读正确。
args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
print(answer or "本次没有返回可见文字。")
print(f"完整响应：{complete}；耗时：{record['elapsed_seconds']} 秒；记录：{args.output}")
if not complete:
    parser.exit(2, "响应为空或未正常结束，保留记录排查，不将本次标为通过。\n")
