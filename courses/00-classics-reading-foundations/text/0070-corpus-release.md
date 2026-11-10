# 审核新资料，再切换活动快照

本单元预计 **40—55 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 新资料先进入候选目录

把修改后的讲稿放在独立候选目录，核对作品标签、来源类型、版本、授权与阅读范围。不要直接覆盖在线文件后期望旧索引自动理解变化。导入前后做字节指纹和正文差异检查，尤其看修订稿是不是撤掉了旧观点。

## 本课使用维护窗口发布

当前 corpus 和 index 分别是文件，不是多文件原子事务。发布时先停止应用接流量和写入，再导入、构建、检查，成功后重启。这样会短暂停用，应提前告知试用者；不把它称作零停机更新。

```bash
# 停止应用接收请求，Qdrant 仍保持运行；等待正在处理的请求结束后再继续维护。
docker compose -f deploy/compose.yaml stop app
# 先保存变更前快照；目标目录必须尚不存在，避免覆盖一份可恢复备份。
python -m companion backup data/backups/before-update-01
# 教学演练先用原五份样本重建同样的快照；真实更新时改成已审核的候选目录。
docker compose -f deploy/compose.yaml run --rm app python -m companion ingest --size 80 --overlap 16
# 在 Compose 网络里构建新索引，完成数量检查后才发布活动指针。
docker compose -f deploy/compose.yaml run --rm app python -m companion index
# 启动应用并验证就绪，然后用固定题集检查资料引用。
docker compose -f deploy/compose.yaml up -d app
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
