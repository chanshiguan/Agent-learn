# 从测试身份切到登录账号（2/3：把本节能力连起来）

本单元预计 **55—70 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《从测试身份切到登录账号（1/3：保存会话状态）》](0056-real-accounts.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

上一小节已经把前一部分写进项目。这一节继续处理 `companion/__main__.py`；先回想它接收什么、交给谁，再往下写。

## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：给命令入口增加 create-user

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        from .graph_cli import main
        main()
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        from .graph_cli import main
        main()
    elif command == "create-user":
        from .accounts_cli import main
        main('create-user')
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。

### 第 2 步：在认证章节才引入 auth

前面已经理解归属，现在用可信的登录身份替换本机测试身份。

**写在哪里：**项目根目录下的 `companion/app.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from . import service, state, actions
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from . import service, state, actions, auth
```

**写完后应当怎样：**普通业务函数仍使用相同 Actor，不需要重写归属 SQL。

### 第 3 步：区分本机练习与登录模式

两种模式有明确边界；生产环境不能因为忘记配置就继续相信测试读者头。

**写在哪里：**项目根目录下的 `companion/app.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
MODE = "lab"
CHAPTER = 19
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
MODE = os.environ.get("APP_MODE","lab")
CHAPTER = int(os.environ.get("COURSE_CHAPTER","21"))
if MODE not in {"lab","authenticated"}:
    raise ValueError("APP_MODE 只能是 lab 或 authenticated。")
if os.environ.get("APP_ENV")=="production" and MODE!="authenticated":
    raise ValueError("生产配置禁止测试身份。")
```

**写完后应当怎样：**生产配置加 lab 会在启动时失败。

### 第 4 步：让身份只由验证过的令牌决定

认证模式忽略 X-Lab-Reader；客户端不能通过另一个字段覆盖本人身份。

**写在哪里：**项目根目录下的 `companion/app.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    raise HTTPException(403,"当前只支持本机测试身份。")
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    bearer = request.headers.get("Authorization", "")
    if not bearer.startswith("Bearer "):
        raise HTTPException(401, "请先登录。")
    return auth.authenticate(bearer[7:])
```

**写完后应当怎样：**未登录返回401，无效令牌不能访问私人记录。

### 第 5 步：连接 Login 登录入口

输入格式、账号校验和令牌撤销分别负责，错误不回显原口令。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 目的：输入格式、账号校验和令牌撤销分别负责，错误不回显原口令。
# 预期：登录成功取得短期令牌，退出后令牌失效。
class Login(Input):
    tenant: str = Field(min_length=1, max_length=40)
    username: str = Field(min_length=1, max_length=40)
    password: str = Field(min_length=1, max_length=128)
```

**写完后应当怎样：**登录成功取得短期令牌，退出后令牌失效。

### 第 6 步：连接 login 登录入口

输入格式、账号校验和令牌撤销分别负责，错误不回显原口令。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：输入格式、账号校验和令牌撤销分别负责，错误不回显原口令。
# 预期：登录成功取得短期令牌，退出后令牌失效。
@app.post("/api/login")
def login(body: Login, request: Request):
    if MODE != "authenticated":
        raise HTTPException(409, "当前是本机练习模式。")
    return auth.login(body.tenant, body.username, body.password, request.client.host if request.client else "unknown")
```

**写完后应当怎样：**登录成功取得短期令牌，退出后令牌失效。

### 第 7 步：连接 logout 登录入口

输入格式、账号校验和令牌撤销分别负责，错误不回显原口令。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：输入格式、账号校验和令牌撤销分别负责，错误不回显原口令。
# 预期：登录成功取得短期令牌，退出后令牌失效。
@app.post("/api/logout")
def logout(request: Request, who=Depends(actor)):
    auth.logout(request.headers.get("Authorization", "")[7:])
    return {"logged_out": True}
```

**写完后应当怎样：**登录成功取得短期令牌，退出后令牌失效。

### 第 8 步：增加登录表单与退出入口

令牌只放页面内存，口令输入后清空；家庭进度区先隐藏，下一单元才验证关联。

**写在哪里：**项目根目录下的 `companion/web/index.html`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```html
    </div>
```

</details>

**先理解：**标签确定页面结构，id 让后面的 JavaScript 找到同一个控件。label 关联输入框；hidden 只是隐藏显示，不负责服务端权限。

```html
    </div>
    <section id="login-panel" hidden>
      <h1>登录你的阅读账号</h1>
      <form id="login-form">
        <label>机构<input name="tenant" value="demo" required maxlength="40" /></label>
        <label
          >账号<input name="username" autocomplete="username" required maxlength="40"
        /></label>
        <label
          >口令<input
            name="password"
            type="password"
            autocomplete="current-password"
            required
            maxlength="128"
        /></label>
        <button>登录</button>
      </form>
    </section>
    <button id="logout" hidden>退出登录</button>
    <section id="family-panel" hidden>
      <h2>孩子明确记录的进度</h2>
      <label for="child">已关联账号</label><input id="child" /><button id="family">
        查看进度
      </button>
```

```html
      <pre id="family-result"></pre>
    </section>
```

**写完后应当怎样：**认证模式先显示登录表单，刷新后需重新登录。

### 第 9 步：登录成功后再进入工作区

切换界面不等于登录，只有服务端认证成功才设置 token 并加载本人数据。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
async function enter() {
  const expectedView = viewVersion;
```

</details>

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
async function enter() {
  const expectedView = viewVersion;
  $('login-panel').hidden = true;
```

**写完后应当怎样：**新登录收到的数据不会与旧登录混合。

### 第 10 步：登录成功后再进入工作区

切换界面不等于登录，只有服务端认证成功才设置 token 并加载本人数据。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
  $('workspace').hidden = false;
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

```javascript
  $('workspace').hidden = false;
  $('logout').hidden = config.mode === 'lab';
```

**写完后应当怎样：**新登录收到的数据不会与旧登录混合。

### 第 11 步：给登录请求也加迟到响应检查

连续两次登录时，第一个慢响应不能覆盖后来的账号；返回后核对视图代次。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
  });
}
```

</details>

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
  });
}

$('login-form').onsubmit = async (event) => {
  event.preventDefault();
  const expectedView = ++viewVersion;
  try {
    const values = Object.fromEntries(new FormData(event.target));
    const result = await api('/api/login', 'POST', values);
    if (viewVersion !== expectedView) return;
    token = result.access_token;
    event.target.password.value = '';
    $('family-panel').hidden = result.role !== 'parent';
    await enter();
    if (viewVersion === expectedView) status('已登录。');
  } catch (e) {
    if (viewVersion === expectedView) status(e.message);
  }
};
```

**写完后应当怎样：**旧登录结果被丢弃，口令输入框清空。

## 在这里停一下，检查刚写的部分

```bash
# 只检查本节已写文件的语法；成功通常没有输出，不代表模型或完整页面已经运行。
python -m py_compile companion/__main__.py companion/app.py
```

先不看说明，说出本节最后一步为什么要做、写完以后哪件事应当发生。

<details class="answer-key"><summary>参考答案与下一步</summary>

连续两次登录时，第一个慢响应不能覆盖后来的账号；返回后核对视图代次。 旧登录结果被丢弃，口令输入框清空。 这次停点只检查当前文件；整条链路会在本组最后一节运行。

</details>

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
