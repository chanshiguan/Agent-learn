# 目的：导入资料与构建向量索引不是同一件事；分开命令便于定位哪一步失败。
# 预期：index 命令明确完成建索引，查询不偷偷重建。
import json
from .vectors import build_index


def main():
    print(json.dumps(build_index(),ensure_ascii=False,indent=2))
