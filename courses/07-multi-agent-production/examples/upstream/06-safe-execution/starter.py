"""批准、检查点、恢复和幂等的离线示例。

这里的“外部动作”仅写入一条 JSON 登记，不进行网络请求。
"""

# 先保存待审动作，决定后写本地账本，再更新状态；恢复时核对记录，避免重复效果。

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
WAITING = "waiting_for_approval"
COMPLETED = "completed"
CANCELLED = "cancelled"
VALID_STATUSES = {WAITING, COMPLETED, CANCELLED}
KEY_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,100}$")


class StateError(ValueError):
    """当已保存状态损坏或相互矛盾时抛出，阻止在错误状态下继续执行。"""


def _read_json(path: Path) -> Any:
    try:
        # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
        # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
        # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise StateError(f"无法读取可信的 JSON 状态：{path.name}") from error


# 先写临时文件再替换目标，减少读到半份 JSON 的风险；不等于跨文件事务。
def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
            # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            # 要求系统把写入推进到存储层，降低崩溃后丢失状态的风险；仍需结合原子替换与业务幂等。
            os.fsync(stream.fileno())
        # 按参数替换 temporary 的内容或目标。
        # 使用新内容替换对应目标；在状态保存流程中，原子替换可避免读到半个 JSON 文件。
        temporary.replace(path)
    except Exception:
        # 删除 temporary 指定的文件。
        temporary.unlink(missing_ok=True)
        raise


# 检查待执行动作是否符合本例的字段约定，再允许写入状态。
def _validate_action(action: str) -> str:
    if not isinstance(action, str):
        raise StateError("action 必须是文本")
    cleaned = action.strip()
    if not cleaned or len(cleaned) > 200:
        raise StateError("action 必须包含 1–200 个可见字符")
    return cleaned


def _validate_key(idempotency_key: str) -> str:
    if not isinstance(idempotency_key, str):
        raise StateError("幂等键必须是文本")
    if not KEY_PATTERN.fullmatch(idempotency_key):
        raise StateError(
            "幂等键长度须为 1–100，只能包含字母、数字、点、冒号、连字符或下划线"
        )
    return idempotency_key


