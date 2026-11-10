# 活着不等于已经能接待读者

本单元预计 **35—50 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《从单个容器走到一组服务（2/2：连接接口与业务）》](0064-compose-deployment-02.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 两个检查回答不同问题

`/healthz` 只表示进程能响应；`/readyz` 检查资料、状态库、所选向量索引与模型列表。模型断了时，进程仍可能活着，因此不能只凭健康状态放行流量。某些供应商不支持 models.list，需要按真实接口调整 readiness，并补最小生成检查，不能伪造模型已就绪。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：把存活和可以接单分开检查

资料、状态库、所选索引和生成模型都需要就绪；不通过时先定位依赖，不直接重启一切。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：资料、状态库、所选索引和生成模型都需要就绪；不通过时先定位依赖，不直接重启一切。
# 预期：healthz 可200而readyz为503；恢复依赖后才返回ready。
@app.get("/readyz")
def ready():
    corpus = load("corpus.json")
    if not corpus:
        raise HTTPException(503, "资料尚未准备好。")
    with state.connect() as db:
        db.execute("SELECT 1 FROM sessions LIMIT 1")
    if os.environ.get("RETRIEVAL", "keyword") != "keyword":
        from .vectors import connection
        current = load("index.json")
        if not current or current["corpus_revision"] != corpus["revision"]:
            raise HTTPException(503, "资料索引待更新。")
        with connection() as db:
            db.get_collection(current["collection"])
    from .models import client
    sdk, model = client(timeout=5)
    with sdk:
        available = {item.id for item in sdk.models.list().data}
    if model not in available:
        raise HTTPException(503, "生成模型尚未就绪。")
    return {"status": "ready", "revision": corpus["revision"][:12]}
```

**写完后应当怎样：**healthz 可200而readyz为503；恢复依赖后才返回ready。


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
# 检查进程存活；预期返回 alive。
curl --fail http://127.0.0.1:8000/healthz
# 检查依赖就绪；缺资料、索引或模型时应非成功状态。
curl --fail http://127.0.0.1:8000/readyz
# 查看有限的服务日志定位启动问题；不要把含凭据的配置完整贴给他人。
docker compose --env-file .env -f deploy/compose.yaml logs --tail 40 app
```

本地与线上路线都用同一个故障实验：先记下 `.env` 中已经验证的 LLM_MODEL，再暂改为 `course-model-does-not-exist`。这只改你自己的应用配置，不关闭任何共享服务。

```bash
# 让修改后的 .env 进入新应用容器；不需要重建代码镜像。
docker compose --env-file .env -f deploy/compose.yaml up -d --no-deps --force-recreate app
# 进程仍应能响应存活检查。
curl --fail http://127.0.0.1:8000/healthz
# 预期因模型不在列表中返回非成功状态；保留这一失败作为演练结果。
curl --fail http://127.0.0.1:8000/readyz
```

再从页面提问，核对错误提示。然后把 `.env` 的 LLM_MODEL 改回记下的真实值，重复上面的重建容器命令和两项检查，直到就绪与问答都恢复。后续章节从恢复成功的状态继续。

若正在使用 hybrid，再单独测试 Qdrant：

```bash
# 只停止这套练习项目的向量服务；应用进程保留，观察依赖故障与存活的区别。
docker compose --env-file .env -f deploy/compose.yaml stop qdrant
# 预期就绪失败；不要把这次故意失败算成安装损坏。
curl --fail http://127.0.0.1:8000/readyz
# 恢复同一命名卷上的 Qdrant，数据不因 stop 被删除。
docker compose --env-file .env -f deploy/compose.yaml up -d qdrant
```

等待向量服务启动后重新检查 readyz 和同一个问题，确认恢复，再进入下一节。keyword 路线不依赖向量服务，此项可跳过。

## 真正对外访问前补哪条连接

公司受控访问通常由 HTTPS 反向代理接到本机 8000。`deploy/Caddyfile.example` 展示这层关系，实际域名、DNS、证书、访问范围和运维账号由部署负责人配置；`.env` 的 ALLOWED_HOSTS 加入真实域名。仅准备配置文件不算完成 HTTPS 验证。

先在受保护测试域名验证登录、来源、反馈与错误，再允许试用。应用端口、数据库端口、模型端口不直接暴露公网。本课单 worker 配置与进程内限流一致，多副本扩容前需要共享状态、限流和取消机制。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. healthz 成功、readyz 失败合理吗？
2. 有 Caddyfile 就算 HTTPS 上线了吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**healthz 成功、readyz 失败合理吗？**

合理。进程活着但依赖未就绪，应停止接纳需要这些依赖的业务流量。

**有 Caddyfile 就算 HTTPS 上线了吗？**

没有。必须完成实际域名、证书、网络与访问验证，并按公司要求审核。

**通过证据：**模型故障前后的双检查与用户界面记录；对外访问项注明实际完成或待办。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
