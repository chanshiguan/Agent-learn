# 在虚构网页中完成可验证动作

## 单元一：选择最低成本的接口

已有结构化 API 时先调用 API；只需资料时先搜索或读取；需要网页状态时用 Browser Use；操作整个桌面才用 Computer Use；执行未知程序时另考虑 Sandbox。浏览器执行器不是模型，模型也不直接点击鼠标：模型提出动作，应用决定是否允许，执行器改变外部状态，再把观察交回。

DOM 或可访问性树提供元素与语义；截图提供像素，适合图像控件和视觉回退。页面变化后原来的坐标可能指向另一个按钮，所以观察必须有时间/版本。不要根据旧截图执行新动作。

## 单元二：先完成真实执行器，再连接智能提议

本课的 browser_loop 使用真实 Playwright、完全本地页面和可重放的固定提议。它完成观察、提议、策略、操作者接受/拒绝、执行、读取页面实际结果。这样先验证控制流程，避免把模型随机性和执行器错误混在一起。固定提议只能验证执行流程，不能说明模型会自行选对动作。

只在缺依赖时安装：

```bash
# 在所用环境中安装本例列出的依赖及版本；这不会下载课程正文。
courses/.venv-verification/bin/python -m pip install playwright
# 用本行指定的 Python 运行模块或查看解释器信息。
courses/.venv-verification/bin/python -m playwright install chromium
```

完整测试顺序：

```bash
# 运行 courses/08-agent-interfaces/examples/browser_loop.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/08-agent-interfaces/examples/browser_loop.py --decision accept
# 运行 courses/08-agent-interfaces/examples/browser_loop.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/08-agent-interfaces/examples/browser_loop.py --decision reject
# 运行 courses/08-agent-interfaces/examples/browser_loop.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/08-agent-interfaces/examples/browser_loop.py --scenario stale --decision accept
# 运行 courses/08-agent-interfaces/examples/browser_loop.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/08-agent-interfaces/examples/browser_loop.py --scenario failure --decision accept
# 运行 courses/08-agent-interfaces/examples/browser_loop.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/08-agent-interfaces/examples/browser_loop.py --scenario offsite
# 运行 courses/08-agent-interfaces/examples/browser_loop.py，按本行参数完成当前案例并核对输出。
courses/.venv-verification/bin/python courses/08-agent-interfaces/examples/browser_loop.py --scenario send
```

分别期待 VERIFIED、REJECTED、STALE_REQUIRES_NEW_REVIEW、FAILED、BLOCKED、BLOCKED。只有第一条实际填了“课程学习草稿”；截图和 receipt.json 默认在 `/tmp/ai-learn-action-loop`，要保留每次结果就用 `--output` 给不同目录。CLI 的 decision 来自操作者，不能从模型提议读取“我已获准”。

{{code:../examples/browser_loop.py}}

## 单元三：把供应商协议接到同一控制层

无论供应商如何命名，基本消息链相同：请求携带工具定义与观察 → 响应包含调用 ID 和动作 → 应用检查并执行 → 结果携带同一调用 ID → 下一轮模型观察结果。不能把多个工具结果都配给同一个 ID，也不能漏掉未执行动作的明确失败结果。

Anthropic 的客户端工具调用要返回对应 tool_use_id；toolset 还需匹配对应名称。OpenAI 的 computer 调用结果对应 call_id，可有一批 actions；顺序执行，前一步失败后后续依赖动作不能继续。截图应来自实际执行后的环境，不由模型生成。不同版本的旧 preview 与新工具名称不能混用，原课协议说明与本地版本说明列出快照差异。

把固定 propose 替换为模型的第一步，不是开放所有点击，而是只接受当前定义的动作枚举和字段；未知动作拒绝，有限次数循环，外部状态每步重读。批量操作也要逐项检查是否符合执行策略；批准绑定具体内容、页面版本与操作者，变化就重审。读取网页中的“忽略规则”是读取数据，不是获得授权。

## 单元四：Sandbox 的完整责任

运行环境有四样东西：初始化文件、当前活跃会话、可恢复快照、聊天记录。它们生命周期不同。Manifest 描述新环境要有哪些文件，不意味着续接旧 session 时会自动清空所有修改。快照也可能保存敏感内容，需访问与保留策略。

容器共享宿主内核，虚拟机提供不同隔离边界；不能仅凭 Docker 字样认为绝对安全。最低配置包括只读输入、单独输出、非 root、资源与时间上限、关闭不需要网络、不挂载宿主凭证。托管 E2B/Modal/Vercel 等还涉及实例生命周期、凭证、计费和下载产物；结束任务后应清理环境。

本课 plot_csv.py 与 Dockerfile 已给出固定任务的完整代码。只得到 SVG 不证明容器隔离，必须记录实际容器命令与挂载/网络设置。没有 Docker 的机器可以理解并审查配置，但容器这一项保持未执行。

## 单元五：原四题的完整成果

| 原题 | 完整实现 | 通过证据 |
|---|---|---|
| 1 打开并截图 | browser_lab.py --live | example.com 的标题、最终 URL 和截图 |
| 2 策略 | policy.py 与正反例 | 合法读允许，发送待审，离域/异常动作拒绝 |
| 3 隔离绘图 | plot_csv.py、Dockerfile | 实际隔离配置、输入输出、产物 |
| 4 动作闭环 | browser_loop.py | 六个场景的状态与实际页面内容一致 |

第 4 题完整参考就是本章代码；接真实模型是后续效果实验，不影响本地流程验收。扩展到真实登录、邮件与付款不是本课作业。

## 参考资源与测验边界

Playwright MCP 把执行能力接给支持 MCP 的宿主；browser-use 组织网页 Agent 工作；OmniParser 帮助把截图变成元素信息；它们职责不同。WebArena、BrowserGym、Mind2Web、OSWorld 等提供不同任务、数据或环境，比较成绩要固定环境、步数和评分器。离线动作数据不等于获得访问任意真实网站的许可。

最终测验必须检查外部状态：声称填入但输入框仍空，失败；拒绝后却执行，失败；旧状态被接受，失败。迁移题是在同一虚构页加第二个只填写字段，复用同样六类测试，不能通过扩大域名许可来绕过问题。