# 恢复前检查状态结构及字段关系，损坏记录不能当作可信批准。
def _validate_state(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise StateError("检查点必须是 JSON 对象")
    required = {
        "schema_version",
        "task_id",
        "action",
        "idempotency_key",
        "status",
        "checkpoint",
        "approval",
    }
    if set(payload) != required:
        raise StateError("检查点字段不符合当前结构约定")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise StateError("不支持这个检查点版本")
    _validate_action(payload["action"])
    # 检查幂等键的格式，避免使用不合法标识恢复任务。
    _validate_key(payload["idempotency_key"])
    if payload["task_id"] != payload["idempotency_key"]:
        raise StateError("任务 ID 与幂等键不匹配")
    if payload["status"] not in VALID_STATUSES:
        raise StateError("检查点包含未知状态")
    if type(payload["checkpoint"]) is not int or payload["checkpoint"] < 1:
        raise StateError("检查点编号必须是正整数")
    if payload["approval"] not in {None, "approved", "rejected"}:
        raise StateError("检查点包含未知审批决定")
    expected_approval = {
        WAITING: None,
        COMPLETED: "approved",
        CANCELLED: "rejected",
    }[payload["status"]]
    if payload["approval"] != expected_approval:
        raise StateError("检查点状态与审批决定不一致")
    return payload


# 核对既有执行记录，避免以为读取失败就等于从未执行。
def _load_ledger(path: Path) -> dict[str, list[dict[str, str]]]:
    if not path.exists():
        return {"executed": []}
    payload = _read_json(path)
    if not isinstance(payload, dict) or set(payload) != {"executed"}:
        raise StateError("执行登记字段不符合当前结构约定")
    records = payload["executed"]
    if not isinstance(records, list):
        raise StateError("执行登记中的 records 必须是列表")
    seen_keys: set[str] = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != {"idempotency_key", "action"}:
            raise StateError("执行登记包含无效记录")
        key = _validate_key(record["idempotency_key"])
        _validate_action(record["action"])
        if key in seen_keys:
            raise StateError("执行登记包含重复幂等键")
        seen_keys.add(key)
    return payload


# 只创建待审状态，不在这一步产生已批准动作的效果。
def start_workflow(state_path: Path, *, action: str, idempotency_key: str) -> dict[str, Any]:
    """创建检查点，并在模拟外部动作之前暂停，使批准发生在执行之前。"""

    action = _validate_action(action)
    idempotency_key = _validate_key(idempotency_key)
    if state_path.exists():
        state = _validate_state(_read_json(state_path))
        if state["action"] != action or state["idempotency_key"] != idempotency_key:
            raise StateError("已有检查点属于另一项任务")
        return state

    state = {
        "schema_version": SCHEMA_VERSION,
        "task_id": idempotency_key,
        "action": action,
        "idempotency_key": idempotency_key,
        "status": WAITING,
        "checkpoint": 1,
        "approval": None,
    }
    _atomic_write_json(state_path, state)
    return state


# 先核对状态、决定与账本；已有相同效果时只恢复状态，不重复写入。
def resume_workflow(
    state_path: Path,
    ledger_path: Path,
    *,
    decision: str,
) -> dict[str, Any]:
    """恢复一个暂停任务；用执行登记保证这个串行教学流程中的模拟动作最多执行一次。"""

    if decision not in {"approve", "reject"}:
        raise StateError("decision 必须是 approve 或 reject")
    if not state_path.exists():
        raise StateError("检查点不存在")

    state = _validate_state(_read_json(state_path))
    # 执行登记用于判断同一动作是否已经发生；只保存模型对话不足以阻止恢复时重复执行副作用。
    ledger = _load_ledger(ledger_path)
    key = state["idempotency_key"]
    matching = [record for record in ledger["executed"] if record["idempotency_key"] == key]
    if matching and matching[0]["action"] != state["action"]:
        raise StateError("这个幂等键已用于另一项动作")

    # 登记表记录模拟外部动作。即使检查点显示已结束，也要先核对登记表，
    # 再接受检查点状态或迟到的拒绝决定，防止把已执行动作当作未执行。
    if state["status"] == COMPLETED:
        if not matching:
            raise StateError("已完成的检查点缺少对应执行登记")
        return state
    if state["status"] == CANCELLED:
        if matching:
            raise StateError("已取消的检查点与已有执行登记冲突")
        return state
    if state["status"] != WAITING:
        raise StateError("当前流程没有在等待批准")

    if matching:
        state["approval"] = "approved"
        state["status"] = COMPLETED
        state["checkpoint"] += 1
        _atomic_write_json(state_path, state)
        return state

    if decision == "reject":
        state["approval"] = "rejected"
        state["status"] = CANCELLED
        state["checkpoint"] += 1
        _atomic_write_json(state_path, state)
        return state

    if not matching:
        ledger["executed"].append({"idempotency_key": key, "action": state["action"]})
        # 先写执行登记，再将检查点标为完成。如果进程恰好在两次写入之间退出，
        # 下次恢复可通过登记中的幂等键识别已经发生的动作，
        # 从而避免重复执行。
        _atomic_write_json(ledger_path, ledger)

    state["approval"] = "approved"
    state["status"] = COMPLETED
    state["checkpoint"] += 1
    _atomic_write_json(state_path, state)
    return state


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument(
        "--state",
        type=Path,
        default=Path(".cache/safe-execution-state.json"),
        help="检查点文件（默认 .cache/safe-execution-state.json）",
    )
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path(".cache/safe-execution-ledger.json"),
        help="模拟动作登记表（默认 .cache/safe-execution-ledger.json）",
    )
    # required：明确哪些字段不可缺少；有默认值与必须提供是两种不同的接口约定。
    subparsers = parser.add_subparsers(dest="command", required=True)
    start = subparsers.add_parser("start", help="创建检查点并暂停")
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    # required：明确哪些字段不可缺少；有默认值与必须提供是两种不同的接口约定。
    start.add_argument("--action", required=True)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    # required：明确哪些字段不可缺少；有默认值与必须提供是两种不同的接口约定。
    start.add_argument("--key", required=True)
    resume = subparsers.add_parser("resume", help="批准或拒绝已暂停的任务")
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    # required：明确哪些字段不可缺少；有默认值与必须提供是两种不同的接口约定。
    resume.add_argument("--decision", choices=("approve", "reject"), required=True)
    return parser


def main() -> int:
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = _parser().parse_args()
    try:
        if args.command == "start":
            state = start_workflow(
                args.state,
                action=args.action,
                idempotency_key=args.key,
            )
        else:
            state = resume_workflow(
                args.state,
                args.ledger,
                decision=args.decision,
            )
    except StateError as error:
        print(f"已停止：{error}")
        return 1
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
