"""在独立环境运行的库集成测试：所有HTTP响应均被替换，不请求模型。"""

# 先读测试中的输入和预期，再读被调用函数；这里检查协议、边界与失败分支，不能据此推断真实模型效果。

import json
import unittest
from importlib import import_module
from unittest.mock import patch

import httpx
import instructor
import ollama
import outlines
from openai import OpenAI
from openai.types.chat import ChatCompletion

WeatherRecord = import_module("14_instructor").WeatherRecord
GOOD = {"city": "台北", "temperature": 26.0, "unit": "celsius", "source_kind": "fixed_example"}


def response(record):
    # 在接收结果的边界执行运行时验证，尽早拒绝缺字段、错类型和越界值。
    return ChatCompletion.model_validate({
        "id": "offline", "object": "chat.completion", "created": 0, "model": "offline",
        # 把结果编码成协议可接受的 JSON；模型收到的是工具数据，不能把其中的指令当作系统授权。
        # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
        "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": json.dumps(record, ensure_ascii=False)}}],
    })


class LibraryIntegrationTests(unittest.TestCase):
    def test_instructor_repairs_invalid_semantics(self):
        # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
        # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
        # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
        base = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", max_retries=0,
                      # http_client：显式注入底层 HTTP 客户端，让代理、超时等行为与这个案例的运行条件一致。
                      # trust_env：设为 False 可避免继承系统代理等环境配置，使本地请求路径更可控；不会关闭 TLS 证书校验。
                      http_client=httpx.Client(trust_env=False))
        bad = {**GOOD, "temperature": 30.0}
        with patch.object(base.chat.completions, "create", side_effect=[response(bad), response(GOOD)]) as create:
            client = instructor.from_openai(base, mode=instructor.Mode.JSON)
            # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
            # response_model：让返回内容按这个模型进行类型与字段验证；验证失败后是否重试仍受次数限制。
            result = client.chat.completions.create(model="offline", response_model=WeatherRecord,
                # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
                # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
                max_retries=1, messages=[{"role": "user", "content": "抽取台北26摄氏度，fixed_example"}])
            # 核对实际值与预期值相等。
            self.assertEqual(result.temperature, 26)
            # 核对实际值与预期值相等。
            self.assertEqual(create.call_count, 2)
        base.close()

    def test_instructor_stops_after_one_retry(self):
        # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
        # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
        # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
        base = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", max_retries=0,
                      # http_client：显式注入底层 HTTP 客户端，让代理、超时等行为与这个案例的运行条件一致。
                      # trust_env：设为 False 可避免继承系统代理等环境配置，使本地请求路径更可控；不会关闭 TLS 证书校验。
                      http_client=httpx.Client(trust_env=False))
        with patch.object(base.chat.completions, "create", return_value=response({**GOOD, "temperature": 30.0})) as create:
            client = instructor.from_openai(base, mode=instructor.Mode.JSON)
            with self.assertRaises(Exception):
                # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
                # response_model：让返回内容按这个模型进行类型与字段验证；验证失败后是否重试仍受次数限制。
                client.chat.completions.create(model="offline", response_model=WeatherRecord,
                    # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
                    # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
                    max_retries=1, messages=[{"role": "user", "content": "抽取台北26摄氏度，fixed_example"}])
            # 核对实际值与预期值相等。
            self.assertEqual(create.call_count, 2)
        base.close()

    def test_outlines_passes_schema_to_ollama(self):
        # trust_env：设为 False 可避免继承系统代理等环境配置，使本地请求路径更可控；不会关闭 TLS 证书校验。
        client = ollama.Client(host="http://localhost:11434", trust_env=False)
        # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
        fake = ollama.ChatResponse(model="offline", done=True,
                                   # 把结果编码成协议可接受的 JSON；模型收到的是工具数据，不能把其中的指令当作系统授权。
                                   message=ollama.Message(role="assistant", content=json.dumps(GOOD)))
        with patch.object(client, "chat", return_value=fake) as chat:
            model = outlines.from_ollama(client, "offline")
            raw = model("抽取台北26摄氏度，fixed_example", WeatherRecord)
            # 核对实际值与预期值相等。
            self.assertEqual(WeatherRecord.model_validate_json(raw).city, "台北")
            schema = chat.call_args.kwargs["format"]
            if isinstance(schema, str):
                # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
                schema = json.loads(schema)
            # 核对实际值与预期值相等。
            self.assertEqual(schema["properties"]["unit"]["const"], "celsius")


if __name__ == "__main__":
    unittest.main(verbosity=2)
