# 把这次能跑的条件记录下来

本单元预计 **35—50 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## “我这儿能跑”缺了哪些条件

同样源码配不同依赖、模型、Prompt 或资料，行为可能不同。候选版本至少记录程序提交、依赖、镜像摘要、Prompt 版本、模型配置、资料 revision 和索引版本。凭据不能混进清单。

```bash
# 执行自动行为检查，先挡住确定的回归。
python -m unittest discover -s ../tests -v
# 记录当前依赖与资料/索引指纹；输出不包含模型密钥。
python -m companion manifest
# 若候选运行在 Compose 中，再记录容器里的实际依赖；它可能与主机环境不同。
docker compose -f deploy/compose.yaml run --rm app python -m companion manifest
# 保存实际解析后的依赖版本，便于在相同平台重建；跨平台仍要重新安装验证。
python -m pip freeze > data/live/requirements-resolved.txt
# 记录候选镜像的实际标识，不只写容易被覆盖的 candidate 标签。
docker image inspect classics-companion:candidate --format '{{.Id}}'
```

检查 `release-manifest.json` 的 packages 中是否有 null；没有安装的组件要明确说明，不假装环境完整。课程文件标注的直接依赖版本与 pip freeze 的完整依赖是两个层次。

## 把检查搬到自动流程

配套 `deploy/ci.example.yml` 提供 GitHub Actions 示例。若把本课程目录作为独立练习仓库，把它放到该仓库 `.github/workflows/check.yml`。它安装依赖并运行行为测试，不需要模型密钥，不进行发布；真实模型评阅和公司审批仍是独立证据。

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
