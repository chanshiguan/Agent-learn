# 从测试身份切到登录账号（3/3：连接页面交互）

本单元预计 **35—50 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《从测试身份切到登录账号（2/3：把本节能力连起来）》](0056-real-accounts-02.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

上一小节已经把前一部分写进项目。这一节继续处理 `companion/web/reader.js`；先回想它接收什么、交给谁，再往下写。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：退出时同时清本地界面与服务端令牌

先捕获旧令牌发退出请求，立即清页面身份；迟到结果不能重置后来新登录的页面。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
on('logout', async () => {
  const request = api('/api/logout', 'POST');
  token = '';
  reset();
  const expectedView = viewVersion;
  $('workspace').hidden = true;
  $('login-panel').hidden = false;
  $('logout').hidden = true;
  await request;
  if (viewVersion === expectedView) status('已退出登录。');
});
```

**写完后应当怎样：**退出后旧对话消失，刷新不会自动恢复令牌。

### 第 2 步：启动时按服务端模式选择入口

不能让浏览器自行决定是否需要登录；模式来自 API 配置。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
  config = await api('/api/config');
  await enter();
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
  config = await api('/api/config');
  $('lab-notice').hidden = config.mode !== 'lab';
  $('lab-picker').hidden = config.mode !== 'lab';
  if (config.mode === 'lab') await enter();
  else {
    $('workspace').hidden = true;
    $('login-panel').hidden = false;
  }
```

**写完后应当怎样：**本机模式看见虚构读者，认证模式看见登录表单。

## 运行并观察

```bash
# 分别创建读者、家长和内容管理员；每条命令会要求输入两次至少 12 字符的口令。
python -m companion create-user student-a
python -m companion create-user parent-a --role parent
python -m companion create-user editor-a --role content_admin
# 换为真实登录模式，页面显示登录入口；测试读者请求头不再决定身份。
export APP_MODE=authenticated
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```

先以 student-a 登录创建阅读，再退出。parent-a 登录后只能查看已关联孩子明确记录的进度，不自动看到私密对话或笔记。editor-a 也不能靠角色名读取别人私人内容；内容导入仍通过受控的管理员命令行执行，本课没有公开上传后台。

## 令牌不是永久钥匙

本实现令牌有效期一小时，保存在浏览器内存，刷新后需重新登录；退出会撤销服务端令牌。口令派生、登录限流和 HTTPS 是不同层面的保护，不能互相代替。

公司上线前还需按实际身份体系决定 SSO、账号恢复、MFA、审计和用户生命周期。本课程最小账号实现用于把边界跑通，不代表已经覆盖公司身份平台。


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

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion import state,auth
state.initialize()
auth.create_user("demo","guided-reader","a-synthetic-password-123")
t=auth.login("demo","guided-reader","a-synthetic-password-123","test")
assert auth.authenticate(t["access_token"]).user=="guided-reader"
auth.logout(t["access_token"])
try:
    auth.authenticate(t["access_token"]);raise AssertionError("退出令牌应失效")
except PermissionError:print("登录与撤销通过")
PY
```

**预期：**使用合成测试账号验证行为；正式口令按交互命令输入。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
