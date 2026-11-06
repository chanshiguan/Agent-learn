"""单任务 SDK 托管样例：独立目录、超时、结果分类、会话续接。"""

# 从 run 看任务目录与收据，再读 live_query 和 make_options；默认 demo 不调用云端。
import argparse
import asyncio
import json
import os
from pathlib import Path
from types import SimpleNamespace


# SDK 正常结束只表示调用成功；内容还需核对，所以返回 NEEDS_REVIEW。
def result_record(message):
    success = message.subtype == 'success' and not message.is_error
    return {'status': 'NEEDS_REVIEW' if success else 'FAILED',
            'subtype': message.subtype, 'session_id': message.session_id,
            'answer': message.result if success else None,
            'usage': message.usage, 'total_cost_usd': message.total_cost_usd}


# 恢复需要原 session_id 和会话目录；空工具池用于限制本例的执行能力。
def make_options(job, resume=False):
    from claude_agent_sdk import ClaudeAgentOptions
    session = None
    if resume:
        # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
        # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
        previous = json.loads((job/'session.json').read_text())
        session = previous.get('session_id')
        if not session:
            raise ValueError('没有可恢复 session_id')
    # cwd：限定命令的工作目录，防止相对路径落到用户的其他项目或错误位置。
    # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
    # allowed_tools：缩小宿主允许调用的工具集合；提示词里写“只读”不能替代这里的权限配置。
    return ClaudeAgentOptions(cwd=str(job), tools=[], allowed_tools=[],
        # setting_sources：限定从哪些位置加载规则，避免实验被用户全局设置或其他目录的配置悄悄影响。
        strict_mcp_config=True, mcp_servers={}, setting_sources=[],
        # max_turns：限制 Agent 与模型交互的总轮数，避免角色交接或工具调用迟迟不能结束。
        max_turns=2, max_budget_usd=0.20, resume=session,
        # env：只把本次需要的环境交给子进程；环境变量是否包含凭证应由调用方明确控制。
        env={'CLAUDE_CONFIG_DIR': str(job/'session-store')},
        system_prompt='根据给定的虚构正文检查是否包含运行说明。不使用工具。只回答缺项及理由。')


# 持续读取消息，只有 ResultMessage 才作为终止结果；普通文本不能代替收据。
async def live_query(job, resume):
    from claude_agent_sdk import query, ResultMessage
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    prompt = (job/'request.txt').read_text()
    final = None
    async for message in query(prompt=prompt, options=make_options(job, resume)):
        if isinstance(message, ResultMessage):
            final = result_record(message)
    if final is None:
        raise RuntimeError('消息流结束但没有 ResultMessage')
    return final


async def run(job, mode='demo', scenario='success', resume=False, timeout=90):
    # 把相对路径变成绝对路径并解析符号链接；涉及目录权限时，还要检查解析后的位置是否在允许目录内。
    job = Path(job).resolve()
    job.mkdir(parents=True, exist_ok=True)
    request = job/'request.txt'
    if not request.exists():
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        request.write_text('虚构 README：项目用于问候；需要 Python 3；尚未写运行步骤。请指出缺项。')
    if resume and mode != 'live':
        raise ValueError('demo 会话不能当真实 SDK 会话恢复')
    if not resume and (job/'result.json').exists():
        raise ValueError('该任务已有结果；新任务请使用新目录，续接请显式 --resume --live')
    try:
        if mode == 'live':
            # 独立配置目录不复制用户 CLI 登录文件；采用调用者提供的 API 身份。
            if not os.environ.get('ANTHROPIC_API_KEY'):
                raise ValueError('live 需要 ANTHROPIC_API_KEY；不要写入源码或提交文件')
            # 超时由应用包住整个异步任务；轮数限制和等待时间限制分别设置。
            # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
            result = await asyncio.wait_for(live_query(job, resume), timeout=timeout)
        elif scenario == 'timeout':
            raise TimeoutError('演示超时')
        else:
            message = SimpleNamespace(subtype='success' if scenario == 'success' else 'error_max_turns',
                is_error=scenario != 'success', session_id=None,
                result='缺少运行说明，应写出命令及预期输出。', usage={}, total_cost_usd=None)
            result = result_record(message)
    except TimeoutError:
        result = {'status': 'TIMEOUT', 'session_id': None, 'answer': None}
    except Exception as error:
        # 不将服务异常原文（可能含凭证/正文）直接写入教学日志。
        result = {'status': 'FAILED', 'error_type': type(error).__name__,
                  'session_id': None, 'answer': None}
    result['mode'] = mode
    # 只有真实运行返回的会话 ID 才保存为恢复依据，demo 不伪造会话。
    if mode == 'live' and result.get('session_id'):
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
        (job/'session.json').write_text(json.dumps({'session_id':result['session_id']}))
    destination = job/'result.json'
    if destination.exists():
        # 续接前保留上一轮收据，以免失败覆盖唯一的 session_id。
        # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
        # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
        (job/'previous-result.json').write_text(destination.read_text())
    # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    # required：明确哪些字段不可缺少；有默认值与必须提供是两种不同的接口约定。
    parser.add_argument('--job-dir', required=True, type=Path)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--live', action='store_true')
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--resume', action='store_true')
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--scenario', choices=['success','limit','timeout'], default='success')
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    output = asyncio.run(run(args.job_dir, 'live' if args.live else 'demo', args.scenario,args.resume))
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(output, ensure_ascii=False, indent=2))
    raise SystemExit(0 if output['status']=='NEEDS_REVIEW' else 1)
