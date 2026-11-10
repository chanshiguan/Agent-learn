# 真的恢复一次，再谈备份可靠

本单元预计 **45—65 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 备份成功只证明写出了文件

本课备份 SQLite 一致快照、corpus、人工范围和索引元数据，逐文件记录 SHA-256。它不含模型权重与 Qdrant 卷，恢复后依据 corpus 重建索引。原始 DOCX 需另行受控保管；仅此备份不足以恢复完整资料来源。

```bash
# 在已停止写入的窗口创建新备份目录；不要复用已经存在的名字。
python -m companion backup data/backups/restore-drill-01
# 恢复到全新目录，保留现有学习状态；指纹不符应拒绝，旧令牌撤销、待确认动作过期。
python -m companion restore data/backups/restore-drill-01 data/restored-01
# 仅在恢复副本上做向前兼容迁移；给 notes 新增可空字段，重复执行不应重复加列。
READING_DATA_DIR=data/restored-01 python -m companion.migrate
READING_DATA_DIR=data/restored-01 python -m companion.migrate
# 用临时数据验证备份被篡改时拒绝恢复；不修改真实备份。
PYTHONPATH=../tests python -m unittest test_companion.CompanionTests.test_backup_restore_verifies_hash_and_revokes_tokens -v
```

在第二个终端设置 READING_DATA_DIR=data/restored-01，启动独立端口 8001 的 authenticated 服务，重新登录。核对本人笔记内容和条数、会话进度、未知范围排除、过期批准不可恢复。keyword 路线可先验证；向量路线按实际运行位置重建 index，再查同一来源。

迁移前后核对 note_count，旧字段仍能读写。此例是新增可空字段的兼容迁移；删列、改含义或换存储不是同样简单，需单独数据转换和回滚方案。

## 记录两个恢复目标

RTO 是恢复到可用花了多久；RPO 是最多可能丢失多久的数据。记录真实开始、结束和备份时刻，而不是填一个想达到的数字。目标由公司确认，实际结果由演练证明。

恢复旧备份还要重放之后的删除清单，避免复活已删除个人内容。备份访问、保留期限和原始资料恢复一起纳入操作手册。

## 对照完整实现

先读上面标出的函数，再展开文件。配套包已包含它及依赖文件；不需要把后续章节一起学完。注释重点解释为什么这样处理，以及出错时应发生什么。

<details><summary>展开本单元完整源码：companion/maintenance.py</summary>

{{code:companion/maintenance.py}}

</details>

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 为何恢复后要重新登录并让批准过期？
2. 本备份包足够恢复所有东西吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为何恢复后要重新登录并让批准过期？**

避免旧令牌重新生效，也避免把备份里的陈旧确认当成现在仍有效的用户意图。

**本备份包足够恢复所有东西吗？**

不够。Qdrant 索引需重建，模型权重需缓存或重下，原始 DOCX、配置与凭据需按独立受控流程恢复。

**通过证据：**新目录实际恢复、内容核对、索引重建、迁移前后计数及实测 RTO/RPO。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
