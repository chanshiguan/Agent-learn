"""手动检查 Smolagents 的 Docker 控制通道。

先确认 docker version 成功，再运行本文件。它会构建并启动官方
Jupyter 执行器，检查宿主能否执行一条简单语句，以及控制端口是否只绑定
本机回环地址。普通离线测试不会运行此文件。
"""

# 本组测试围绕以下行为检查正反例：比较 JSON 参数调用与代码行动；算术用 AST 白名单，CodeAct 的执行依赖受限 Docker。

from __future__ import annotations

import sys

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from smolagents import DockerExecutor
from smolagents.monitoring import AgentLogger, LogLevel

from starter import codeact_executor_config


def test_docker_control_channel() -> None:
    config = codeact_executor_config()
    executor = None
    try:
        executor = DockerExecutor(
            additional_imports=[],
            logger=AgentLogger(level=LogLevel.ERROR),
            build_new_image=True,
            **config,
        )
        output = executor.run_code_raise_errors("print(2 + 2)")
        assert "4" in output.logs
        executor.container.reload()
        bindings = executor.container.attrs["NetworkSettings"]["Ports"]["8888/tcp"]
        assert bindings
        assert all(binding["HostIp"] == "127.0.0.1" for binding in bindings)
    # 无论成功还是失败，都执行这里的收尾步骤。
    finally:
        if executor is not None:
            executor.cleanup()


if __name__ == "__main__":
    test_docker_control_channel()
    print("docker smoke pass")
