# 综合题完整答案：三份来源、修订与五类验收

## 输入、输出与适用边界

输入是三份教材内虚构资料：protocol 说明结果与调用 ID；permission 说明执行前检查；approval 说明人工批准与修订。来源记录 id、text、origin、retrieved_at，后者是本次本地载入时间，不伪装成网络采集时间。输出是逐条带 source_id 的摘录、不可变草稿、审批状态、本地账本与完整收据。

默认模式直接摘录原文，不调用模型；后面的 --live 模式让模型挑选摘录句。两种模式都严格检查句子是否来自对应来源，因此可以自动判定这项条件。换成自然语言总结时，应额外核对事实和语义；来源 ID 正确不足以证明整句正确。三份资料的完整文本已写在程序的 SOURCE_TEXTS 中，不需要外部文件。

## 先生成，再在另一个进程恢复

在项目根目录执行；目录用过时换新的名字，避免把历史任务当新实验。

```bash
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
python3 courses/07-multi-agent-production/examples/production_case.py /tmp/course7-three-v1
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
python3 courses/07-multi-agent-production/examples/production_case.py /tmp/course7-three-v1 --decision approve
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
python3 courses/07-multi-agent-production/examples/production_case.py /tmp/course7-three-v1 --decision approve
```

第一条 waiting_for_approval；第二条 completed；第三条仍 completed，ledger 只有一条。receipt 中 result 与三份摘录一致，sources 有三份，approval.effective 为 approved，bound_sha256 对应草稿。usage 为零且注明没有模型调用；不是把未知费用估算为零。

## 修改后生成第二版，旧版不能再批准

先创建另一个未批准任务，再提交明确的修订内容。本例把前两句顺序调整，第三句缩短为“修改后重新审核。”。

{{code:../examples/revision-claims.json}}

```bash
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
python3 courses/07-multi-agent-production/examples/production_case.py /tmp/course7-edit-v1
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
python3 courses/07-multi-agent-production/examples/production_case.py /tmp/course7-edit-v2 --revise-from /tmp/course7-edit-v1 --claims courses/07-multi-agent-production/examples/revision-claims.json
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
python3 courses/07-multi-agent-production/examples/production_case.py /tmp/course7-edit-v1 --decision approve
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
python3 courses/07-multi-agent-production/examples/production_case.py /tmp/course7-edit-v2 --decision approve
```

完整参考：旧版先被终止，第三条依然 cancelled，effective=rejected，requested=approve 只表示这次请求，不会篡改历史决定；新版本 artifact_version=2，parent_task_id 指回旧任务，批准后只有新版账本有记录。不能把 approved 与 cancelled 互相改写成“再试一次”。

如果修订加入“可以免审核”而原文没有，必须 ValueError，旧版仍待审；如果直接篡改 draft.json 再恢复，必须停止并保存 failed-attempt.json，不影响已经存在的成功收据。修改内容需要走 revise，不能只手改哈希。

{{code:../examples/production_case.py}}

底层完整的状态检查、原子保存与幂等账本在[原核心练习](05-original-labs.md)及本课完整代码页。示例只支持单操作者顺序执行，不具备服务器身份认证，也不承诺防止同一账号恶意同时改状态和草稿；部署时另加可信存储、身份认证、授权与数据库事务。

## 五类 development case 与逐题答案

```bash
# 运行 courses/07-multi-agent-production/examples/control_eval.py，按本行参数完成当前案例并核对输出。
python3 courses/07-multi-agent-production/examples/control_eval.py
```

| 题目 | Outcome 参考 | Trajectory 参考 |
|---|---|---|
| 正常三份资料 | completed；结果等于三条原文，source ID 对齐 | policy 允许后再审批，账本一次 |
| 无资料 | NO_EVIDENCE；不造摘要 | 没进入接受步骤，没有账本 |
| 非法 send 工具 | BLOCKED | 执行前拒绝，未发送 |
| 步数预算为零 | BUDGET_EXHAUSTED | 不生成也不批准，保留失败类型 |
| 人工拒绝 | cancelled；result=null | 不产生接受效果，留下 rejected |

