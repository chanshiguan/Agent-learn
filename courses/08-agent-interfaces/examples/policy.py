"""动作策略检查器；不是网络隔离或完整浏览器沙箱。"""

# 先解析 URL 并核对精确主机，再按动作分类；ASK 只表示待批准，不会执行操作。
from urllib.parse import urlsplit


def check(action, url):
    try:
        parts = urlsplit(url)
        port = parts.port
    except (ValueError, TypeError):
        return "BLOCK"
    if parts.scheme != "https" or parts.hostname != "example.com" or port not in {None, 443}:
        return "BLOCK"
    if parts.username is not None or parts.password is not None:
        return "BLOCK"
    if not isinstance(action, str):
        return "BLOCK"
    name = action.strip().lower()
    if name in {"read", "screenshot"}:
        return "ALLOW"
    if name in {"login", "purchase", "delete", "send"}:
        return "ASK"
    return "BLOCK"


if __name__ == "__main__":
    for action, url in [("read", "https://example.com"), ("send", "https://example.com"), ("read", "https://example.com.evil.test"), ("read", "file:///etc/passwd")]:
        print(action, url, check(action, url))
