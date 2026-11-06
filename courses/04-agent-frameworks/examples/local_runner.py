"""当前项目的 LangGraph 本地入口，复用原课程图；不读取代理环境。"""

# 复用原题的图，只配置本机模型与 HTTP 客户端；先确认 Ollama 已有对应模型。
import importlib.util
import json
import sys
from pathlib import Path
from langchain_openai import ChatOpenAI
from openai import DefaultHttpxClient, DefaultAsyncHttpxClient

path = Path(__file__).with_name("upstream") / "01-same-agent-two-frameworks/starter.py"
spec = importlib.util.spec_from_file_location("course4_original", path)
original = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = original
spec.loader.exec_module(original)


def main():
    # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
    # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
    llm = ChatOpenAI(base_url="http://localhost:11434/v1", api_key="ollama", model="gemma4:e4b",
                    # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
                    # reasoning_effort：配置模型支持的推理行为；这里的值必须与所用服务兼容，不能当作所有模型通用的开关。
                    # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
                    # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
                    # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
                    temperature=0, reasoning_effort="none", max_tokens=600, timeout=60, max_retries=0,
                    # http_client：显式注入底层 HTTP 客户端，让代理、超时等行为与这个案例的运行条件一致。
                    # trust_env：设为 False 可避免继承系统代理等环境配置，使本地请求路径更可控；不会关闭 TLS 证书校验。
                    http_client=DefaultHttpxClient(trust_env=False),
                    # trust_env：设为 False 可避免继承系统代理等环境配置，使本地请求路径更可控；不会关闭 TLS 证书校验。
                    http_async_client=DefaultAsyncHttpxClient(trust_env=False), http_socket_options=())
    question = "调用 search 时把 query 设为“台北”。只用中文概括返回的固定资料，并明确说明这是教学数据。"
    result = original.run(question, llm)
    if result["steps"] < 4:
        raise RuntimeError("没有完成可见的工具往返")
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # 进入本文件的演示入口。
    main()
