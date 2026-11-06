"""第七课共用评测器：将题目、评分与具体模型服务分开，以便按相同标准比较。"""

# 固定题集与评分规则，保存每次试跑和基线差异；开发题与保留题分开使用。

from __future__ import annotations

import argparse
import json
import math
import os
import re
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable


DEFAULT_DATASET_PATH = Path(__file__).with_name("eval_cases.json")
VALID_SPLITS = {"dev", "holdout"}
VALID_GRADERS = {"substring", "exact", "regex", "llm_judge"}
MAX_TRIALS = 20


def require_text(value: str | None, label: str) -> str:
    """只返回非空模型正文；缺失正文就停止，避免后续误用无效结果。"""
    text = (value or "").strip()
    if not text:
        raise ValueError(f"{label} 返回了空文本")
    return text


# 严格解析裁判输出；格式错误不能默认判为通过。
def parse_verdict(verdict: str) -> bool:
    """裁判必须只返回完整的 PASS 或 FAIL；包含解释或截断的结果不能冒充有效评分。"""
    match = re.fullmatch(r"(PASS|FAIL)", verdict.strip(), re.IGNORECASE)
    if not match:
        raise ValueError("裁判必须只返回 PASS 或 FAIL")
    return match.group(1).upper() == "PASS"


def load_dataset(path: str | Path = DEFAULT_DATASET_PATH) -> dict[str, Any]:
    """读取带版本号的教学题集，在请求模型前检查字段与评分规则。"""
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
    dataset = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_dataset(dataset)


# 先检查题集字段、划分和评分规则，再发模型请求，避免对坏题集花费调用。
def validate_dataset(dataset: Any) -> dict[str, Any]:
    """在调用模型或裁判之前校验题集字段，防止错误评分配置浪费请求。"""
    if not isinstance(dataset, dict):
        raise ValueError("题集必须是 JSON 对象")
    version = dataset.get("dataset_version")
    cases = dataset.get("cases")
    if (
        not isinstance(version, str)
        or not version.strip()
        or version != version.strip()
    ):
        raise ValueError("dataset_version 必须是两端无空白的非空字符串")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases 必须是非空列表")

    required = {
        "id",
        "split",
        "category",
        "input",
        "success_criteria",
        "grader",
        "source",
    }
    # 跨轮记录已见过的调用 ID，避免模型重复使用同一个 ID 导致结果无法可靠关联。
    seen_ids: set[str] = set()
    seen_splits: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or not required <= case.keys():
            raise ValueError(f"每道题必须包含：{', '.join(sorted(required))}")
        case_id = case["id"]
        if (
            not isinstance(case_id, str)
            or not case_id.strip()
            or case_id != case_id.strip()
            or case_id in seen_ids
        ):
            raise ValueError("题目 ID 必须非空、唯一且两端无空白")
        seen_ids.add(case_id)
        split = case["split"]
        if not isinstance(split, str) or split not in VALID_SPLITS:
            raise ValueError(f"case {case_id}: split 必须是 dev 或 holdout")
        seen_splits.add(split)
        for field in ("category", "input", "source"):
            value = case[field]
            if (
                not isinstance(value, str)
                or not value.strip()
                or value != value.strip()
            ):
                raise ValueError(
                    f"case {case_id}: {field} 必须是两端无空白的非空字符串"
                )
        criteria = case["success_criteria"]
        if (
            not isinstance(criteria, list)
            or not criteria
            or not all(
                isinstance(item, str) and item.strip() and item == item.strip()
                for item in criteria
            )
        ):
            raise ValueError(
                f"case {case_id}: success_criteria 必须是非空字符串列表"
            )
        grader = case["grader"]
        grader_type = grader.get("type") if isinstance(grader, dict) else None
        if not isinstance(grader_type, str) or grader_type not in VALID_GRADERS:
            raise ValueError(f"case {case_id}: 不支持的评分规则")
        if (
            not isinstance(grader.get("value"), str)
            or not grader["value"].strip()
            or grader["value"] != grader["value"].strip()
        ):
            raise ValueError(f"case {case_id}: grader.value 必须是非空字符串")
        if grader_type == "regex":
            try:
                re.compile(grader["value"])
            except re.error as error:
                raise ValueError(
                    f"case {case_id}: 无效的正则表达式"
                ) from error
    if seen_splits != VALID_SPLITS:
        raise ValueError("题集必须同时包含 dev 开发题和 holdout 保留题")
    return dataset


# 按指定划分取题，避免无意把保留题混进日常开发评测。
def select_cases(dataset: dict[str, Any], split: str) -> list[dict[str, Any]]:
    """选择开发集或保留集，不修改原题集，避免选题过程污染后续比较。"""
    if split == "all":
        return list(dataset["cases"])
    if split not in VALID_SPLITS:
        raise ValueError("split 必须是 dev、holdout 或 all")
    return [case for case in dataset["cases"] if case["split"] == split]


