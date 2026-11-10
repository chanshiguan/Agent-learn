"""维护者验证：只从公开输入和页面可见编辑重建项目，学员无需运行此脚本。"""
import ast
import json
import os
from pathlib import Path
import re
import shutil
import shlex
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
        # Check the command options at the exact lesson where the prose first uses them.
        command_modules = {}
        entry = work / 'companion/__main__.py'
        if entry.exists():
            for node in ast.walk(ast.parse(entry.read_text())):
                if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
                    test = node.test
                    if isinstance(test.left, ast.Name) and test.left.id == 'command' and isinstance(test.comparators[0], ast.Constant):
                        imports = [n for n in node.body if isinstance(n, ast.ImportFrom)]
                        if imports:
                            command_modules[test.comparators[0].value] = 'companion/' + imports[0].module + '.py'
        for block in re.findall(r'^```bash\n([\s\S]*?)\n```', markdown, re.M):
            for line in block.replace('\\\n', ' ').splitlines():
                if not re.search(r'\bpython -m companion(?: |\.)', line) or line.lstrip().startswith('#'):
                    continue
                tokens = shlex.split(line, comments=True)
                at = tokens.index('python')
                module = tokens[at + 2]
                if module == 'companion':
                    command = tokens[at + 3]
                    assert command in command_modules, (unit, '命令尚未接入', command)
                    filename = command_modules[command]
                    args = tokens[at + 4:]
                else:
                    filename = module.replace('.', '/') + '.py'
                    args = tokens[at + 3:]
                assert filename in created, (unit, '模块尚未创建', filename)
                arguments = {'--help'}
                for call in ast.walk(ast.parse((work / filename).read_text())):
                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'add_argument':
                        arguments.update(a.value for a in call.args if isinstance(a, ast.Constant) and isinstance(a.value, str))
                for value in args:
                    if value.startswith('--'):
                        assert value.split('=')[0] in arguments, (unit, '参数尚未实现', value)
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
        # Recreate two states the prose asks learners to produce before its end-of-unit check.
        precondition = None
        if unit == '0044-reviewed-ranges':
            precondition = '''from companion.files import load,save
chunks=load("corpus.json")["chunks"]
save("ranges.json",{c["id"]:{"range_end":1,"reviewed":True} for c in chunks[:2]})
'''
        if part['original'] == '0052-write-drafts' and part['checks']:
            precondition = '''from companion import state,actions
state.initialize();a=state.Actor("demo","reader-a")
d=actions.draft(a,"note","先前已保存的测试笔记","existing-note")
actions.approve(a,d["id"],d["revision"],d["digest"],True)
'''
        if precondition:
            subprocess.run([sys.executable, '-B', '-c', precondition], cwd=work, env=env, check=True, capture_output=True)
        for check in part['checks']:
            response = subprocess.run([sys.executable, '-B', '-c', check['code']], cwd=work, env=env, text=True, capture_output=True)
            assert response.returncode == 0, (unit, response.stdout, response.stderr)
            checks += 1
        if part['original'] == '0052-write-drafts' and part['checks']:
            subprocess.run([sys.executable, '-B', '-c',
                'from companion import state,actions; assert len(actions.notes(state.Actor("demo","reader-a")))==1'],
                cwd=work, env=env, check=True, capture_output=True)
        if unit == '0037-context-neighbors':
            subprocess.run([sys.executable, '-m', 'companion', 'evaluate', '--expand', '--output', 'expand-check.json'],
                cwd=work, env=env, check=True, capture_output=True)
            assert json.loads((work / 'data/live/expand-check.json').read_text())['options']['expand'] is True
        if unit == '0038-hybrid-rerank':
            # A clear test double checks CLI wiring here; it is not a model ranking result.
            code = 'import runpy,sys\nfrom unittest.mock import patch\nfrom companion.files import load\nsys.argv=["companion","evaluate","--rerank","--output","rerank-check.json"]\nwith patch("companion.evaluation.rerank",side_effect=lambda question,hits:list(reversed(hits))) as ranking:\n    runpy.run_module("companion",run_name="__main__")\n    assert ranking.call_count > 0\nassert load("rerank-check.json")["options"]["rerank"] is True\n'
            subprocess.run([sys.executable, '-B', '-c', code], cwd=work, env=env, check=True, capture_output=True)
        print(unit + ': 当前代码与检查通过', flush=True)
    for name in created:
        assert (work / name).read_bytes() == (COURSE / 'examples' / name).read_bytes(), ('课后参考文件与逐步写成结果不同', name)
print(json.dumps({'units': len(plan), 'edits': edits, 'created_files': len(created), 'checks': checks, 'initial_input': 'only 5 public DOCX'}, ensure_ascii=False))
