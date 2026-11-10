# 启动向量库，重启后继续查

本单元预计 **35—50 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 复用前面学过的 Docker

Qdrant 保存向量和元数据，并按相似度查询。collection 可以先理解为一份有固定向量维度的索引集合。第 9 章的生成路线不变，这次只把内存里的检索数据搬到服务中。

```bash
# 创建专用持久卷；容器移除后数据仍留在这个卷中。
docker volume create classics-qdrant
# 仅把服务端口开放给本机；首次下载镜像需要网络，已有同名容器时改用 start。
docker run -d --name classics-qdrant -p 127.0.0.1:6333:6333 -v classics-qdrant:/qdrant/storage qdrant/qdrant:v1.15.5
# 连接本机 Qdrant；正常课程不要设置仅供离线测试的 QDRANT_MODE=local。
export QDRANT_URL=http://127.0.0.1:6333
# 编码当前快照并发布活动索引指针；预期 count 与 corpus 中片段数一致。
python -m companion index
# 按语义查询持久索引；返回的仍是可回查的讲稿片段。
python -m companion search "文言文序言" --method semantic
```

若 connection refused，先看容器是否运行及端口映射；若提示模型窗口超限，检查是否仍用第 9 章的 80/16 小块。向量维度由编码器决定，不要手填一个猜测的维度。

## 证明数据确实持久化

```bash
# 停止再启动同一个练习容器；预期原集合仍在，不需要删除卷或重建资料。
docker stop classics-qdrant
docker start classics-qdrant
# 服务启动完成后重查；若暂时连接失败，先检查容器状态再重试。
python -m companion search "文言文序言" --method semantic
```

记录重启前后的集合名、条数和一条来源 ID。这证明的是本次恢复可用，不证明公司级可用性。卷损坏或主机丢失仍需备份，第 28 章专门演练。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 容器和卷分别保存什么？
2. Qdrant 能替你判断讲稿观点正确吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**容器和卷分别保存什么？**

容器运行 Qdrant 进程，命名卷保存持久数据。删容器不等于删卷，但删除卷会丢失其中索引。

**Qdrant 能替你判断讲稿观点正确吗？**

不能。它负责存储和检索，文学事实与解释仍需来源和评测。

**通过证据：**有真实 Qdrant 容器记录和重启后相同来源的查询结果；未在 Docker 跑过就标待运行。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/06-memory-rag.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter8)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
