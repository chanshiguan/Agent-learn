"""保留原课程标识；目录名不是学习顺序。"""
COURSES = [
    ("04-agent-frameworks", "4", "Workflow Graph 与 Agent 框架", "stages/04-agent-frameworks.zh-Hans.md", "B 线；先完成第三课", "4"),
    ("05-claude-code-ecosystem", "5", "Claude Code 生态系统", "stages/05-claude-code-ecosystem.zh-Hans.md", "A/B 共用；A 线先学 A2，5.1–5.4 为核心", "5"),
    ("06-memory-rag", "6", "RAG 与 Memory", "stages/06-memory-rag.zh-Hans.md", "B 线；推荐第五课之后", "6"),
    ("07-multi-agent-production", "7", "Agent 上线工程", "stages/07-multi-agent-production.zh-Hans.md", "B 线；先有可运行的工具或 RAG 系统", "7"),
    ("07.5-advanced-agentic-concepts", "7.5", "进阶 Agentic 选择", "stages/07.5-advanced-agentic-concepts.zh-Hans.md", "B 线；必须先有第七课的评测和单 Agent 基线", None),
    ("08-agent-interfaces", "8", "Browser Use、Computer Use 与 Sandbox", "stages/08-agent-interfaces.zh-Hans.md", "A/B 共用；最低先修是第三课工具循环；A 线结业前建议学", None),
    ("A1-cli-intro", "A1", "选一个 CLI agent，安全完成第一个任务", "tracks/cli/A1-cli-intro.zh-Hans.md", "A 线；共用基础 0–2 之后", None),
    ("A2-cli-workflow", "A2", "让 CLI agent 按同一套方法做事", "tracks/cli/A2-cli-workflow.zh-Hans.md", "A 线；先学 A1", None),
    ("A3-cli-production", "A3", "把 CLI agent 接入团队流程", "tracks/cli/A3-cli-production.zh-Hans.md", "A 线；先学 A1、A2、第五课核心", None),
    ("branch-researcher", "研究分支", "研究人员延伸路线", "branches/for-researcher.zh-Hans.md", "身份选修；与主线并行，论文核对不要求写 Agent", None),
    ("branch-developer", "开发分支", "开发者延伸路线", "branches/for-developer.zh-Hans.md", "身份选修；推荐 A1→A2→第五课核心→A3", None),
    ("branch-teacher", "教师分支", "教师延伸路线", "branches/for-teacher.zh-Hans.md", "身份选修；从无学生信息的备课草稿开始", None),
    ("branch-knowledge-worker", "知识工作分支", "知识工作者延伸路线", "branches/for-knowledge-worker.zh-Hans.md", "身份选修；先完成一个只读、可核对的任务", None),
    ("branch-everyday-users", "日常分支", "日常用户延伸路线", "branches/for-everyday-users.zh-Hans.md", "身份选修；可以直接进入，不必走完整主线", None),
    ("capstone-a", "结业 A", "CLI Power User 结业专题", "CAPSTONE.zh-Hans.md", "A1→A2→第五课核心→A3；第八课建议完成", None),
    ("capstone-b", "结业 B", "Agent Builder 结业专题", "CAPSTONE.zh-Hans.md", "B 线完成 3→4→5→6→7→7.5→8", None),
]

# 文件名保留，避免旧链接失效；目录与前后章导航统一使用这里的学习顺序。
LESSON_ORDER = {
    "04-agent-frameworks": ["01-guide", "02-readings", "04-patterns", "05-original-labs", "06-framework-apis", "03-workshop", "99-exercises"],
    "06-memory-rag": ["01-guide", "02-readings", "08-example-readings", "05-original-labs", "03-workshop", "04-advanced", "07-direct-readings", "06-abc-experiment", "99-exercises"],
    "07-multi-agent-production": ["01-guide", "02-readings", "07-example-readings", "05-original-labs", "03-workshop", "06-complete-project", "99-exercises"],
    "A2-cli-workflow": ["01-guide", "02-readings", "04-original-cli", "03-workshop", "99-exercises"],
}


def ordered_lessons(source_dir):
    paths = {path.stem: path for path in source_dir.glob("*.md")}
    order = LESSON_ORDER.get(source_dir.parent.name, sorted(paths))
    if len(order) != len(set(order)) or set(order) != set(paths):
        raise ValueError(f"{source_dir}: 学习顺序有重复或遗漏，请同步更新 LESSON_ORDER")
    if not order or order[-1] != "99-exercises":
        raise ValueError(f"{source_dir}: 课后练习必须放在最后")
    return [paths[name] for name in order]
