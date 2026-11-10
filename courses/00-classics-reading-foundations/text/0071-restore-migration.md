# 真的恢复一次，再谈备份可靠

本单元预计 **35—50 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《审核新资料，再切换活动快照》](0070-corpus-release.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 备份成功只证明写出了文件

本课备份 SQLite 一致快照、corpus、人工范围和索引元数据，逐文件记录 SHA-256。它不含模型权重与 Qdrant 卷，恢复后依据 corpus 重建索引。原始 DOCX 需另行受控保管；仅此备份不足以恢复完整资料来源。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：写一次可重复的数据结构升级

使用事务和 user_version 识别升级状态；升级后旧笔记与新写入都需要回查。

**写在哪里：**项目根目录下的 `companion/migrate.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：使用事务和 user_version 识别升级状态；升级后旧笔记与新写入都需要回查。
# 预期：重复运行不重复改结构，失败时回滚，不要求删库重来。
"""第 28 章：只在恢复副本上练习向前兼容迁移，旧程序仍可读取原字段。"""
from .state import connect, initialize


def migrate():
    initialize()
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version == 1:
            # 新字段允许为空，使已有笔记不必编造时间或补填不存在的信息。
            db.execute("ALTER TABLE notes ADD COLUMN archived_at REAL")
            db.execute("PRAGMA user_version=2")
        elif version != 2:
            raise ValueError("未知数据库版本，先准备单独的迁移方案。")
        return {"schema_version": 2, "note_count": db.execute("SELECT count(*) FROM notes").fetchone()[0]}


if __name__ == "__main__":
    print(migrate())
```

**写完后应当怎样：**重复运行不重复改结构，失败时回滚，不要求删库重来。

## 运行并观察

应用停止前，先在页面记录本人的一条笔记、会话进度和一条未确认草稿的内容；没有笔记或待确认草稿时，沿用第19章的操作各准备一条。保留这份记录，恢复后逐项核对，不能只检查“恢复成功”的提示。

```bash
# 先停止上一节仍在运行的应用，避免备份时会话或资料继续变化。
docker compose --env-file .env -f deploy/compose.yaml stop app
# 确认 app 已停止；同时结束其他终端的导入、建索引和宿主 Uvicorn 进程。
docker compose --env-file .env -f deploy/compose.yaml ps -a app
# 确认没有写入任务后创建新备份目录；不要复用已经存在的名字。
READING_DATA_DIR=data/live python -m companion backup data/backups/restore-drill-01
# 恢复到全新目录，保留现有学习状态；指纹不符应拒绝，旧令牌撤销、待确认动作过期。
python -m companion restore data/backups/restore-drill-01 data/restored-01
# 仅在恢复副本上做向前兼容迁移；给 notes 新增可空字段，重复执行不应重复加列。
READING_DATA_DIR=data/restored-01 python -m companion.migrate
READING_DATA_DIR=data/restored-01 python -m companion.migrate
```

现在备份和恢复目录已经分开。接下来用停止服务前留下的记录检查恢复副本。

在第二个终端进入同一个项目并启用 `.venv`，沿用第4章已经验证的模型配置，然后启动恢复副本。下面这一行只为该进程设置数据目录和端口，不会把主应用指向副本：

```bash
# 用隔离目录和端口启动恢复副本；authenticated 要求登录，development 允许本机 HTTP 演练。
READING_DATA_DIR=data/restored-01 APP_MODE=authenticated APP_ENV=development RETRIEVAL=keyword ALLOWED_HOSTS=localhost,127.0.0.1 COURSE_CHAPTER=29 python -m uvicorn companion.app:app --host 127.0.0.1 --port 8001 --workers 1 --no-access-log
```

打开 `http://127.0.0.1:8001`，用恢复前已有账号重新登录。核对本人笔记内容和条数、会话进度、未知范围排除；尝试批准那条旧草稿，应因过期失败。没有旧草稿时，先记录该项“缺测试数据”，准备一条待确认草稿后重新备份演练，不应直接打勾。keyword 路线可先验证；向量路线需在副本目录重建 index，再查同一来源。

迁移前后核对 note_count，旧字段仍能读写。此例是新增可空字段的兼容迁移；删列、改含义或换存储不是同样简单，需单独数据转换和回滚方案。

## 记录两个恢复目标

RTO 是恢复到可用花了多久；RPO 是最多可能丢失多久的数据。记录真实开始、结束和备份时刻，而不是填一个想达到的数字。目标由公司确认，实际结果由演练证明。

恢复旧备份可能让备份之后已删除的个人内容重新出现。当前程序只删除活动业务库中的内容，没有生成独立删除账本，也没有自动在恢复时重放删除操作。这个缺口必须写入上线阻塞项，不能把本节演练当成生产隐私恢复已经完成。公司上线前需要确定并验证独立保存删除记录、恢复后重放和备份到期清除的流程。

完成演练后，在副本终端按 `Ctrl+C` 停止 8001 服务，再回到原终端恢复主应用：

```bash
# 恢复原应用；它仍挂载 data/live，不会使用 data/restored-01。
docker compose --env-file .env -f deploy/compose.yaml up -d app
# 待应用启动后核对就绪；失败时先看日志，不能把恢复服务等同于业务恢复。
curl --fail http://127.0.0.1:8000/readyz
```

项目记录中分别留下“副本验证”和“原服务恢复”结果。下一章汇总上线证据时要引用它们，并保留未完成的恢复事项。


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

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
import tempfile
from pathlib import Path
from companion.maintenance import backup,restore
with tempfile.TemporaryDirectory() as d:
    backup(Path(d)/"backup")
    r=restore(Path(d)/"backup",Path(d)/"restored")
    assert r["index_rebuild_required"] and r["login_required"]
print("独立目录恢复通过；未替换活动库")
PY
```

**预期：**备份指纹校验与独立恢复通过；生产恢复仍需按真实环境演练。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
