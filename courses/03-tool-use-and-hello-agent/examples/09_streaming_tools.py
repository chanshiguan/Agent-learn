"""收齐流式工具参数后，再交给原有 Agent 验证与执行。"""

# 流式参数可能被拆成多个字符串；全部收齐且正常结束后，才能交给执行器。

import argparse
import json
import os

from agent import print_run, run_agent


# 按 index 拼接同一次调用的名称、ID 和参数，最后整理成 run_agent 接受的普通消息。
def collect_stream(chunks):
    content = ""
    calls = {}
    finish_reason = None
    tokens = 0
    size = 0
    for chunk in chunks:
        # 用量来自服务实际报告，用于成本和预算核对；缺失时保留未知，不自行估算成确定账单。
        usage = chunk.get("usage")
        if usage:
            tokens = usage.get("total_tokens", 0)
        choices = chunk.get("choices") or []
        if not choices:
            continue
        choice = choices[0]
        delta = choice.get("delta") or {}
        if delta.get("refusal"):
            raise RuntimeError("流式响应包含拒答")
        text = delta.get("content") or ""
        content += text
        size += len(text)
        for part in delta.get("tool_calls") or []:
            index = part.get("index")
            if type(index) is not int or not 0 <= index < 8:
                raise RuntimeError("工具片段缺少合法 index，或单轮请求过多")
            # 同轮多个调用的碎片可能交错，用 index 分组，不能只按到达顺序拼成一条。
            call = calls.setdefault(index, {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
            for key in ("id",):
                fragment = part.get(key) or ""
                call[key] += fragment
                size += len(fragment)
            function = part.get("function") or {}
            for key in ("name", "arguments"):
                fragment = function.get(key) or ""
                if not isinstance(fragment, str):
                    raise RuntimeError("兼容接口的流式参数片段必须是字符串")
                call["function"][key] += fragment
                size += len(fragment)
            if part.get("type") not in (None, "function"):
                raise RuntimeError("不是本课支持的函数工具")
        if size > 65536:
            raise RuntimeError("流式响应超过教学大小上限")
        if choice.get("finish_reason") is not None:
            finish_reason = choice["finish_reason"]
    # 没有正常结束信号就拒绝整批请求，不能执行一半参数。
    if finish_reason not in ("stop", "tool_calls"):
        raise RuntimeError(f"流没有完整结束，禁止执行：{finish_reason}")
    message = {"role": "assistant", "content": content}
    if calls:
        if sorted(calls) != list(range(len(calls))):
            raise RuntimeError("工具片段 index 不连续")
        message["tool_calls"] = [calls[index] for index in sorted(calls)]
    return {"message": message, "finish_reason": finish_reason, "tokens": tokens}


# 这里只适配流式接口；工具授权和参数检查仍由原 Agent 循环负责。
def make_stream_ask():
    from openai import OpenAI

    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
    # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=60, max_retries=0)

    def ask(messages, tools):
        with client.chat.completions.create(
            # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
            # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
            # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
            model=os.environ.get("OLLAMA_MODEL", "gemma4:e4b"), messages=messages, tools=tools,
            # stream：以增量片段接收响应，改善首字等待；工具参数必须收齐并校验后才能执行。
            # stream_options：请求流结束时附带用量等信息；没有收到用量时应记为未知，不能据此声称免费。
            stream=True, stream_options={"include_usage": True},
            # reasoning_effort：配置模型支持的推理行为；这里的值必须与所用服务兼容，不能当作所有模型通用的开关。
            # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
            # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
            reasoning_effort="none", temperature=0, max_tokens=768,
        ) as stream:
            # 把 SDK 或模型对象转成普通数据，方便保存与返回；不要把对象的调试字符串当作协议 JSON。
            # exclude_none：省略值为 None 的可选字段，避免把“未返回”误写成一项有内容的协议字段。
            return collect_stream(chunk.model_dump(exclude_none=True) for chunk in stream)

    return ask


# 故意把 city 参数拆成两个片段，验证拼接顺序与结束判断。
def mock_ask(messages, tools):
    if any(message["role"] == "tool" for message in messages):
        chunks = [{"choices": [{"delta": {"content": "台北固定示例气温为26摄氏度，非实时。"}, "finish_reason": "stop"}]}]
    else:
        chunks = [
            {"choices": [{"delta": {"tool_calls": [{"index": 0, "id": "stream-1", "type": "function", "function": {"name": "get_weather", "arguments": '{"city":"'}}]}}]},
            {"choices": [{"delta": {"tool_calls": [{"index": 0, "function": {"arguments": '台北"}'}}]}, "finish_reason": "tool_calls"}]},
        ]
    return collect_stream(chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--live", action="store_true")
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    print("本机真实流式请求" if args.live else "离线分片演示，不代表模型表现")
    print_run(run_agent("查询台北的示例气温。", make_stream_ask() if args.live else mock_ask))
