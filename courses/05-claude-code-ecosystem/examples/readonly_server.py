"""MCP Python SDK 1.x 的 stdio 示例。不是手写最新协议实现。"""

# MCP 服务的标准输出用于协议消息，调试信息不能随意 print 到这里。
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 把相对路径变成绝对路径并解析符号链接；涉及目录权限时，还要检查解析后的位置是否在允许目录内。
ROOT = Path(__file__).resolve().parent / "demo-data"
server = FastMCP("course-readonly")


# 先把路径解析成真实位置再检查范围；教学目录需可信，不能防并发替换文件的攻击。
@server.tool()
def read_note(name: str) -> str:
    """读取教学目录里的 UTF-8 txt 文件，最多 20 KB。"""
    # 把相对路径变成绝对路径并解析符号链接；涉及目录权限时，还要检查解析后的位置是否在允许目录内。
    path = (ROOT / name).resolve()
    # 用解析后的路径检查是否位于允许目录；字符串前缀相同不等于属于同一目录。
    # 把相对路径变成绝对路径并解析符号链接；涉及目录权限时，还要检查解析后的位置是否在允许目录内。
    if not path.is_relative_to(ROOT.resolve()) or path.suffix != ".txt":
        raise ValueError("只允许 demo-data 内的 txt 文件")
    # 先限制大小，再读完整正文，避免一次调用读入过大文件。
    if path.stat().st_size > 20_000:
        raise ValueError("文件超过教学上限")
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    server.run(transport="stdio")
