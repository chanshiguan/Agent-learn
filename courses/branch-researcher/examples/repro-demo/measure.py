"""固定虚构数据的可复现实验，不是论文训练结果。"""

# 从同目录读取各题的 correct 标记，计算样本数与准确率，再保存指标；它没有训练或评估新模型。
import csv
import json
from pathlib import Path

rows=list(csv.DictReader(Path('data.csv').open()))
values=[int(row['correct']) for row in rows]
if not values or any(value not in (0,1) for value in values):
    raise ValueError('correct 必须为0或1，且至少一行')
# 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
# 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
# indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
Path('metrics.json').write_text(json.dumps({'count':len(values),'accuracy':sum(values)/len(values)},indent=2))
# 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
print(Path('metrics.json').read_text())
