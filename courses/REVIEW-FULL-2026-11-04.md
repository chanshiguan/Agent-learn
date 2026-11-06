# 2026-11-04 全量课程与原题复核

本轮核对第四课起的 16 个课程目录、原课必读清单、两条直接支线、练习目录 README 的阅读入口，以及题目、完整答案与验收。第二、三课及其共享素材的71个内容文件与本轮开始的哈希快照完全一致。

2026-11-04 从 GitHub API 读取的 upstream HEAD 为 `9ef03ca034704bf9cdd403673b3116fda7ec8672`，与本地固定源码相同。浏览器搜索缓存曾显示旧提交列表，版本判断采用实际 API 结果，未据缓存推断课程过期。

## 发现的问题与修复

| 问题 | 修复与复核 |
|---|---|
| 第五课 Hook 缺原题工具名称和时间 | 增加 UTC 时间、工具白名单；Write/Edit 可区分；不保存输入正文或未知工具原值；同步讲义和日志验收 |
| A2 CLI-6 被 README 标题检查替代 | 改为 review-changes，读取真实 Git diff，新增坏命令/失效链接样本与逐行答案；README 检查明确保留作补充 |
| A2 CLI-5/7/8 缺完整对应产物 | 四字段规则、双 README 原始/目标文件、四步任务卡、真实 diff 与检查程序、迁移对照表齐全 |
| A3 CLI-9/12 对应不完整 | 增加官方 filesystem 连接、实际允许目录与 Roots 检查、移除流程；完整团队 Plugin 使用同一 review-changes，包校验通过 |
| A1 混淆两种认证错误 | 补未登录/API key/模型/权限及连接故障的完整模拟程序、恢复建议；明确模拟不等于真实登录实验 |
| 第七课综合题答案小于题目 | 三来源、URL/取得时间、模型或摘录两路径、修订新版本、旧版取消、内容绑定、完整收据、五类逐题评测全部落实 |
| 第六课 Memory 原题不完全对应 | 增加时间/期限可见字段、旧库时间未知的迁移、短版→表格的实际显示、另一进程读回和删除前用户隔离验证 |
| 第六课原代码被讲错 | 原练习实际为 Chroma PersistentClient，已有跨进程测试；纠正“临时存储”“原 Mem0 实现”“必须二选一”等错误，区分产品介绍与指定实作 |
| 研究分支缺本地原文核对材料 | 添加有限原文摘录、章节定位、原三问证据 ID 与未支持反例；中文转述、短引文和教材推断分开 |
| 主课清单未包含练习 README 阅读 | 新增49条 README阅读映射及第六/七课中文补充章；总147条来源记录、118个不同URL、27份来源文档；不把目录里的每家产品都变成必装项 |
| 没有逐题防遗漏检查 | 新增53项原题/选修/支线/综合任务映射，检查标题集合、来源内容哈希、答案文件与验收；每课覆盖页和总入口可直接查 |
| 手机长链接溢出 | 只修改后续课程 later.css 的换行，98页桌面和手机检查通过，未影响第二、三课素材 |

## 当前覆盖结论

[逐题对应表](reference/exercise-correspondence.html)列出53项，每项有原题、范围、本地讲解、完整答案和验收。147条阅读对应保留主课、直接支线与README的来源身份，避免只统计主课清单而漏掉实作目录。每课课后练习仍在最后，A/B路线、身份分支、原课选修和结业门槛保留。

按这一固定版本中规定的学习能力和任务范围，本轮没有留下已发现而未补齐的教材缺项。学习者可以在项目内阅读讲解、代码、资料、参考答案和评分规则；实际执行需要的宿主、模型、账户或 Docker 是运行条件，不能用虚构成功代替。这里不声称已复制每个外部网站的全部页面或复现全部参考论文。

映射表与链接测试只能证明对应关系存在；本轮还逐项检查了题目要求是否真的由相应实现满足。典型反例正是 Hook、Git diff、三来源与 Memory，这些不能靠“已有相近示例”算覆盖。

## 验收质量

