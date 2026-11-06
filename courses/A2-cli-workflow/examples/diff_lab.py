"""创建隔离的双 README 演示，保存真实 diff；不调用 Agent。"""

# 在新的演示目录生成 baseline/broken/fixed 三类 Git diff；不修改主项目仓库。
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BEFORE = "# 学习记录演示\n\n只处理虚构记录。\n\n## 运行\n\n尚未写入运行命令。\n"
AFTER = "# 学习记录演示\n\n只处理虚构记录。\n\n## 运行\n\n从仓库根目录执行 `python3 run.py`，应显示 `学习记录检查完成`。\n"
BROKEN = "# 学习记录演示\n\n只处理虚构记录。\n\n## 运行\n\n从仓库根目录执行 `python3 missing.py`。\n\n[操作说明](missing-guide.md)\n"
CHECK = '''from pathlib import Path
for name in ("README.md", "docs/README.md"):
    text = Path(name).read_text()
    assert "python3 run.py" in text, name + " 缺少正确命令"
    assert "学习记录检查完成" in text, name + " 缺少预期输出"
print("PASS：两份 README 都有命令与预期输出")
'''


def run(directory, mode):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise ValueError("只接受空的演示目录，防止覆盖已有工作")
    (directory / 'docs').mkdir()
    for name in ('README.md', 'docs/README.md'):
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        (directory / name).write_text(BEFORE)
    # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
    (directory / 'run.py').write_text('print("学习记录检查完成")\n')
    # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
    (directory / 'check.py').write_text(CHECK)
    # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
    (directory / '.gitignore').write_text('review-evidence.json\n')
    commands = [['git', 'init', '-q'], ['git', 'add', '.'],
                ['git', '-c', 'user.name=Course Demo', '-c',
                 'user.email=demo@example.invalid', 'commit', '-qm', 'docs: 保存练习基线']]
    for command in commands:
        # 运行参数中明确指定的命令，并按选项收集结果。
        # cwd：限定命令的工作目录，防止相对路径落到用户的其他项目或错误位置。
        # check：子进程返回非零状态时抛错，使失败不会被后续步骤误当作成功。
        # capture_output：保存子进程的真实输出，后续报告才能引用实际结果而不是声称“已运行”。
        subprocess.run(command, cwd=directory, check=True, capture_output=True)
    if mode == 'broken':
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        (directory / 'README.md').write_text(BROKEN)
    elif mode == 'fixed':
        for name in ('README.md', 'docs/README.md'):
            # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
            (directory / name).write_text(AFTER)
    # cwd：限定命令的工作目录，防止相对路径落到用户的其他项目或错误位置。
    # text：按文本而不是字节接收子进程输出，便于检查断言和生成可读报告。
    diff = subprocess.check_output(['git', 'diff', '--no-ext-diff', '--no-textconv', 'HEAD'], cwd=directory, text=True)
    # cwd：限定命令的工作目录，防止相对路径落到用户的其他项目或错误位置。
    # text：按文本而不是字节接收子进程输出，便于检查断言和生成可读报告。
    status = subprocess.check_output(['git', 'status', '--short'], cwd=directory, text=True)
    # cwd：限定命令的工作目录，防止相对路径落到用户的其他项目或错误位置。
    # capture_output：保存子进程的真实输出，后续报告才能引用实际结果而不是声称“已运行”。
    # text：按文本而不是字节接收子进程输出，便于检查断言和生成可读报告。
    whitespace = subprocess.run(['git', 'diff', '--check'], cwd=directory, capture_output=True, text=True)
    # cwd：限定命令的工作目录，防止相对路径落到用户的其他项目或错误位置。
    # capture_output：保存子进程的真实输出，后续报告才能引用实际结果而不是声称“已运行”。
    # text：按文本而不是字节接收子进程输出，便于检查断言和生成可读报告。
    check = subprocess.run([sys.executable, 'check.py'], cwd=directory, capture_output=True, text=True)
    report = {'mode': mode, 'agent_executed': False, 'directory': str(directory),
              'diff': diff, 'status': status, 'diff_check_exit': whitespace.returncode,
              'check_exit': check.returncode, 'check_output': check.stdout + check.stderr,
              'expected_review': 'FAIL' if mode == 'broken' else 'PASS' if mode == 'fixed' else 'NEEDS_IMPLEMENTATION'}
    # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    (directory / 'review-evidence.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--mode', choices=['baseline', 'broken', 'fixed'], default='broken')
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--output', type=Path)
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    location = args.output or Path(tempfile.mkdtemp(prefix='course-a2-'))
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(run(location, args.mode), ensure_ascii=False, indent=2))
