"""离线检查批准、检查点、恢复以及同一动作不会重复执行的约定。"""

# 本组测试围绕以下行为检查正反例：先保存待审动作，决定后写本地账本，再更新状态；恢复时核对记录，避免重复效果。

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from starter import (
    CANCELLED,
    COMPLETED,
    WAITING,
    StateError,
    resume_workflow,
    start_workflow,
)


# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _paths(directory: str) -> tuple[Path, Path]:
    root = Path(directory)
    return root / "state.json", root / "ledger.json"


def test_start_pauses_without_a_side_effect() -> None:
    with tempfile.TemporaryDirectory() as directory:
        state_path, ledger_path = _paths(directory)
        state = start_workflow(state_path, action='发布草稿', idempotency_key="task-001")
        assert state["status"] == WAITING
        assert state["approval"] is None
        assert not ledger_path.exists()


def test_rejection_cancels_without_a_side_effect() -> None:
    with tempfile.TemporaryDirectory() as directory:
        state_path, ledger_path = _paths(directory)
        start_workflow(state_path, action='发布草稿', idempotency_key="task-002")
        state = resume_workflow(state_path, ledger_path, decision="reject")
        assert state["status"] == CANCELLED
        assert state["approval"] == "rejected"
        assert not ledger_path.exists()


def test_approval_executes_exactly_once() -> None:
    with tempfile.TemporaryDirectory() as directory:
        state_path, ledger_path = _paths(directory)
        start_workflow(state_path, action='发布草稿', idempotency_key="task-003")
        first = resume_workflow(state_path, ledger_path, decision="approve")
        second = resume_workflow(state_path, ledger_path, decision="approve")
        # 执行登记用于判断同一动作是否已经发生；只保存模型对话不足以阻止恢复时重复执行副作用。
        # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
        # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
        # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        assert first["status"] == COMPLETED
        assert second == first
        assert ledger["executed"] == [
            {"idempotency_key": "task-003", "action": '发布草稿'}
        ]


def test_resume_after_ledger_write_does_not_repeat_the_side_effect() -> None:
    with tempfile.TemporaryDirectory() as directory:
        state_path, ledger_path = _paths(directory)
        start_workflow(state_path, action='发布草稿', idempotency_key="task-004")
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        ledger_path.write_text(
            # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
            json.dumps(
                {
                    "executed": [
                        {"idempotency_key": "task-004", "action": '发布草稿'}
                    ]
                }
            ),
            # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
            encoding="utf-8",
        )
        state = resume_workflow(state_path, ledger_path, decision="approve")
        # 执行登记用于判断同一动作是否已经发生；只保存模型对话不足以阻止恢复时重复执行副作用。
        # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
        # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
        # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        assert state["status"] == COMPLETED
        assert len(ledger["executed"]) == 1


def test_recorded_side_effect_wins_over_a_late_reject() -> None:
    with tempfile.TemporaryDirectory() as directory:
        state_path, ledger_path = _paths(directory)
        start_workflow(state_path, action='发布草稿', idempotency_key="task-008")
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        ledger_path.write_text(
            # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
            json.dumps(
                {
                    "executed": [
                        {"idempotency_key": "task-008", "action": '发布草稿'}
                    ]
                }
            ),
            # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
            encoding="utf-8",
        )
        state = resume_workflow(state_path, ledger_path, decision="reject")
        # 执行登记用于判断同一动作是否已经发生；只保存模型对话不足以阻止恢复时重复执行副作用。
        # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
        # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
        # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        assert state["status"] == COMPLETED
        assert state["approval"] == "approved"
        assert len(ledger["executed"]) == 1


def test_completed_checkpoint_requires_a_matching_ledger_record() -> None:
    with tempfile.TemporaryDirectory() as directory:
        state_path, ledger_path = _paths(directory)
        start_workflow(state_path, action='发布草稿', idempotency_key="task-009")
        # 依据批准决定和已有登记恢复工作流。
        resume_workflow(state_path, ledger_path, decision="approve")
        # 删除 登记文件路径（ledger_path） 指定的文件。
        ledger_path.unlink()
        try:
            # 依据批准决定和已有登记恢复工作流。
            resume_workflow(state_path, ledger_path, decision="approve")
        except StateError as error:
            assert "缺少对应执行登记" in str(error)
        else:
            raise AssertionError("completed state without a ledger record must fail closed")

    with tempfile.TemporaryDirectory() as directory:
        state_path, ledger_path = _paths(directory)
        start_workflow(state_path, action='发布草稿', idempotency_key="task-010")
        # 依据批准决定和已有登记恢复工作流。
        resume_workflow(state_path, ledger_path, decision="approve")
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        ledger_path.write_text(
            # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
            json.dumps(
                {
                    "executed": [
                        {"idempotency_key": "task-010", "action": '删除草稿'}
                    ]
                }
            ),
            # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
            encoding="utf-8",
        )
        try:
            # 依据批准决定和已有登记恢复工作流。
            resume_workflow(state_path, ledger_path, decision="approve")
        except StateError as error:
            assert "另一项动作" in str(error)
        else:
            raise AssertionError("completed state with a mismatched ledger must fail closed")


