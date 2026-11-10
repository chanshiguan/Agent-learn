# 用权限表查出遗漏的入口

本单元预计 **35—50 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 页面藏按钮不等于授权

浏览器可以直接发请求。即使按钮没显示，服务端也必须检查身份。用两个独立浏览器会话登录 student-a 与另一个测试读者，别只在一个窗口里切页面。

建立权限表：本人会话、别人的会话、本人笔记、别人的笔记、同租户资料、其他租户资料、已关联孩子进度、未关联孩子进度。每格写允许或拒绝，再记录实际状态码。

```bash
# 检查本地权限实现：他人会话不能读取、家长只得到显式进度、退出后的令牌不能再用。
PYTHONPATH=../tests python -m unittest test_companion.CompanionTests.test_api_scope_and_password_not_echoed test_companion.CompanionTests.test_family_sees_progress_only test_companion.CompanionTests.test_auth_token_revocation -v
```

这些自动测试验证函数和 API 边界；还要用真实登录模式在页面上重复操作。用浏览器 Network 的“编辑并重新发送”把会话 ID 换成另一个人的 ID，应返回拒绝。截图和报告中遮住 Authorization，不复制令牌到工单。

## 检查容易遗漏的出口

来源接口、待确认草稿、恢复任务都要验证归属。当前没有公共“导出全部数据”接口，也没有回答缓存，所以不要声称这些功能已经通过；如果以后新增，必须把它们加到同一权限表。

Embedding 缓存只处理资料文本，当前不缓存私人问题和回答；它也包含资料表示，磁盘仍需要受保护。不能因为它不是明文全文就当作无敏感信息。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 内容管理员能否绕过 owner 检查？
2. 不存在的导出接口应该记“通过”吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**内容管理员能否绕过 owner 检查？**

不能。内容管理职责不自动带来读取所有私人对话与笔记的权限。

**不存在的导出接口应该记“通过”吗？**

应记未实现/不适用，并写明新增时必须验收的隔离要求；不能用缺少功能冒充完成测试。

**通过证据：**一张逐入口权限矩阵、自动测试记录和至少两次真实登录下的越权拒绝。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
