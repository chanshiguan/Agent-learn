"""创建连接本机 Ollama 的模型请求函数，不读取或使用 OpenAI 云端密钥。"""

# 导入 os，用于读取可选的 OLLAMA_MODEL 环境变量。
import os
# 导入 time，用于在可重试错误发生后短暂等待。
import time


# 这是一个函数工厂：先配置客户端和模型，再返回真正发送请求的 ask 函数。
def make_ask():
    # 延迟导入 SDK；只有实际创建请求函数时才要求安装 openai 包。
    from openai import APIConnectionError, APIStatusError, OpenAI

    # 创建兼容 OpenAI API 的客户端，但把请求地址指向本机 Ollama。
    client = OpenAI(
        # Ollama 默认监听 11434 端口，并在 /v1 提供 OpenAI 兼容接口。
        # base_url：把请求发到这个地址，而不是 SDK 的默认云服务；使用 OpenAI 客户端并不代表数据一定发给 OpenAI。
        base_url="http://localhost:11434/v1",
        # OpenAI SDK 要求提供 api_key；本地 Ollama 默认不会验证这个占位值。
        # api_key：这是客户端要求的鉴权参数；本机 Ollama 的占位值不是云端密钥，也不提供执行授权。
        api_key="ollama",
        # 单次请求最多等待 60 秒，防止模型无响应时程序永久卡住。
        # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
        timeout=60.0,
        # 关闭 SDK 内置重试，由下面的代码统一控制重试次数。
        # max_retries：控制客户端自动重试次数。设为 0 可把重试统一交给外层，避免两层重试相乘。
        max_retries=0,
    )

    # 优先使用环境变量指定的模型；未设置时默认使用本课程的 gemma4:e4b。
    model = os.environ.get("OLLAMA_MODEL", "gemma4:e4b")

    # 定义真正发送请求的内部函数；它会记住上面的 client 和 model。
    def ask(messages, tools):
        # 最多尝试两次：第一次正常请求，发生可恢复错误时再重试一次。
        for attempt in range(2):
            # 捕获连接错误和部分临时 HTTP 错误，以决定是否重试。
            try:
                # 调用 Chat Completions 接口，把对话历史和工具定义一起交给模型。
                response = client.chat.completions.create(
                    # 指定本次请求使用的 Ollama 模型。
                    # model：显式指定本次使用的模型或测试替身，避免悄悄使用默认值；换模型后要重新核对本例的输出约定。
                    model=model,
                    # 传入 system、user、assistant、tool 等完整对话历史。
                    # messages：传入本轮模型要读取的角色与内容；工具循环还须保留历史请求和结果，模型才知道前一步实际发生了什么。
                    messages=messages,
                    # 告诉模型当前允许请求哪些函数工具。
                    # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
                    tools=tools,
                    # 限制模型本次最多生成 768 个输出 token，避免无边界生成。
                    # max_tokens：限制本次响应最多生成多少 token，约束延迟和输出规模；达到上限后必须检查是否截断。
                    max_tokens=768,
                    # 使用确定性更高的输出，便于课程示例稳定复现。
                    # temperature：降低采样随机性，便于比较实验结果；即使为 0，也不能保证每次输出完全相同或事实正确。
                    temperature=0,
                    # reasoning_effort：配置模型支持的推理行为；这里的值必须与所用服务兼容，不能当作所有模型通用的开关。
                    reasoning_effort="none",
                )

                # 正常响应至少要包含一个候选结果，否则无法继续处理。
                if not response.choices:
                    # 用明确异常代替后续访问 choices[0] 时产生的索引错误。
                    raise RuntimeError("API 没有返回 choices")

                # 本课程只使用第一个候选回答。
                choice = response.choices[0]

                # SDK 可能不返回 usage；缺失时用 0，保证返回结构稳定。
                # 用量来自服务实际报告，用于成本和预算核对；缺失时保留未知，不自行估算成确定账单。
                usage = response.usage.total_tokens if response.usage else 0

                # 把 SDK 对象整理为课程其他文件容易处理的普通字典。
                return {
                    # 删除值为 None 的字段，保留文本内容或工具调用等有效字段。
                    # 把 SDK 或模型对象转成普通数据，方便保存与返回；不要把对象的调试字符串当作协议 JSON。
                    # exclude_none：省略值为 None 的可选字段，避免把“未返回”误写成一项有内容的协议字段。
                    "message": choice.message.model_dump(exclude_none=True),
                    # 保存结束原因，用于区分正常回答、工具调用和内容截断。
                    "finish_reason": choice.finish_reason,
                    # 保存本次请求的总 token 数，便于后续观察用量。
                    "tokens": usage,
                }

            # 连接不上本机 Ollama 时进入这里，例如服务尚未启动。
            except APIConnectionError:
                # attempt 从 0 开始；等于 1 表示第二次尝试也失败了。
                if attempt == 1:
                    # 原样抛出 SDK 异常，让调用者看到真实的连接失败原因。
                    raise

            # Ollama 返回非成功 HTTP 状态码时进入这里，并保留错误详情。
            except APIStatusError as error:
                # 第二次失败，或错误本身不可恢复时，不再继续重试。
                if attempt == 1 or error.status_code not in (429, 500, 502, 503, 504):
                    # 429 和常见 5xx 可重试；其他状态码通常需要修改请求后再试。
                    raise

            # 第一次遇到可重试错误后等待半秒，避免立刻再次冲击服务。
            time.sleep(0.5)

        # 理论上循环只会成功返回或抛出异常；此处作为防御性兜底。
        raise RuntimeError("模型请求未完成")

    # 返回内部函数而不是立刻请求模型，让调用者可以多次复用同一客户端配置。
    return ask
