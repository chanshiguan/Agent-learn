"""临时目录内复现修改、验证和定点撤回；不会更改项目文件。"""

# 在临时副本里演示修改、检查和撤回；固定脚本的结果不能冒充 CLI Agent 实测。
import difflib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run():
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    data=json.loads(Path(__file__).with_name('reference-work.json').read_text())
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder)
        readme=root/'README.md'
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        readme.write_text(data['before'])
        checker=root/'check.py'
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        checker.write_text("from pathlib import Path\ntext=Path('README.md').read_text()\nassert '## 运行' in text and 'python check.py' in text, '缺运行说明'\nprint('PASS')\n")
        # cwd：限定命令的工作目录，防止相对路径落到用户的其他项目或错误位置。
        # capture_output：保存子进程的真实输出，后续报告才能引用实际结果而不是声称“已运行”。
        # text：按文本而不是字节接收子进程输出，便于检查断言和生成可读报告。
        before=subprocess.run([sys.executable,'check.py'],cwd=root,capture_output=True,text=True)
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        readme.write_text(data['after'])
        # cwd：限定命令的工作目录，防止相对路径落到用户的其他项目或错误位置。
        # capture_output：保存子进程的真实输出，后续报告才能引用实际结果而不是声称“已运行”。
        # text：按文本而不是字节接收子进程输出，便于检查断言和生成可读报告。
        after=subprocess.run([sys.executable,'check.py'],cwd=root,capture_output=True,text=True)
        # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
        diff=''.join(difflib.unified_diff(data['before'].splitlines(True),readme.read_text().splitlines(True),fromfile='README.md',tofile='README.md'))
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        readme.write_text(data['before'])
        # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
        assert before.returncode!=0 and after.returncode==0 and readme.read_text()==data['before']
        return {'before_exit':before.returncode,'after_output':after.stdout.strip(),'diff':diff,'rollback_verified':True}


if __name__=='__main__':
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(run(),ensure_ascii=False,indent=2))
