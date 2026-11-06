"""补充案例的边界与反馈流程测试，默认不安装Instructor/Outlines也能执行。"""

# 先读测试中的输入和预期，再读被调用函数；这里检查协议、边界与失败分支，不能据此推断真实模型效果。

import copy
import threading
import unittest
from importlib import import_module
from unittest.mock import patch

from agent import run_agent
from test_agent import final_reply, sequence, tool_reply

streaming = import_module("09_streaming_tools")
choices = import_module("10_tool_choice")
parallel = import_module("11_parallel_tools")
refine = import_module("12_self_refine")
reflexion = import_module("13_reflexion")
typed = import_module("14_instructor")
codeact = import_module("16_codeact")
retrieval = import_module("17_react_retrieval")


class StreamingTests(unittest.TestCase):
    def test_fragmented_arguments_complete_before_execution(self):
        result = run_agent("天气", streaming.mock_ask)
        # 核对实际值与预期值相等。
        self.assertEqual(result["trace"][0]["arguments"], '{"city":"台北"}')
        # 核对条件成立。
        self.assertTrue(result["trace"][1]["result"]["ok"])

    def test_interleaved_call_indexes(self):
        parts = [
            {"choices": [{"delta": {"tool_calls": [{"index": 1, "id": "b", "function": {"name": "get_weather", "arguments": '{"city":'}}]}}]},
            {"choices": [{"delta": {"tool_calls": [{"index": 0, "id": "a", "function": {"name": "get_weather", "arguments": '{"city":"台北"}'}}]}}]},
            {"choices": [{"delta": {"tool_calls": [{"index": 1, "function": {"arguments": '"北京"}'}}]}, "finish_reason": "tool_calls"}]},
            {"choices": [], "usage": {"total_tokens": 12}},
        ]
        reply = streaming.collect_stream(parts)
        # 核对实际值与预期值相等。
        self.assertEqual([call["id"] for call in reply["message"]["tool_calls"]], ["a", "b"])
        # 核对实际值与预期值相等。
        self.assertEqual(reply["tokens"], 12)

    def test_incomplete_stream_never_executes(self):
        chunks = [{"choices": [{"delta": {"content": "半截"}}]}]
        with patch("agent.execute") as runner:
            with self.assertRaisesRegex(RuntimeError, "禁止执行"):
                # 运行有轮数与工具次数限制的 Agent 循环。
                run_agent("天气", lambda messages, tools: streaming.collect_stream(chunks))
            runner.assert_not_called()

    def test_truncated_stream_rejected(self):
        with self.assertRaises(RuntimeError):
            streaming.collect_stream([{"choices": [{"delta": {}, "finish_reason": "length"}]}])

    def test_invalid_index_and_size(self):
        with self.assertRaises(RuntimeError):
            streaming.collect_stream([{"choices": [{"delta": {"tool_calls": [{"index": 9}]}}]}])
        with self.assertRaises(RuntimeError):
            streaming.collect_stream([{"choices": [{"delta": {"content": "x" * 65537}, "finish_reason": "stop"}]}])


