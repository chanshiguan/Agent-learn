"""评分分为确定性证据检查与人工语义复核，未知不算通过。"""

# 先读 grade 的证据检查，再看 evaluate 如何逐题多次运行；待复核不会计入通过率。
import argparse
import json
import time
from pathlib import Path
from rag_agent import run, make_ask, retrieve


# 重新执行轨迹中的查询，拒绝伪造证据；完全摘录可自动判定，改写留给人工复核。
def grade(case, result):
    errors = []
    answer, refs = result.get('answer'), result.get('source_ids')
    trace = result.get('trace', [])
    if not isinstance(answer, str) or not answer.strip():
        errors.append('答案为空或不是字符串')
    if not isinstance(refs, list) or not all(isinstance(x, str) for x in refs):
        errors.append('来源格式错误')
        refs = []
    if len(refs) != len(set(refs)) or set(refs) != set(case['sources']):
        errors.append('来源集合不符合本题证据要求')
    observed = {}
    for step in trace:
        if step.get('tool') != 'retrieve' or not isinstance(step.get('query'), str):
            errors.append('轨迹不是允许的检索步骤')
            continue
        # 用记录中的查询重新检索，防止提交者手填一份看似成功的工具结果。
        expected = retrieve(step['query'])
        if step.get('result') != expected:
            errors.append('轨迹中的证据与实际检索不一致')
        observed.update({x['id']: x['text'] for x in expected})
    if not trace or not set(refs).issubset(observed):
        errors.append('缺少支持本次来源的检索轨迹')
    if errors:
        return {'status': 'FAIL', 'reasons': errors}
    if not refs:
        return {'status': 'PASS' if answer == '资料不足，无法回答。' else 'FAIL',
                'reasons': ['无证据题只接受明确拒答']}
    # 只对完全一致的已知摘录自动通过。改写不武断判错，也不默认为对。
    exact = '\n'.join(observed[x] for x in refs)
    if answer == exact:
        return {'status': 'PASS', 'reasons': ['答案为本次可信资料的完整摘录；来源与轨迹符合本题']}
    return {'status': 'NEEDS_REVIEW', 'reasons': [
        '这是改写答案，需按本题人工量规逐条核对；关键词命中不计分',
        '核对主体、数字、否定与例外；每条事实有支持；没有额外编造；确实回答问题']}


# 题集、次数和输入版本固定后逐题记录；异常归为失败，不丢掉失败行。
def evaluate(split='development', trials=1, live=False, submission=None):
    if not 1 <= trials <= 5:
        raise ValueError('试跑次数必须为 1–5')
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    data = json.loads(Path(__file__).with_name('eval_cases.json').read_text())
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    supplied = json.loads(Path(submission).read_text()) if submission else None
    if supplied is not None and set(supplied) != {c['id'] for c in data[split]}:
        raise ValueError('提交 JSON 顶层必须包含所选题集的全部且仅有题号')
    rows = []
    ask = make_ask() if live else None
    for case in data[split]:
        for trial in range(trials):
            start = time.perf_counter()
            try:
                result = supplied[case['id']] if supplied is not None else run(case['question'], ask)
                row = {'id': case['id'], 'trial': trial+1, 'result': result, **grade(case, result)}
            except Exception as exc:
                row = {'id': case['id'], 'status': 'FAIL', 'reasons': [str(exc)]}
            row['seconds'] = round(time.perf_counter()-start, 3)
            rows.append(row)
    # 把待人工复核单独计数，不混入自动通过率。
    counts = {s: sum(x['status'] == s for x in rows) for s in ['PASS', 'FAIL', 'NEEDS_REVIEW']}
    return {'dataset_version': data['version'], 'split': split, 'counts': counts,
            'automatic_pass_rate': counts['PASS']/len(rows),
            'meaning': '待人工复核不计入通过；公开题不能作为盲测；不会据此记录学习者掌握', 'rows': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    p.add_argument('--split', choices=['development', 'holdout'], default='development')
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    p.add_argument('--trials', type=int, default=1)
    # 让真实模型、固定答案或提交文件等模式互斥，避免一次运行混用两种来源而无法解释结果。
    group = p.add_mutually_exclusive_group()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    group.add_argument('--live', action='store_true')
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    group.add_argument('--submission', type=Path)
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    a = p.parse_args()
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(evaluate(a.split, a.trials, a.live, a.submission), ensure_ascii=False, indent=2))
