# 目的：保留输出文件名参数，下一次实验不要覆盖上一份基线。
# 预期：同一份题单与快照可重复观察；记录不自动等于通过。
import argparse
import json
from .evaluation import evaluate


def main():
    parser = argparse.ArgumentParser(description="记录固定题集表现")
    parser.add_argument("--cases",default="eval/dev.json")
    parser.add_argument("--method",default="keyword")
    parser.add_argument("--generate",action="store_true")
    parser.add_argument("--output",default="evaluation.json")
    parser.add_argument("--expand",action="store_true")
    parser.add_argument("--rerank",action="store_true")
    parser.add_argument("--rewrite",action="store_true")
    args=parser.parse_args()
    print(json.dumps(evaluate(args.cases,args.method,args.generate,args.expand,args.rerank,args.rewrite,args.output),ensure_ascii=False,indent=2))
