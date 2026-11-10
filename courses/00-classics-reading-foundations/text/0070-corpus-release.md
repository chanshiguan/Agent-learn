# 审核新资料，再切换活动快照

本单元预计 **55—70 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《先小范围验证，再练一次撤回》](0069-release-rollback.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 新资料先进入候选目录

把修改后的讲稿放在独立候选目录，核对作品标签、来源类型、版本、授权与阅读范围。不要直接覆盖在线文件后期望旧索引自动理解变化。导入前后做字节指纹和正文差异检查，尤其看修订稿是不是撤掉了旧观点。

## 本课使用维护窗口发布

当前 corpus 和 index 分别是文件，不是多文件原子事务。发布时先停止应用接流量和写入，再导入、构建、检查，成功后重启。这样会短暂停用，应提前告知试用者；不把它称作零停机更新。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：实现 backup 的边界

业务数据库用 SQLite 一致快照 API；先停止写入以保持多文件版本一致。

**写在哪里：**项目根目录下的 `companion/maintenance.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：业务数据库用 SQLite 一致快照 API；先停止写入以保持多文件版本一致。
# 预期：恢复失败不覆盖现用目录；备份不是只复制一个文件就宣称可靠。
def backup(destination):
    target = Path(destination)
    target.mkdir(parents=True, exist_ok=False)
    original = data_dir()
    # SQLite backup API 取得一致快照。完整系统备份仍需先停止写入和索引任务，保证多文件版本一致。
    for name in ("reading.sqlite3", "checkpoints.sqlite3"):
        if (original / name).exists():
            with sqlite3.connect(original / name) as source, sqlite3.connect(target / name) as copy:
                source.backup(copy)
    for name in ("corpus.json", "ranges.json", "index.json"):
        if (original / name).exists():
            shutil.copy2(original / name, target / name)
    hashes = {file.name: hashlib.sha256(file.read_bytes()).hexdigest() for file in target.iterdir() if file.is_file()}
    (target / "manifest.json").write_text(json.dumps({"files": hashes, "strategy": "索引可由 corpus 重建；此包不含 Qdrant 卷与模型权重"}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"backup": str(target), "files": list(hashes)}
```

**写完后应当怎样：**恢复失败不覆盖现用目录；备份不是只复制一个文件就宣称可靠。

### 第 2 步：实现 restore 的边界

先核对备份文件白名单与指纹，再恢复到新目录；撤销旧令牌，索引明确重建。

**写在哪里：**项目根目录下的 `companion/maintenance.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：先核对备份文件白名单与指纹，再恢复到新目录；撤销旧令牌，索引明确重建。
# 预期：恢复失败不覆盖现用目录；备份不是只复制一个文件就宣称可靠。
def restore(source, destination):
    source, target = Path(source), Path(destination)
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    allowed = {"reading.sqlite3", "checkpoints.sqlite3", "corpus.json", "ranges.json", "index.json"}
    if not set(manifest["files"]).issubset(allowed):
        raise ValueError("备份包含未约定的文件名。")
    for name, expected in manifest["files"].items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"备份指纹不符：{name}")
    target.mkdir(parents=True, exist_ok=False)
    for name in manifest["files"]:
        if name != "index.json":
            shutil.copy2(source / name, target / name)
    if (target / "reading.sqlite3").exists():
        with sqlite3.connect(target / "reading.sqlite3") as db:
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("数据库完整性检查失败。")
            # 恢复后重新登录，避免把备份里的旧访问令牌重新激活。
            db.execute("DELETE FROM tokens")
            db.execute("UPDATE actions SET expires=0 WHERE status='pending'")
    return {"restored": str(target), "index_rebuild_required": True, "login_required": True}
```

**写完后应当怎样：**恢复失败不覆盖现用目录；备份不是只复制一个文件就宣称可靠。

### 第 3 步：接入已经写出的备份和恢复函数

命令入口不另造一套文件复制逻辑。

**写在哪里：**项目根目录下的 `companion/maintenance_cli.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .maintenance import manifest
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .maintenance import manifest, backup, restore
```

**写完后应当怎样：**不同动作复用同一套校验。

### 第 4 步：把恢复目录显式交给调用者

不默认覆盖活动数据，先在新目录验证成功再安排切换。

**写在哪里：**项目根目录下的 `companion/maintenance_cli.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    initialize()
    result=manifest()
    save("release-manifest.json",result)
```

</details>

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

```python
    parser=argparse.ArgumentParser(description="记录、备份与恢复")
    if kind=="backup":parser.add_argument("destination")
    elif kind=="restore":
        parser.add_argument("source");parser.add_argument("destination")
    args=parser.parse_args();initialize()
    if kind=="backup":result=backup(args.destination)
    elif kind=="restore":result=restore(args.source,args.destination)
    else:
        result=manifest();save("release-manifest.json",result)
```

**写完后应当怎样：**恢复后重新登录并重建向量索引。

### 第 5 步：给命令入口增加 backup

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        main('manifest')
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        main('manifest')
    elif command == "backup":
        from .maintenance_cli import main
        main('backup')
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。

### 第 6 步：给命令入口增加 restore

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        main('backup')
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        main('backup')
    elif command == "restore":
        from .maintenance_cli import main
        main('restore')
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。

## 运行并观察

```bash
# 停止应用接收请求，Qdrant 仍保持运行；等待正在处理的请求结束后再继续维护。
docker compose --env-file .env -f deploy/compose.yaml stop app
# 先保存变更前快照；目标目录必须尚不存在，避免覆盖一份可恢复备份。
python -m companion backup data/backups/before-update-01
# 教学演练先用原五份样本重建同样的快照；真实更新时改成已审核的候选目录。
docker compose --env-file .env -f deploy/compose.yaml run --rm app python -m companion ingest --size 80 --overlap 16
# 在 Compose 网络里构建新索引，完成数量检查后才发布活动指针。
docker compose --env-file .env -f deploy/compose.yaml run --rm app python -m companion index
# 启动应用并验证就绪，然后用固定题集检查资料引用。
docker compose --env-file .env -f deploy/compose.yaml up -d app
curl --fail http://127.0.0.1:8000/readyz
```

记录旧新 revision、集合名、片段数量和一条变化后的检索结果。需要练真实变更时，只改候选副本一处已审核文本，再重复完整步骤。失败时保持维护状态，恢复对应 corpus 与 index 组合，或按下一单元从备份重建。

撤下文件后检查新检索不再出现它；旧集合、Embedding 缓存、原始存储和备份按留存规则清理。在线不可见不等于物理删除完成。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 为什么必须先停止写入？
2. 切换活动索引是否自动清理所有旧资料？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么必须先停止写入？**

备份与更新跨多个文件和数据库，单个文件写入原子并不保证整套状态同一时刻一致。

**切换活动索引是否自动清理所有旧资料？**

不会。旧集合与缓存保留用于回滚，永久删除需单独处理并记录。

**通过证据：**一次完整维护窗口、前后资料与索引版本、固定题复测和失败恢复方案。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
