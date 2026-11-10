# 目的：状态保存在 SQLite 而非 Python 变量；重新启动后仍从数据库确认本人动作。
# 预期：关闭程序再运行 list，旧草稿仍在；批准仍要求当前预览。
import argparse
import json
import uuid
from . import actions
from .state import Actor, initialize


def main():
    parser=argparse.ArgumentParser(description="跨进程检查待确认动作")
    parser.add_argument("operation",choices=["draft","list","notes","revise","approve"])
    parser.add_argument("--user",default="reader-a")
    parser.add_argument("--text",default="我想回查文言文序言和日记之间的关系。")
    args=parser.parse_args();initialize();actor=Actor("demo",args.user)
    if args.operation=="draft":result=actions.draft(actor,"note",args.text,uuid.uuid4().hex)
    elif args.operation=="list":result=actions.pending(actor)
    elif args.operation=="notes":result=actions.notes(actor)
    else:
        identity=input("本人草稿 ID：").strip()
        item=next((x for x in actions.pending(actor) if x["id"]==identity),None)
        if not item:raise ValueError("没有找到本人草稿。")
        if args.operation=="revise":result=actions.revise(actor,identity,args.text)
        else:
            print(json.dumps(item,ensure_ascii=False,indent=2))
            confirmed=input("确认当前预览？输入 YES：")=="YES"
            result=actions.approve(actor,identity,item["revision"],item["digest"],confirmed)
    print(json.dumps(result,ensure_ascii=False,indent=2))
