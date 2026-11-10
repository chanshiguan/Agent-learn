# 重复点击、过期与换人都要试

本单元预计 **45—60 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《先预览一份笔记，确认后再保存（3/3：连接页面交互）》](0052-write-drafts-03.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：让修改后的草稿需要重新确认

修改正文同时递增版本、更新摘要与有效期；旧确认不能批准新内容。

**写在哪里：**项目根目录下的 `companion/actions.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**SQL 语句处理持久记录；问号占位符把值作为数据传入。`with` 管理事务，代码抛错时不要把半次更新当作成功。

```python
# 目的：修改正文同时递增版本、更新摘要与有效期；旧确认不能批准新内容。
# 预期：旧 revision/digest 失败，新预览可以确认。
def revise(actor, identity, body):
    if not isinstance(body, str) or not 1 <= len(body.strip()) <= 6000:
        raise ValueError("草稿长度需为 1—6000 字符。")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM actions WHERE id=? AND tenant=? AND owner=? AND status='pending'", (identity, actor.tenant, actor.user)).fetchone()
        if row is None:
            raise PermissionError("没有可修改的本人草稿。")
        db.execute("UPDATE actions SET body=?,digest=?,revision=revision+1,expires=? WHERE id=?",
                   (body, digest([row["kind"], body]), time.time() + 900, identity))
        return dict(db.execute("SELECT * FROM actions WHERE id=?", (identity,)).fetchone())
```

**写完后应当怎样：**旧 revision/digest 失败，新预览可以确认。

### 第 2 步：接入草稿修改接口

只允许本人修改 pending 状态的内容，已经提交的笔记不通过此入口重写。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 目的：只允许本人修改 pending 状态的内容，已经提交的笔记不通过此入口重写。
# 预期：编辑后需要重新预览。
class Revision(Input):
    body: str = Field(min_length=1, max_length=6000)
```

**写完后应当怎样：**编辑后需要重新预览。

### 第 3 步：接入草稿修改接口

只允许本人修改 pending 状态的内容，已经提交的笔记不通过此入口重写。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：只允许本人修改 pending 状态的内容，已经提交的笔记不通过此入口重写。
# 预期：编辑后需要重新预览。
@app.patch("/api/drafts/{identity}")
def revise(identity: str, body: Revision, who=Depends(actor)):
    return actions.revise(who, identity, body.body)
```

**写完后应当怎样：**编辑后需要重新预览。

### 第 4 步：开放编辑并要求先保存修改

页面文本变了但还没保存时不能点确认；保存后重新取得服务端版本与摘要。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
    edit.hidden = true;
    text.readOnly = true;
```

</details>

**先理解：**这里用元素 ID 找到控件，再设置文字、状态或事件。函数名后带括号才是调用；注册事件后，要等点击或提交时才运行。

**写完后应当怎样：**修改草稿后只能确认当前版本。

### 第 5 步：开放编辑并要求先保存修改

页面文本变了但还没保存时不能点确认；保存后重新取得服务端版本与摘要。

**写在哪里：**项目根目录下的 `companion/web/reader.js`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```javascript
    approve.textContent = '确认保存这一版';
```

</details>

**先理解：**`async` 函数在等待网络时可以暂停；`await` 后面完成了，才继续处理返回值。页面还要核对当前读者，等待期间换人会使旧结果失效。

```javascript
    approve.textContent = '确认保存这一版';
    edit.onclick = async () => {
      const actionView = viewVersion;
      try {
        await api('/api/drafts/' + draft.id, 'PATCH', { body: text.value });
        if (viewVersion !== actionView) return;
        await refreshNotes();
        if (viewVersion === actionView) status('草稿已修改，请重新阅读后确认。');
      } catch (e) {
        if (viewVersion === actionView) status(e.message);
      }
    };
```

**写完后应当怎样：**修改草稿后只能确认当前版本。

## 先理解幂等

同一个已确认动作提交两次，结果应与提交一次相同。这里把动作 ID 也作为笔记 ID，写笔记与标记 committed 放进同一个 SQLite 事务；中途失败一起回滚，不留下“状态说成功，内容却没保存”的半成品。

草稿还带 revision、内容 digest 和 15 分钟有效期。它们分别防止用旧版本批准、确认内容被替换、长期挂起的批准被误用。内容摘要不是签名，也不替代身份认证。


用临时数据重复验证旧版批准、越权批准、重复提交和过期；不写入你的实际笔记库。


手动再做一次：批准同一草稿两次，notes 应只多一条。创建新草稿后不确认，等过期或在独立测试数据里调整 expires，再批准应失败。不要修改真实业务库时间来做实验。

## 分清本章保证的范围

同一 SQLite 事务能保护本地两次写入；如果未来动作变为外部发送消息或支付，数据库事务不能撤回已发生的外部副作用。那时需要外部幂等键、投递状态与补偿设计，不能直接照搬一句“失败就重试”。

保留动作预览、批准版本和最终笔记 ID。日志中记录状态，不写完整私人笔记正文。下一章在进程重启后继续同一批准流程。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 事务和幂等分别解决什么？
2. 过期后能自动延长原批准吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**事务和幂等分别解决什么？**

事务防止一次动作部分写入；幂等防止同一动作重试造成重复副作用。两者不能互相替代。

**过期后能自动延长原批准吗？**

不能。应重新查看当前内容并取得新的确认，避免用很久以前的意图执行现在的动作。

**通过证据：**测试通过记录与手动重复提交后的单条笔记；能说明外部副作用不在本地事务保证内。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/03-tool-use-and-hello-agent.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion import state,actions
a=state.Actor("demo","reader-a")
d=actions.draft(a,"note","旧正文","revision-test")
n=actions.revise(a,d["id"],"新正文")
try:
    actions.approve(a,d["id"],d["revision"],d["digest"],True);raise AssertionError("旧预览不应通过")
except ValueError:pass
r=actions.approve(a,n["id"],n["revision"],n["digest"],True)
assert actions.approve(a,n["id"],n["revision"],n["digest"],True)["replayed"] is True
print("旧预览拒绝，重复批准不重复写入")
PY
```

**预期：**确认内容与版本绑定，重放不会产生重复笔记。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
