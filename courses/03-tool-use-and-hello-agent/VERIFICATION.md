# 第三课实际验证记录

日期：2026-11-03。此记录描述交付时实际运行的结果，不代表学习者已掌握，也不是长期成功率保证。

## 环境

- Python：项目 `.venv`，3.14.6。
- OpenAI Python SDK：3.37.0。
- Ollama 模型：`gemma4:e4b`，本机列表 ID `eb2177adf764`。
- 模型请求仅发往 `http://localhost:11434/v1`。

## 已通过

- 26 项离线测试：参数与权限验证、错误回传、消息历史、请求 ID、多请求批次、多步依赖、自然结束、强制停止、截断与拒答、数值评分，以及 Anthropic 消息格式。
- `01_hello_tool.py` 真实模型往返：台北 → 工具结果 26°C → 最终回答。
- `04_multi_step.py` 真实模型依赖任务：第一轮查天气，第二轮使用实际返回的 26 换算，第三轮回答 78.8°F。
- `07_structured_output.py` 真实模型抽取：城市台北、温度 26、单位 celsius。
- `06_schema_eval.py --repeat 1`：明确版 5/5，弱版 5/5，完整轨迹在 `examples/eval_results.json`。两版在本轮没有显示质量差异；未运行五轮的完整比较，不据此宣称明确版更优。
- 离线错误演示与 Anthropic 离线示例可直接运行，不需要密钥。
- HTML 检查：14 个页面（含总课程入口）、247 个本地引用；无断链、失效锚点或学习页面外链。
- 完整代码集与实际案例文件逐字同步；Python 语法检查及课程交互 JavaScript 语法检查通过。
- 课后练习 4 的完整补丁通过 dry-run，未把练习答案应用到原始工具文件。
- 第二课 8 个 HTML、3 个参考 HTML 与 2 个共享组件的文件哈希与工作开始时相同。
- Safari 已打开第三课首页，页面标题、目录、学习单元和参考导航可见。

## 验证中修正

- 初版数值评分把中文紧贴数字的回答误判为失败；已改为按数字边界识别，并新增“26.0摄氏度”回归测试。
- 错误路径评测现在明确要求实际调用工具，避免模型根据工具说明直接拒绝查询时，与实验验收目标发生歧义。

## 尚未验证

- Anthropic 收费云端请求未运行，原生协议仅做离线测试。
- 没有逐项运行所有扩展仓库，也没有复现 ReAct 论文实验。
- 已验证首页显示；浏览器后续状态读取超时，未完成浏览器端逐个按钮的点击验证。交互脚本已做语法检查，页面与代码引用已做静态检查。

## 复查命令

```bash
cd /Users/owen/Documents/ai-learn
.venv/bin/python courses/03-tool-use-and-hello-agent/build_course.py
.venv/bin/python courses/03-tool-use-and-hello-agent/check_course.py
.venv/bin/python -m unittest discover -s courses/03-tool-use-and-hello-agent/examples -p 'test_*.py' -v
node --check courses/03-tool-use-and-hello-agent/assets/course.js
```

## 补充单元9–15的实际核验

同日完成，第三课现有15个学习单元，新增9个程序入口（09–17）、一个共用JSON客户端、完整测试与最后7道补充练习。

- 标准主环境测试：52项通过；独立库集成测试：3项通过，共55项。
- 09流式：真实本机请求经过片段收集、工具执行、最终答案，成功。离线验证交错index、截断与断流不执行。
- 10工具选择：auto、none、required、specific均实际运行；none直接问候，其他模式完成天气往返。
- 11并发：真实模型同轮提出台北和北京两个请求，线程池执行并保持ID；测试用Barrier证明两个工作线程有重叠。模拟I/O实测顺序约0.170秒、并发约0.085秒，不视为模型基准。
- 12 Self-Refine：真实模型初稿通过5项规则，批评器返回空问题列表；本次不需要修订。离线测试验证修订改善与拒绝退步。
- 13 Reflexion：最终真实模型结果78.8/fahrenheit/fixed_example，首轮通过；离线脚本验证错误、经验、下一次成功及经验复用。没有虚构真实模型“反思后提升”的成绩。
- 14 Instructor：真实抽取正确；库集成测试验证先错后对、最多一次重试（总共两次尝试）。
- 15 Outlines：真实抽取正确；库集成测试验证输出Schema确实传给Ollama后端。
- 16 CodeAct：真实模型生成受限代码，先查固定天气，再将实际26换成78.8°F。最终完整说明台北、固定示例和非实时。新增测试禁止用最终文字伪造错误的执行结果。
- 17检索：真实无查询路径回答“不知道”，有查询路径按青禾号→林遥查询后答海城。该结果只说明原创小环境路径可用，不是ReAct论文benchmark复现。
- 新HTML经构建与本地引用检查，代码集直接嵌入全部新增文件，不依赖网页fetch源码。

独立库环境：`.venv-libraries311`，Python3.11，OpenAI2.15.0、Instructor1.17.0、Outlines1.3.3、Ollama0.6.3、httpx0.28.1及SOCKS支持。项目原有`.venv`仍为Python3.14和OpenAI3.37.0。

实际遇到并修复的事项：Outlines不支持Python3.14；Instructor与主SDK的jiter范围冲突；Ollama导入时需要电脑现有代理配置的SOCKS依赖；单位需枚举；检索需明确证据门槛；代码结果与最终说明分别验收。课程已写明这些细节。

补充复查：

```bash
cd /Users/owen/Documents/ai-learn
.venv/bin/python -m unittest discover -s courses/03-tool-use-and-hello-agent/examples -p 'test_*.py' -v
cd courses/03-tool-use-and-hello-agent/examples
../.venv-libraries311/bin/python verify_libraries.py
```
