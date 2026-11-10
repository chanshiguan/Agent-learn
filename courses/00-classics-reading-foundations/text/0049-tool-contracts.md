# 让越界请求有可重复的失败结果

本单元预计 **30—45 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《先由程序员调用工具，再交给模型》](0048-readonly-tools.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：为模型描述工具名与参数形状

JSON Schema 只说明能请求什么；真正的执行权限仍由 ReaderTools 检查。

**写在哪里：**项目根目录下的 `companion/tools.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
# 目的：JSON Schema 只说明能请求什么；真正的执行权限仍由 ReaderTools 检查。
# 预期：工具参数中没有 tenant 和 user，未知字段禁止。
SCHEMAS = [
    {"type": "function", "function": {"name": "search_lectures", "description": "在当前读者允许范围内查询讲稿。", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "read_source", "description": "读取本次已经检索到的一条来源。", "parameters": {"type": "object", "properties": {"source_id": {"type": "string"}}, "required": ["source_id"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "get_progress", "description": "查看当前会话的显式阅读进度。", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}},
]
```

**写完后应当怎样：**工具参数中没有 tenant 和 user，未知字段禁止。

## 让刚写的代码生效

如果上一节的服务仍在运行，先在那个终端按 Ctrl+C 停止。确认当前终端仍有模型配置，再从项目根目录重启，随后刷新浏览器。没有使用自动重载时，仅保存文件不会更新运行中的 Python 进程。

```bash
# 载入刚写完的接口、业务模块和页面；等终端显示服务启动后再进行下面的交互。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```


## 先把失败当作预期行为

工具拒绝越权参数不是系统坏了，是边界生效。把它变成测试，以后改 Prompt、模型或框架时都能重跑。


仅运行工具边界测试；PYTHONPATH 让 Python 找到课程 tests 目录，不改变已安装依赖。
再验证来源和未知进度过滤；这两项不调用真实模型，也不等于模型质量测试。


本页末尾直接调用你已经写出的工具，检查越界请求是否被拒绝。第 22 章再把这些边界写成自己的 unittest。

## 补一个自己的反例

复制一种合法调用，把工具名改成 `delete_notes`。它没有登记，预期拒绝，不应猜测你的意图后执行别的函数。再把 query 改为 501 个字符，验证长度边界。

写一张工具契约表：名称、允许参数、身份来源、可读取范围、失败行为。模型看到的描述越清楚，越容易正确选择；但真正的权限仍由程序执行。

这些工具没有写数据库的能力。第 19 章会用独立批准流程处理笔记，而不是在此处悄悄增加一个万能工具。


## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 未知工具名应怎样处理？
2. 离线测试通过能证明模型会正确用工具吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**未知工具名应怎样处理？**

明确拒绝，并把可处理的错误返回给调用方；不把字符串当代码执行。

**离线测试通过能证明模型会正确用工具吗？**

不能。它证明程序边界；真实模型能否按协议请求工具，要在第 18 章实测。

**通过证据：**两项测试结果、一个自加的越界用例和完整工具契约表。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/03-tool-use-and-hello-agent.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter4)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion import state
from companion.tools import ReaderTools
a=state.Actor("demo","reader-a");s=state.create_session(a);t=ReaderTools(a,s["id"])
for name,args in [("get_progress",{"user":"reader-b"}),("run_shell",{"command":"pwd"})]:
    try:
        t.execute(name,args);raise AssertionError("越界不应成功")
    except ValueError:pass
print("改身份与未知工具均被拒绝")
PY
```

**预期：**模型请求不会直接变成任意 Python 或终端执行。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
