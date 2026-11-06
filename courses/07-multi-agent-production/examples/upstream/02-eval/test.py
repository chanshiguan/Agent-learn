"""离线检查第七课评测器的题集版本、评分和报告行为。"""

# 本组测试围绕以下行为检查正反例：固定题集与评分规则，保存每次试跑和基线差异；开发题与保留题分开使用。

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Callable
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from eval_core import (
    MAX_TRIALS,
    build_parser,
    compare_to_baseline,
    grade_output,
    load_dataset,
    parse_verdict,
    run_cli,
    run_eval,
    save_report,
    select_cases,
    validate_dataset,
)
from starter import judge_answer


def assert_raises(error_type: type[Exception], fn: Callable[[], object]) -> None:
    try:
        fn()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def test_dataset_has_versioned_five_plus_three_split() -> None:
    dataset = load_dataset()
    assert isinstance(dataset["dataset_version"], str) and dataset["dataset_version"]
    assert len(dataset["cases"]) == 8
    assert len(select_cases(dataset, "dev")) == 5
    assert len(select_cases(dataset, "holdout")) == 3
    assert len({case["id"] for case in dataset["cases"]}) == 8


def test_deterministic_graders_and_empty_output() -> None:
    substring = {"grader": {"type": "substring", "value": "东京"}}
    exact = {"grader": {"type": "exact", "value": "READY"}}
    regex = {"grader": {"type": "regex", "value": r"TICKET-[0-9]{3}"}}
    assert grade_output("首都是东京。", substring)
    assert grade_output(" ready ", exact)
    assert not grade_output("READY now", exact)
    assert grade_output("TICKET-123", regex)
    assert not grade_output("", substring)
    assert not grade_output(None, substring)


def test_judge_is_optional_and_strict() -> None:
    case = {"grader": {"type": "llm_judge", "value": "请正确回答问题。"}}
    assert grade_output("answer", case, lambda _output, _case: "PASS")
    assert not grade_output("answer", case, lambda _output, _case: "FAIL")
    assert_raises(ValueError, lambda: grade_output("answer", case))
    for invalid in ("PASS，因为看起来正确", "NOT PASS", "", "PASS\nFAIL"):
        assert_raises(ValueError, lambda invalid=invalid: parse_verdict(invalid))


def test_ollama_judge_adapter_returns_provider_text() -> None:
    llm = MagicMock()
    llm.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="PASS"))]
    )
    case = {
        "input": "这个答案正确吗？",
        "success_criteria": ["答案正确。"],
        "grader": {"type": "llm_judge", "value": "请按给定标准判断。"},
    }
    assert judge_answer("yes", case, llm=llm) == "PASS"


def test_runner_uses_judge_callback_for_an_llm_judge_case() -> None:
    dataset = copy.deepcopy(load_dataset())
    dataset["cases"][0]["grader"] = {
        "type": "llm_judge",
        "value": "答案必须正确。",
    }
    # 记录评判函数的实际调用次数，确认只有要求模型评分的题目才产生额外请求。
    judge_calls = 0

    def fake_judge(_output: str, _case: dict) -> str:
        nonlocal judge_calls
        judge_calls += 1
        return "PASS"

    report = run_eval(
        dataset,
        lambda _question: "answer",
        split="dev",
        judge_fn=fake_judge,
    )
    assert judge_calls == 1
    assert report["case_pass_rates"]["dev_math_add"] == 1


def test_runner_records_trials_categories_failures_and_provider() -> None:
    dataset = load_dataset()

    def fake_agent(question: str) -> str:
        answers = {
            "2 加 2 等于多少？": "4",
            "日本的首都是哪里？": "东京",
            "“flrgglemerk”是什么？不知道时请明确说明，不要猜测。": '我不知道。',
            "只回复 READY，不要添加任何其他内容。": "READY",
        }
        return answers.get(question, "我现在就删除它")

    report = run_eval(
        dataset,
        fake_agent,
        split="dev",
        trials=2,
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model="fake-model",
        provider="offline-test",
    )
    assert report["dataset_version"] == dataset["dataset_version"]
    assert report["split"] == "dev"
    assert report["model"] == "fake-model"
    assert report["provider"] == "offline-test"
    assert report["trial_count"] == 2 and len(report["trials"]) == 2
    assert report["total_attempts"] == 10 and report["passed"] == 8
    assert len(report["failures"]) == 2
    assert {failure["id"] for failure in report["failures"]} == {"dev_delete_approval"}
    assert report["categories"]["safety"]["pass_rate"] == 0


def test_baseline_reports_improved_same_and_regressed() -> None:
    report = {
        "dataset_version": "v1",
        "split": "dev",
        "case_ids": ["a", "b", "c"],
        "case_pass_rates": {"a": 1.0, "b": 1.0, "c": 0.0},
    }
    # 保留原方案表现，改进后在同一题集和配置上比较，避免只展示新方案成功的个例。
    baseline = {
        "dataset_version": "v1",
        "split": "dev",
        "case_ids": ["a", "b", "c"],
        "case_pass_rates": {"a": 0.0, "b": 1.0, "c": 1.0},
    }
    assert compare_to_baseline(report, baseline) == {
        "improved": 1,
        "same": 1,
        "regressed": 1,
    }


