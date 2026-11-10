# 目的：python -m companion 先运行 __main__.py；把命令名取走后，剩余参数交给本节解析器。这里只接入已经写好的能力。
# 预期：本节命令可以识别，尚未实现的命令会明确拒绝。
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("请在 companion 后写本节子命令。")
    command = sys.argv.pop(1)
    if command == "manual":
        from .manual import main
        main()
    elif command == "ingest":
        from .ingest_cli import main
        main()
    elif command == "search":
        from .query import main
        main('search')
    elif command == "ask":
        from .query import main
        main('ask')
    elif command == "evaluate":
        from .evaluate_cli import main
        main()
    elif command == "grade":
        from .grade_cli import main
        main()
    elif command == "direct-vector":
        from .query import main
        main('direct-vector')
    elif command == "index":
        from .index_cli import main
        main()
    elif command == "action":
        from .actions_cli import main
        main()
    elif command == "graph":
        from .graph_cli import main
        main()
    elif command == "create-user":
        from .accounts_cli import main
        main('create-user')
    elif command == "link-family":
        from .family_cli import main
        main()
    elif command == "manifest":
        from .maintenance_cli import main
        main('manifest')
    elif command == "backup":
        from .maintenance_cli import main
        main('backup')
    elif command == "restore":
        from .maintenance_cli import main
        main('restore')
    else:
        raise SystemExit("当前课程还没有这个命令。")
