# 第三课：工具使用与第一个 Agent Loop

打开 `index.html` 开始。所有必要讲解、必修阅读的中文知识整理、完整代码与课后练习均在本目录。

## 目录

- `lessons/`：15 个顺序学习单元；这里的单元编号不等于总课程阶段编号。
- `reference/`：必修阅读讲义、术语、协议速查、覆盖表、完整代码集。
- `examples/`：可直接运行的完整 Python 文件、固定评测题和离线测试。
- `assets/`：本课交互与样式扩展；基础样式继续复用项目根目录 `assets/`。
- `RESOURCES.md`：原始来源链接与适用范围，用于核查，不是课外阅读任务。
- `VERIFICATION.md`：实际验证结果及未验证范围。
- `build_course.py`：将课程正文与实际代码生成静态 HTML；修改代码后运行一次同步代码展示。
- `supplement_lessons.py`：单元9–15的中文正文和补充覆盖表。
- `check_course.py`：检查本地页面链接、锚点和完整代码展示是否同步。

第二课仍位于项目原有 `lessons/`、`reference/`，没有迁移或覆盖。未来课程采用相邻目录 `courses/04-主题/`、`courses/05-主题/`。总入口是 `courses/index.html`。

## 运行

```bash
cd /Users/owen/Documents/ai-learn
source .venv/bin/activate
python -m pip install -r courses/03-tool-use-and-hello-agent/examples/requirements.txt
cd courses/03-tool-use-and-hello-agent/examples
python -m unittest discover -p 'test_*.py' -v
python 05_error_recovery.py
python 08_anthropic_agent.py
```

前三个运行命令不调用模型。下面访问本机 Ollama，需要服务已启动且 `gemma4:e4b` 已安装：

```bash
python 01_hello_tool.py
python 02_multi_tool.py "请用工具计算 12 乘以 8。"
python 03_agent_loop.py
python 04_multi_step.py
python 07_structured_output.py
python 06_schema_eval.py --variant good --repeat 1
```

完整 Schema 对比是 `python 06_schema_eval.py --repeat 5`，共 50 道运行任务，每题可能多轮请求。离线测试通过不代表模型测试通过。天气数据全部是固定教学数据。

## 已补充的主题

单元9–15依次覆盖流式参数组装、四种工具选择、线程池并发、ReAct论文方法与两跳检索、Self-Refine、Reflexion、Instructor、Outlines、CodeAct，以及最后的补充课后练习。全部案例源码嵌入本地代码页。

以下命令仍在 `examples/` 目录执行；不带 `--live` 的示例使用明确标注的离线脚本：

```bash
python 09_streaming_tools.py
python 09_streaming_tools.py --live
python 10_tool_choice.py specific
python 11_parallel_tools.py
python 11_parallel_tools.py --live
python 12_self_refine.py --live
python 13_reflexion.py --live
python 16_codeact.py --live
python 17_react_retrieval.py --live
```

Instructor和Outlines使用独立环境，避免与主环境的Python和SDK依赖冲突：

```bash
cd /Users/owen/Documents/ai-learn
/opt/homebrew/bin/python3.11 -m venv courses/03-tool-use-and-hello-agent/.venv-libraries311
courses/03-tool-use-and-hello-agent/.venv-libraries311/bin/python -m pip install -r courses/03-tool-use-and-hello-agent/examples/requirements-libraries.txt
cd courses/03-tool-use-and-hello-agent/examples
../.venv-libraries311/bin/python 14_instructor.py
../.venv-libraries311/bin/python 15_outlines.py
../.venv-libraries311/bin/python verify_libraries.py
```
