# 原练习逐题运行与验收

以下命令从 ai-learn 根目录运行。每题有独立 Python 3.11 环境；创建和安装只在首次需要，日常直接用对应环境解释器。requirements.txt 列依赖，不是课程正文。不要将这些依赖安装进主环境或第二、三课环境。

原始代码完整保留在源码页，标为 upstream；补充参考解在本课实作章。原材料中的云价格与产品状态是来源快照，实际开销以账户和用量为准。

这五题可以按同样的顺序排错：遇到 ModuleNotFoundError，先确认安装依赖和运行程序用的是同一个 Python；提示模型不存在时，用 ollama list 核对名称；返回格式不符合要求时，保存原始输出继续检查。依赖版本和本地模型的支持情况都会影响结果，mock 测试与真实调用要分开记录。

## 01-same-agent-two-frameworks：同任务、双框架

先固定查询与工具资料；LangGraph 和 CrewAI 分别运行，比较真实工具往返和摘要，不只比较措辞。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-04-01
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-04-01/bin/python -m pip install -r courses/04-agent-frameworks/examples/upstream/01-same-agent-two-frameworks/requirements.txt
# 运行 courses/04-agent-frameworks/examples/upstream/01-same-agent-two-frameworks/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-04-01/bin/python courses/04-agent-frameworks/examples/upstream/01-same-agent-two-frameworks/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-04-01/bin/python courses/04-agent-frameworks/examples/upstream/01-same-agent-two-frameworks/starter.py
```

双框架第二条路径：

```bash
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=ollama/gemma4:e4b courses/.venv-lab-04-01/bin/python courses/04-agent-frameworks/examples/upstream/01-same-agent-two-frameworks/starter_crewai.py
```

验收：原测试检查工具循环；另检查查询不存在时是否诚实说明。



## 02-multi-agent-roles：研究→写作→审核

检查研究结果是否实际传入写作任务，再检查审核是否拿到同一证据。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-04-02
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-04-02/bin/python -m pip install -r courses/04-agent-frameworks/examples/upstream/02-multi-agent-roles/requirements.txt
# 运行 courses/04-agent-frameworks/examples/upstream/02-multi-agent-roles/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-04-02/bin/python courses/04-agent-frameworks/examples/upstream/02-multi-agent-roles/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=ollama/gemma4:e4b courses/.venv-lab-04-02/bin/python courses/04-agent-frameworks/examples/upstream/02-multi-agent-roles/starter.py
```

验收：每角色有可查看产物；没有来源的断言不能因为角色同意而通过。



## 03-graph-workflow：图、检查点与人审

看条件边与 interrupt，原例使用内存检查点；跨进程综合题使用本课 summary_workflow。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-04-03
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-04-03/bin/python -m pip install -r courses/04-agent-frameworks/examples/upstream/03-graph-workflow/requirements.txt
# 运行 courses/04-agent-frameworks/examples/upstream/03-graph-workflow/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-04-03/bin/python courses/04-agent-frameworks/examples/upstream/03-graph-workflow/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-04-03/bin/python courses/04-agent-frameworks/examples/upstream/03-graph-workflow/starter.py
```

验收：接受与拒绝分别验证，不能把内存示范当重启恢复。



## 04-codeact-vs-json-tool：CodeAct 与 JSON 工具

先读执行器设置；没有 Docker 时不要运行未隔离的任意代码作为替代。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-04-04
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-04-04/bin/python -m pip install -r courses/04-agent-frameworks/examples/upstream/04-codeact-vs-json-tool/requirements.txt
# 运行 courses/04-agent-frameworks/examples/upstream/04-codeact-vs-json-tool/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-04-04/bin/python courses/04-agent-frameworks/examples/upstream/04-codeact-vs-json-tool/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-04-04/bin/python courses/04-agent-frameworks/examples/upstream/04-codeact-vs-json-tool/starter.py
```

验收：相同计算任务与非法表达式都测；隔离实际未运行则记录未执行。



## 05-typed-agent：类型化结果

看 answer、confidence、sources 的约束与真实验证错误。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-04-05
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-04-05/bin/python -m pip install -r courses/04-agent-frameworks/examples/upstream/05-typed-agent/requirements.txt
# 运行 courses/04-agent-frameworks/examples/upstream/05-typed-agent/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-04-05/bin/python courses/04-agent-frameworks/examples/upstream/05-typed-agent/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-04-05/bin/python courses/04-agent-frameworks/examples/upstream/05-typed-agent/starter.py
```

验收：confidence 越界、来源空、字段类型错应被拒；合法结构仍需核对事实。


