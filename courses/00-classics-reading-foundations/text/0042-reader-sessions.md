# 两位读者，不共用一段对话

本单元预计 **35—50 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 从临时页面走到持久会话

会话是一次连续阅读的容器，保存作品、最近对话和进度。它不是知识库，也不是模型重新训练。SQLite 是一个本地数据库文件；适合本课单实例练习，多副本和高并发另需设计。

先用 Ctrl+C 停止第 13 章服务，再启动加入会话的版本。

```bash
# 保持测试身份模式，只在本机练习；章节值用于逐步显示已经学过的页面功能。
export APP_MODE=lab
export COURSE_CHAPTER=14
# 先使用已验证的词面基线；选择 hybrid 时还要保证 Qdrant 与索引就绪。
export RETRIEVAL=keyword
# 启动带会话的同源页面；数据写到 data/live/reading.sqlite3。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```

选择读者 A，创建《狂人日记》阅读，问一个问题；切到读者 B，应看不到 A 的会话。B 新建记录后，切回 A 检查它仍在。停止并重启服务，再检查持久性。

## 身份来自哪里

本章 `X-Lab-Reader` 只允许两个测试值，且服务限本机。它方便验证隔离，却不是认证系统：知道测试值的人就能选身份。第 21 章才换真实登录。`COURSE_CHAPTER` 只是页面教学开关，也不是权限控制。

每次查询会话都带 `tenant` 和 `owner`；仅知道会话 ID 不能越过它们。数据库写入还检查 revision，避免两次并发请求用旧状态互相覆盖。冲突会让你重读状态，不静默丢掉一段对话。

## 对照完整实现

先读上面标出的函数，再展开文件。配套包已包含它及依赖文件；不需要把后续章节一起学完。注释重点解释为什么这样处理，以及出错时应发生什么。

<details><summary>展开本单元完整源码：companion/state.py</summary>

{{code:companion/state.py}}

</details>

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 用不同 UUID 是否就实现了权限？
2. 测试身份模式为什么不能上线？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**用不同 UUID 是否就实现了权限？**

没有。ID 不容易猜也不能替代服务端的所属人和租户检查。

**测试身份模式为什么不能上线？**

客户端能够选择身份，没有证明“你是谁”。本章只检验归属逻辑，真实认证在第 21 章接入。

**通过证据：**A/B 两个独立会话和重启后的保留记录；能说明测试身份的限制。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter9)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
