"""可选 OpenAI 受管检索：只上传本脚本内虚构文件，默认不联网。"""

# 选修云端路径：创建临时资料库 → 上传 → 等索引 → 搜索 → 清理；默认入口不联网。
import argparse
import io
import json
from openai import OpenAI


def run():
    # 使用调用者显式配置的 OPENAI_API_KEY；不会从项目文件寻找密钥。
    # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
    # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
    client = OpenAI(timeout=30, max_retries=0)
    store_id = None
    file_id = None
    try:
        store = client.vector_stores.create(name='ai-learn-disposable',
                                            expires_after={'anchor': 'last_active_at', 'days': 1})
        store_id = store.id
        uploaded = client.files.create(file=('fictional.txt', io.BytesIO('虚构课程开放时间为09:00到18:00。'.encode())), purpose='assistants')
        file_id = uploaded.id
        # 等待索引完成后再搜索；文件上传成功并不代表向量已就绪。
        attached = client.vector_stores.files.create_and_poll(vector_store_id=store_id, file_id=file_id,
                                                             attributes={'owner': 'alice'}, max_wait_seconds=60)
        if attached.status != 'completed':
            raise RuntimeError('索引未完成，不能把上传成功当可检索')
        result = client.vector_stores.search(store_id, query='课程开放时间', max_num_results=5,
                                             filters={'type': 'eq', 'key': 'owner', 'value': 'alice'})
        return {'mode': '真实云端检索', 'store_id': store_id, 'file_id': file_id,
                # 把 SDK 或模型对象转成普通数据，方便保存与返回；不要把对象的调试字符串当作协议 JSON。
                'results': result.model_dump(), 'answer_generated': False}
    # 无论成功还是失败，都执行这里的收尾步骤。
    finally:
        # 仅清理由本次 run 创建的资源；两项都尝试，清理错误必须可见。
        errors = []
        for kind, resource_id, delete in [('store', store_id, client.vector_stores.delete),
                                          ('file', file_id, client.files.delete)]:
            if resource_id:
                try:
                    delete(resource_id)
                except Exception as error:
                    errors.append({'kind': kind, 'id': resource_id, 'error_type': type(error).__name__})
        # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
        # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
        print(json.dumps({'cleanup_errors': errors}, ensure_ascii=False))
        client.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--live', action='store_true', help='使用自己的 OpenAI API 凭证；可能收费')
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    if args.live:
        # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
        # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
        # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
        print(json.dumps(run(), ensure_ascii=False, indent=2))
    else:
        print('未联网。此选修依赖 OpenAI 3.37.0 已核对的接口；需要自己的 API 账户才使用 --live。')
