"""检查 Markdown 小节存在且非空；内容准确性另由逐项人工量规判断。"""

# 结构检查只认约定标题与非空正文；错误命令即使有文字，也可能需要人工发现。
import json
import re
import sys
from pathlib import Path


def review(path):
    if not path.is_file():
        return {'status':'FAIL','issues':['文件不存在']}
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
    text=path.read_text(encoding='utf-8')
    sections={}
    for match in re.finditer(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)',text,flags=re.M|re.S):
        sections[match.group(1).strip()]=match.group(2).strip()
    issues=[]
    for title in ['用途','运行','验收']:
        if title not in sections: issues.append('缺少标题：'+title)
        elif not re.sub(r'[`\s#*-]','',sections[title]): issues.append('小节为空：'+title)
    return {'status':'FAIL' if issues else 'PASS','issues':issues,
            'scope':'仅结构与非空检查；运行说明准确性需实际执行核对'}


if __name__=='__main__':
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('sample.md')
    report=review(path)
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(report['status']!='PASS')
