# 用权限表查出遗漏的入口

本单元预计 **55—70 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《从测试身份切到登录账号（3/3：连接页面交互）》](0056-real-accounts-03.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 页面藏按钮不等于授权

浏览器可以直接发请求。即使按钮没显示，服务端也必须检查身份。用两个独立浏览器会话登录 student-a 与另一个测试读者，别只在一个窗口里切页面。

建立权限表：本人会话、别人的会话、本人笔记、别人的笔记、同租户资料、其他租户资料、已关联孩子进度、未关联孩子进度。每格写允许或拒绝，再记录实际状态码。


检查本地权限实现：他人会话不能读取、家长只得到显式进度、退出后的令牌不能再用。


这次先用真实登录和接口请求逐格检查，记录账号角色、操作、预期与实际状态码。用浏览器 Network 的“编辑并重新发送”把会话 ID 换成另一个人的 ID，应返回拒绝。截图和报告中遮住 Authorization，不复制令牌到工单。第 22 章开始写自动测试时，可以从这张矩阵选出能够稳定复现的边界；手工观察与自动测试要分别记录。

## 检查容易遗漏的出口

来源接口、待确认草稿、恢复任务都要验证归属。当前没有公共“导出全部数据”接口，也没有回答缓存，所以不要声称这些功能已经通过；如果以后新增，必须把它们加到同一权限表。

Embedding 缓存只处理资料文本，当前不缓存私人问题和回答；它也包含资料表示，磁盘仍需要受保护。不能因为它不是明文全文就当作无敏感信息。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：先验证两侧角色，再保存家庭关联

家长角色不能自动查看任意孩子；管理员还需要在线下核实关系。

**写在哪里：**项目根目录下的 `companion/auth.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：家长角色不能自动查看任意孩子；管理员还需要在线下核实关系。
# 预期：只有已关联的家长能读取该孩子的显式进度。
def link_family(tenant, parent, child):
    with connect() as db:
        roles = dict(db.execute("SELECT username,role FROM users WHERE tenant=? AND username IN (?,?)", (tenant, parent, child)).fetchall())
        if roles.get(parent) != "parent" or roles.get(child) != "reader":
            raise ValueError("先创建本租户家长和读者账号。管理员应在线下核对关联关系。")
        db.execute("INSERT OR IGNORE INTO families VALUES(?,?,?)", (tenant, parent, child))
```

**写完后应当怎样：**只有已关联的家长能读取该孩子的显式进度。

### 第 2 步：只返回家长需要的进度字段

关联不代表可读私密聊天；查询列仅包含作品和进度。

**写在哪里：**项目根目录下的 `companion/state.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：关联不代表可读私密聊天；查询列仅包含作品和进度。
# 预期：响应中没有 history 或笔记正文。
def family_report(actor, child):
    with connect() as db:
        linked = db.execute("SELECT 1 FROM families WHERE tenant=? AND parent=? AND child=?", (actor.tenant, actor.user, child)).fetchone()
        if actor.role != "parent" or not linked:
            raise PermissionError("没有已确认的家长关联。")
        # 家长仅查看显式进度，不自动读取孩子的私密对话或笔记。
        return [dict(r) for r in db.execute("SELECT book,progress FROM sessions WHERE tenant=? AND owner=?", (actor.tenant, child))]
```

**写完后应当怎样：**响应中没有 history 或笔记正文。

### 第 3 步：把家庭进度接到经过验证的身份

复用 Actor 与关联检查，不接受页面自己声称的家长角色。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：复用 Actor 与关联检查，不接受页面自己声称的家长角色。
# 预期：未关联或非家长请求被拒绝。
@app.get("/api/family/{child}")
def family(child: str, who=Depends(actor)):
    return state.family_report(who, child)
```

**写完后应当怎样：**未关联或非家长请求被拒绝。

### 第 4 步：给管理员一个明确的关联操作

关联需要单独动作，不在用户注册或模型回答时自动推断。

**写在哪里：**项目根目录下的 `companion/family_cli.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

```python
# 目的：关联需要单独动作，不在用户注册或模型回答时自动推断。
# 预期：命令成功后仅开放已约定进度字段。
import argparse
from .state import initialize
from .auth import link_family


def main():
    parser=argparse.ArgumentParser(description="管理员核实后关联家长与读者")
    parser.add_argument("parent");parser.add_argument("child")
    parser.add_argument("--tenant",default="demo")
    args=parser.parse_args();initialize();link_family(args.tenant,args.parent,args.child)
    print("关联已保存；只授权读取显式进度。")
```

**写完后应当怎样：**命令成功后仅开放已约定进度字段。

### 第 5 步：给命令入口增加 link-family

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        main('create-user')
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        main('create-user')
    elif command == "link-family":
        from .family_cli import main
        main()
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。

### 第 6 步：读取进度时继续检查页面代次

迟到的家庭报告同样可能出现在错误登录页面，不能只保护聊天内容。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
on('family', async () => {
  const expectedView = viewVersion;
  const result = await api('/api/family/' + encodeURIComponent($('child').value));
  if (viewVersion === expectedView)
    $('family-result').textContent = JSON.stringify(result, null, 2);
});
```

**写完后应当怎样：**换账号后的旧进度响应被丢弃。

### 第 7 步：退出或换人时清除家庭报告

不仅聊天，任何带个人归属的数据都需要清除旧视图。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
  $('drafts').replaceChildren();
  $('notes').replaceChildren();
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
  $('drafts').replaceChildren();
  $('notes').replaceChildren();
  $('family-result').textContent = '';
```

**写完后应当怎样：**新账号不会看见前一账号的家庭进度。


## 让刚写的代码生效

如果上一节的服务仍在运行，先在那个终端按 Ctrl+C 停止。确认当前终端仍有模型配置，再从项目根目录重启，随后刷新浏览器。没有使用自动重载时，仅保存文件不会更新运行中的 Python 进程。

```bash
# 载入刚写完的接口、业务模块和页面；等终端显示服务启动后再进行下面的交互。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```


## 运行并观察

```bash
# 只关联自己创建的虚构测试账号；下一次家长查询才能读取该学生的显式进度。
python -m companion link-family parent-a student-a
```

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 内容管理员能否绕过 owner 检查？
2. 不存在的导出接口应该记“通过”吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**内容管理员能否绕过 owner 检查？**

不能。内容管理职责不自动带来读取所有私人对话与笔记的权限。

**不存在的导出接口应该记“通过”吗？**

应记未实现/不适用，并写明新增时必须验收的隔离要求；不能用缺少功能冒充完成测试。

**通过证据：**一张有实际状态码的逐入口权限矩阵，至少两次真实登录下的越权拒绝，以及关联前后家长查询的对照。本单元尚未编写自动权限测试，不把手工记录标成自动通过。

</details>

## 下次开始前

下次从权限矩阵挑一个拒绝项，先预测状态码，再用两个虚构账号核对。回想“身份已登录”和“家庭关系已核实”为什么是两件事。把具体请求步骤保留好，后面编写回归时才能把观察变成可重复断言。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