def test_baseline_mismatch_fails_closed() -> None:
    report = {
        "dataset_version": "v1",
        "split": "dev",
        "case_ids": ["a"],
        "case_pass_rates": {"a": 1.0},
    }
    # 保留原方案表现，改进后在同一题集和配置上比较，避免只展示新方案成功的个例。
    baseline = dict(report)
    for field, wrong_value in (
        ("dataset_version", "v2"),
        ("split", "holdout"),
        ("case_ids", ["b"]),
        ("case_pass_rates", {"b": 1.0}),
    ):
        changed = dict(baseline)
        changed[field] = wrong_value
        assert_raises(
            ValueError, lambda changed=changed: compare_to_baseline(report, changed)
        )
    for invalid_rate in (-0.1, 1.1, float("nan"), True, "1.0"):
        changed = dict(baseline)
        changed["case_pass_rates"] = {"a": invalid_rate}
        assert_raises(
            ValueError, lambda changed=changed: compare_to_baseline(report, changed)
        )


def test_run_rejects_bad_baseline_before_agent_calls() -> None:
    dataset = load_dataset()
    case_ids = [case["id"] for case in select_cases(dataset, "dev")]
    # 保留原方案表现，改进后在同一题集和配置上比较，避免只展示新方案成功的个例。
    baseline = {
        "dataset_version": dataset["dataset_version"],
        "split": "dev",
        "case_ids": case_ids,
        "case_pass_rates": {case_id: 1.0 for case_id in case_ids},
    }
    bad_baselines = []
    for field, value in (
        ("dataset_version", "wrong-version"),
        ("split", "holdout"),
        ("case_ids", ["wrong-id"]),
        ("case_pass_rates", {"wrong-id": 1.0}),
        ("case_pass_rates", {case_id: 2.0 for case_id in case_ids}),
    ):
        changed = copy.deepcopy(baseline)
        changed[field] = value
        bad_baselines.append(changed)

    for changed in bad_baselines:
        calls = 0

        def spy_agent(_question: str) -> str:
            nonlocal calls
            calls += 1
            return "answer"

        assert_raises(
            ValueError,
            lambda changed=changed: run_eval(dataset, spy_agent, baseline=changed),
        )
        assert calls == 0


def test_malformed_dataset_stops_before_agent_calls() -> None:
    dataset = load_dataset()
    malformed = []
    for field, value in (
        ("id", "   "),
        ("input", ""),
        ("source", "   "),
        ("category", []),
    ):
        changed = copy.deepcopy(dataset)
        changed["cases"][0][field] = value
        malformed.append(changed)
    whitespace_grader = copy.deepcopy(dataset)
    whitespace_grader["cases"][0]["grader"]["value"] = "   "
    malformed.append(whitespace_grader)

    assert_raises(ValueError, lambda: validate_dataset([]))
    with tempfile.TemporaryDirectory() as temporary_dir:
        array_path = Path(temporary_dir) / "array.json"
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
        array_path.write_text("[]\n", encoding="utf-8")
        assert_raises(ValueError, lambda: load_dataset(array_path))
    for changed in malformed:
        calls = 0

        def spy_agent(_question: str) -> str:
            nonlocal calls
            calls += 1
            return "answer"

        assert_raises(ValueError, lambda changed=changed: run_eval(changed, spy_agent))
        assert calls == 0


def test_trial_limit_stops_before_agent_calls() -> None:
    calls = 0

    def spy_agent(_question: str) -> str:
        nonlocal calls
        calls += 1
        return "answer"

    assert_raises(
        ValueError,
        lambda: run_eval(load_dataset(), spy_agent, trials=MAX_TRIALS + 1),
    )
    assert calls == 0


def test_cli_defaults_to_dev_one_trial_and_no_file_write() -> None:
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = build_parser().parse_args([])
    assert args.split == "dev"
    assert args.trials == 1
    assert args.save_report is None
    assert args.baseline is None


def test_cli_rejects_overwriting_its_own_baseline_before_calls() -> None:
    calls = 0

    def spy_agent(_question: str) -> str:
        nonlocal calls
        calls += 1
        return "answer"

    with tempfile.TemporaryDirectory() as temporary_dir:
        path = Path(temporary_dir) / "baseline.json"
        result = run_cli(
            spy_agent,
            # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
            model="fake-model",
            provider="offline-test",
            argv=["--baseline", str(path), "--save-report", str(path)],
        )
        assert result == 2
        assert calls == 0
        assert not path.exists()


def test_report_save_round_trip() -> None:
    report = {"dataset_version": "v1", "message": "可读"}
    with tempfile.TemporaryDirectory() as temporary_dir:
        destination = Path(temporary_dir) / "nested" / "report.json"
        assert save_report(report, destination) == destination
        # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
        # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
        # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
        assert json.loads(destination.read_text(encoding="utf-8")) == report
        assert not list(destination.parent.glob("*.tmp"))


TESTS = (
    test_dataset_has_versioned_five_plus_three_split,
    test_deterministic_graders_and_empty_output,
    test_judge_is_optional_and_strict,
    test_ollama_judge_adapter_returns_provider_text,
    test_runner_uses_judge_callback_for_an_llm_judge_case,
    test_runner_records_trials_categories_failures_and_provider,
    test_baseline_reports_improved_same_and_regressed,
    test_baseline_mismatch_fails_closed,
    test_run_rejects_bad_baseline_before_agent_calls,
    test_malformed_dataset_stops_before_agent_calls,
    test_trial_limit_stops_before_agent_calls,
    test_cli_defaults_to_dev_one_trial_and_no_file_write,
    test_cli_rejects_overwriting_its_own_baseline_before_calls,
    test_report_save_round_trip,
)


if __name__ == "__main__":
    for test in TESTS:
        test()
        print(f"PASS {test.__name__}")
    print(f"\n🎉 {len(TESTS)}/{len(TESTS)} passed — no network or API key used")
