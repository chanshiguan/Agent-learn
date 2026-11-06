"""读取三份已授权 MIT 课程来源，保留 URL、时间、原文和摘录。"""

# 把获准读取的来源保存为带时间和出处的本地记录，供摘要流程继续处理。
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

COMMIT = '9ef03ca034704bf9cdd403673b3116fda7ec8672'
DOCUMENTS = [
    ('protocol', 'stages/03-tool-use-and-hello-agent.zh-Hans.md', '工具'),
    ('permission', 'stages/05-claude-code-ecosystem.zh-Hans.md', 'Skill'),
    ('approval', 'stages/07-multi-agent-production.zh-Hans.md', '批准'),
]


def collect(destination, network=False):
    destination = Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('使用新的空目录，保留旧采集记录')
    destination.mkdir(parents=True, exist_ok=True)
    # 把相对路径变成绝对路径并解析符号链接；涉及目录权限时，还要检查解析后的位置是否在允许目录内。
    snapshot = Path(__file__).resolve().parents[2] / '_sources/upstream'
    records = []
    for key, relative, keyword in DOCUMENTS:
        raw_url = f'https://raw.githubusercontent.com/WenyuChiou/awesome-agentic-ai-zh/{COMMIT}/{relative}'
        if network:
            # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
            with urlopen(raw_url, timeout=30) as response:
                text = response.read().decode('utf-8')
        else:
            # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
            text = (snapshot / relative).read_text()
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        (destination / f'{key}.md').write_text(text)
        # 选择一个可回查的短段落；不假称抓取整站或自动完成文献综合。
        paragraphs = [part.strip() for part in text.split('\n\n')]
        excerpt = next(part for part in paragraphs if keyword in part and 20 <= len(part) <= 300
                       and not part.startswith(('#', '|', '<', '```', '>', '[', '-')))
        records.append({'id': key, 'text': excerpt,
                        'url': f'https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/{COMMIT}/{relative}',
                        'retrieved_at': datetime.now(timezone.utc).isoformat(),
                        'origin': '网络抓取固定版本' if network else '本地固定版本快照；此时间为读取时间',
                        # 把相对路径变成绝对路径并解析符号链接；涉及目录权限时，还要检查解析后的位置是否在允许目录内。
                        'full_text_file': str((destination / f'{key}.md').resolve())})
    # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    (destination / 'sources.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('destination', type=Path)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--network', action='store_true')
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(collect(args.destination, args.network), ensure_ascii=False, indent=2))
