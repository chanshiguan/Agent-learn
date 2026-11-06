"""沙箱中的固定绘图任务；读取两列 CSV，输出独立 SVG。"""

# 读取固定 CSV 后输出 SVG；本脚本负责绘图，隔离依靠运行它的容器配置。
import csv
from html import escape
from pathlib import Path


def plot(source, destination):
    # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
    with source.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or len(rows) > 20:
        raise ValueError("需要 1–20 条记录")
    values = [float(row["value"]) for row in rows]
    if any(not 0 <= value <= 10000 for value in values):
        raise ValueError("数值必须在 0–10000")
    scale = 360 / max(max(values), 1)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="600" height="700"><rect width="100%" height="100%" fill="white"/>']
    for i, (row, value) in enumerate(zip(rows, values)):
        y = 20 + i * 32
        parts.append(f'<text x="10" y="{y+15}">{escape(row["label"])}</text><rect x="150" y="{y}" width="{value*scale}" height="22" fill="#9a3412"/><text x="520" y="{y+15}">{value:g}</text>')
    parts.append('</svg>')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
    destination.write_text(''.join(parts))


if __name__ == "__main__":
    plot(Path("/input/data.csv"), Path("/output/chart.svg"))
