"""离线错误恢复：固定脚本模拟模型，不需要 Ollama 或密钥。"""

# 这里故意查询不存在的城市，检查错误能否作为工具结果回到下一轮。

import json

from agent import print_run, run_agent


# 首轮返回工具请求，下一轮检查失败结果并说明原因；这两轮响应均为固定脚本。
def scripted_ask(messages, tools):
    results = [message for message in messages if message["role"] == "tool"]
    if not results:
        return {"finish_reason": "tool_calls", "message": {"role": "assistant", "tool_calls": [
            {"id": "bad-city", "type": "function", "function": {
                "name": "get_weather", "arguments": '{"city":"火星"}'}}
        ]}}
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    error = json.loads(results[-1]["content"])
    assert error["ok"] is False
    return {"finish_reason": "stop", "message": {"role": "assistant",
        "content": "没有火星的示例气温数据，无法查询；目前支持台北、北京、上海。"}}


if __name__ == "__main__":
    print("离线演示：下一步回答来自固定脚本，用于验证程序能否返回错误。")
    print_run(run_agent("查火星的示例气温", scripted_ask))