class ExecutionTests(unittest.TestCase):
    def test_tool_choice_shapes(self):
        # 核对实际值与预期值相等。
        self.assertEqual(choices.choice_value("specific")["function"]["name"], "get_weather")
        for mode in ("auto", "none", "required"):
            # 核对实际值与预期值相等。
            self.assertEqual(choices.choice_value(mode), mode)
        with self.assertRaises(ValueError):
            choices.choice_value("admin")

    def test_parallel_workers_really_overlap_and_preserve_order(self):
        barrier = threading.Barrier(2)
        # 没有调用时才进入最终回答分支；空列表是“本轮不执行工具”，不是已经取得工具结果。
        calls = [tool_reply(arguments=f'{{"city":"{city}"}}', call_id=str(i))["message"]["tool_calls"][0]
                 for i, city in enumerate(("台北", "北京"))]

        def runner(name, arguments, allowed):
            # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
            barrier.wait(timeout=2)
            from tools import execute
            return execute(name, arguments, allowed)

        results = parallel.execute_parallel(calls, {"get_weather"}, runner)
        # 核对实际值与预期值相等。
        self.assertEqual([result["data"]["city"] for result in results], ["台北", "北京"])

    def test_parallel_error_result_not_dropped(self):
        # 没有调用时才进入最终回答分支；空列表是“本轮不执行工具”，不是已经取得工具结果。
        calls = [tool_reply()["message"]["tool_calls"][0], tool_reply("unknown", call_id="c2")["message"]["tool_calls"][0]]
        result = parallel.execute_parallel(calls, {"get_weather"})
        # 核对条件成立。
        self.assertTrue(result[0]["ok"])
        # 核对条件不成立。
        self.assertFalse(result[1]["ok"])

    def test_parallel_loop_keeps_call_ids(self):
        reply = tool_reply()
        reply["message"]["tool_calls"] += tool_reply(call_id="c2")["message"]["tool_calls"]
        result = run_agent("两城", sequence(reply, final_reply()), batch_executor=parallel.execute_parallel)
        # 核对实际值与预期值相等。
        self.assertEqual([message["tool_call_id"] for message in result["messages"] if message["role"] == "tool"], ["c1", "c2"])

    def test_bad_batch_executor_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "对应结果"):
            # 运行有轮数与工具次数限制的 Agent 循环。
            run_agent("天气", sequence(tool_reply()), batch_executor=lambda calls, allowed: [])


