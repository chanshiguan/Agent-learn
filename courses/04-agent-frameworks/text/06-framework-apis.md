# 必读 API 实作：动态分工与交接

## 环境与本章目标

前面的 patterns.py 教控制关系，本章实际调用 LangGraph 的 Send/reducer 和 OpenAI Agents SDK 的 as_tool/handoffs。默认模型响应是可重放脚本，因此不需要密钥；编排代码由真正的框架运行。它能证明接线正确，不能证明模型会自行选对专家。

在项目根运行。已有 courses/.venv-verification 时使用该解释器；如果是新复制的项目，先用 Python 3.11 创建该环境，再装本章依赖，避免改变根 .venv：

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-verification
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-verification/bin/python -m pip install -r courses/04-agent-frameworks/examples/requirements-orchestration.txt
```

第一行仅在环境不存在时需要；requirements 写精确验证版本。SDK 与 OpenAI Python 包是不同层，安装 SDK 不等于得到模型访问能力。

## 动态工作者：Send 与 reducer

输入是文档列表。调度节点根据列表长度创建 Send，每个工作者只收到自己那份 document。两个工作者都更新 checks，所以必须规定合并方式：`Annotated[list[dict], operator.add]` 将各结果拼接，而非互相覆盖。

执行顺序为 START → validate → 动态 check_document → merge → END。并行分支的完成顺序不作为业务排序；merge 按文档 ID 排序。检查只验证“目的”“运行”两个词是否出现，题目明确限定这两项，不据此声称 README 内容正确。

{{code:../examples/dynamic_workers.py}}

```bash
# 运行 courses/04-agent-frameworks/examples/dynamic_workers.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/04-agent-frameworks/examples/dynamic_workers.py
# 运行 courses/04-agent-frameworks/examples/dynamic_workers.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/04-agent-frameworks/examples/dynamic_workers.py --fixed
```

第一条应 FAIL，a 无缺项，b 缺“运行”；第二条 PASS，两个结果都留下。不是只打印两个角色名，而是实际分发两次工作节点、合并两份 state 更新。输入空列表或重复 ID 会抛 ValueError，防止漏查与覆盖。

为什么不用普通赋值字段？多个分支同一轮写 checks 时，需要明确允许多值并定义合并；移除 reducer 是常见错误。为什么不在 worker 中修改共享原列表？框架依靠节点返回的 state 更新安排合并，直接修改共享对象会使行为难以追踪。

## 两种交接：最终由谁回答

manager-as-tools：主管请求专家工具 → 专家返回 → 主管继续。适合统一口径汇总。handoff：分诊者移交 → 专家继续后续对话；最终 agent 变了。交接不是隔离权限的同义词，专家能看到什么历史、有哪些工具，仍由配置决定。

{{code:../examples/sdk_orchestration.py}}

```bash
# 运行 courses/04-agent-frameworks/examples/sdk_orchestration.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/04-agent-frameworks/examples/sdk_orchestration.py
```

应有两行模式结果：manager_as_tools 的 final_agent=manager；handoff 的 final_agent=specialist。事件中前者出现 tool_call_item 与 tool_call_output_item，后者出现 handoff 相关事件。不能只检查最终文本里有没有“专家”两个字。

代码使用 ScriptedModel 给出预设响应，真实 Runner 负责消费工具、传回结果与改变当前 Agent。每个实验单独创建模型，避免第一次消耗掉脚本队列。`max_turns=4` 防止非预期循环；不用流式时不必实现流式路径。关闭 tracing 是为了这个本地教学例不上传轨迹。

可选真实本地模型：确保 Ollama 正在运行，`ollama list` 中已有 gemma4:e4b，然后执行：

```bash
# 运行 courses/04-agent-frameworks/examples/sdk_orchestration.py，按本行参数完成当前案例并核对输出；--live 会进入真实服务路径，需先满足本章环境要求。
courses/.venv-verification/bin/python courses/04-agent-frameworks/examples/sdk_orchestration.py --live
```

如果模型直接回答而不调用工具，内容可能看起来正确，但本题编排要求不通过；检查 events 与 final_agent，不能把提示词说“必须调用”当成执行保证。若模型无法产出合法工具参数，先保留失败轨迹，再调整工具说明或选择已支持工具调用的本地模型。

## 本章练习与完整答案

练习一：给动态工作者增加第三份文档 c，仅含“运行”，预期 a 完整、b 缺运行、c 缺目的；输出三行且最终 FAIL。下面是完整输入，可在 Python 交互环境导入 dynamic_workers.run 后传入：

```python
# 从 dynamic_workers 导入 run；供下方相应函数或类型使用。
from dynamic_workers import run
# 打印结果，供运行后核对：run([{'id': 'a', 'text': '目的：演示。运行：python ap…。
print(run([
    # 填写 标识（id） 字段：文本 'a'；填写 文本（text） 字段：文本 '目的：演示。运行：python app.py'。
    {'id':'a','text':'目的：演示。运行：python app.py'},
    # 填写 标识（id） 字段：文本 'b'；填写 文本（text） 字段：文本 '目的：教学'。
    {'id':'b','text':'目的：教学'},
    # 填写 标识（id） 字段：文本 'c'；填写 文本（text） 字段：文本 '运行：python demo.py'。
    {'id':'c','text':'运行：python demo.py'},
# 结束当前列表；前面的字段或参数至此组装完毕。
]))
```

在 examples 目录用专用解释器执行这段代码，或写成同目录新文件；不要从项目根直接猜 import 搜索路径。完整实现不需要改 worker，输入数量就是工作者数量。

练习二：不运行先预测两种交接的 final_agent，再核对事件。答案是 manager/specialist，理由是专家工具会返回主管，handoff 改变负责后续的 Agent。迁移时让专家返回“资料不足”，主管也应保留这个限制，不自行发明日期。

验收：保存两种模式事件、最终 agent 与回答；动态分工交三份结果；解释 reducer 的合并职责及权限边界。延迟两天重新画输入→工作者→结果的路径，不能只背 API 名称。本课最终作业仍集中在课末。
