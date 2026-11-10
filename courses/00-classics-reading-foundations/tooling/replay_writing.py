"""维护者验证：只从公开输入和页面可见编辑重建项目，学员无需运行此脚本。"""
import ast
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

COURSE = Path(__file__).resolve().parents[1]
plan = json.loads((COURSE / 'writing/plan.json').read_text())
units = json.loads((COURSE / 'units.json').read_text())
assert list(plan) == [u['file'] for u in units]
checks = 0
edits = 0
with tempfile.TemporaryDirectory(prefix='classics-writing-') as directory:
    work = Path(directory).resolve()
    (work / 'data/input').mkdir(parents=True)
    samples = list((COURSE / 'examples/data/input').glob('*.docx'))
    assert len(samples) == 5
    for file in samples:
        shutil.copy2(file, work / 'data/input' / file.name)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', READING_DATA_DIR=str(work / 'data/live'))
    env.pop('PYTHONPATH', None)
    created = set()
    for unit, part in plan.items():
        markdown = (COURSE / 'text' / (unit + '.md')).read_text()
        sections = re.split(r'^### 第 \d+ 步：.*\n', markdown, flags=re.M)[1:]
        assert len(sections) == len(part['edits']), (unit, '步骤数与页面不同')
        for index, edit in enumerate(part['edits']):
            # Verify all new code is visible in the same order as the replay; old text is only a locator.
            visible = re.sub(r'<details>[\s\S]*?</details>', '', sections[index])
            language = 'python' if edit['file'].endswith('.py') else 'javascript' if edit['file'].endswith('.js') else 'html' if edit['file'].endswith('.html') else 'css' if edit['file'].endswith('.css') else 'json' if edit['file'].endswith('.json') else 'yaml' if edit['file'].endswith(('.yaml','.yml')) else 'dockerfile' if 'Dockerfile' in edit['file'] else 'text'
            blocks = re.findall(r'^```' + language + r'\n([\s\S]*?)\n```', visible, re.M)
            expected = edit['code'].splitlines()
            actual = '\n'.join(blocks).splitlines()
            # Chunk fences may absorb a separating blank line, which does not change program behavior.
            assert [l for l in actual if l.strip()] == [l for l in expected if l.strip()], (unit, edit['file'], '页面代码和复演代码不一致')
            target = work / edit['file']
            assert target.resolve().is_relative_to(work)
            target.parent.mkdir(parents=True, exist_ok=True)
            current = target.read_text() if target.exists() else ''
            if edit['action'] == 'create':
                assert not target.exists(), (unit, edit['file'])
                result = edit['code']
                created.add(edit['file'])
            elif edit['action'] == 'append':
                assert target.exists()
                result = current.rstrip() + '\n\n' + edit['code']
            else:
                assert current.count(edit['old']) == 1, (unit, edit['file'])
                result = current.replace(edit['old'], edit['code'] if edit.get('exact') else edit['code'].rstrip('\n'), 1)
            target.write_text(result)
            edits += 1
        for name in created:
            if name.endswith('.py'):
                ast.parse((work / name).read_text(), filename=name)
        modules = [name[:-3].replace('/', '.') for name in sorted(created)
                   if name.startswith('companion/') and name.endswith('.py')
                   and not name.endswith(('__main__.py','__init__.py'))]
        if modules:
            imports = subprocess.run([sys.executable, '-B', '-c',
                'import importlib; ' + '; '.join('importlib.import_module(' + repr(m) + ')' for m in modules)],
                cwd=work, env=env, text=True, capture_output=True)
            assert imports.returncode == 0, (unit, '当前模块无法导入', imports.stderr)
        for check in part['checks']:
            response = subprocess.run([sys.executable, '-B', '-c', check['code']], cwd=work, env=env, text=True, capture_output=True)
            assert response.returncode == 0, (unit, response.stdout, response.stderr)
            checks += 1
        print(unit + ': 当前代码与检查通过', flush=True)
    for name in created:
        assert (work / name).read_bytes() == (COURSE / 'examples' / name).read_bytes(), ('课后参考文件与逐步写成结果不同', name)
print(json.dumps({'units': len(plan), 'edits': edits, 'created_files': len(created), 'checks': checks, 'initial_input': 'only 5 public DOCX'}, ensure_ascii=False))