class FeedbackTests(unittest.TestCase):
    def test_self_refine_improves_draft(self):
        result = refine.run_self_refine(refine.mock_ask)
        # 核对条件成立。
        self.assertTrue(result["passed"])
        # 核对条件成立。
        self.assertTrue(any(event["event"] == "revision" for event in result["trace"]))

    def test_self_refine_rejects_regression(self):
        outputs = iter([{"text": "台北固定示例78.8华氏，非实时。"}, {"issues": ["改措辞"]}, {"text": "天气不错"}])
        result = refine.run_self_refine(lambda messages, schema: next(outputs), max_rounds=1)
        # 核对条件成立。
        self.assertTrue(result["passed"])
        # 核对条件不成立。
        self.assertFalse(result["trace"][-1]["accepted"])

    def test_reflexion_uses_experience(self):
        result = reflexion.run_reflexion(reflexion.mock_ask)
        # 核对条件成立。
        self.assertTrue(result["passed"])
        # 核对实际值与预期值相等。
        self.assertEqual(len(result["trace"]), 2)
        # 核对实际值与预期值相等。
        self.assertEqual(len(result["memory"]), 1)
        repeated = reflexion.run_reflexion(reflexion.mock_ask, result["memory"])
        # 核对实际值与预期值相等。
        self.assertEqual(len(repeated["trace"]), 1)

    def test_reflexion_failure_stops_at_limit(self):
        def failing(messages, schema):
            return {"lesson": "需重新换算"} if schema == reflexion.LESSON_SCHEMA else {"value": 0, "unit": "x", "source_kind": "x"}
        result = reflexion.run_reflexion(failing)
        # 核对条件不成立。
        self.assertFalse(result["passed"])
        # 核对实际值与预期值相等。
        self.assertEqual(len(result["trace"]), 3)

    def test_reflexion_rejects_invalid_memory_and_nan(self):
        with self.assertRaises(ValueError):
            reflexion.run_reflexion(reflexion.mock_ask, [4])
        # 核对条件成立。
        self.assertTrue(reflexion.evaluate({"value": float("nan"), "unit": "fahrenheit", "source_kind": "fixed_example"}))

    def test_typed_record_checks_semantics_and_extra_fields(self):
        record = {"city": "台北", "temperature": 26.0, "unit": "celsius", "source_kind": "fixed_example"}
        # 核对实际值与预期值相等。
        # 在接收结果的边界执行运行时验证，尽早拒绝缺字段、错类型和越界值。
        self.assertEqual(typed.WeatherRecord.model_validate(record).city, "台北")
        for change in ({"temperature": 30.0}, {"extra": True}, {"temperature": True}, {"source_kind": "live"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                # 按 typed.WeatherRecord 的模型定义验证输入。
                # 在接收结果的边界执行运行时验证，尽早拒绝缺字段、错类型和越界值。
                typed.WeatherRecord.model_validate({**record, **change})


class CodeActionTests(unittest.TestCase):
    def test_codeact_composes_tools(self):
        result = codeact.run_codeact(codeact.mock_ask)
        # 核对实际值与预期值相等。
        self.assertEqual(result["result"]["value"], 78.8)

    def test_forbidden_python_features(self):
        cases = ["import os", 'answer = open("secret")', 'answer = (1).__class__',
                 "while True:\n    answer = 1", "answer = 2 ** 10000", "answer = [x for x in range(100)]",
                 'answer = get_weather(**{"city":"台北"})']
        for source in cases:
            with self.subTest(source=source), self.assertRaises(ValueError):
                codeact.TinyPython().run(source)

    def test_tool_validation_still_applies(self):
        with self.assertRaises(ValueError):
            codeact.TinyPython().run('answer = get_weather(city="火星")')

    def test_state_persists_but_new_answer_is_required(self):
        interpreter = codeact.TinyPython()
        # 核对实际值与预期值相等。
        self.assertEqual(interpreter.run("a = 2\nanswer = a + 3"), 5)
        # 核对实际值与预期值相等。
        self.assertEqual(interpreter.run("answer = a * 4"), 8)
        with self.assertRaises(ValueError):
            interpreter.run("b = 8")

    def test_final_without_execution_rejected(self):
        with self.assertRaises(RuntimeError):
            codeact.run_codeact(lambda messages, schema: {"kind": "final", "code": "", "answer": "78.8"})

    def test_final_text_cannot_forge_execution_result(self):
        outputs = iter([{"kind": "code", "code": "answer = 1", "answer": ""},
                        {"kind": "final", "code": "", "answer": "台北固定示例78.8华氏，非实时"}])
        with self.assertRaisesRegex(RuntimeError, "执行结果"):
            codeact.run_codeact(lambda messages, schema: next(outputs))

    def test_missing_final_labels_are_repaired_without_new_code(self):
        first = codeact.mock_ask([{}], codeact.DECISION_SCHEMA)
        outputs = iter([first, {"kind": "final", "code": "", "answer": "78.8"},
                        {"kind": "final", "code": "", "answer": "台北固定示例78.8华氏，非实时"}])
        result = codeact.run_codeact(lambda messages, schema: next(outputs))
        # 核对实际值与预期值相等。
        self.assertEqual(len(result["trace"]), 1)

    def test_retrieval_cannot_finish_without_evidence(self):
        with self.assertRaisesRegex(RuntimeError, "证据"):
            retrieval.run_retrieval(lambda messages, schema: {"kind": "final", "entity": "", "answer": "海城"})

    def test_codeact_loop_stops(self):
        with self.assertRaisesRegex(RuntimeError, "最大轮数"):
            # max_steps：限制循环最多执行多少步；它是程序的停止条件，不能只在提示词里写“不要无限循环”。
            codeact.run_codeact(lambda messages, schema: {"kind": "code", "code": "answer = 1", "answer": ""}, max_steps=2)

    def test_retrieval_uses_two_observations(self):
        result = retrieval.run_retrieval(retrieval.mock_ask)
        # 核对条件成立。
        self.assertTrue(result["passed"])
        # 核对实际值与预期值相等。
        self.assertEqual([step["entity"] for step in result["trace"]], ["青禾号", "林遥"])
        # 核对条件不成立。
        self.assertFalse(retrieval.run_retrieval(retrieval.mock_ask, use_tools=False)["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
