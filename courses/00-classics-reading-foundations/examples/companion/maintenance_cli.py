# 目的：每次候选版本重跑，而不复制上一版记录里的成功结论。
# 预期：生成 release-manifest.json，原业务数据不改动。
import argparse
import json
from .files import save
from .state import initialize
from .maintenance import manifest, backup, restore


def main(kind="manifest"):
    parser=argparse.ArgumentParser(description="记录、备份与恢复")
    if kind=="backup":parser.add_argument("destination")
    elif kind=="restore":
        parser.add_argument("source");parser.add_argument("destination")
    args=parser.parse_args();initialize()
    if kind=="backup":result=backup(args.destination)
    elif kind=="restore":result=restore(args.source,args.destination)
    else:
        result=manifest();save("release-manifest.json",result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
