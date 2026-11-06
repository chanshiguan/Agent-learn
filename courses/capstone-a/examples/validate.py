"""验证固定会议示范；结构检查与事实验收分开。"""

# 只验证行动表的字段和来源；是否准确保留责任人、时间与待决定事项，还需逐句核对。
import json
import sys
from pathlib import Path

# 把相对路径变成绝对路径并解析符号链接；涉及目录权限时，还要检查解析后的位置是否在允许目录内。
HERE=Path(__file__).resolve().parent


def validate(data):
    if not isinstance(data,dict) or set(data)!={'actions','needs_confirmation'}:
        raise ValueError('需要 actions 与 needs_confirmation')
    if not isinstance(data['actions'],list) or not data['actions']:
        raise ValueError('缺行动列表')
    for row in data['actions']:
        if not isinstance(row,dict) or set(row)!={'task','owner','due','source'}:
            raise ValueError('行动字段错误')
        if not all(isinstance(value,str) and value.strip() for value in row.values()):
            raise ValueError('字段不能为空')
        if not set(row['source'].split(',')).issubset({'M1','M2','M3'}):
            raise ValueError('未知来源')
        if row['owner']!='小林':
            raise ValueError('固定示范中只有小林被指定负责，不能补造其他负责人')
        if row['due']!='周五，具体日期待确认':
            raise ValueError('固定示范未给具体日期；使用完整的待确认期限')
    if not isinstance(data['needs_confirmation'],list) or not all(isinstance(x,str) for x in data['needs_confirmation']):
        raise ValueError('待确认项必须是文本列表')
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    reference=json.loads((HERE/'reference-draft.json').read_text())
    exact=data==reference
    return {'status':'PASS_REFERENCE' if exact else 'NEEDS_REVIEW',
            'scope':'仅固定会议数据；换资料必须重建事实断言，不照搬负责人规则',
            'next':'逐句核对任务是否保留不发布、是否遗漏预算待确认；再检查实际 CLI 证据。复制参考答案不能证明独立完成。'}


if __name__=='__main__':
    path=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'reference-draft.json'
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    print(json.dumps(validate(json.loads(path.read_text())),ensure_ascii=False,indent=2))
