# 第八课：让 Agent 接触界面

前面的工具接收结构化参数；这一课把工具扩展到网页和运行环境。先分清接口和权限，再做读取与截图、策略检查、容器绘图，最后完成表单动作循环。B 线按四项验收；A 线至少完成读取与截图，其余按需要选学。

## 1. 选最小的执行接口

有正式 API 就优先 API；只需读取资料用检索或 fetch；需要网页交互才用浏览器；跨桌面应用才用 computer use；执行代码需要受控 workspace 或 sandbox。它们不是必须一级级升级的等级。通过屏幕操作时，页面布局和状态可能变化，通常需要更多检查才能确认执行结果。

Browser Use 通过 DOM、无障碍树或截图理解网页。DOM 描述结构与属性；Accessibility Tree 描述角色、名称和状态；截图只有像素。Canvas、拖拽和某些视觉内容可能需要截图。固定脚本自动化偏向已知路径；Agent 根据观察选择下一步，但两者都要检查真实结果。

## 2. 完整动作循环

observe → propose → policy → approve/execute → verify → 下一轮或停止。

Observe 读取当前页面和 URL；Propose 是模型提出请求；Policy 检查域名、动作和权限；需要批准时等待可信用户；Executor 执行；Verify 看新的外部状态。模型说“按钮点了”不是证据，界面可能没变化或点错。

一个响应可能带多条动作，顺序执行；第一条失败后后续动作可能已不适用。不能拿旧截图坐标点击新页面；缩放截图时必须同步坐标变换。设置总步数、超时和最大重试，找不到目标就报告，不无限点击。

## 3. 四道边界

隔离：专用浏览器 profile、无真实账户资料、最少挂载与凭证。白名单：允许哪些域、路径、操作。批准：发消息、购买、删除、登录等敏感动作单独处理。验证与日志：保存动作、结果、截图和失败原因，但避免敏感内容外泄。

URL 检查不能用字符串 contains：example.com.evil.test 不属于 example.com。解析 scheme、hostname、port 和 userinfo；检查重定向后的地址以及子资源请求。策略函数仍不是完整网络沙箱，不能代替 DNS、网络出口和浏览器进程权限控制。

## 4. 原练习 1：打开安全页

Track A 可以只做这一项：用受限浏览器打开 example.com，记录标题、最终 URL、截图，不登录、不下载、不离开允许域。提供的 browser_lab.py 默认创建内存页面；加 --live 才访问该示例网站。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
/opt/homebrew/bin/python3.11 -m venv courses/08-agent-interfaces/.venv
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/08-agent-interfaces/.venv/bin/python -m pip install -r courses/08-agent-interfaces/examples/requirements.txt
# 用本行指定的 Python 运行模块或查看解释器信息。
courses/08-agent-interfaces/.venv/bin/python -m playwright install chromium
# 运行 courses/08-agent-interfaces/examples/browser_lab.py，按本行参数完成当前案例并核对输出。
courses/08-agent-interfaces/.venv/bin/python courses/08-agent-interfaces/examples/browser_lab.py
# 运行 courses/08-agent-interfaces/examples/browser_lab.py，按本行参数完成当前案例并核对输出；--live 会进入真实服务路径，需先满足本章环境要求。
courses/08-agent-interfaces/.venv/bin/python courses/08-agent-interfaces/examples/browser_lab.py --live
```

首次 Chromium 安装会下载浏览器。程序会操作真实浏览器，不过执行哪些动作由固定列表决定。这次运行可以验证浏览器操作，不能用来评价模型的规划能力。输出在 /tmp/ai-learn-browser，包含 trace.json 和 observed.png。内存页 URL 是 about:blank，报告明确区分它与真实 example.com。

## 5. 原练习 2：先检查，再执行

examples/policy.py 把 read/screenshot 设为 ALLOW，把 login/purchase/delete/send 设为 ASK，其余 BLOCK。ASK 不是批准；没有人类回答不能自动执行。域不对时即使只读也阻断。

检查器返回分类，不直接执行动作。这样才能用普通单元测试覆盖各种恶意域、file URL、未知动作。浏览器执行器每次消费动作前都检查，而不是只在任务开始检查一次。

## 6. 原练习 3：隔离代码

Container 通常共享宿主内核，VM 有独立内核，microVM 缩小虚拟机开销，gVisor 在系统调用层增加隔离。启动快不等于安全；只换工作目录也不等于 sandbox。

本课 Dockerfile 只装固定 Python 脚本，非 root 运行；输入只读、输出单独挂载、关闭网络和多余能力、限制内存/进程/CPU。Docker 安装和镜像下载是额外前置，制作教材不替你执行任意模型代码。

```bash
# 按指定 Dockerfile 构建本地示例镜像。
docker build -t ai-learn-plot courses/08-agent-interfaces/examples
# 创建本例需要的目录。
mkdir -p /tmp/ai-learn-plot-output
# 设置本例文件所需的执行权限。
chmod 777 /tmp/ai-learn-plot-output
# 按本行挂载、网络、用户和资源参数运行隔离案例；这些限制由命令实际落实。
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --memory 128m --cpus 1 --pids-limit 64 --mount type=bind,src=/Users/owen/Documents/ai-learn/courses/08-agent-interfaces/examples/data.csv,dst=/input/data.csv,readonly --mount type=bind,src=/tmp/ai-learn-plot-output,dst=/output ai-learn-plot
```

这里只对新建的临时输出目录开放写入以方便不同 UID 的教学容器；生产采用明确用户权限，不照搬 777。输出 chart.svg 是完整可打开的图；输入是固定虚构数字。检查容器配置和挂载证据，不能仅凭“图出来了”证明隔离。

## 7. 原练习 4：接起循环

browser_loop.py 完成真实观察、固定提议、策略检查、接受或拒绝、状态再检查、填写及结果核验；正常、拒绝、状态过期、执行失败、离域和发送六条路径的完整命令见本课“分步实作与完整参考”。browser_lab.py 只作为前面的读取与截图入门。模型接入时，只替换 propose，让模型按约定结构产生 action 与 url；不要开放任意 Playwright 调用或任意 JavaScript。接入后的模型效果须另测，固定提议的测试只证明执行链正确。

## 8. 两类云端协议如何读

Anthropic 当前 computer/browser toolset 请求含 member name、toolset_name 与 input；结果要匹配 tool_use_id 和 toolset_name。保留完整 assistant 内容，再回工具结果。批次失败后停止执行后续动作，但仍按协议给后续每个调用回错误结果，不能丢消息。

OpenAI Responses 的 computer_call 可能含 actions 数组；执行后回 computer_call_output，匹配 call_id，提供新截图，并用 previous_response_id 续接。请求的 status=completed 只表示请求生成完成，不表示实际动作成功。遇到 Pending safety checks 时，需要等待实际批准，程序不能自行填入“用户已批准”。

这些协议说明帮助读原课完整示例；没有云端认证时不需要购买接口才能完成本地练习。截图提供观察，动作描述要做什么，服务端权限决定能否执行。这些需要分别处理，执行器的隔离措施仍由你负责。
