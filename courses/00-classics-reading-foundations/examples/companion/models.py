# 目的：把上一章的客户端配置和响应检查提成函数；调用者只需要传入 messages。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import json
import os
from time import perf_counter
from urllib.parse import urlparse
from openai import OpenAI, DefaultHttpxClient

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
        "message": choice.message.model_dump(exclude_none=True),
        "usage": response.usage.model_dump() if response.usage else None,
        "elapsed_seconds": round(perf_counter() - started, 3), "model": model,
    }

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
