"""只用标准库的离线测试：验证程序逻辑，不预测模型质量。"""

# 先读测试中的输入和预期，再读被调用函数；这里检查协议、边界与失败分支，不能据此推断真实模型效果。

import copy
import json
import unittest
from unittest.mock import patch

from agent import run_agent
from tools import TOOLS, execute
from importlib import import_module

eval_module = import_module("06_schema_eval")


def tool_reply(name="get_weather", arguments=None, call_id="c1"):
    if arguments is None:
        arguments = '{"city":"台北"}'
    return {"finish_reason": "tool_calls", "tokens": 10, "message": {"role": "assistant", "tool_calls": [
        {"id": call_id, "type": "function", "function": {"name": name, "arguments": arguments}}
    ]}}


def final_reply(text="台北的示例气温为摄氏 26 度。"):
    return {"finish_reason": "stop", "tokens": 10, "message": {"role": "assistant", "content": text}}


def sequence(*replies):
    iterator = iter(copy.deepcopy(replies))
    return lambda messages, tools: next(iterator)


class ToolTests(unittest.TestCase):
    def test_weather(self):
        # 核对实际值与预期值相等。
        self.assertEqual(execute("get_weather", '{"city":"台北"}', {"get_weather"})["data"]["temperature"], 26)

    def test_untrusted_parameters(self):
        cases = ["{bad", "[]", '{"city":""}', '{"city":12}', '{"city":"台北","admin":true}']
        for arguments in cases:
            with self.subTest(arguments=arguments):
                # 核对条件不成立。
                self.assertFalse(execute("get_weather", arguments, {"get_weather"})["ok"])

    def test_unknown_tool_not_executed(self):
        # 核对条件不成立。
        self.assertFalse(execute("delete_files", "{}", {"get_weather"})["ok"])

    def test_hidden_tool_not_executed(self):
        with patch("tools.calculator", side_effect=AssertionError("不应执行")):
            # 核对条件不成立。
            self.assertFalse(execute("calculator", "{}", {"get_weather"})["ok"])

    def test_numeric_boundaries(self):
        for value in (True, float("nan"), float("inf"), 1000001, "2"):
            with self.subTest(value=value):
                # 核对条件不成立。
                self.assertFalse(execute("calculator", {"operation": "add", "left": value, "right": 2}, {"calculator"})["ok"])

    def test_bad_operation(self):
        # 核对条件不成立。
        self.assertFalse(execute("calculator", '{"operation":"exec","left":1,"right":2}', {"calculator"})["ok"])

    def test_zero_division(self):
        result = execute("calculator", '{"operation":"divide","left":1,"right":0}', {"calculator"})
        # 核对目标包含在结果中。
        self.assertIn("除数", result["error"]["message"])

    def test_conversion(self):
        # 核对实际值与预期值相等。
        self.assertEqual(execute("convert_temperature", '{"value":26,"from_unit":"celsius","to_unit":"fahrenheit"}', {"convert_temperature"})["data"]["value"], 78.8)


