"""README 标题与正文的确定性初筛；不执行输入中的命令。"""

# 先识别约定标题，再检查正文是否为空；这只是结构检查，运行命令是否正确还需核对。
import argparse
import json
import re
from pathlib import Path

REQUIRED = ("项目目的", "安装方法", "运行示例", "许可证")


def check(path):
    path = Path(path)
    if not path.is_file():
        return {"status": "FAIL", "reason": "文件不存在", "path": str(path)}
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
    source = path.read_text(encoding="utf-8")
    sections = {name.strip(): body.strip() for name, body in
                re.findall(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", source, re.M | re.S)}
    missing = [name for name in REQUIRED if not sections.get(name)]
    return {"status": "FAIL" if missing else "NEEDS_REVIEW", "missing": missing,
            "sections": {name: sections.get(name, "") for name in REQUIRED},
            "meaning": "只检查四个约定标题及非空正文；语义、命令和许可需逐项复核"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("path", type=Path)
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    result = check(parser.parse_args().path)
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["status"] == "FAIL" else 0)
