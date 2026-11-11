# 名著 AI 伴读助手：公开实战课程

从五份新编《狂人日记》讲解稿开始，学习 Python、Docker、本地或线上模型，再逐步完成 RAG、启发式伴读、可控 Agent，以及上线评审所需的权限、评测和运维练习。

**开始学习：**打开[课程网站](https://chanshiguan.github.io/Agent-learn/)，从导学创建空目录开始。全课为导学加 29 章、80 个连续练习单元和 16 篇选读，主线约 57—77 小时；安装、下载和公司审核另计。所有程序、依赖清单和部署文件都在单元中逐步带写，说明目的、位置、运行方式和预期结果；验收题附折叠答案。只有五份讲稿需要单独下载。

这是一套通用课程，不依赖编写者的电脑环境。命令以 macOS 的 Bash/Zsh 为主；M1 16 GB 是本地路线的参考设备，性能须自行测量。线上与本地生成路线共用项目代码。课程网站是静态教材，实际 Python 伴读服务在学习环境中运行。

## 知识库有什么

[公开样本及来源](courses/00-classics-reading-foundations/public-materials/README.md)包含五篇新编正文、Word 文件的生成说明和人工参考答案。素材明确区分原著短引句与课程解释，不提供未经核对的纸质页码。

课程保留原题与七阶段目标，较大的带写任务拆成连续小节；样本换成新稿后，证据短句、来源文件名和预期计数已经同步更新。真实模型、向量索引、API 与 Agent 的运行结果和失败记录见[验证范围](courses/00-classics-reading-foundations/VERIFICATION.md)，问题与修复见[审查记录](courses/00-classics-reading-foundations/REVIEW.md)。目标设备性能和公司上线仍需按课程自行验收。

## 放到 GitHub 时使用哪个目录

本目录是一份独立的公开导出。建立 GitHub 仓库时，以本目录为仓库根目录；不要把它外面的私人工作区一起上传，也不要复制原工作区的 `.git` 历史。

本目录包含课程正文、示例代码、公开新编样本与验证记录；不包含私人原讲稿、个人学习档案、原课程压缩包、模型权重、密钥或业务数据库。现有忽略规则允许五份公开 DOCX，其他运行数据仍排除。以后加入的真实公司资料、读者信息和日志应继续留在数据目录。

公开维护分支为 `codex/public-course`。[课程网站](https://chanshiguan.github.io/Agent-learn/)由 GitHub Actions 验证业务测试、Docker/Compose、样本白名单和构建后部署，失败时保留上一版网站。Pages 只展示教材，不能替代第 13 章起需要启动的 Python API 服务。生成模型的 API key 仍由后端读取，不写进网页。

## 修改后怎样重新生成

普通学习者不需要构建页面，也不需要提前安装全部课程依赖。维护课程时，在实际开发电脑完成以下步骤：

```bash
# 在仓库根目录安装指定版本的页面构建依赖；生成 node_modules，不会启动模型或部署网站。
npm ci --ignore-scripts
# 用 Markdown 和示例源码更新 HTML，保留课程的相对链接与页面样式。
npm run build
```

以下仅供维护者：修改五篇公开正文后，在仓库的 `courses/00-classics-reading-foundations/examples/` 中运行：

```bash
# 将修改后的公开材料生成为新的空目录，避免覆盖已有练习数据；核对后再替换输入。
python prepare_samples.py --output data/review-input
```

维护者确认新输入后，需要重新运行评测并更新讲义中的字符数、切块数和证据说明。不要继续引用本版旧成绩。`publication-files.json` 是公开文件白名单；新增公开文件时显式添加相对路径，再在课程目录运行：

```bash
# 只检查公开清单、样本来源、页面链接和命令语法；不生成代码包。
python tooling/verify_public.py
# 从五份输入开始，复演页面的全部代码编辑及当前模块导入，核对中途和最终状态。
python tooling/replay_writing.py
```

测试命令在课程目录执行，先安装各章节所需依赖：

```bash
# 检查离线业务边界和公开样本保护；测试替身不代表真实模型效果。
python -m unittest discover -s tests -v
```

技术主线依据 [awesome-agentic-ai-zh](https://github.com/WenyuChiou/awesome-agentic-ai-zh) 和 [Hello-Agents](https://github.com/datawhalechina/hello-agents)，文学核对与选读另在来源页列明。没有把第三方项目、文库或依赖的许可改为本项目许可；公开可见也不等于所有第三方材料可任意再分发。

主机环境统一为全局Python3.12，软件优先用Homebrew安装，各章不创建项目虚拟环境。Python库用同一解释器的pip安装到当前账号；Docker练习使用3.12系列镜像，运行位置与包目录的区别在第2章说明。
