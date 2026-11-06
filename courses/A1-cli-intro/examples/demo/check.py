
# 只检查教学 README 里约定的内容；修改 README 后重跑，不要通过删检查来获得通过。
from pathlib import Path

path = Path(__file__).with_name("README.md")
# 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
# encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
text = path.read_text(encoding="utf-8")
assert text.startswith("# 学习演示项目"), "缺项目标题"
assert "python check.py" in text, "丢失检查命令"
assert "虚构资料" in text, "丢失资料说明"
print("PASS：标题、检查命令和资料说明仍存在")
