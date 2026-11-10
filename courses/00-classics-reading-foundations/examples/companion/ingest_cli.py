# 目的：同一个整理函数接受不同大小；这里不增加检索，也不会连接模型。
# 预期：ingest 命令输出文档数、块数与资料版本。
import argparse
import json
from .corpus import ingest


def main():
    parser = argparse.ArgumentParser(description="整理当前作品讲稿")
    parser.add_argument("--source", default="data/input")
    parser.add_argument("--strategy", default="fixed")
    parser.add_argument("--size", type=int, default=600)
    parser.add_argument("--overlap", type=int, default=60)
    parser.add_argument("--tenant", default="demo")
    parser.add_argument("--book", default="狂人日记")
    args = parser.parse_args()
    print(json.dumps(ingest(args.source,args.strategy,args.size,args.overlap,args.tenant,args.book), ensure_ascii=False, indent=2))
