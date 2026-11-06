"""不调用模型，检查教学助手的离线输入、工具与输出约定。"""

# 检查评测材料的字段与章节定位，防止题目引用不存在的学习内容。

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# 把相对路径变成绝对路径并解析符号链接；涉及目录权限时，还要检查解析后的位置是否在允许目录内。
ROOT = Path(__file__).resolve().parents[1]
CONFIG = Path(__file__).with_name("evals.json")
EXPECTED_ROUTES = {"a", "b", "c", "d", "away"}
# 教学包只分发简体中文入口与同语种翻译稿；检查实际打包的两份文件，不依赖未收录的英文文件。
SKILLS = (
    ROOT / "SKILL.md",
    ROOT / "translations/SKILL.zh-Hans.md",
)


def heading_slugs(text: str) -> set[str]:
    """按这份测试数据使用的规则生成标题锚点，核对目录能否跳到对应章节。"""
    slugs: set[str] = set()
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*$", text, flags=re.MULTILINE):
        clean = re.sub(r"[`*_]", "", heading).strip().lower()
        clean = re.sub(r"[^\w\-\u3400-\u9fff ]", "", clean)
        slugs.add(re.sub(r"[\s-]+", "-", clean).strip("-"))
    return slugs


def validate_case(case: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(case, dict):
        return ["case must be an object"]

    case_id = case.get("id", "<missing-id>")
    for key in ("id", "locale", "input", "expected_route", "reference", "must_cover"):
        if key not in case:
            errors.append(f"{case_id}: missing {key}")

    route = case.get("expected_route")
    if route not in EXPECTED_ROUTES:
        errors.append(f"{case_id}: unknown route {route!r}")

    must_cover = case.get("must_cover")
    if not isinstance(must_cover, list) or len(must_cover) < 2:
        errors.append(f"{case_id}: must_cover needs at least two checks")
    elif any(not isinstance(item, str) or not item.strip() for item in must_cover):
        errors.append(f"{case_id}: must_cover entries must be non-empty strings")

    reference = case.get("reference")
    if route == "away":
        if reference != "":
            errors.append(f"{case_id}: route-away case must not invent a reference")
        return errors
    if not isinstance(reference, str) or not reference.startswith("references/"):
        errors.append(f"{case_id}: reference must stay inside references/")
        return errors

    path_text, _, anchor = reference.partition("#")
    target = ROOT / path_text
    if not target.is_file():
        errors.append(f"{case_id}: missing reference file {path_text}")
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
    elif anchor and anchor not in heading_slugs(target.read_text(encoding="utf-8")):
        errors.append(f"{case_id}: missing reference anchor #{anchor}")
    return errors


def main() -> int:
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
    document = json.loads(CONFIG.read_text(encoding="utf-8"))
    errors: list[str] = []
    if document.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    cases = document.get("cases")
    if not isinstance(cases, list):
        errors.append("cases must be a list")
        cases = []

    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(cases) != 5:
        errors.append(f"expected 5 cases, found {len(cases)}")
    if len(ids) != len(set(ids)):
        errors.append("case ids must be unique")
    routes = {
        case.get("expected_route") for case in cases if isinstance(case, dict)
    }
    if routes != EXPECTED_ROUTES:
        errors.append(f"routes must be exactly {sorted(EXPECTED_ROUTES)}")
    for case in cases:
        errors.extend(validate_case(case))

    for skill in SKILLS:
        # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
        # encoding：明确按 UTF-8 读写中文，避免不同终端或系统默认编码导致乱码。
        text = skill.read_text(encoding="utf-8")
        if "name: tool-calling-tutor" not in text:
            errors.append(f"{skill.name}: missing stable skill name")
        if "${CLAUDE_SKILL_DIR}/references/" not in text:
            errors.append(f"{skill.name}: bundled references are not install-safe")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: {len(cases)}/5 道离线验收题的字段、路由和资料链接通过检查")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
