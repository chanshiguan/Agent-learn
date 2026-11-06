"""记录时间、事件和工具类别，不存工具输入、命令正文或凭证。"""

# Hook 从标准输入取得事件；保存的是少量事件字段，不是完整输入副本。
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# 只接受约定事件名和工具名，其余归为 other，避免任意输入进入日志。
def observe(payload, directory):
    event = payload.get("hook_event_name", "unknown")
    if event not in {"PreToolUse", "PostToolUse", "SessionStart", "Stop"}:
        event = "other"
    tool = payload.get("tool_name", "unknown")
    if tool not in {"Read", "Write", "Edit", "Bash", "Glob", "Grep", "Agent"}:
        tool = "other"
    # 只挑白名单字段写日志，不复制 payload 中的参数、正文或密钥。
    record = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "event": event, "tool_name": tool, "observed": True}
    directory.mkdir(parents=True, exist_ok=True)
    # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
    with (directory / "events.jsonl").open("a", encoding="utf-8") as stream:
        # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
        # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


if __name__ == "__main__":
    payload = json.load(sys.stdin)
    location = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / ".course-hook-log"
    observe(payload, location)
