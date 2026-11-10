# 先小范围验证，再练一次撤回

本单元预计 **35—50 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《把这次能跑的条件记录下来》](0068-release-manifest.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 发布前先知道怎样退回来

上一节已经构建并验证了 `classics-companion:candidate`。现在保存它，再做一个只改页面标题的新版本；用肉眼可见的变化判断实际运行的是哪一版。演练不修改数据结构，因此回退不需要恢复数据库。

## 保存并验证第一版

```bash
# 把刚验证的候选保留为第一版；后面构建新版本时不会覆盖这个标签。
docker tag classics-companion:candidate classics-companion:trial-v1
# 启动指定版本；--no-build 保证使用保存的产物，不根据当前源码偷偷重建。
RELEASE_TAG=trial-v1 docker compose --env-file .env -f deploy/compose.yaml up -d --no-build app
# 等应用启动后检查就绪，再打开网页核对标题、登录、问答和来源。
curl --fail http://127.0.0.1:8000/readyz
# 记录第一版实际镜像 ID，后面用它判断是否真的回到原产物。
docker image inspect classics-companion:trial-v1 --format '{{.Id}}'
```

在页面确认标题是“一起读《狂人日记》”，完成登录、问答、查看来源、批准一条测试笔记，并记录结果。这里保存的笔记也用于观察切换版本后数据是否仍在。

## 做一个可识别的第二版

在编辑器打开 `companion/web/index.html`，将唯一一行 `<h1>一起读《狂人日记》</h1>` 改成 `<h1>一起读《狂人日记》 · 版本演练</h1>`，其他内容保留。标题变化只是这次练习的版本标记，不改变问答逻辑。

```bash
# 将改过标题的源码构建为第二版；保留 trial-v1，也不覆盖 candidate。
docker build -f deploy/Dockerfile -t classics-companion:trial-v2 .
# 切换到第二版；数据仍来自原来的挂载目录。
RELEASE_TAG=trial-v2 docker compose --env-file .env -f deploy/compose.yaml up -d --no-build app
# 第二版就绪后再检查页面，不用启动瞬间的连接失败判断发布失败。
curl --fail http://127.0.0.1:8000/readyz
# 第二版 ID 应与第一版不同；保存记录供撤回时对照。
docker image inspect classics-companion:trial-v2 --format '{{.Id}}'
```

刷新浏览器，应看到“版本演练”；重做前面的四项业务检查。随后在编辑器把标题还原为原来那一行并保存。此时**不要构建**，再次刷新：正在运行的第二版标题仍有“版本演练”，因为容器使用已构建的镜像，不会自动读取宿主源码修改。

## 实际撤回第一版

```bash
# 撤回已验证的第一版，不从当前源码重建；这是产物切换，不只是重启同一容器。
RELEASE_TAG=trial-v1 docker compose --env-file .env -f deploy/compose.yaml up -d --no-build app
# 等待就绪后刷新网页，预期标题恢复，之前的测试笔记仍可读取。
curl --fail http://127.0.0.1:8000/readyz
# 查看当前应用所用镜像标签，预期为 classics-companion:trial-v1。
docker compose --env-file .env -f deploy/compose.yaml ps --format json app
```

再做四项业务检查，把前后镜像 ID、标题、笔记是否保留和开始结束时间写在项目记录中。这次证明的是同一数据结构下的镜像切换；若新版本改变资料字段或数据库结构，不能据此认定旧程序也能读取，需要第28章的迁移与恢复验证。

结束时先确认源码标题已经还原，再回到后续章节使用的 candidate：

```bash
# 恢复本次练习前的候选；下一节会继续在它的基础上构建资料发布功能。
RELEASE_TAG=candidate docker compose --env-file .env -f deploy/compose.yaml up -d --no-build app
```

## 小范围试用看什么

限制试用账号、资料与时间窗口，确认告警和联系人。收集问题后按严重程度处理：越权、错误副作用和无法恢复的数据问题先阻止扩大范围；普通表达改进可进入待办，但要有负责人。

回滚记录写原因、前后版本、开始结束时间、数据是否变化、复测结果。仅把容器重新启动不等于回滚。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 为什么回滚可能还涉及资料与数据库？
2. 只有一个镜像能完成回滚演练吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么回滚可能还涉及资料与数据库？**

旧程序可能读不懂新结构，旧 Prompt 也可能依赖旧资料字段。必须验证版本组合，必要时恢复兼容快照。

**只有一个镜像能完成回滚演练吗？**

不能证明版本切换。先保留并验证两个明确产物，再实际切回并复测。

**通过证据：**两份真实版本的切换与回退记录，以及四条业务冒烟检查。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
