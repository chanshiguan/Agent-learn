# 最新：全量逐题复核（2026-11-04）

最新结论见 [完整复核报告](REVIEW-FULL-2026-11-04.md)。本轮修正练习错配、原记忆实现描述与 README 阅读遗漏；147条阅读映射、53项原题对应、71项回归测试和32个原版离线脚本通过。第二、三课71个内容文件保持一致。以下为历史记录，遇到差异以最新报告为准。

# 最新验证：2026-11-04

- 回归测试 **54/54**；静态检查 **218页、5626条本地引用、108个 Python案例语法和完整展示**；新增五章与16课来源表共21页的桌面/手机布局通过。
- LangGraph Send/reducer、Agents SDK as_tool/handoff 已用真实框架运行；两种交接另用本机 Ollama gemma4:e4b 各运行一次。控制权正确，主管引用用工具名仍需内容复核，未计为来源质量全部通过。
- 20题A/B/C输出60行，保留完整证据、摘录答案、Recall@5、MRR、耗时与成本口径。重排无额外平均收益和一条无答案误检都保留，不当成全部质量通过。
- Plugin manifest 通过本机CLI校验；workflow 正常/取消契约通过；Claude SDK实际options和恢复ID构造通过。没有执行Claude云端调用、Dynamic workflows真实宿主运行、Docker或新embedding下载。
- 专用环境增加 openai-agents 0.24.0、claude-agent-sdk 0.2.178，websockets 因SDK要求调整为16.1.1；pip check通过，实际锁文件更新。根环境OpenAI仍为3.37.0。
- 第二、三课教材内容未写入；Finder元数据不计为教材修改。

新证据和逐项结论见 [本轮复核](REVIEW-2026-11-04.md)。下面保留前一轮验证历史；旧页数、测试数和未验证项如与本节不同，以本节为准。

# 后续课程验证记录（修复后）

日期：2026-11-03。此记录取代修复前的当前状态说明；历史测试保存在 `.scratch/remaining-courses/verification/`，本轮证据在 `.scratch/remaining-courses/repair/`。代码提供、程序正确、模型输出正确与用户掌握分别判断。

## 课程与内容

- 16 个独立目录保留原编号和路线：4/5/6/7/7.5/8、A1/A2/A3、五条身份分支、双轨结业。
- 每课包含中文讲义、必读知识、分步实作与完整参考、完整代码页、精确覆盖表、课末练习及答案/量规。复杂课程另有原实验运行说明和进阶单元。
- 123 条能力映射逐项指向本地章节、案例、验收。745 个来源入口包含选修工具目录和辅助资料；入口数量不是已全文教学的文章数量。
- 上游课程固定提交 `9ef03ca034704bf9cdd403673b3116fda7ec8672`，保留 MIT 许可。外部报告、论文不因此变为 MIT；本地讲解是围绕课程能力的原创解释，不是所有外站的全文翻译。
- 本轮没有写入第二、三课。保护清单共 72 文件：69 与起始摘要一致，第三课 3 个工作期间发生同步修改的文件按观察摘要保留；未替他人还原。检查覆盖文件内容，不把缓存文件算作教材修改。

## 本轮实际通过的检查

| 检查 | 实际结果 | 能证明的范围 |
|---|---|---|
| 生成与静态检查 | 213 个 HTML、5243 条本地引用、102 个 Python 文件语法及完整展示通过 | 页面/锚点存在、案例代码完整；不能单独证明内容正确 |
| 单元回归 | 42/42 通过 | 包括评分反例、主体错误、来源轨迹、空文档、跨进程恢复、记忆显示/删除与旧课保护 |
| 原课程离线脚本 | 15/15 通过，合计 83 个 test 函数 | 包含 LangGraph、Pydantic AI TestModel、切分和第七课本地及 Anthropic mock 路径；非云端实测 |
| 案例入口检查 | 18 个入口输出符合预期 | 运行正常不等于开放文本合格；五分支参考产物正确保留 NEEDS_REVIEW |
| 第四课暂停恢复 | SQLite 跨进程恢复/拒绝等路径通过 | 来源检查、暂停与恢复控制真实运行 |
| 第五课 MCP | SDK 1.30.0 真实 stdio 初始化、发现、调用，合法读取成功，越界返回错误 | 已完成协议往返；没有注册进用户 CLI |
| 第八课完整循环 | 六场景通过：正常接受、拒绝、状态过期、执行失败、离域、发送 | 真浏览器读取和填写并检查实际页面；使用固定提议，不是模型规划成绩 |
| 课程界面 | 64 页浏览器检查、16 课手机宽度检查、目录锚点/折叠答案/原图、无 JS 错误 | 已检查页面的浏览与展示 |
| 独立依赖环境 | pip check 通过，实际版本已更新锁文件 | 验证环境依赖一致；没有升级根环境 |

