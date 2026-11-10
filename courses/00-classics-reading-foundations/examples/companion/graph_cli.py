# 目的：恢复必须使用已显示的具体预览，不能只传一个“同意”就写入。
# 预期：不同进程的 start/resume 能完成一次批准。
import argparse
import json
from .files import load
from .graph import run_review
from .state import Actor,initialize


def main():
    parser=argparse.ArgumentParser(description="暂停与恢复同一批准")
    parser.add_argument("operation",choices=["start","resume"])
    parser.add_argument("--user",default="reader-a")
    args=parser.parse_args();initialize();actor=Actor("demo",args.user)
    identity=input("本人草稿 ID：").strip()
    decision=None
    if args.operation=="resume":
        preview=load("graph-preview.json")
        if not preview or preview["id"]!=identity:raise ValueError("请先取得匹配预览。")
        print(json.dumps(preview,ensure_ascii=False,indent=2))
        if input("确认这份预览？输入 YES：")!="YES":
            print("没有批准，保持暂停。")
            return
        decision={"revision":preview["revision"],"digest":preview["digest"],"confirmed":True}
    print(json.dumps(run_review(actor,identity,decision),ensure_ascii=False,indent=2))