def test_cancelled_checkpoint_rejects_an_existing_ledger_record() -> None:
    with tempfile.TemporaryDirectory() as directory:
        state_path, ledger_path = _paths(directory)
        start_workflow(state_path, action='发布草稿', idempotency_key="task-011")
        # 依据批准决定和已有登记恢复工作流。
        resume_workflow(state_path, ledger_path, decision="reject")
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        ledger_path.write_text(
            # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
            json.dumps(
                {
                    "executed": [
                        {"idempotency_key": "task-011", "action": '发布草稿'}
                    ]
                }
            ),
            # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
            encoding="utf-8",
        )
        try:
            # 依据批准决定和已有登记恢复工作流。
            resume_workflow(state_path, ledger_path, decision="reject")
        except StateError as error:
            assert "已取消的检查点与已有执行登记冲突" in str(error)
        else:
            raise AssertionError("cancelled state with a ledger record must fail closed")


def test_corrupt_or_mismatched_state_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as directory:
        state_path, ledger_path = _paths(directory)
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
        state_path.write_text("not-json", encoding="utf-8")
        try:
            # 依据批准决定和已有登记恢复工作流。
            resume_workflow(state_path, ledger_path, decision="approve")
        except StateError as error:
            assert "可信的 JSON" in str(error)
        else:
            raise AssertionError("corrupt state must fail closed")

    with tempfile.TemporaryDirectory() as directory:
        state_path, _ = _paths(directory)
        start_workflow(state_path, action='发布草稿', idempotency_key="task-005")
        try:
            start_workflow(state_path, action='删除草稿', idempotency_key="task-005")
        except StateError as error:
            assert "另一项任务" in str(error)
        else:
            raise AssertionError("one key must not be reused for another action")

    with tempfile.TemporaryDirectory() as directory:
        state_path, ledger_path = _paths(directory)
        state = start_workflow(
            state_path,
            action='发布草稿',
            idempotency_key="task-006",
        )
        state["approval"] = "approved"
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
        # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
        state_path.write_text(json.dumps(state), encoding="utf-8")
        try:
            # 依据批准决定和已有登记恢复工作流。
            resume_workflow(state_path, ledger_path, decision="approve")
        except StateError as error:
            assert "不一致" in str(error)
        else:
            raise AssertionError("contradictory status and approval must fail closed")

    with tempfile.TemporaryDirectory() as directory:
        state_path, ledger_path = _paths(directory)
        start_workflow(state_path, action='发布草稿', idempotency_key="task-007")
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        ledger_path.write_text(
            # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
            json.dumps(
                {
                    "executed": [
                        {"idempotency_key": "task-007", "action": '发布草稿'},
                        {"idempotency_key": "task-007", "action": '发布草稿'},
                    ]
                }
            ),
            # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
            encoding="utf-8",
        )
        try:
            # 依据批准决定和已有登记恢复工作流。
            resume_workflow(state_path, ledger_path, decision="approve")
        except StateError as error:
            assert "重复幂等键" in str(error)
        else:
            raise AssertionError("duplicate ledger keys must fail closed")


if __name__ == "__main__":
    tests = (
        test_start_pauses_without_a_side_effect,
        test_rejection_cancels_without_a_side_effect,
        test_approval_executes_exactly_once,
        test_resume_after_ledger_write_does_not_repeat_the_side_effect,
        test_recorded_side_effect_wins_over_a_late_reject,
        test_completed_checkpoint_requires_a_matching_ledger_record,
        test_cancelled_checkpoint_rejects_an_existing_ledger_record,
        test_corrupt_or_mismatched_state_fails_closed,
    )
    for test in tests:
        test()
        print(f"✅ {test.__name__}")
    print("\n🎉 8/8 passed — paused, approved/rejected, reconciled, and executed at most once")
