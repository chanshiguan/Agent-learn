"""五类控制题及完整逐题收据；测试控制逻辑，不评分模型智能。"""

# 用正常与故障场景检查控制流程；每题都要留下状态和是否产生效果的证据。
import json
import tempfile
import time
from pathlib import Path
from production_case import SOURCE_TEXTS, prepare, resume

CASES = [
    {'id': 'normal', 'sources': True, 'tool': 'extract', 'budget': 1, 'decision': 'approve', 'expected': 'completed'},
    {'id': 'no-evidence', 'sources': False, 'tool': 'extract', 'budget': 1, 'decision': 'approve', 'expected': 'NO_EVIDENCE'},
    {'id': 'invalid-tool', 'sources': True, 'tool': 'send', 'budget': 1, 'decision': 'approve', 'expected': 'BLOCKED'},
    {'id': 'budget', 'sources': True, 'tool': 'extract', 'budget': 0, 'decision': 'approve', 'expected': 'BUDGET_EXHAUSTED'},
    {'id': 'reject', 'sources': True, 'tool': 'extract', 'budget': 1, 'decision': 'reject', 'expected': 'cancelled'},
]


def attempt(case, folder):
    start = time.perf_counter()
    trace = []
    error = None
    if case['tool'] != 'extract':
        status, error = 'BLOCKED', 'tool_not_allowed'
    elif case['budget'] <= 0:
        status, error = 'BUDGET_EXHAUSTED', 'no_steps_left'
    elif not case['sources']:
        status, error = 'NO_EVIDENCE', 'no_authorized_sources'
    else:
        trace.append({'step': 'policy', 'status': 'ALLOW'})
        prepare(folder)
        receipt = resume(folder, case['decision'])
        trace.extend(receipt['trace'])
        return {**receipt, 'trace': trace}
    trace.append({'step': 'policy', 'status': status})
    return {'task_id': case['id'], 'status': status, 'result': None, 'sources': [],
            'trace': trace, 'seconds': time.perf_counter() - start,
            'usage': {'input_tokens': 0, 'output_tokens': 0}, 'errors': [error],
            'state_version': None, 'approval': None, 'published': False}


def grade(case, receipt, folder):
    # 执行登记用于判断同一动作是否已经发生；只保存模型对话不足以阻止恢复时重复执行副作用。
    ledger = folder / 'ledger.json'
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    effects = json.loads(ledger.read_text())['executed'] if ledger.exists() else []
    expected_effects = 1 if case['expected'] == 'completed' else 0
    outcome = receipt['status'] == case['expected']
    if expected_effects:
        outcome = outcome and receipt['result'] == '\n'.join(text for _, text in SOURCE_TEXTS)
        outcome = outcome and {s['id'] for s in receipt['sources']} == {key for key, _ in SOURCE_TEXTS}
    else:
        outcome = outcome and receipt['result'] is None
    trajectory = (len(effects) == expected_effects and not receipt['published']
                  and not any(step['step'] == 'send' for step in receipt['trace']))
    return {'outcome_pass': outcome, 'trajectory_pass': trajectory,
            'status': 'PASS' if outcome and trajectory else 'FAIL', 'effects': len(effects)}


def evaluate():
    rows = []
    with tempfile.TemporaryDirectory(prefix='course7-eval-') as directory:
        for case in CASES:
            folder = Path(directory) / case['id']
            receipt = attempt(case, folder)
            rows.append({'case': case, 'receipt': receipt, 'grade': grade(case, receipt, folder)})
    return {'dataset_version': 'control-v1', 'split': 'development', 'trials': 1,
            'baseline': '同版本确定性控制流程；没有模型效果对照',
            'rows': rows, 'passed': sum(row['grade']['status'] == 'PASS' for row in rows)}


if __name__ == '__main__':
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
