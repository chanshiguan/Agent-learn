"""课程命令入口；每个子命令只新增一件事，不要求一开始理解整个项目。"""
import argparse
import getpass
import json
import sys
import uuid
from pathlib import Path

from .files import load, save
from .state import Actor, initialize


def main():
    parser = argparse.ArgumentParser(description="名著伴读课程练习")
    sub = parser.add_subparsers(dest="command", required=True)
    manual = sub.add_parser("manual", help="第 5 章：显式选择一段资料")
    manual.add_argument("--file", default="data/output/first.json")
    manual.add_argument("--start", type=int, default=200)
    manual.add_argument("--chars", type=int, default=900)
    manual.add_argument("--question", default="这份讲稿怎样解释文言文序言与白话日记的关系？")
    manual.add_argument("--no-context", action="store_true")
    ingest = sub.add_parser("ingest", help="第 6 章：整理讲稿和来源")
    ingest.add_argument("--source", default="data/input")
    ingest.add_argument("--strategy", choices=["fixed", "paragraph", "heading"], default="fixed")
    ingest.add_argument("--size", type=int, default=600)
    ingest.add_argument("--overlap", type=int, default=60)
    ingest.add_argument("--tenant", default="demo")
    ingest.add_argument("--book", default="狂人日记")
    for command in ("search", "ask", "direct-vector"):
        item = sub.add_parser(command)
        item.add_argument("question")
        item.add_argument("--method", choices=["keyword", "semantic", "hybrid"], default="keyword")
        item.add_argument("--book", default="狂人日记")
        item.add_argument("--tenant", default="demo")
        item.add_argument("--expand", action="store_true")
        item.add_argument("--rerank", action="store_true")
        item.add_argument("--rewrite", action="store_true")
    sub.add_parser("index", help="第 10 章：构建并切换 Qdrant 索引")
    evaluation = sub.add_parser("evaluate")
    evaluation.add_argument("--cases", default="eval/dev.json")
    evaluation.add_argument("--method", choices=["keyword", "semantic", "hybrid"], default="keyword")
    evaluation.add_argument("--generate", action="store_true")
    evaluation.add_argument("--expand", action="store_true")
    evaluation.add_argument("--rerank", action="store_true")
    evaluation.add_argument("--rewrite", action="store_true")
    evaluation.add_argument("--output", default="evaluation.json")
    grade = sub.add_parser("grade")
    grade.add_argument("report")
    user = sub.add_parser("create-user")
    user.add_argument("username")
    user.add_argument("--tenant", default="demo")
    user.add_argument("--role", choices=["reader", "parent", "content_admin"], default="reader")
    family = sub.add_parser("link-family")
    family.add_argument("parent"); family.add_argument("child"); family.add_argument("--tenant", default="demo")
    action = sub.add_parser("action")
    action.add_argument("operation", choices=["draft", "list", "revise", "approve", "notes"])
    action.add_argument("--user", default="reader-a")
    action.add_argument("--text", default="我想回查文言文序言和日记之间的关系。")
    graph = sub.add_parser("graph")
    graph.add_argument("operation", choices=["start", "resume"])
    graph.add_argument("--user", default="reader-a")
    backup = sub.add_parser("backup"); backup.add_argument("destination")
    restore = sub.add_parser("restore"); restore.add_argument("source"); restore.add_argument("destination")
    sub.add_parser("manifest")
    args = parser.parse_args()
    # 前期检索实验不提前创建业务数据库；到账号、审批与维护练习才准备状态表。
    if args.command in {"create-user", "link-family", "action", "graph", "backup", "manifest"}:
        initialize()
    if args.command == "manual":
        from .models import complete
        from .rag import answer
        document = json.loads(Path(args.file).read_text(encoding="utf-8"))
        text = document["paragraphs"][0]["text"][args.start:args.start + args.chars]
        if args.no_context:
            result = complete([{"role": "user", "content": args.question}])
            result["knowledge_base_used"] = False
        else:
            if not text:
                raise ValueError("选定范围没有文字，请检查起点与长度。")
            result = answer(args.question, [{"id": "manual-01", "file": document["source_file"], "kind": "讲解稿", "text": text, "start": args.start}])
        save("manual-no-context.json" if args.no_context else "manual-context.json", result)
    elif args.command == "ingest":
        from .corpus import ingest
        result = ingest(args.source, args.strategy, args.size, args.overlap, args.tenant, args.book)
    elif args.command in {"search", "ask", "direct-vector"}:
        from .rag import retrieve, answer, rewrite, rerank
        query = rewrite(args.question) if args.rewrite else args.question
        if args.command == "direct-vector":
            from .corpus import visible
            from .vectors import embed
            chunks = visible(load("corpus.json")["chunks"], args.tenant, args.book)
            if not chunks:
                raise ValueError("没有当前范围的资料。")
            vectors = embed([c["text"] for c in chunks]); vector = embed([query])[0]
            hits = sorted([{**c, "score": sum(a * b for a, b in zip(v, vector))} for c, v in zip(chunks, vectors)], key=lambda c: -c["score"])[:5]
        else:
            hits = retrieve(query, args.tenant, args.book, args.method, expand=args.expand)
        if args.rerank:
            hits = rerank(args.question, hits)
        result = answer(args.question, hits) if args.command == "ask" else {"question": args.question, "query": query, "hits": hits}
        save(f"{args.command}.json", result)
    elif args.command == "index":
        from .vectors import build_index
        result = build_index()
    elif args.command == "evaluate":
        from .evaluation import evaluate
        result = evaluate(args.cases, args.method, args.generate, args.expand, args.rerank, args.rewrite, args.output)
    elif args.command == "grade":
        from .evaluation import quality_gate
        result = quality_gate(args.report)
    elif args.command == "create-user":
        from .auth import create_user
        password = getpass.getpass("设置至少 12 字符的口令（不回显）：")
        if password != getpass.getpass("再次输入："):
            raise ValueError("两次口令不同。")
        create_user(args.tenant, args.username, password, args.role)
        result = {"created": args.username, "role": args.role}
    elif args.command == "link-family":
        from .auth import link_family
        link_family(args.tenant, args.parent, args.child)
        result = {"linked": True, "scope": "家长只读显式进度，不读私密对话"}
    elif args.command in {"action", "graph"}:
        from . import actions
        actor = Actor("demo", args.user)
        if args.command == "action" and args.operation == "draft":
            result = actions.draft(actor, "note", args.text, uuid.uuid4().hex)
        elif args.command == "action" and args.operation in {"list", "notes"}:
            result = actions.pending(actor) if args.operation == "list" else actions.notes(actor)
        else:
            identity = input("输入要操作的本人草稿 ID：").strip()
            item = next((x for x in actions.pending(actor) if x["id"] == identity), None)
            if not item:
                raise ValueError("未找到本人草稿。")
            if args.command == "action" and args.operation == "revise":
                result = actions.revise(actor, identity, args.text)
            elif args.command == "graph" and args.operation == "start":
                from .graph import run_review
                result = run_review(actor, identity)
            else:
                preview = load("graph-preview.json") if args.command == "graph" else item
                if not preview or preview["id"] != identity:
                    raise ValueError("没有匹配的预览文件，请重新开始。")
                print(json.dumps(preview, ensure_ascii=False, indent=2))
                confirmed = input("确认保存以上当前预览？输入 YES：") == "YES"
                if not confirmed:
                    result = {"status": "not_approved"}
                elif args.command == "graph":
                    from .graph import run_review
                    result = run_review(actor, identity, {"revision": preview["revision"], "digest": preview["digest"], "confirmed": True})
                else:
                    result = actions.approve(actor, identity, item["revision"], item["digest"], True)
    elif args.command in {"backup", "restore", "manifest"}:
        from . import maintenance
        if args.command == "backup": result = maintenance.backup(args.destination)
        elif args.command == "restore": result = maintenance.restore(args.source, args.destination)
        else:
            result = maintenance.manifest(); save("release-manifest.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "grade" and not result["passed"]:
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, PermissionError, FileNotFoundError) as error:
        print(f"未完成：{error}", file=sys.stderr)
        sys.exit(2)
    except Exception as error:
        print(f"运行失败：{type(error).__name__}。先检查对应服务与依赖；不要分享包含凭据的原始错误。", file=sys.stderr)
        sys.exit(2)
