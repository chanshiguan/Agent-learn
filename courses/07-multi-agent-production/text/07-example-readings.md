# 原练习 README 的工程阅读补充

这里对应六个原练习 README 中的阅读与学习资源。核心练习仍是 Eval、观测、批准恢复、Deploy；辩论与缓存保持选修。工具名不是额外的必做作业，学习它负责的环节，再按需要选实现。

## Eval：同一份题集怎样搬进不同工具

一条记录固定输入、初始状态、参考结果、禁止动作、评分方法和版本；每次试跑记录输出与工具轨迹。规则能判断的先写规则，语义判断交人工或校准后的模型评审。一次改动后按题号比较改善、持平、回退，不只比较总分。

promptfoo 以 cases/providers/assertions 组织评测；Console Evals 在界面组织测试与提示版本；LangSmith、Weave、Braintrust 将数据集、运行与实验比较关联。共同验收是能导出或重现逐题结果，不能只看到绿色面板。上传前明确题目、原始 prompt、工具结果和用户资料是否允许离开本机；本课的 eval_core.py 已完整实现版本、trial、grader 与 baseline 对比，使用它即可完成原题。

原完整代码与五开发三保留题在 upstream/02-eval；公开给学习者看的示范保留题不再是其独立盲测。新增自己的题时先保留答案，再决定哪个分区可用于改进。

## Observability：从请求到一次可解释的失败

一次任务是 trace，每次模型、工具或检索操作是 span；用父子关系和任务 ID 串起来。记录开始/结束、状态、用量和错误类型，不收集无关正文。模型返回失败、网络超时、权限阻挡分开，才知道该改哪里。

Langfuse 组合 trace、评测与提示管理；Phoenix 关注基于 OpenTelemetry 的链路与评估；LangSmith 贴近 LangChain 应用；Helicone 可在代理层观察请求；Datadog 将 LLM 链路接入已有监控；Console 的 usage/账单是供应商计量入口。选择一个足够，不要求同时上报六份日志。代理看见请求不代表看见全部本地工具动作；SDK 自动 span 也不一定覆盖你的普通函数。

本地完整 observability 原例与 production_case 收据分别演示链路和业务结果。排错时先用任务 ID 找错误 span，再核对外部效果；不得因重试成功就覆盖失败证据。实际 exporter 另有传输、访问控制、保留和删除责任；只加脱敏 processor 不能假设已关闭原 exporter。

## Streaming、Prompt caching 与 Batch：三件不同的事

Streaming 是响应按事件增量到达。文本块拼接不代表工具参数 JSON 已完整；等块结束后再解析，发生 error 或缺少完成事件时不能当最终成功。原 upstream/04-sdk-advanced 两条 provider 路径与测试完整展示增量处理。

Prompt caching 复用相同前缀的计算，通常把稳定规则、工具定义、长资料放前，变化的问题放后。Anthropic 的缓存断点、最小长度和 TTL 受模型/平台条件约束，前缀变化可能失去命中；usage 的 cache_creation_input_tokens 与 cache_read_input_tokens 分别反映写入与读取。它不是保存答案，下次仍会生成。[官方缓存机制](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

原 starter_anthropic.py 包含 cache_control 配置；先跑同目录 test_anthropic.py 核对事件与用量处理，再由自己的账户决定是否真实调用。默认5分钟和可选1小时是此供应商功能的时间设置，不能套到所有模型；具体资格和费用留在实际运行记录中。长前缀只是达到候选条件，必须看到实际 cache_read 字段才算命中。

成本核算应分普通输入、缓存写入、缓存读取、输出及环境费用，分别乘对应单价并记录价格核查日期；只知道总 token 时不能编出缓存节省比例。Batch 面向可等待的一批独立请求：给每题唯一 custom_id，提交后按状态轮询，结果按 ID 合并，失败项单独处理。它不适合每步依赖上一轮观察的实时 Agent loop；费用或时限未确认时不写固定承诺。

## Deploy：FastAPI 与 Docker 还各负责什么

FastAPI 用请求模型约束字段与长度，用响应模型固定接口结果，HTTPException 等错误路径告诉调用者哪些请求不可接受。依赖可管理客户端或身份检查；异步接口里直接阻塞调用可能占住事件循环，需选择异步客户端或合适执行方式。health 只检查已定义的健康条件，不把它等同所有模型任务成功。[FastAPI 教学](https://fastapi.tiangolo.com/tutorial/)

原 upstream/05-deploy 给出完整服务、mock 测试、requirements 与 Dockerfile。先用 TestClient 检查正常、坏输入和依赖失败，再在本机开服务。Docker 构建安装依赖，运行时才配置凭证；不要 COPY 本机 .env 或密钥进镜像。采用较小可信基础镜像、适当忽略文件、非 root 和及时更新，不因容器化就免去应用鉴权。

发布端口 `127.0.0.1:8000:8000` 将容器8000映射到宿主回环地址，省略前面的地址通常扩大监听面；EXPOSE 是说明，不是发布命令。Docker网络行为还受实际版本与主机配置影响。[端口映射说明](https://docs.docker.com/engine/network/port-publishing/)

本课完整启动命令与验证在原题实作章。模型失败时明确失败状态而非200加“完成”；公开部署还需认证、权限、并发、限制、密钥与回滚。本课不要求公开上线。

## 辩论、批准恢复与扩展教材

AutoGen 是多 Agent 框架的选用参考，更多角色不能保证独立证据；本课原辩论代码保留每轮意见，可与单 Agent 同题对照。hello-agents 和 awesome-harness-engineering 是补背景与找模式的目录，不要求再完成另一套教材。原题所需机制已在本课讲解与完整代码中。

批准与恢复的四份来源已有逐篇讲解：OpenAI 的 RunState/interruptions、LangGraph 的 thread/checkpointer/interrupt、Anthropic 的 outcome/trajectory。第七课的综合题让批准绑定来源与草稿版本，实际恢复只协调一次账本效果；这些是执行层责任，不能由模型说“我记得批准过”替代。

## 自测与逐项答案

提交同一失败的逐题 Eval 与 trace，并回答：评分通过却发送到错误对象是否通过（不通过，outcome 错）；缓存写入有值是否等于命中（不等于，要看读取）；Batch 顺序是否等于输入顺序（按 ID 关联）；health 正常是否证明生成正常（不能）；重复恢复为什么不重复登记（幂等键与账本协调）。每题完整行为代码来自原六题或综合题，没有要求依赖外部平台才能理解。