class LoopTests(unittest.TestCase):
    def test_stop_without_tool_call(self):
        result = run_agent("你好", sequence(final_reply("你好")))
        # 核对实际值与预期值相等。
        self.assertEqual(result["steps"], 1)
        # 核对实际值与预期值相等。
        self.assertEqual([event["event"] for event in result["trace"]], ["final"])

    def test_complete_history_and_call_id(self):
        def ask(messages, tools):
            if len(messages) == 2:
                return tool_reply()
            # 核对实际值与预期值相等。
            self.assertEqual(messages[-2]["role"], "assistant")
            # 核对实际值与预期值相等。
            self.assertEqual(messages[-1]["tool_call_id"], "c1")
            # 核对实际值与预期值相等。
            # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
            self.assertEqual(json.loads(messages[-1]["content"])["data"]["temperature"], 26)
            return final_reply()
        # 核对实际值与预期值相等。
        self.assertEqual(run_agent("查气温", ask)["steps"], 2)

    def test_multiple_calls_get_multiple_results(self):
        reply = tool_reply()
        reply["message"]["tool_calls"].extend(tool_reply(call_id="c2")["message"]["tool_calls"])
        result = run_agent("两次", sequence(reply, final_reply()))
        # 核对实际值与预期值相等。
        self.assertEqual(len([message for message in result["messages"] if message["role"] == "tool"]), 2)

    def test_dependent_calls_and_eval(self):
        conversion = tool_reply("convert_temperature", '{"value":26,"from_unit":"celsius","to_unit":"fahrenheit"}', "c2")
        result = run_agent("换算", sequence(tool_reply(), conversion, final_reply("示例气温华氏 78.8 度")))
        case = {"id": "chain", "actions": ["get_weather", "convert_temperature"], "number": 78.8, "city": "台北"}
        # 核对条件成立。
        self.assertTrue(eval_module.score(case, result)[0])
        result["trace"][2]["step"] = 1
        # 核对条件不成立。
        self.assertFalse(eval_module.score(case, result)[0])

    def test_eval_chinese_number_boundary(self):
        result = run_agent("天气", sequence(tool_reply(), final_reply("台北示例气温为26.0摄氏度。")))
        case = {"id": "weather", "actions": ["get_weather"], "number": 26, "city": "台北"}
        # 核对条件成立。
        self.assertTrue(eval_module.score(case, result)[0])
        case["number"] = 6
        # 核对条件不成立。
        self.assertFalse(eval_module.score(case, result)[0])

    def test_eval_error_must_query_requested_city(self):
        result = run_agent("错误实验", sequence(tool_reply(arguments='{"city":"月球"}'), final_reply("没有数据")))
        case = {"id": "missing", "actions": ["get_weather"], "error": True, "city": "火星"}
        # 核对条件不成立。
        self.assertFalse(eval_module.score(case, result)[0])

    def test_unknown_and_parse_errors_returned(self):
        for reply in (tool_reply("unknown"), tool_reply(arguments="{bad")):
            result = run_agent("测试", sequence(reply, final_reply("无法完成")))
            # 核对条件不成立。
            self.assertFalse(result["trace"][1]["result"]["ok"])

    def test_recovery_with_corrected_arguments(self):
        result = run_agent("查气温", sequence(tool_reply(arguments="{}"), tool_reply(call_id="c2"), final_reply()))
        # 核对条件不成立。
        self.assertFalse(result["trace"][1]["result"]["ok"])
        # 核对条件成立。
        self.assertTrue(result["trace"][3]["result"]["ok"])

    def test_step_limit(self):
        with self.assertRaisesRegex(RuntimeError, "超过 2 轮"):
            # 运行有轮数与工具次数限制的 Agent 循环。
            # max_steps：限制循环最多执行多少步；它是程序的停止条件，不能只在提示词里写“不要无限循环”。
            run_agent("循环", sequence(tool_reply(call_id="c1"), tool_reply(call_id="c2")), max_steps=2)

    def test_call_limit_checks_whole_batch(self):
        reply = tool_reply()
        reply["message"]["tool_calls"].extend(tool_reply(call_id="c2")["message"]["tool_calls"])
        with patch("agent.execute") as execute_mock:
            with self.assertRaisesRegex(RuntimeError, "次数上限"):
                # 运行有轮数与工具次数限制的 Agent 循环。
                run_agent("循环", sequence(reply), max_calls=1)
            execute_mock.assert_not_called()

    def test_missing_or_duplicate_ids(self):
        for call_id in (None, ""):
            with self.assertRaisesRegex(RuntimeError, "结构无效"):
                # 运行有轮数与工具次数限制的 Agent 循环。
                run_agent("错误 ID", sequence(tool_reply(call_id=call_id)))
        with self.assertRaisesRegex(RuntimeError, "重复"):
            # 运行有轮数与工具次数限制的 Agent 循环。
            run_agent("重复 ID", sequence(tool_reply(), tool_reply()))

    def test_truncated_refused_and_empty_output(self):
        replies = [final_reply(""), final_reply(), final_reply(), final_reply()]
        replies[1]["finish_reason"] = "length"
        replies[2]["message"]["refusal"] = "拒答"
        replies[3]["finish_reason"] = "unknown"
        for reply in replies:
            with self.subTest(reply=reply), self.assertRaises(RuntimeError):
                # 运行有轮数与工具次数限制的 Agent 循环。
                run_agent("测试", sequence(reply))

    def test_token_limit(self):
        with self.assertRaisesRegex(RuntimeError, "token"):
            # 运行有轮数与工具次数限制的 Agent 循环。
            # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
            run_agent("测试", sequence(final_reply()), max_tokens=5)

    def test_time_limit(self):
        with self.assertRaisesRegex(RuntimeError, "时长"):
            # 运行有轮数与工具次数限制的 Agent 循环。
            run_agent("测试", sequence(final_reply()), max_seconds=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
