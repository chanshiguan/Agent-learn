# 从测试身份切到登录账号

本单元预计 **40—55 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 先确认是谁，再判断能做什么

认证回答“你是谁”，授权回答“你能读写哪些内容”。之前有授权检查但身份可由测试请求头选择，这次换成登录后签发的短期令牌。口令不存明文，令牌在数据库也只存摘要。

先关闭服务。以下使用虚构账号，不录入真实学生姓名；输入口令时终端不回显，避免口令出现在命令历史。

```bash
# 分别创建读者、家长和内容管理员；每条命令会要求输入两次至少 12 字符的口令。
python -m companion create-user student-a
python -m companion create-user parent-a --role parent
python -m companion create-user editor-a --role content_admin
# 在实际产品中先核实家长关系；此处只关联自己创建的虚构测试账号。
python -m companion link-family parent-a student-a
# 换为真实登录模式，页面显示登录入口；测试读者请求头不再决定身份。
export APP_MODE=authenticated
export COURSE_CHAPTER=21
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```

先以 student-a 登录创建阅读，再退出。parent-a 登录后只能查看已关联孩子明确记录的进度，不自动看到私密对话或笔记。editor-a 也不能靠角色名读取别人私人内容；内容导入仍通过受控的管理员命令行执行，本课没有公开上传后台。

## 令牌不是永久钥匙

本实现令牌有效期一小时，保存在浏览器内存，刷新后需重新登录；退出会撤销服务端令牌。口令派生、登录限流和 HTTPS 是不同层面的保护，不能互相代替。

公司上线前还需按实际身份体系决定 SSO、账号恢复、MFA、审计和用户生命周期。本课程最小账号实现用于把边界跑通，不代表已经覆盖公司身份平台。

## 对照完整实现

先读上面标出的函数，再展开文件。配套包已包含它及依赖文件；不需要把后续章节一起学完。注释重点解释为什么这样处理，以及出错时应发生什么。

<details><summary>展开本单元完整源码：companion/auth.py</summary>

{{code:companion/auth.py}}

</details>

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 家长身份是否意味着能看孩子全部数据？
2. 刷新后需要重新登录是错误吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**家长身份是否意味着能看孩子全部数据？**

不意味着。这里仅允许已核实关联的显式进度，私密对话和笔记仍归本人。

**刷新后需要重新登录是错误吗？**

这是本课程把令牌只存内存的取舍；持久登录需要另外评估安全存储与会话策略。

**通过证据：**三种角色的真实登录与越权尝试记录，明确哪些公司身份能力尚待接入。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