# 按每题约定选择评分方式；缺输出或评分器错误也要留下明确结果。
def grade_output(
    output: str | None,
    case: dict[str, Any],
    judge_fn: Callable[[str, dict[str, Any]], str] | None = None,
) -> bool:
    """按本题配置选择判定规则；模型没有输出时直接失败，不能被宽松匹配误判通过。"""
    text = (output or "").strip()
    if not text:
        return False
    grader = case["grader"]
    grader_type = grader["type"]
    expected = grader["value"]
    if grader_type == "substring":
        return expected.casefold() in text.casefold()
    if grader_type == "exact":
        return text.casefold() == expected.strip().casefold()
    if grader_type == "regex":
        return re.fullmatch(expected, text) is not None
    if judge_fn is None:
        raise ValueError("llm_judge 必须显式提供 judge_fn 评分函数")
    return parse_verdict(require_text(judge_fn(text, case), "Judge"))


def _category_summary(
    results: list[dict[str, Any]],
) -> dict[str, dict[str, float | int]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"passed": 0, "total": 0})
    for result in results:
        category = counts[result["category"]]
        category["total"] += 1
        category["passed"] += int(result["passed"])
    return {
        name: {**values, "pass_rate": values["passed"] / values["total"]}
        for name, values in sorted(counts.items())
    }


# 同题与基线逐项比较，分别记录改善、持平和退步。
def compare_to_baseline(
    report: dict[str, Any], baseline: dict[str, Any]
) -> dict[str, int]:
    """只比较同一题集版本与分组的报告；版本不匹配时停止，避免把题目差异误认为模型变化。"""
    # 核对基线是否可与本次评测比较。
    validate_baseline(
        baseline,
        dataset_version=report["dataset_version"],
        split=report["split"],
        case_ids=report["case_ids"],
    )

    comparison = {"improved": 0, "same": 0, "regressed": 0}
    for case_id, current_rate in report["case_pass_rates"].items():
        previous_rate = baseline["case_pass_rates"][case_id]
        if current_rate > previous_rate:
            comparison["improved"] += 1
        elif current_rate < previous_rate:
            comparison["regressed"] += 1
        else:
            comparison["same"] += 1
    return comparison


# 基线必须与当前题集、划分和运行条件兼容，否则比较没有意义。
def validate_baseline(
    baseline: Any,
    *,
    dataset_version: str,
    split: str,
    case_ids: list[str],
) -> None:
    """在发起服务调用前拒绝不兼容的基线，避免花费请求后才发现无法比较。"""
    if not isinstance(baseline, dict):
        raise ValueError("基线报告必须是 JSON 对象")
    expected = {
        "dataset_version": dataset_version,
        "split": split,
        "case_ids": case_ids,
    }
    for field in ("dataset_version", "split", "case_ids"):
        if baseline.get(field) != expected[field]:
            raise ValueError(f"baseline {field} 与本轮配置不匹配")
    baseline_rates = baseline.get("case_pass_rates")
    if not isinstance(baseline_rates, dict) or set(baseline_rates) != set(case_ids):
        raise ValueError("基线的 case_pass_rates 与本轮题目不匹配")
    if not all(
        isinstance(rate, (int, float))
        and not isinstance(rate, bool)
        and math.isfinite(rate)
        and 0 <= rate <= 1
        for rate in baseline_rates.values()
    ):
        raise ValueError("基线 case_pass_rates 必须是 0 到 1 之间的数值")


