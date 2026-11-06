"""Anthropic 原生消息格式。默认离线；只有 --live 才访问云端。"""

# 阅读顺序：run_claude 的消息循环 → mock_create 的离线响应 → main 的模式选择。

import argparse
import json
import os
import time
from types import SimpleNamespace

from agent import SYSTEM
from tools import TOOLS, execute


# 保留 assistant 的完整内容块，并用对应的 tool_use_id 返回每个工具结果。
def run_claude(create, question, model, max_steps=6, max_calls=8, max_tokens=20000, max_seconds=180):
    tools = [{"name": tool["function"]["name"], "description": tool["function"]["description"],
              "input_schema": tool["function"]["parameters"]} for tool in TOOLS]
    # 执行白名单取自本轮公开的工具，防止模型用一个实现中存在、但本轮未授权的函数名绕过限制。
    allowed = {tool["name"] for tool in tools}
    # 这份历史同时保存问题、模型请求和工具观察；下一轮需要它们才能沿用真实结果，保持调用与结果的顺序。
    messages = [{"role": "user", "content": question}]
    # 跨轮记录已见过的调用 ID，避免模型重复使用同一个 ID 导致结果无法可靠关联。
    seen_ids = set()
    # 累计的是实际工具次数，与模型轮数不同；一轮可能同时请求多个工具，所以要单独限额。
    call_count = 0
    # 累加服务报告的用量，作为停止依据之一；服务漏报时这里只能观察，不能保证严格账单上限。
    used_tokens = 0
    # 记录循环开始的时刻，后面在请求前后检查总耗时，避免每轮各自未超时却总任务无限拖长。
    started = time.monotonic()
    for step in range(1, max_steps + 1):
        if time.monotonic() - started >= max_seconds:
            raise RuntimeError("达到时长检查上限")
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
        # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
        # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
        response = create(model=model, max_tokens=1024, system=SYSTEM, tools=tools, messages=messages)
        # 用量来自服务实际报告，用于成本和预算核对；缺失时保留未知，不自行估算成确定账单。
        usage = getattr(response, "usage", None)
        if usage:
            used_tokens += usage.input_tokens + usage.output_tokens
        if used_tokens >= max_tokens or time.monotonic() - started >= max_seconds:
            raise RuntimeError("达到 token 或时长检查上限")
        if response.stop_reason not in ("tool_use", "end_turn"):
            raise RuntimeError(f"停止原因需处理，不能当成成功：{response.stop_reason}")
        # 把 SDK 或模型对象转成普通数据，方便保存与返回；不要把对象的调试字符串当作协议 JSON。
        # exclude_none：省略值为 None 的可选字段，避免把“未返回”误写成一项有内容的协议字段。
        blocks = [block.model_dump(exclude_none=True) if hasattr(block, "model_dump") else block
                  for block in response.content]
        # 保留整组内容块，包括存在时的 thinking / signature，不过滤重建。
        messages.append({"role": "assistant", "content": blocks})
        # 没有调用时才进入最终回答分支；空列表是“本轮不执行工具”，不是已经取得工具结果。
        calls = [block for block in blocks if block["type"] == "tool_use"]
        if not calls:
            answer = "\n".join(block["text"] for block in blocks if block["type"] == "text")
            if response.stop_reason != "end_turn" or not answer.strip():
                raise RuntimeError("没有有效最终文字")
            return {"answer": answer, "messages": messages, "steps": step, "tokens": used_tokens}
        if response.stop_reason != "tool_use" or call_count + len(calls) > max_calls:
            raise RuntimeError("工具请求状态错误或达到次数上限")
        # 先检查整批调用是否重复，再执行任何一个工具；发现坏请求时不能让前几个副作用已经发生。
        batch_ids = set()
        for call in calls:
            call_id = call.get("id")
            if (not isinstance(call_id, str) or not call_id or call_id in seen_ids
                    or call_id in batch_ids or not isinstance(call.get("name"), str) or "input" not in call):
                raise RuntimeError("工具请求结构错误或 ID 重复")
            batch_ids.add(call_id)
        seen_ids.update(batch_ids)
        results = []
        for call in calls:
            result = execute(call["name"], call["input"], allowed)
            results.append({"type": "tool_result", "tool_use_id": call["id"],
                            # 把结果编码成协议可接受的 JSON；模型收到的是工具数据，不能把其中的指令当作系统授权。
                            # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
                            # allow_nan：设为 False 时拒绝 NaN 和无穷大，避免产生不符合标准 JSON 或业务数值范围的结果。
                            "content": json.dumps(result, ensure_ascii=False, allow_nan=False),
                            "is_error": not result["ok"]})
            call_count += 1
        # 全部结果立即接在对应 assistant 后面，Anthropic 使用 user 角色。
        messages.append({"role": "user", "content": results})
    raise RuntimeError(f"Agent 超过 {max_steps} 轮模型请求，已停止")


# 固定模拟工具请求与最终回复，用来检查协议；不代表 Claude 的实际表现。
def mock_create(**kwargs):
    if len(kwargs["messages"]) == 1:
        return SimpleNamespace(stop_reason="tool_use", content=[{
            "type": "tool_use", "id": "demo-1", "name": "get_weather", "input": {"city": "台北"}}])
    return SimpleNamespace(stop_reason="end_turn", content=[{
        "type": "text", "text": "台北的固定教学气温是摄氏 26 度，不是实时天气。"}])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--live", action="store_true", help="显式运行收费云端 API")
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("question", nargs="?", default="查询台北的示例气温。")
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    if args.live:
        import anthropic

        model = os.environ.get("ANTHROPIC_MODEL")
        if not model or not os.environ.get("ANTHROPIC_API_KEY"):
            parser.error("先设置 ANTHROPIC_MODEL 和 ANTHROPIC_API_KEY；模型必须是账号当前可用 ID")
        # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
        # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
        client = anthropic.Anthropic(timeout=60.0, max_retries=1)
        result = run_claude(client.messages.create, args.question, model)
    else:
        print("离线固定脚本；不代表 Claude 的真实表现。")
        result = run_claude(mock_create, args.question, "offline-demo")
    print(result["answer"])
    # 把结果编码成协议可接受的 JSON；模型收到的是工具数据，不能把其中的指令当作系统授权。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(result["messages"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # 进入本文件的演示入口。
    main()
