# 原练习逐题运行与验收

以下命令从 ai-learn 根目录运行。每题有独立 Python 3.11 环境；创建和安装只在首次需要，日常直接用对应环境解释器。requirements.txt 列依赖，不是课程正文。不要将这些依赖安装进主环境或第二、三课环境。

原始代码完整保留在源码页，标为 upstream；补充参考解在本课实作章。原材料中的云价格与产品状态是来源快照，实际开销以账户和用量为准。

这些练习共用同一套排错方法：如果出现 ModuleNotFoundError，核对运行解释器与安装解释器是否相同；模型不存在先用 ollama list 核对名字；模型返回格式不符则保留实际输出，不伪造成功。原包版本与本地模型支持情况会影响结果，mock 测试和真实调用分开记录。

先完成下面四项核心练习，再按需要选择辩论与 SDK 进阶。目录名保留原编号，阅读顺序按知识依赖安排。

## 02-eval：评测

先读 eval_cases 和 eval_core，区分 development 与 holdout。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-07-02
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-07-02/bin/python -m pip install -r courses/07-multi-agent-production/examples/upstream/02-eval/requirements.txt
# 运行 courses/07-multi-agent-production/examples/upstream/02-eval/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-07-02/bin/python courses/07-multi-agent-production/examples/upstream/02-eval/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-07-02/bin/python courses/07-multi-agent-production/examples/upstream/02-eval/starter.py
```

验收：规则初筛仍需人工校准；结业项目使用 evaluate.py，继续检查回答与证据是否一致。


## 03-observability：观测

看任务 ID、步骤、计时、用量与错误的关联。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-07-03
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-07-03/bin/python -m pip install -r courses/07-multi-agent-production/examples/upstream/03-observability/requirements.txt
# 运行 courses/07-multi-agent-production/examples/upstream/03-observability/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-07-03/bin/python courses/07-multi-agent-production/examples/upstream/03-observability/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-07-03/bin/python courses/07-multi-agent-production/examples/upstream/03-observability/starter.py
```

验收：故意失败后能定位具体步骤，不记录凭证。


## 06-safe-execution：安全执行

本题仅用 Python 标准库，不需要 requirements.txt。先跑离线测试，再用本课 production_case 完成摘要绑定与收据。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-07-06
# 运行 courses/07-multi-agent-production/examples/upstream/06-safe-execution/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-07-06/bin/python courses/07-multi-agent-production/examples/upstream/06-safe-execution/test.py
```

验收：拒绝后不写执行记录；重复恢复不重复写入；状态损坏时停止。


## 05-deploy：本地 API

启动后保持终端，另开终端测 health/chat；Ctrl+C 结束本地服务。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-07-05
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-07-05/bin/python -m pip install -r courses/07-multi-agent-production/examples/upstream/05-deploy/requirements.txt
# 运行 courses/07-multi-agent-production/examples/upstream/05-deploy/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-07-05/bin/python courses/07-multi-agent-production/examples/upstream/05-deploy/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-07-05/bin/python courses/07-multi-agent-production/examples/upstream/05-deploy/starter.py
```

验收：坏输入、正常输入和模型不可用分别测试；本地启动不算生产部署。


## 01-multi-agent-debate：多角色辩论（选修）

比较单 Agent 与多角色输入输出，固定题目与预算。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-07-01
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-07-01/bin/python -m pip install -r courses/07-multi-agent-production/examples/upstream/01-multi-agent-debate/requirements.txt
# 运行 courses/07-multi-agent-production/examples/upstream/01-multi-agent-debate/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-07-01/bin/python courses/07-multi-agent-production/examples/upstream/01-multi-agent-debate/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-07-01/bin/python courses/07-multi-agent-production/examples/upstream/01-multi-agent-debate/starter.py
```

验收：意见一致不证明事实，保留来源与最终责任。


## 04-sdk-advanced：SDK 进阶（选修）

观察流式片段、结束状态与缓存用量，别把半截输出当完整回答。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-07-04
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-07-04/bin/python -m pip install -r courses/07-multi-agent-production/examples/upstream/04-sdk-advanced/requirements.txt
# 运行 courses/07-multi-agent-production/examples/upstream/04-sdk-advanced/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-07-04/bin/python courses/07-multi-agent-production/examples/upstream/04-sdk-advanced/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-07-04/bin/python courses/07-multi-agent-production/examples/upstream/04-sdk-advanced/starter.py
```

验收：截断与正常结束分开；缓存收益来自实际 usage。