{{code:../examples/control_eval.py}}

参考应为 passed=5，每题同时有 case、receipt、grade。这是 development、单 trial、确定性控制测试；没有测试大模型生成可靠性，不与真实模型 Eval 分数混用。保存为 baseline 后再修改控制逻辑，按 case.id 比较两个版本的 outcome_pass、trajectory_pass；只要原通过题变 FAIL，就出现回归，不能只看平均值。

## 一题贯穿多个章节的独立练习

换三份你有权使用的小资料，把逐字摘录保留为第一版；执行批准、拒绝、修订、重复恢复和篡改五项，再换一个相似但不受支持的摘录，证明它被退回。提交原始来源、两版草稿、各次收据、逐题报告与一句失败解释。

验收逐项必过：三份来源和本地取得时间齐全；每条摘录可回查；未批准无效果；旧版无法重新批准；重复恢复不重复效果；失败留有原因；报告区分控制测试与模型效果。没有某个文件就退回对应步骤，不以总分抵消。两天后只凭 receipt 重建过程，一周后把确定性摘录替换为模型草稿，再保留同样执行约束并增加人工事实检查。

## 对齐原项目的 URL 来源与真实模型路径

上面的固定资料先练控制逻辑。原项目还要求来源 URL、抓取时间及 Agent 摘要，下面把三份 MIT 课程原文接入同一流程。默认读取项目中已有快照，不用访问外站；`--network` 才真正请求固定版本并保存抓取时间。两种模式在 origin 中明确区分。

{{code:../examples/collect_sources.py}}

```bash
# 运行 courses/07-multi-agent-production/examples/collect_sources.py，按本行参数完成当前案例并核对输出。
python3 courses/07-multi-agent-production/examples/collect_sources.py /tmp/course7-collected
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
python3 courses/07-multi-agent-production/examples/production_case.py /tmp/course7-real-sources --sources /tmp/course7-collected/sources.json
```

参考：sources.json 恰有三份不同 id，每份 url 指向固定提交，full_text_file 有完整原文，text 能在原文中找到。第二条仍是确定性摘录；可以先批准它验证来源字段完整。若要自己验证真实采集，用另一个空目录执行 `collect_sources.py /tmp/course7-network --network`，origin 必须为“网络抓取固定版本”。

接入当前项目已有的本地模型：

```bash
# 列出本机已安装的模型，不会下载新模型。
ollama list
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出；--live 会进入真实服务路径，需先满足本章环境要求。
.venv/bin/python courses/07-multi-agent-production/examples/production_case.py /tmp/course7-model --sources /tmp/course7-collected/sources.json --live
# 运行 courses/07-multi-agent-production/examples/production_case.py，按本行参数完成当前案例并核对输出。
.venv/bin/python courses/07-multi-agent-production/examples/production_case.py /tmp/course7-model --decision approve
```

默认使用 gemma4:e4b，已有模型不会重复下载；也可以用 OLLAMA_MODEL 环境变量指定其他已安装模型。--live 请求固定的 localhost 地址。如果返回的 JSON 不合法、缺少来源，或内容没有原文支持，程序会明确报错，不生成可批准的草稿。

模型在这里负责挑选摘要句子，读取来源、验证、批准和恢复都由程序控制。这是固定 workflow 中的一次模型调用，没有让模型自主联网研究。运行后，先打开 draft.json 核对内容，再批准；下面的命令虽然列在一起，检查这一步仍要实际完成。

收据保存该次实际 usage。修订版是人工改稿，无新增模型调用，旧版用量仍在旧草稿与收据中；统计整条任务链时按 parent_task_id 汇总，不能用最新版零用量覆盖此前调用。固定示范不替代真实模型 trial；真正的单 Agent 基线应保存每题每次生成结果，再用同一判据比较回归。
