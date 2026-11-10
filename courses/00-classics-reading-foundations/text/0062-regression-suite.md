# 自动检查行为，不假装评完文学

本单元预计 **40—55 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《把一次模型调用拆成时间和用量》](0061-latency-cost.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 给测试分三层

第一层是确定行为：权限、引用 ID、批准、状态与恢复。第二层是真实模型效果：有据解释、无答案、不同问法、工具调用。第三层是真实使用：学生是否知道下一步、家长能否核对、失败是否可理解。三层需要不同证据。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：把已经理解的三种失败写成回归

测试描述业务结果：旧更新不能覆盖、重复确认不重复写、旧预览不能批准新内容。

**写在哪里：**项目根目录下的 `tests/test_workflow.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

下面 2 段按顺序组成同一处代码。每段最多 25 行；保留空行和缩进，全部写完并保存后再检查。

**连续代码 1/2**

```python
# 目的：测试描述业务结果：旧更新不能覆盖、重复确认不重复写、旧预览不能批准新内容。
# 预期：一旦以后改坏事务或版本检查，测试会失败。
import unittest
import uuid
from companion import actions,state


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        state.initialize()
        self.actor=state.Actor("demo","test-"+uuid.uuid4().hex)

    def test_old_progress_cannot_replace_new(self):
        session=state.create_session(self.actor)
        state.update_session(self.actor,session,progress=3)
        with self.assertRaises(ValueError):
            state.update_session(self.actor,session,progress=1)
        self.assertEqual(state.get_session(self.actor,session["id"])["progress"],3)

    def test_confirming_twice_writes_one_note(self):
        item=actions.draft(self.actor,"note","只保存一次",uuid.uuid4().hex)
        for _ in range(2):
            actions.approve(self.actor,item["id"],item["revision"],item["digest"],True)
        self.assertEqual(len(actions.notes(self.actor)),1)

```

**连续代码 2/2**（接在上一段后，不额外增加缩进）

```python
    def test_changed_draft_rejects_old_confirmation(self):
        item=actions.draft(self.actor,"note","旧正文",uuid.uuid4().hex)
        actions.revise(self.actor,item["id"],"新正文")
        with self.assertRaises(ValueError):
            actions.approve(self.actor,item["id"],item["revision"],item["digest"],True)


if __name__=="__main__":
    unittest.main()
```

**写完后应当怎样：**一旦以后改坏事务或版本检查，测试会失败。

## 运行并观察

```bash
# 安装固定版本清单中的项目依赖，让当前虚拟环境能导入测试涉及的模块。
python -m pip install -r requirements-web.txt -r requirements-rag.txt -r requirements-graph.txt
# 在全新临时库中运行自己写的测试，结束后清理，避免污染主线会话。
python - <<'PY'
import os
import subprocess
import sys
import tempfile

# 每次回归使用全新数据库，避免测试读者和笔记混进正在练习的阅读记录。
with tempfile.TemporaryDirectory(prefix="reading-regression-") as directory:
    environment = dict(os.environ, READING_DATA_DIR=directory)
    subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        check=True,
        env=environment,
    )
# 子进程失败会在上面报错；成功后临时数据库自动清理，主线 data/live 不变。
PY
```

现在应运行到两份文件里的六条测试：0058 的无证据不生成、工具参数不能改身份、布尔值不能冒充审核范围，以及本节的旧进度拒绝、重复确认单条笔记、修改草稿后拒绝旧确认。逐条对照测试名称与断言；它们都不调用真实模型。

这六条还没有自动覆盖登录 API 的全部越权入口、过期批准、图恢复、Qdrant 网络服务或备份篡改。保留第 21 章的手工权限矩阵；后面做恢复演练时，再补相应证据。不能把作者的其他验证算成自己已经编写的测试。

## 添一条有意义的回归

从你自己的失败记录中选一条能确定判断的边界，例如未检索过的 source_id。先确认现有行为是否符合预期，再添加测试。不要写只把函数输出复制一遍的测试，那只会把当前错误固定下来。

每次运行记录程序版本、依赖版本、资料版本和测试范围。测试全绿不意味着未覆盖的风险也安全。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 这六条测试通过，能证明模型会正确回答文学问题吗？
2. 为什么回归要使用临时数据库？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**这六条测试通过，能证明模型会正确回答文学问题吗？**

不能。它们核对程序可确定的边界，没有调用真实模型，也没有评阅文学解释。下一单元才用真实问答和人工复核补这一层证据。

**为什么回归要使用临时数据库？**

测试会创建虚构会话、草稿和笔记。独立临时目录让每次从已知空状态开始，结束后清理，不把测试记录混进正在学习的阅读内容。

**通过证据：**临时目录中运行的已有六条测试报告，以及从自己的失败记录新增的一条断言与重跑结果。逐项写清自动覆盖了什么，仍需手工或真实服务验证什么。

</details>

## 下次开始前

下次先不看实现，说出“旧 revision”“重复批准”“旧内容摘要”各自会触发哪条测试，再用本页的临时目录命令重跑。保留测试名称、结果和未覆盖清单；下一单元的真实模型评阅会补不同证据，不把两种成绩合成一句“全部正确”。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter12)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
import os
import subprocess
import sys
import tempfile

# 每次回归使用全新数据库，避免测试读者和笔记混进正在练习的阅读记录。
with tempfile.TemporaryDirectory(prefix="reading-regression-") as directory:
    environment = dict(os.environ, READING_DATA_DIR=directory)
    subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        check=True,
        env=environment,
    )
# 子进程失败会在上面报错；成功后临时数据库自动清理，主线 data/live 不变。
PY
```

**预期：**已写的六条测试和你新增的断言通过；失败时根据具体测试名定位，测试数据不写入主线学习库。它们不评价文学答案质量。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
