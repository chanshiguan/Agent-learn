# 目的：自动流水线需要知道通过还是失败；失败应退出非零，而不只打印一句提醒。
# 预期：未完成核对时退出码为 2，并说明缺失项。
import argparse
import json
from .evaluation import quality_gate


def main():
    parser=argparse.ArgumentParser(description="检查已人工核对的报告")
    parser.add_argument("report")
    result=quality_gate(parser.parse_args().report)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not result["passed"]:
        raise SystemExit(2)
