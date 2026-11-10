# 把这次能跑的条件记录下来

本单元预计 **60—75 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《小步加负载，检查拒绝与取消（2/2：连接接口与业务）》](0067-load-and-limits-02.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## “我这儿能跑”缺了哪些条件

同样源码配不同依赖、模型、Prompt 或资料，行为可能不同。候选版本至少记录程序提交、依赖、镜像摘要、Prompt 版本、模型配置、资料 revision 和索引版本。凭据不能混进清单。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：先写这个文件需要的导入

把一次能运行的条件写成记录；数据库、资料、模型与源码版本要区分。

**写在哪里：**项目根目录下的 `companion/maintenance.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：把一次能运行的条件写成记录；数据库、资料、模型与源码版本要区分。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import hashlib
import json
import os
import shutil
import sqlite3
from pathlib import Path
from .files import data_dir, load
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 2 步：记录当前源码、依赖、模型和资料版本

只写镜像标签无法复现真实状态；把本次实际条件和缺失项一起列出。

**写在哪里：**项目根目录下的 `companion/maintenance.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：只写镜像标签无法复现真实状态；把本次实际条件和缺失项一起列出。
# 预期：记录真实值，不把缺失依赖或未测路线写成已验证。
def manifest():
    import importlib.metadata
    packages = {}
    for name in ("python-docx", "openai", "fastapi", "qdrant-client", "sentence-transformers", "langgraph"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    from .state import connect
    with connect() as db:
        schema_version = db.execute("PRAGMA user_version").fetchone()[0]
    source_root = Path(__file__).parent
    source_hashes = {str(f.relative_to(source_root)): hashlib.sha256(f.read_bytes()).hexdigest()
                     for f in source_root.rglob("*") if f.is_file() and f.suffix in {".py", ".html", ".js", ".css"}}
    return {"application": "classics-course-v2", "source_hashes": source_hashes,
            "generation_model": os.environ.get("LLM_MODEL"), "generation_route": os.environ.get("LLM_MODE"), "prompt_version": "grounded-v1",
            "corpus_revision": (load("corpus.json") or {}).get("revision"),
            "index": load("index.json"), "packages": packages,
            "schema_version": schema_version}
```

**写完后应当怎样：**记录真实值，不把缺失依赖或未测路线写成已验证。

### 第 3 步：让版本记录成为可重复命令

每次候选版本重跑，而不复制上一版记录里的成功结论。

**写在哪里：**项目根目录下的 `companion/maintenance_cli.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

```python
# 目的：每次候选版本重跑，而不复制上一版记录里的成功结论。
# 预期：生成 release-manifest.json，原业务数据不改动。
import argparse
import json
from .files import save
from .state import initialize
from .maintenance import manifest


def main(kind="manifest"):
    initialize()
    result=manifest()
    save("release-manifest.json",result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
```

**写完后应当怎样：**生成 release-manifest.json，原业务数据不改动。

### 第 4 步：给命令入口增加 manifest

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        from .family_cli import main
        main()
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        from .family_cli import main
        main()
    elif command == "manifest":
        from .maintenance_cli import main
        main('manifest')
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。

### 第 5 步：亲手写最小持续检查流程

测试已经在本机跑过，现在让 GitHub 在每次提交时重复执行。路径从你自建仓库根目录计算。

**写在哪里：**项目根目录下的 `.github/workflows/check.yml`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**YAML 用缩进表示归属；先分清服务名、配置键和值。配置文件本身不会执行，运行 Compose 或触发工作流时才会使用它。

```yaml
# 目的：每次提交都运行自己写出的六项检查，先拦住确定的行为回归。
# 预期：没有模型密钥也可执行；通过不等于文学答案或生产部署通过。
name: companion-checks
on: [push, pull_request]
jobs:
  contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: '3.12'
      - name: 安装测试所需依赖
        run: python -m pip install -r requirements.txt -r requirements-model.txt -r requirements-web.txt -r requirements-graph.txt
      - name: 检查本人归属、批准与输入边界
        run: python -m unittest discover -s tests -v
```

**写完后应当怎样：**推送练习仓库后可查看 Actions 的通过或失败日志；此流程不发布网站或服务。


## 更新容器后再验证

Docker 镜像保存的是构建时的代码。刚改的宿主文件不会自动进入旧容器；先在这个练习环境重建 app 镜像并替换 app 容器，再执行下面的检查。数据目录通过挂载保留，Qdrant 不需要跟着重建。

```bash
# 将本节刚写的代码装进新镜像；不会把 .env 或 data 复制进镜像。
docker compose --env-file .env -f deploy/compose.yaml build app
# 按新镜像重新创建 app，仍使用原挂载数据；等待启动后再访问接口。
docker compose --env-file .env -f deploy/compose.yaml up -d --no-deps --force-recreate app
```


## 运行并观察

```bash
# 执行自动行为检查，先挡住确定的回归。
python -m unittest discover -s tests -v
# 记录当前依赖与资料/索引指纹；输出不包含模型密钥。
python -m companion manifest
# 若候选运行在 Compose 中，再记录容器里的实际依赖；它可能与主机环境不同。
docker compose --env-file .env -f deploy/compose.yaml run --rm app python -m companion manifest
# 保存实际解析后的依赖版本，便于在相同平台重建；跨平台仍要重新安装验证。
python -m pip freeze > data/live/requirements-resolved.txt
# 记录候选镜像的实际标识，不只写容易被覆盖的 candidate 标签。
docker image inspect classics-companion:candidate --format '{{.Id}}'
```

检查 `release-manifest.json` 的 packages 中是否有 null；没有安装的组件要明确说明，不假装环境完整。课程文件标注的直接依赖版本与 pip freeze 的完整依赖是两个层次。

## 把检查搬到自动流程

刚写出的 `.github/workflows/check.yml` 位于你自建项目内。将这个项目作为独立练习仓库推送后，GitHub 才会执行它。它安装依赖并运行行为测试，不需要模型密钥，不进行发布；真实模型评阅和公司审批仍是独立证据。

不要把私人 DOCX、.env、数据状态库和报告中的私人内容提交到公开仓库。复现依赖程序和合规的测试样本，不依赖公开个人资料。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 为什么镜像标签还不够？
2. CI 通过就能自动开放给学生吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么镜像标签还不够？**

标签可能指向不同镜像。记录实际镜像标识或发布摘要，才能知道运行的确切产物。

**CI 通过就能自动开放给学生吗？**

不能。CI 只覆盖确定行为，仍需质量、容量、隔离、内容与公司上线审查。

**通过证据：**候选清单、解析依赖、镜像标识与自动测试报告，明确真实模型评阅另在何处。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
