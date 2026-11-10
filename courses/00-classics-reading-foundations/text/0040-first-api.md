# 用一个 API 接住读者的问题

本单元预计 **35—50 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 先把已有行为包成服务

前面每次在终端提问。API 让页面也能调用同一套检索与回答。FastAPI 接收请求，Pydantic 校验字段，随后调用已经认识的 `retrieve()` 和 `answer()`。这一步不改变文学回答的质量。

HTTP 可以先理解为一次有约定格式的往返：浏览器发送 JSON，服务返回状态码与 JSON。成功不只是 200，还要有页面能理解的回答和来源。

```bash
# 安装网页服务依赖，复用已有虚拟环境；不需要另学一套前端框架。
python -m pip install -r requirements-web.txt
# 启动本章最小服务，只监听本机；终端会持续运行，用 Ctrl+C 停止。
python -m uvicorn companion.basic_app:app --host 127.0.0.1 --port 8000
```

保持第 4 章模型变量有效，并已完成 ingest。浏览器打开 `http://127.0.0.1:8000`，输入序言关系的问题。当前页面固定使用关键词检索，便于先验证完整请求链。它没有账号，不能直接开放给其他人。

## 看懂一次错误

把问题留空尝试提交，再临时关闭模型服务提交正常问题。前者应由输入校验阻止；后者应显示服务暂不可用，而不是一直转圈或出现上一次答案。恢复模型后重试。

源码里 `response_model` 并不是此例的重点，先看输入模型与 `POST /api/ask`：限制问题长度与未知字段，避免随便接收整个对象。不要把 API key 写进浏览器 JavaScript。

## 对照完整实现

先读上面标出的函数，再展开文件。配套包已包含它及依赖文件；不需要把后续章节一起学完。注释重点解释为什么这样处理，以及出错时应发生什么。

<details><summary>展开本单元完整源码：companion/basic_app.py</summary>

{{code:companion/basic_app.py}}

</details>

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 页面应该直接带 API key 调模型吗？
2. 浏览器收到 200 是否说明答案有据？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**页面应该直接带 API key 调模型吗？**

不应该。服务端持有模型凭据，页面只访问自己的业务 API，避免把密钥交给每个浏览器。

**浏览器收到 200 是否说明答案有据？**

只说明请求成功返回；仍需看引用与人工评测，不能把传输成功当语义正确。

**通过证据：**本机网页成功问答一次，并记录空输入与模型不可用时的界面表现。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