- 检索、模型生成、执行状态、学习者独立作答分开验收。固定脚本成绩不当作模型质量。
- 开放题有完整参考产物与逐项量规，结构通过返回 NEEDS_REVIEW；不因文字相同就记录掌握。
- 关键事实、来源、权限与实际外部效果是必过项，不用漂亮表达或总分抵消失败。
- 原文范围与教材迁移题分开：A2 审查的是改动；教师分支保留影长活动；研究分支保留原三问；知识/日常分支保留原材料。
- 公布答案的示范 holdout 不再计作学习者自己的盲测；结业需要另备新题并保留真实执行证据。

## 验证记录

本轮71项回归测试通过，覆盖新旧数据库、三来源、修订、拒绝、重复恢复、篡改、评分反例、读取范围、原题映射与所有层级阅读清单。224个HTML页面、6341条本地引用、114个Python案例的语法和完整代码展示通过；98个课程及对应页面在1280与390像素宽度下无横向溢出，目录跳转正常。

真实本地 Ollama 生成了三份来源的六条摘录，每条能在原文找到；实际返回输入714、输出264 tokens。之后在另一进程批准，再重复恢复，始终只有一条本地账本记录。它是固定 workflow 中的模型摘要路径，没有假称自主浏览或真实发布。

原版练习32个离线测试脚本全部通过：第四课11个、第六课10个、第七课11个，包含两条 provider 路径、CrewAI 结构、Smolagents 接口与 Chroma 跨进程持久化。Docker smoke 未执行，不包含在32个通过脚本中。离线 mock、真实框架对象构造和真实模型生成各有边界，不能据此声称所有云端集成都已通过。

初次检查发现专用通用环境缺 CrewAI、Smolagents、Chroma，因此为三组另建验证环境，不修改根 .venv；根 OpenAI 仍为3.37.0。补齐 langchain-anthropic 和 SOCKS 代理支持后重跑失败路径；四个独立验证环境均通过依赖一致性检查。CrewAI 测试关闭遥测、使用假 API key、未执行 kickoff；框架导入初始化了系统应用数据目录，任务存储置于临时目录。

实际依赖版本记录：[通用验证环境](tooling/verification-requirements.lock.txt)、[CrewAI 1.15.35](tooling/review-crewai.lock.txt)、[Smolagents 1.26.0](tooling/review-codeact.lock.txt)、[Chroma 1.5.9](tooling/review-chroma.lock.txt)。不要把这些锁文件安装到主环境。

## 仍需明确区分的执行边界

完整材料已提供，以下不冒报成已完成的用户实操：真实账户登录、Claude 实际 Hook/Plugin 触发、跨两个宿主比较、远端 GitHub PR、云端 OpenAI 受管检索、Claude SDK 与新版 Dynamic workflow 实跑、Docker 隔离运行。相应课程均说明步骤、预期产物、失败与撤销方法。具备这些条件的学习者可按本地材料继续，不要求去外站找缺失正文。

字符向量/规则重排仍是教学基线，公开20题中“无答案误检”保留为失败分析；高级系统不因有完整示例就适合直接上线。没有新增“用户已掌握”的学习记录。

## 本地证据

- [测试输出](../.scratch/remaining-courses/full-review-2026-11-04/tests.txt)
- [原版练习测试](../.scratch/remaining-courses/full-review-2026-11-04/original-tests.json)
- [页面与链接](../.scratch/remaining-courses/full-review-2026-11-04/links.txt)、[桌面/手机检查](../.scratch/remaining-courses/full-review-2026-11-04/ui.json)
- [原题与答案清单](reference/exercise-correspondence.json)、[全部阅读对应](reference/required-readings.json)
- [实际模型草稿](../.scratch/remaining-courses/full-review-2026-11-04/production-live-draft.json)、[批准收据](../.scratch/remaining-courses/full-review-2026-11-04/production-approved.json)、[重复恢复](../.scratch/remaining-courses/full-review-2026-11-04/production-replayed.json)
- [第二、三课保护结果](../.scratch/remaining-courses/full-review-2026-11-04/protected-result.json)、[上游版本核查](../.scratch/remaining-courses/full-review-2026-11-04/upstream-version.json)
