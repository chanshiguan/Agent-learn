"""只读确认 CLI 是否存在及版本；不登录、不输出账户与凭证。"""

# 只查询程序位置和版本，不安装、登录或更改 Claude Code 配置。
import json
import shutil
import subprocess

path = shutil.which('claude')
if path:
    # capture_output：保存子进程的真实输出，后续报告才能引用实际结果而不是声称“已运行”。
    # text：按文本而不是字节接收子进程输出，便于检查断言和生成可读报告。
    # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
    completed = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=15)
    print(json.dumps({'installed': completed.returncode == 0, 'path': path,
                      # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
                      'version': completed.stdout.strip(), 'next': '在演示目录开始首次会话'},ensure_ascii=False))
else:
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    print(json.dumps({'installed': False, 'next': '执行讲义安装步骤，再开新终端检查'},ensure_ascii=False))
