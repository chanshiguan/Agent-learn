"""不安装 Anthropic SDK 也能运行原生消息格式的离线测试。"""

# 先读测试中的输入和预期，再读被调用函数；这里检查协议、边界与失败分支，不能据此推断真实模型效果。

import copy
import json
import unittest
from importlib import import_module
from types import SimpleNamespace

run_claude = import_module("08_anthropic_agent").run_claude


class AnthropicTests(unittest.TestCase):
    def test_preserve_blocks_and_error_result(self):
        thinking = {"type": "thinking", "thinking": "不透明测试对象", "signature": "fixture-signature"}
        call = {"type": "tool_use", "id": "t1", "name": "get_weather", "input": {"city": "火星"}}

        def create(**kwargs):
            if len(kwargs["messages"]) == 1:
                return SimpleNamespace(stop_reason="tool_use", content=[copy.deepcopy(thinking), copy.deepcopy(call)])
            # 这份历史同时保存问题、模型请求和工具观察；下一轮需要它们才能沿用真实结果，保持调用与结果的顺序。
            messages = kwargs["messages"]
            # 核对实际值与预期值相等。
            self.assertEqual(messages[-2]["content"][0], thinking)
            result = messages[-1]["content"][0]
            # 核对实际值与预期值相等。
            self.assertEqual(messages[-1]["role"], "user")
            # 核对实际值与预期值相等。
            self.assertEqual(result["tool_use_id"], "t1")
            # 核对条件成立。
            self.assertTrue(result["is_error"])
            # 核对条件不成立。
            # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
            self.assertFalse(json.loads(result["content"])["ok"])
            return SimpleNamespace(stop_reason="end_turn", content=[{"type": "text", "text": "无法查询"}])

        # 核对实际值与预期值相等。
        self.assertEqual(run_claude(create, "查火星", "mock")["answer"], "无法查询")

    def test_multiple_calls_and_success(self):
        def create(**kwargs):
            if len(kwargs["messages"]) == 1:
                return SimpleNamespace(stop_reason="tool_use", content=[
                    {"type": "tool_use", "id": f"t{i}", "name": "get_weather", "input": {"city": city}}
                    for i, city in enumerate(("台北", "北京"))])
            results = kwargs["messages"][-1]["content"]
            # 核对实际值与预期值相等。
            self.assertEqual(len(results), 2)
            # 核对条件成立。
            self.assertTrue(all(not result["is_error"] for result in results))
            return SimpleNamespace(stop_reason="end_turn", content=[{"type": "text", "text": "已查两座城市"}])
        # 核对实际值与预期值相等。
        self.assertEqual(run_claude(create, "查询", "mock")["steps"], 2)

    def test_truncation_stops_before_execution(self):
        def create(**kwargs):
            return SimpleNamespace(stop_reason="max_tokens", content=[])
        with self.assertRaisesRegex(RuntimeError, "停止原因"):
            run_claude(create, "测试", "mock")

    def test_loop_limit(self):
        def create(**kwargs):
            return SimpleNamespace(stop_reason="tool_use", content=[{
                "type": "tool_use", "id": str(len(kwargs["messages"])), "name": "get_weather", "input": {"city": "台北"}}])
        with self.assertRaisesRegex(RuntimeError, "超过 2 轮"):
            # max_steps：限制循环最多执行多少步；它是程序的停止条件，不能只在提示词里写“不要无限循环”。
            run_claude(create, "循环", "mock", max_steps=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
