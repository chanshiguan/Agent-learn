# 关闭程序后，接着处理同一草稿

本单元预计 **40—55 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《重复点击、过期与换人都要试》](0053-approval-replays.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 恢复的对象是业务状态

前一章 actions 表保存草稿、版本、状态和期限。进程退出不会抹掉它。恢复不是重新执行整个对话，也不是把上次所有工具再跑一次；先读当前动作状态，判断还允许做什么。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：用新进程读回旧草稿

状态保存在 SQLite 而非 Python 变量；重新启动后仍从数据库确认本人动作。

**写在哪里：**项目根目录下的 `companion/actions_cli.py`。 先在编辑器新建文件；父目录没有时先建目录。不要把代码正文当成终端命令执行。

**先理解：**`argparse` 把终端参数转成有名字的值。先看默认值，再看当前命令是否覆盖它；`--help` 可以核对参数名。

```python
# 目的：状态保存在 SQLite 而非 Python 变量；重新启动后仍从数据库确认本人动作。
# 预期：关闭程序再运行 list，旧草稿仍在；批准仍要求当前预览。
import argparse
import json
import uuid
from . import actions
from .state import Actor, initialize


def main():
    parser=argparse.ArgumentParser(description="跨进程检查待确认动作")
    parser.add_argument("operation",choices=["draft","list","notes","revise","approve"])
    parser.add_argument("--user",default="reader-a")
    parser.add_argument("--text",default="我想回查文言文序言和日记之间的关系。")
    args=parser.parse_args();initialize();actor=Actor("demo",args.user)
    if args.operation=="draft":result=actions.draft(actor,"note",args.text,uuid.uuid4().hex)
    elif args.operation=="list":result=actions.pending(actor)
    elif args.operation=="notes":result=actions.notes(actor)
    else:
        identity=input("本人草稿 ID：").strip()
        item=next((x for x in actions.pending(actor) if x["id"]==identity),None)
        if not item:raise ValueError("没有找到本人草稿。")
        if args.operation=="revise":result=actions.revise(actor,identity,args.text)
        else:
            print(json.dumps(item,ensure_ascii=False,indent=2))
            confirmed=input("确认当前预览？输入 YES：")=="YES"
            result=actions.approve(actor,identity,item["revision"],item["digest"],confirmed)
    print(json.dumps(result,ensure_ascii=False,indent=2))
```

**写完后应当怎样：**关闭程序再运行 list，旧草稿仍在；批准仍要求当前预览。

### 第 2 步：给命令入口增加 action

这里只增加一个分支，并在选中时导入对应模块；前期命令不会提前加载后期功能。

**写在哪里：**项目根目录下的 `companion/__main__.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
        from .index_cli import main
        main()
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
        from .index_cli import main
        main()
    elif command == "action":
        from .actions_cli import main
        main()
```

**写完后应当怎样：**旧命令仍可运行，新命令调用你刚完成的函数。


## 让刚写的代码生效

如果上一节的服务仍在运行，先在那个终端按 Ctrl+C 停止。确认当前终端仍有模型配置，再从项目根目录重启，随后刷新浏览器。没有使用自动重载时，仅保存文件不会更新运行中的 Python 进程。

```bash
# 载入刚写完的接口、业务模块和页面；等终端显示服务启动后再进行下面的交互。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```


## 运行并观察

```bash
# 创建尚未批准的新草稿，记录输出 ID；命令结束后进程已经退出。
python -m companion action draft --text "重启后先检查当前版本，再决定是否保存这份阅读笔记。"
# 新命令是新的 Python 进程；预期仍能列出刚才的持久草稿。
python -m companion action list
# 再读完整预览并决定是否批准；不是自动续用上一次的口头同意。
python -m companion action approve
```

分别在三种时点模拟退出：创建后、批准前、批准成功后但页面尚未看到响应。恢复时预期分别是待确认、待确认、已保存且重复提交不新增。

## 故障表要有具体动作

| 看到的状态 | 可以做什么 |
|---|---|
| pending 且当前版本有效 | 展示内容，请用户确认 |
| pending 但已过期 | 重新生成或修订预览，再确认 |
| committed | 返回原结果，不能再写一条 |
| 找不到或不属于本人 | 拒绝，不猜测相近 ID |

受限资料、账号身份和作品范围在恢复时也要重新检查。持久化一个 ID 不等于永久保留权限。

下一单元引入框架，是为了清楚表达流程与检查点；业务批准规则继续复用，不让框架替代它。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 恢复任务就是重跑所有步骤吗？
2. 为什么恢复时还要看期限？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**恢复任务就是重跑所有步骤吗？**

不是。先读已完成状态，避免重复副作用；只继续当前允许的步骤。

**为什么恢复时还要看期限？**

进程保存了状态，但读者的批准可能已经失效，数据也可能变化。

**通过证据：**三个退出时点的状态记录，以及恢复后没有重复笔记的证据。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/04-agent-frameworks.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
