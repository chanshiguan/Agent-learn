"""真实 Agents SDK 编排；默认脚本模型，--live 才接本地 Ollama。"""

# 同一问题做两次实验：专家作为工具时主管回答，handoff 后由专家回答。
import argparse
import asyncio
import json
from agents import Agent, Runner, Model, ModelResponse, Usage, set_tracing_disabled, set_trace_provider
from agents.tracing.provider import DefaultTraceProvider
from openai.types.responses import ResponseOutputMessage, ResponseOutputText, ResponseFunctionToolCall


# 构造 SDK 可消费的文本消息对象，作为离线模型的预设输出。
def text_item(text):
    return ResponseOutputMessage(id='msg_demo', type='message', role='assistant', status='completed',
        content=[ResponseOutputText(type='output_text',text=text,annotations=[])])


class ScriptedModel(Model):
    """模型替身只控制响应；工具调用、交接与运行循环由真实 SDK 执行。"""
    def __init__(self, outputs):
        self.outputs = list(outputs)

    async def get_response(self, *args, **kwargs):
        if not self.outputs:
            raise RuntimeError('脚本响应耗尽，可能发生非预期循环')
        return ModelResponse(output=self.outputs.pop(0), usage=Usage(), response_id=None)

    async def stream_response(self, *args, **kwargs):
        raise NotImplementedError('本教学例仅验证非流式路径')
        if False:
            # 保留异步生成器接口的语法形状；上方已明确抛错，这个分支不会实际产出值。
            yield None


# 只有 live 模式使用本机 Ollama；客户端不会读取系统代理设置。
def local_model(name):
    from agents import OpenAIChatCompletionsModel
    from openai import AsyncOpenAI, DefaultAsyncHttpxClient
    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
    # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
    client = AsyncOpenAI(base_url='http://localhost:11434/v1',api_key='ollama',timeout=60,max_retries=0,
                         # http_client：显式注入底层 HTTP 客户端，让代理、超时等行为与这个案例的运行条件一致。
                         # trust_env：设为 False 可避免继承系统代理等环境配置，使本地请求路径更可控；不会关闭 TLS 证书校验。
                         http_client=DefaultAsyncHttpxClient(trust_env=False))
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    return OpenAIChatCompletionsModel(model=name, openai_client=client)


async def run(live=False, model_name='gemma4:e4b'):
    # 不注册网络 exporter，避免离线案例也初始化代理客户端。
    set_trace_provider(DefaultTraceProvider())
    set_tracing_disabled(True)
    specialist = Agent(name='specialist', instructions='依据固定虚构资料回答：报名截止时间为周五18:00。',
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=local_model(model_name) if live else ScriptedModel([[text_item('周五18:00 [signup]')]]))
    # 专家包装成工具后，返回值仍交回主管，由主管组织最后回答。
    expert_tool = specialist.as_tool(tool_name='ask_specialist',tool_description='查询虚构报名截止时间')
    manager = Agent(name='manager', instructions='必须先用 ask_specialist 查询报名时间，再由你总结并保留来源。',
        # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        tools=[expert_tool], model=local_model(model_name) if live else ScriptedModel([
            [ResponseFunctionToolCall(type='function_call',call_id='call_demo',name='ask_specialist',
                                      # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
                                      arguments=json.dumps({'input':'报名截止时间？'}))],
            [text_item('主管汇总：周五18:00 [signup]')]]))
    # max_turns：限制 Agent 与模型交互的总轮数，避免角色交接或工具调用迟迟不能结束。
    managed = await Runner.run(manager,'报名截止时间？',max_turns=4)
    # 两次实验使用独立 Agent 和模型实例，避免脚本队列/会话相互影响。
    receiving = Agent(name='specialist', instructions='直接回答用户：报名截止时间为周五18:00，来源signup。',
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=local_model(model_name) if live else ScriptedModel([[text_item('周五18:00 [signup]')]]))
    # handoff 则改变接下来回答的 Agent；最后检查 last_agent 来验证区别。
    triage = Agent(name='triage', instructions='将报名问题交给 specialist，不自行作答。',handoffs=[receiving],
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        model=local_model(model_name) if live else ScriptedModel([
            [ResponseFunctionToolCall(type='function_call',call_id='handoff_demo',
                                      name='transfer_to_specialist',arguments='{}')]]))
    # max_turns：限制 Agent 与模型交互的总轮数，避免角色交接或工具调用迟迟不能结束。
    handed = await Runner.run(triage,'报名截止时间？',max_turns=4)
    rows = []
    for name,result in [('manager_as_tools',managed),('handoff',handed)]:
        rows.append({'pattern':name,'final_agent':result.last_agent.name,
                     'answer':result.final_output,
                     'events':[{'type':item.type,'agent':item.agent.name} for item in result.new_items]})
    return {'mode':'本地模型' if live else '真实 SDK + 脚本模型，非模型能力评测','rows':rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--live',action='store_true')
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--model',default='gemma4:e4b')
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(asyncio.run(run(args.live,args.model)),ensure_ascii=False,indent=2))
