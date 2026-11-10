"""第 26 章测量：分别记录模型首个内容片段和应用完整响应，不混淆两者。"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import getpass
import json
import time
import uuid
import httpx
from .files import save
from .models import client


def stream_probe():
    sdk, model = client(timeout=60)
    start = time.monotonic()
    first, size = None, 0
    with sdk:
        with sdk.chat.completions.create(model=model, messages=[{"role": "user", "content": "用一句话解释什么是阅读笔记。"}], max_tokens=80, stream=True) as stream:
            for chunk in stream:
                content = chunk.choices[0].delta.content if chunk.choices else None
                if content:
                    if first is None: first = time.monotonic() - start
                    size += len(content)
    if first is None: raise ValueError("没有收到实际内容片段，不能报告首字延迟。")
    result = {"model": model, "first_content_seconds": first, "full_seconds": time.monotonic() - start, "characters": size, "scope": "模型流式接口；课程网页目前等完整回答后显示"}
    save("stream-measure.json", result)
    return result


def api_probe(url, concurrency, count):
    if not (url.startswith("http://127.0.0.1:") or url.startswith("https://")):
        raise ValueError("仅测试本机 HTTP 或受保护的 HTTPS 地址。")
    token = getpass.getpass("输入专用测试账号的访问令牌（不回显、不保存）：")
    with httpx.Client(base_url=url, headers={"Authorization": "Bearer " + token}, timeout=130) as client:
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
