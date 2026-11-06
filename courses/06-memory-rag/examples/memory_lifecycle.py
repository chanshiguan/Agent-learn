"""原 Memory 支线五步：跨进程读取、改表格、隔离、删除。"""

# 按保存、跨进程读取、修改、用户隔离、删除的顺序验证，不能用同一对象里的值证明持久化。
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from memory_store import MemoryStore
from grounded_rag import run


def finish(db):
    store = MemoryStore(db)
    try:
        before = store.get('alice', 'answer_style')
        if before is None:
            raise ValueError('第二进程未找到第一进程的偏好')
        other = store.get('bob', 'answer_style')
        version = store.put('alice', 'answer_style', '先给表格', consent=True,
                            expected_version=before['version'], source='虚构用户在 thread-B 明确更新', ttl=3600)
        after = store.get('alice', 'answer_style')
    # 无论成功还是失败，都执行这里的收尾步骤。
    finally:
        store.close()
    answer = run('报名截止时间', 'alice', db)
    store = MemoryStore(db)
    try:
        store.delete('alice', 'answer_style')
        deleted = store.get('alice', 'answer_style')
    # 无论成功还是失败，都执行这里的收尾步骤。
    finally:
        store.close()
    return {'thread': 'B', 'read_from_thread_A': before, 'other_user_before_deletion': other,
            'updated': after, 'display': answer['display_answer'], 'deleted': deleted,
            'passed': before['value'] == '先短后长' and other is None and version == 2
            and after['value'] == '先给表格' and answer['display_answer'].startswith('| 摘录 |') and deleted is None}


def demo():
    with tempfile.TemporaryDirectory(prefix='course6-memory-') as directory:
        db = Path(directory) / 'memory.sqlite'
        store = MemoryStore(db)
        store.put('alice', 'answer_style', '先短后长', consent=True, expected_version=0,
                  source='虚构用户在 thread-A 明确选择', ttl=3600)
        store.close()
        # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
        # text：按文本而不是字节接收子进程输出，便于检查断言和生成可读报告。
        # 把相对路径变成绝对路径并解析符号链接；涉及目录权限时，还要检查解析后的位置是否在允许目录内。
        return json.loads(subprocess.check_output([sys.executable, str(Path(__file__).resolve()), '--continue-db', str(db)], text=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--continue-db', type=Path)
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(finish(args.continue_db) if args.continue_db else demo(), ensure_ascii=False, indent=2))
