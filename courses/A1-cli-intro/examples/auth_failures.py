"""不连接服务、不读取环境变量的认证与权限故障注入。"""

# 模拟登录、密钥、模型、权限、连接五种失败；不读取正式凭证或联系服务。
import json


class LabError(Exception):
    def __init__(self, category, message):
        self.category = category
        super().__init__(message)


# 检查在哪一层失败就抛对应错误，不把服务认证与本地工具权限混为一谈。
def request(*, logged_in=True, fake_key='DEMO_ACCEPTED', model='demo-model', action='read', available=True):
    if not available:
        raise LabError('connection', '模拟连接失败：演示服务未启动')
    if not logged_in:
        raise LabError('login', '模拟未登录：没有登录会话')
    if fake_key != 'DEMO_ACCEPTED':
        raise LabError('api_key', '模拟 401：provider 拒绝凭证；不回显凭证')
    if model != 'demo-model':
        raise LabError('model', '模拟 404：模型不在允许列表')
    if action != 'read':
        raise LabError('permission', '模拟工具阻挡：当前仅允许 read')
    return '虚构文档读取成功'


CASES = [
    ('login', {'logged_in': False}, '恢复登录会话；不修改任务提示词'),
    ('api_key', {'fake_key': 'not-a-real-key'}, '核对 provider 与凭证来源；不粘贴真实 key'),
    ('model', {'model': 'nonexistent-course-model'}, '选择账户实际可用的模型标识'),
    ('permission', {'action': 'write'}, '确认任务授权与工具范围；不绕过限制'),
    ('connection', {'available': False}, '确认服务、地址、端口和代理'),
]


# 逐个注入故障，再用正常配置作为对照，记录预期与实际分类。
def run():
    records = []
    for expected, config, remedy in CASES:
        try:
            request(**config)
        except LabError as error:
            records.append({'mode': 'mock', 'expected': expected, 'observed': error.category,
                            'message': str(error), 'remedy': remedy,
                            'passed': error.category == expected})
    return {'mode': 'mock', 'network_calls': 0, 'credentials_read': False,
            'records': records, 'healthy_control': request()}


if __name__ == '__main__':
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(run(), ensure_ascii=False, indent=2))
