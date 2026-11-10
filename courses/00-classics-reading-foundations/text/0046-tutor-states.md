# 让读者先说理解，再给提示

本单元预计 **50—65 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《把进度限制贯穿检索和回答》](0045-spoiler-safe-mode.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 先把教学节奏写清楚

自动回答会让读者很快拿到结论，却未必练到阅读。先用三个明确状态：question 提一个开放问题；hint 听到理解后给一级提示；explain 根据读者具体问题检索并解释。状态机就是“当前在哪一步、收到输入后去哪一步”的约定。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：先写这个文件需要的导入

先写固定三阶段伴读，观察教学效果后再决定是否需要 Agent 自主安排。

**写在哪里：**项目根目录下的 `companion/tutor.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 目的：先写固定三阶段伴读，观察教学效果后再决定是否需要 Agent 自主安排。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
from .rag import answer, retrieve
from .state import get_session
```

**写完后应当怎样：**保存后只有导入和定义；导入它不会自动运行整个业务。

### 第 2 步：按 question、hint、explain 推进一次伴读

先邀请读者表达，再追问证据，最后用已实现的有据回答核对；阶段更新交给服务层保存。

**写在哪里：**项目根目录下的 `companion/tutor.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：先邀请读者表达，再追问证据，最后用已实现的有据回答核对；阶段更新交给服务层保存。
# 预期：前两步是明确教学话术，不冒充模型思考或文学评分。
def teach_turn(actor, session_id, text, method="keyword", direct=False):
    session = get_session(actor, session_id)
    if direct:
        hits = retrieve(text, actor.tenant, session["book"], method, session["progress"] if session["strict"] else None)
        return answer(text, hits, strict=bool(session["strict"]))
    phase = session["phase"]
    if phase == "question":
        result = {"answer": "从刚读到的讲稿中选一句你印象深的内容：你怎样理解它？请先说理由，也可以提出不同看法。", "sources": [], "citations": []}
        changes = {"history": [], "phase": "hint"}
    elif phase == "hint":
        result = {"answer": "先把你的看法和证据分开：是哪几个词让你这样想？它们有没有别的解释？下一步输入你想核对的具体问题。", "sources": [], "citations": []}
        changes = {"history": [{"role": "user", "content": text}], "phase": "explain"}
    else:
        hits = retrieve(text, actor.tenant, session["book"], method, session["progress"] if session["strict"] else None)
        result = answer(text, hits, history=[] if session["strict"] else session["history"], strict=bool(session["strict"]))
        changes = {"history": [], "phase": "question"}
    return {**result, "next_phase": changes["phase"], "state_changes": changes}
```

**写完后应当怎样：**前两步是明确教学话术，不冒充模型思考或文学评分。

### 第 3 步：让普通问答与伴读共用状态保存

同一会话可以选择不同模式，但一次请求只执行一条流程。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
from .rag import retrieve, answer
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
from .rag import retrieve, answer
from .tutor import teach_turn
```

**写完后应当怎样：**新增 tutor 模式不会改变 qa 的默认行为。

### 第 4 步：允许已经实现的第二种模式

模式列表与实际实现同步，不接受尚未写出的 agent。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    if mode != "qa":
        raise ValueError("本阶段只实现普通问答。")
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    if mode not in {"qa","tutor"}:
        raise ValueError("当前只支持问答和固定伴读。")
```

**写完后应当怎样：**无效模式明确失败。

### 第 5 步：保存伴读状态，再回给页面

teach_turn 只产生状态变化，由服务层在版本检查下提交，避免并发互相覆盖。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    session=get_session(actor,session_id)
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    session=get_session(actor,session_id)
    if mode == "tutor":
        result=teach_turn(actor,session_id,question,method)
        updated=update_session(actor,session,**result.pop("state_changes"))
        return {**result,"trace_id":request_id,"session_revision":updated["revision"]}
```

**写完后应当怎样：**一次回答之后，下一次请求接着正确阶段进行。

### 第 6 步：在输入协议中开放 tutor

页面选项、API 校验与实际业务函数必须一起更新。

**写在哪里：**项目根目录下的 `companion/app.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    mode: Literal["qa"] = "qa"
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    mode: Literal["qa", "tutor"] = "qa"
```

**写完后应当怎样：**tutor 通过校验，agent 仍被拒绝。

### 第 7 步：让读者主动选择伴读方式

不强迫所有问题进入同一套教学话术，普通问答入口继续保留。

**写在哪里：**项目根目录下的 `companion/web/index.html`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```html
          <option value="qa">直接解答</option>
```

</details>

**先理解：**标签确定页面结构，id 让后面的 JavaScript 找到同一个控件。label 关联输入框；hidden 只是隐藏显示，不负责服务端权限。

```html
          <option value="qa">直接解答</option>
          <option value="tutor">先说理解，再看提示</option>
```

**写完后应当怎样：**页面可以选择 qa 或 tutor。


## 运行并观察

```bash
# 保存刚写的伴读实现后重启；预期模式列表出现启发式伴读。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```

停止上一服务再执行启动命令，避免端口占用。新建阅读，选择启发式伴读，按三轮输入：

1. “我想讨论文言文序言。”预期先得到开放问题。
2. “我觉得文言文听起来离读者更远，因为它像别人替他写的介绍。”预期得到找关键词、考虑另一种解释的提示。
3. “讲稿怎样说明序言与日记的关系？”预期检索讲稿后解释，并回到 question 状态。

前两步是固定教师提示，不假装模型已经精确诊断学生能力。第三步才调用生成；受限阅读开启时仍只展示允许证据。阶段变化和对话写入在请求成功且未取消后才提交。

## 读一小段代码

看 `teach_turn()` 的 phase 分支。它返回 `state_changes`，由服务层在检查请求后保存。把计算与提交分开，是为了防止“读者取消了，教学状态却偷偷前进”。下一章的工具动作也会遇到这个问题。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 状态机和 Agent 自主决策有什么区别？
2. 本章是否已经实现个性化能力诊断？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**状态机和 Agent 自主决策有什么区别？**

状态机的下一步由预先约定的规则决定；Agent 可以请求工具并根据结果继续行动。本章先把稳定的教学节奏做出来。

**本章是否已经实现个性化能力诊断？**

没有。前两步是固定提示，第三步有据解释；不能据三轮对话判断学生真实水平。

**通过证据：**三轮输入、对应阶段和最终来源；能画出 question→hint→explain→question。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter9)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion import state,service
state.initialize();a=state.Actor("demo","reader-a");s=state.create_session(a)
r=service.ask(a,s["id"],"我想讨论叙述者","1"*32,mode="tutor")
assert r["next_phase"]=="hint"
r=service.ask(a,s["id"],"我觉得他并不总可靠","2"*32,mode="tutor")
assert r["next_phase"]=="explain"
print("前两步固定流程已推进；解释阶段需真实模型")
PY
```

**预期：**先邀请理解，再提示找证据，不抢先给出完整解释。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