否定答案加正确关键词现在进入 NEEDS_REVIEW，伪造或缺失检索轨迹为 FAIL，不再得到 100% 自动通过。固定摘录基线开发题 5/5，通过仅代表已知资料与固定题集；不得据此声称生成模型质量或盲测成绩。

第五课的 README 初筛同样不替语义评分：四节非空仍是 NEEDS_REVIEW；空节或缺文件为 FAIL。参考报告把未选定许可证列为待确认，不因为有“许可证”标题就判完工。

## 真实本地模型与内容核对

根 `.venv` 的 OpenAI SDK 仍为 **3.37.0**。独立验证环境的 OpenAI 版本与它不同，见锁文件；不要把独立版本误报成当前主项目版本。

- 本轮第六课：已有 Ollama `gemma4:e4b` 对“主办方取消课程退款”生成带 exception 引用的正确例外说明，内容逐条核对一致。此路径用了字符计数向量，不是语义 embedding；真实 embedding 属于下表未运行项。
- 本轮结业 B：五个开发题各执行一次真实检索和生成；自动结果 **3 PASS、2 NEEDS_REVIEW、0 FAIL**。两项是正确改写，逐条核对后本轮可接受；没有篡改自动分数为全部通过。数据、原输出和核对理由保留。
- 前轮已运行第四课 LangGraph + Ollama 工具往返，以及知识工作者分支真实草稿。本轮未因为改文案重复调用；它们仍不是所有课程模型质量的普遍证明。

人工式内容复核见 [逐条记录](../.scratch/remaining-courses/repair/manual-model-review.md)。这些是固定教学数据上的单次结果，没有测多次稳定率，也没有给学习者登记掌握。

## 未执行的集成边界

| 内容 | 当前状态及学习安排 |
|---|---|
| CrewAI、Smolagents | 原完整代码、依赖与中文运行步骤已提供；本轮没有安装运行这两套框架 |
| 第六课真实 embedding、Chroma | 完整实现/原例、依赖、调用及验收已给出；没有下载模型权重或验证 Chroma 集成。字符向量必须明确叫教学基线 |
| Claude CLI 登录、Hook 注册、Skill 加载、Subagent、Agent SDK 托管 | 完整教学配置/来源代码及中文步骤提供；没有改变用户宿主配置或账户。MCP 独立协议往返已实测 |
| A3 远端 CI、真实 PR 审查、第二 Harness、团队安装 | 完整任务与工作流提供；未创建远端 PR、发送评论、设置密钥或发布 |
| Docker/CodeAct executor | 本机无 Docker；提供 Dockerfile、完整命令和验收；没有把本机 CSV 成功说成隔离成功 |
| DVC、Zotero、Notebook/发布服务集成 | 中文步骤与可复现的小项目已提供；标准库实验已运行，未代操作账户、下载桌面应用或发布数据 |
| 云端 Computer Use、托管 Sandbox、付费模型 | 协议、原例与本地替代实验已提供；没有付费调用或真实账户操作 |
| 其余身份分支的真实模型 | 完整参考产物与任务检查器已验证；不声称每个分支都跑过生成模型评测 |

未执行表示缺少这条环境运行的证据，不代表让学习者去外部文章补课。完成服务集成仍需要相应安装、账户与实际操作；不能把读完教材当成已完成集成。

## 重跑方法

在 ai-learn 项目根目录：

```bash
courses/.venv-verification/bin/python courses/tooling/build_remaining.py
.venv/bin/python courses/tooling/check_remaining.py
.venv/bin/python -m unittest discover -s courses/tooling -p 'test_*.py' -v
.venv/bin/python courses/capstone-b/examples/evaluate.py
courses/.venv-verification/bin/python courses/05-claude-code-ecosystem/examples/mcp_roundtrip.py
```

专用验证环境已存在；无需为阅读再次安装。依赖版本在 [实际环境锁文件](tooling/verification-requirements.lock.txt)，不要安装进根 `.venv`。各课的环境操作按“第一次需要／新终端需要／已完成可跳过”理解，命令是否执行由当前状态决定。

本轮证据：[回归测试](../.scratch/remaining-courses/repair/tests.txt)、[静态检查](../.scratch/remaining-courses/repair/link-check.txt)、[案例入口](../.scratch/remaining-courses/repair/case-smoke-tests.json)、[原测试](../.scratch/remaining-courses/repair/upstream-tests.json)、[MCP](../.scratch/remaining-courses/repair/mcp.txt)、[浏览器六路径](../.scratch/remaining-courses/repair/browser-tests.json)、[界面](../.scratch/remaining-courses/repair/ui-review.json)、[第六课模型](../.scratch/remaining-courses/repair/rag6-live.json)、[结业 B 模型](../.scratch/remaining-courses/repair/capstone-live.json)。

审查结论见 [修复后复核](REVIEW.md)，后续编辑方法见 [维护说明](tooling/README.md)。