# 按题目和试跑次数执行，逐次保存结果，再汇总；不能丢掉失败试跑。
def run_eval(
    dataset: dict[str, Any],
    agent_fn: Callable[[str], str | None],
    *,
    split: str = "dev",
    trials: int = 1,
    model: str = "unknown",
    provider: str = "unknown",
    judge_fn: Callable[[str, dict[str, Any]], str] | None = None,
    baseline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """按指定次数运行所选题目，保留逐题答案、判定和统计，便于复核失败原因。"""
    # 在执行模型请求前验证题集结构。
    validate_dataset(dataset)
    if not 1 <= trials <= MAX_TRIALS:
        raise ValueError(f"trials 必须在 1 到此上限之间：{MAX_TRIALS}")
    cases = select_cases(dataset, split)
    case_ids = [case["id"] for case in cases]
    if baseline is not None:
        # 核对基线是否可与本次评测比较。
        validate_baseline(
            baseline,
            dataset_version=dataset["dataset_version"],
            split=split,
            case_ids=case_ids,
        )
    trial_reports: list[dict[str, Any]] = []
    all_results: list[dict[str, Any]] = []

    for trial_number in range(1, trials + 1):
        results = []
        for case in cases:
            raw_output = agent_fn(case["input"])
            output = (raw_output or "").strip()
            passed = grade_output(output, case, judge_fn)
            result = {
                "id": case["id"],
                "category": case["category"],
                "grader": case["grader"]["type"],
                "passed": passed,
                "output": output,
            }
            results.append(result)
            all_results.append(result)
        passed_count = sum(int(result["passed"]) for result in results)
        trial_reports.append(
            {
                "trial": trial_number,
                "passed": passed_count,
                "total": len(results),
                "pass_rate": passed_count / len(results),
                "results": results,
            }
        )

    case_pass_rates = {
        case["id"]: sum(
            int(result["passed"])
            for result in all_results
            if result["id"] == case["id"]
        )
        / trials
        for case in cases
    }
    passed_count = sum(int(result["passed"]) for result in all_results)
    report: dict[str, Any] = {
        "dataset_version": dataset["dataset_version"],
        "split": split,
        "model": model,
        "provider": provider,
        "trial_count": trials,
        "trials": trial_reports,
        "case_ids": case_ids,
        "case_pass_rates": case_pass_rates,
        "categories": _category_summary(all_results),
        "failures": [
            {"trial": trial["trial"], **result}
            for trial in trial_reports
            for result in trial["results"]
            if not result["passed"]
        ],
        "passed": passed_count,
        "total_attempts": len(all_results),
        "pass_rate": passed_count / len(all_results),
        "improved": 0,
        "same": 0,
        "regressed": 0,
    }
    if baseline is not None:
        report.update(compare_to_baseline(report, baseline))
    return report


def load_report(path: str | Path) -> dict[str, Any]:
    """读取以前的报告作为基线，后续按相同题目比较差异。"""
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("基线报告必须是 JSON 对象")
    return value


def save_report(report: dict[str, Any], path: str | Path) -> Path:
    """仅在传入保存路径时写报告；用原子替换避免读到只写了一半的文件。"""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
            encoding="utf-8",
            newline="\n",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
            # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
            json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            # 要求系统把写入推进到存储层，降低崩溃后丢失状态的风险；仍需结合原子替换与业务幂等。
            os.fsync(handle.fileno())
        # 按参数替换 os 的内容或目标。
        # 使用新内容替换对应目标；在状态保存流程中，原子替换可避免读到半个 JSON 文件。
        os.replace(temporary, destination)
    except Exception:
        if temporary is not None:
            # 删除 temporary 指定的文件。
            temporary.unlink(missing_ok=True)
        raise
    return destination


def _positive_int(value: str) -> int:
    parsed = int(value)
    if not 1 <= parsed <= MAX_TRIALS:
        raise argparse.ArgumentTypeError(f"must be from 1 to {MAX_TRIALS}")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="运行第七课的评测案例。")
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--split", choices=("dev", "holdout", "all"), default="dev")
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--trials", type=_positive_int, default=1)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--save-report", type=Path)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--baseline", type=Path)
    return parser


# 先解析与验证运行选项，再开始评测；保存报告时避免覆盖用于比较的基线。
def run_cli(
    agent_fn: Callable[[str], str | None],
    *,
    model: str,
    provider: str,
    judge_fn: Callable[[str, dict[str, Any]], str] | None = None,
    argv: list[str] | None = None,
) -> int:
    """为选定服务运行统一命令行流程，使两种后端遵循同一评测约定。"""
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = build_parser().parse_args(argv)
    try:
        if (
            args.baseline is not None
            and args.save_report is not None
            # 把相对路径变成绝对路径并解析符号链接；涉及目录权限时，还要检查解析后的位置是否在允许目录内。
            and args.baseline.resolve() == args.save_report.resolve()
        ):
            raise ValueError("基线与新报告必须保存为不同文件")
        dataset = load_dataset(args.dataset)
        # 保留原方案表现，改进后在同一题集和配置上比较，避免只展示新方案成功的个例。
        baseline = load_report(args.baseline) if args.baseline else None
        report = run_eval(
            dataset,
            agent_fn,
            split=args.split,
            trials=args.trials,
            # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
            model=model,
            provider=provider,
            judge_fn=judge_fn,
            baseline=baseline,
        )
        if args.save_report:
            saved = save_report(report, args.save_report)
            print(f"报告已保存：{saved}")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"评测已停止：{error}")
        return 2

    print(
        f"{provider}/{model} · {report['split']} · "
        f"{report['passed']}/{report['total_attempts']} passed "
        f"({report['pass_rate']:.0%})"
    )
    for failure in report["failures"]:
        print(
            f"FAIL trial={failure['trial']} id={failure['id']} category={failure['category']}"
        )
    if baseline is not None:
        print(
            "与基线比较："
            f"{report['improved']} improved, {report['same']} same, "
            f"{report['regressed']} regressed"
        )
    return 0
