"""真实 Playwright 执行器 + 固定动作提议；不是模型智能效果测试。"""

# 默认打开内存中的演示页面；live 才访问 example.com，观察结果与截图来自真实浏览器。
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from policy import check


def run(output, live=False):
    output.mkdir(parents=True, exist_ok=True)
    trace = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=False)
        # 每条网络请求核对域名；本例不接受第三方子资源。
        context.route("**/*", lambda route: route.continue_() if check("read", route.request.url) == "ALLOW" else route.abort())
        page = context.new_page()
        if live:
            # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
            page.goto("https://example.com", timeout=15000)
            if check("read", page.url) != "ALLOW":
                raise RuntimeError("最终 URL 越界")
        else:
            page.set_content('<html><head><title>课程演示</title></head><body><h1>虚构页面</h1><p>没有登录或发送功能。</p></body></html>')
        proposals = [{"action": "read", "url": "https://example.com"}, {"action": "send", "url": "https://example.com"}, {"action": "read", "url": "https://evil.test"}]
        for proposal in proposals:
            verdict = check(**proposal)
            record = {**proposal, "policy": verdict, "executed": False}
            if verdict == "ALLOW":
                record.update({"title": page.title(), "url_observed": page.url, "executed": True})
                page.screenshot(path=str(output / "observed.png"), full_page=True)
            else:
                record["reason"] = "需可信用户批准，当前演示停止该动作" if verdict == "ASK" else "策略拒绝"
            trace.append(record)
        browser.close()
    # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    (output / "trace.json").write_text(json.dumps({"mode": "真实浏览器/固定提议", "network": live, "steps": trace}, ensure_ascii=False, indent=2))
    return trace


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--live", action="store_true", help="访问 example.com；默认只用内存页面")
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--output", type=Path, default=Path("/tmp/ai-learn-browser"))
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(run(args.output, args.live), ensure_ascii=False, indent=2))
