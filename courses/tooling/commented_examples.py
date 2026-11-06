"""重建简体中文教学副本；原始快照与已核对的教学改动分别校验。"""
import ast
import hashlib
import json
from pathlib import Path


def annotate_upstream(home):
    catalog = json.loads(Path(__file__).with_name('upstream-comments.json').read_text())
    for relative, entry in catalog.items():
        if relative.split('/')[0] != home.name:
            continue
        path = home.parent / relative
        original = path.read_text()
        # 上游一旦更新就停止，不能将旧位置的翻译和注释套到另一份代码。
        if hashlib.sha256(original.encode()).hexdigest() != entry['sha256']:
            raise ValueError(f'{path}: 原例已变化，需要重新核对中文教学版本')
        lines = original.splitlines(keepends=True)
        for edit in sorted(entry['edits'], key=lambda row: row['start'], reverse=True):
            lines[edit['start']:edit['end']] = [edit['text']]
        localized = ''.join(lines)
        # 明确保存已核对的结果摘要：允许中文输入与配套匹配规则，不允许静默漂移。
        if hashlib.sha256(localized.encode()).hexdigest() != entry['localized_sha256']:
            raise ValueError(f'{path}: 教学覆盖层与已核对版本不一致')
        if path.suffix == '.py':
            ast.parse(localized)
        elif path.suffix == '.json':
            json.loads(localized)
        path.write_text(localized)
