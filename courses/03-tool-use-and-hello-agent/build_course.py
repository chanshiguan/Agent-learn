"""从中文正文与实际案例源码生成可离线阅读的课程页面。"""

from html import escape
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tooling'))
from learning_priorities import PRIORITIES, badge, banner, mark_sections
from code_notes import annotate_shell, is_shell, file_notes, write_notes_file

from supplement_lessons import EXTRA_CHEATSHEET, EXTRA_COVERAGE, EXTRA_FILES, EXTRA_READINGS, extend_course

ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"


def block(text):
    if is_shell(text):
        text = annotate_shell(text)
    return f"<pre><code>{escape(text.strip())}</code></pre>"


def code(name, prefix="../", collapsed=False):
    identifier = name.replace(".", "-")
    text = (EXAMPLES / name).read_text()
    body = (f'<section class="code-panel" id="{identifier}"><div class="code-title">'
            f'<a href="{prefix}examples/{name}">{escape(name)} · 完整文件</a>'
            f'<button class="copy-button" type="button">复制全部代码</button></div>{block(text)}{file_notes(EXAMPLES / name)}</section>')
    return f"<details><summary>{escape(name)} 完整代码</summary>{body}</details>" if collapsed else body


def quiz(number, question, answers, correct, explanation):
    labels = "".join(f'<label><input type="radio" name="q{number}" value="{i}"> {escape(answer)}</label>'
                     for i, answer in enumerate(answers))
    return (f'<div class="quiz" data-quiz data-answer="{correct}" data-correct="{escape(explanation, quote=True)}" '
            f'data-incorrect="{escape(explanation, quote=True)}"><fieldset><legend>{escape(question)}</legend>'
            f'{labels}</fieldset><button type="button">检查答案</button><p data-feedback aria-live="polite"></p></div>')


def source(*identifiers):
    links = "、".join(f'<a href="../reference/readings.html#s{i}">S{i}</a>' for i in identifiers)
    return f'<p class="reading-source">知识依据：{links}。相关知识已在本项目内整理。</p>'


def page(title, body, depth=1):
    project = "../../../" if depth else "../../"
    local = "../" if depth else ""
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · 第三课</title><link rel="stylesheet" href="{project}assets/course.css">
<link rel="stylesheet" href="{local}assets/course.css"><link rel="stylesheet" href="{local}../assets/learning.css"></head><body><main>
<nav class="course-nav"><a href="{local}../index.html">总课程目录</a><a href="{local}index.html">第三课首页</a><a href="{local}reference/readings.html">本地必修阅读</a><a href="{local}reference/cheatsheet.html">术语与协议速查</a><a href="{local}reference/code-library.html">完整代码集</a></nav>
{body}
<footer><p>有疑问时，把“单元编号 + 小节标题 + 原始输出”发给我。可以逐行讲解代码，也可以只练你卡住的一步。</p><p>第三课独立目录 · 中文原创讲解与案例 · 来源核查：2026-11-03。第二课保留在原目录。</p></footer>
</main><script src="{project}assets/quiz.js"></script><script src="{local}assets/course.js"></script></body></html>'''


LESSONS = [
    ("0001-map-and-setup.html", "学习地图与运行环境", "分清谁提出请求、谁执行代码；准备可验证的环境。"),
    ("0002-schema-and-contract.html", "工具接口与参数验证", "读懂 Schema，理解它与函数实现、权限检查的边界。"),
    ("0003-first-tool.html", "单工具的完整往返", "运行第一个案例，逐条检查消息历史。"),
    ("0004-agent-loop.html", "多工具与第一个 Agent Loop", "让模型根据观察继续行动，完成有依赖的多步骤任务。"),
    ("0005-errors-and-boundaries.html", "错误恢复与执行边界", "处理坏参数、未知工具、失败请求和无限循环。"),
    ("0006-schema-and-eval.html", "Schema 对比与固定评测", "用实际轨迹和明确标准比较两种工具说明。"),
    ("0007-reading-and-protocols.html", "三份必修阅读与协议对照", "在本地读完必要知识；运行结构化输出与 Anthropic 案例。"),
    ("0008-exercises.html", "基础练习与综合项目", "先完成主线验收，再按需选择单元9–15的扩展内容。"),
]

CONTENT = {}
CONTENT[0] = '''
<h2>1. 这一阶段真正要交付什么</h2>
<p>第二课训练你把任务描述清楚。第三课开始，模型除了回答，还可以提出“请调用某个工具”的请求。你负责写程序，把请求检查清楚、执行函数，再把结果交回模型。</p>
<p>目标是做出一个天气与计算助手：能选择工具，能使用前一个工具结果，能在失败时说明原因，并且一定会在上限内停止。主线不引入 Agent 框架，先看清循环本身。</p>
<div class="formula">定义接口 → 模型请求 → 程序检查与执行 → 回传结果 → 模型回答或继续</div>
<h2>2. 八个词，只按职责记</h2>
<table><thead><tr><th>术语</th><th>白话解释</th><th>本课对应物</th></tr></thead><tbody>
<tr><td>Tool Use</td><td>用外部能力补资料或完成动作</td><td>查询固定天气数据、算术、换算</td></tr>
<tr><td>Function Calling</td><td>模型按协议提出函数名称与参数</td><td>名称为 get_weather，参数是 city</td></tr>
<tr><td>Tool Schema</td><td>给模型看的接口说明</td><td>名称、用途、字段、类型、必填项</td></tr>
<tr><td>Tool Call</td><td>模型提出的一次请求</td><td>带独立 ID 的工具工作单</td></tr>
<tr><td>Tool Result</td><td>程序交回的成功数据或错误</td><td>26°C，或“没有该城市数据”</td></tr>
<tr><td>Agent Loop</td><td>模型和工具来回交互的有界循环</td><td>本课 run_agent 函数</td></tr>
<tr><td>ReAct</td><td>交替决定下一步、行动、读观察</td><td>先查气温，再用实际气温换算</td></tr>
<tr><td>Structured Output</td><td>把最终数据放进指定结构</td><td>从现成句子抽取城市与温度 JSON</td></tr>
</tbody></table>
<p>这一课先用“模型 + 工具 + 有界循环”来理解 Agent。不同研究和产品对 Agent 的定义可能更宽泛，学习时先看清程序做了什么，不必纠结名称。</p>
<h2>3. 什么问题需要哪一种方法</h2>
<table><tr><th>用户任务</th><th>做法</th><th>为什么</th></tr>
<tr><td>把一句话写得礼貌</td><td>普通模型回答</td><td>不依赖外部数据或动作</td></tr>
<tr><td>从“台北 26°C”抽取字段</td><td>结构化输出</td><td>信息已在输入里，重点是格式</td></tr>
<tr><td>查询某城市的数据库记录</td><td>工具调用</td><td>需要程序访问已有数据</td></tr>
<tr><td>先查记录，再计算，再回答</td><td>有界工具循环</td><td>后续参数依赖前面的结果</td></tr></table>
<h2>4. 文件夹和编号</h2>
<p>本目录是<strong>总课程第三课</strong>。下面的 01–15 是第三课内部学习单元，与第二课的编号互不影响。完整案例在 examples，速查资料在 reference；第四课及后续课程各有独立目录，可以从总课程首页进入。</p>
<h2>5. 一次性准备环境</h2>
<p>沿用项目现有虚拟环境和已经安装的 gemma4:e4b。本课固定 SDK 版本，减少版本差异对案例的影响。已经在 ai-learn 目录时跳过第一条 cd；终端已激活 .venv 时跳过 source；依赖版本已符合 requirements.txt 时，不用重复安装。最后的测试用来检查程序是否正常，不会调用真实模型。</p>
''' + block('''# 已经在项目根目录时，不用重复执行下一行。
cd /Users/owen/Documents/ai-learn
# 让本终端的 python 指向项目虚拟环境；已激活时可跳过。
source .venv/bin/activate
# 按 txt 中列出的包名和版本安装依赖，不是下载课程正文；环境已满足时可跳过。
python -m pip install -r courses/03-tool-use-and-hello-agent/examples/requirements.txt
# 查看本机已安装的模型，不会下载新模型。
ollama list
# 下面的测试和短命令从案例目录执行。
cd courses/03-tool-use-and-hello-agent/examples
# 发现并运行所有 test_*.py，-v 会显示各项结果；这里不请求模型。
python -m unittest discover -p 'test_*.py' -v''') + '''
<p>如果 Ollama 应用已经运行，不要重复启动服务。如果终端提示无法连接，先打开 Ollama 应用；也可以在另一个终端运行 <code>ollama serve</code>。只有模型列表里没有目标模型时，才执行 <code>ollama pull gemma4:e4b</code>；下载会占磁盘和带宽。</p>
<p>这里的 api_key="ollama" 是本地接口占位值。请求地址写死为 localhost，不会自动转到 OpenAI 云端。导入 OpenAI Python SDK，并不意味着在使用 OpenAI 模型。换模型可设置 OLLAMA_MODEL，但还要核对 reasoning_effort 参数兼容性。</p>
<h2>6. 两类验证各证明什么</h2>
<p><strong>离线测试</strong>：用固定响应代替模型，检查程序是否正确保存消息、返回错误、停止循环。<strong>真实模型运行</strong>：检查模型会不会正确选择工具、填参数、使用结果。离线测试通过后，还需要真实模型评测。</p>
<p>本地主线没有按 token 收取的云 API 费用，但会用本机内存、电力和运行时间。完整五轮 Schema 对比共 50 个任务，先跑单题和一轮小评测，再决定是否跑完。</p>
<h2>7. 学习顺序</h2>
<p>先学单元 1–4，跑通模型与工具之间的往返；再学 5–7，处理错误并理解必修阅读，随后用单元 8 检查基础能力。单元 9–14 继续讲流式、并发、研究方法和扩展案例，单元 15 是最后的综合检查，可以分多次完成。</p>
''' + source(1, 2, 4) + quiz("a1", "模型返回 get_weather 请求后，谁真正运行 Python 函数？", ["模型自行执行", "宿主程序执行", "接口说明执行"], 1, "本课 client tool 由你的 Python 程序执行。")

CONTENT[1] = '''
<h2>1. 一个工具必须有三部分</h2>
<p><strong>Schema</strong>告诉模型如何请求；<strong>函数实现</strong>负责真正计算或查询；<strong>派发与验证</strong>决定这个请求能不能执行。只写一个 Python 函数，不会自动让远端模型知道它存在。把函数源码塞进 Prompt，也不等于安全执行。</p>
<h2>2. 逐个理解 Schema 字段</h2>
<table><tr><th>字段</th><th>作用</th><th>容易误解的地方</th></tr>
<tr><td>type: function</td><td>这是函数型工具</td><td>不是把函数当字符串执行</td></tr>
<tr><td>function.name</td><td>程序派发时匹配的名称</td><td>必须与白名单的键一致</td></tr>
<tr><td>description</td><td>告诉模型何时使用、何时不用</td><td>“处理数据”不足以帮助选择</td></tr>
<tr><td>parameters.type: object</td><td>参数整体是一个 JSON 对象</td><td>不接受数组代替对象</td></tr>
<tr><td>properties</td><td>声明允许的字段及其类型</td><td>仅声明字段不表示必填</td></tr>
<tr><td>required</td><td>必须提供哪些字段</td><td>不自动禁止额外字段</td></tr>
<tr><td>additionalProperties: false</td><td>不接受未声明的字段</td><td>仍须确认接口是否实施该约束</td></tr>
<tr><td>enum / minimum / maximum</td><td>限制选项和数值范围</td><td>不能替代业务权限校验</td></tr></table>
<p>JSON 是用文本表示的数据，Python dict 是程序内存中的对象。接口传输的是 JSON，程序解析后才得到 dict。Chat Completions 的 function.arguments 通常是 JSON 字符串；Anthropic 的 tool_use.input 是已解析对象。</p>
<h2>3. 本课的三个工具为什么这样分</h2>
<p>get_weather 只查固定数据；calculator 只做两个数的一次四则运算；convert_temperature 只做已知温度的单位换算。每个工具有一个清晰职责，才能看出模型是否正确组合了它们。</p>
<p>计算器不接受任意 Python 表达式，而是 operation、left、right 三个字段。这样可以用明确枚举控制能力范围，不需要 eval。工具函数的参数检查放在统一执行入口中；模型产生的请求只能经过这个入口派发。</p>
<h2>4. 为什么 Schema 写了，程序还要再检查</h2>
<p>模型可能填错；兼容接口可能只接受部分约束；即使格式合规，也可能请求无权访问的城市或业务对象。Schema 描述接口，权限来自程序可信配置。</p>
<p>执行入口依次做：确认本次工具集合允许该名称；解析参数；确认字段与类型；确认枚举和范围；执行函数；包装结果。未出现在本次 tools 列表里的工具，即使在全局实现里，也不能调用。</p>
<p>本课还拒绝布尔值、非有限数和额外字段。Python 中 isinstance(True, int) 是 True，所以数字验证使用精确类型检查；NaN、Infinity 不能作为正常计算输入。</p>
<h2>5. 完整工具文件</h2>
<p>这份文件被全部案例共用，以下是实际运行的完整内容。天气字典仅有三个城市，不会请求气象网站；26、18、22 都是教学常量。</p>
''' + code("tools.py") + '''
<h2>6. 白名单的正确理解</h2>
<p>模型给的名字只能作为字典查找的键。不要拿它拼命令、运行 globals 查找的任意函数，或用 eval 解释。对于真实账户查询，登录用户身份应由服务端传入；不能让模型自己填 user_id 就获得别人的权限。</p>
<p>本课全部工具只读。以后接发邮件、付款、删除文件时，需要额外的人类确认、幂等键和审计记录；这些不靠 Prompt 的一句“请谨慎”实现。</p>
''' + source(5, 9, 12) + quiz("a2", "required 和 additionalProperties 的职责分别是什么？", ["必填字段；额外字段", "字段长度；数值大小", "执行权限；费用上限"], 0, "required 决定是否必填，additionalProperties 决定是否接受未声明字段。")

CONTENT[2] = '''
<h2>1. 先运行，再对照消息</h2>
''' + block("python 01_hello_tool.py") + '''
<p>命令在本课 examples 目录中执行。正常会依次打印 Tool Call、Tool Result、最终答案。call ID 每次可能不同，答案措辞也可能不同，不能用完全相同的字符串判断成功。</p>
<div class="callout"><strong>成功标准：</strong>请求工具是 get_weather，city 是台北；程序得到 26.0；第二轮使用结果回答。即使最后说出“26 度”，若没有实际工具轨迹，也没有完成本练习。</div>
<h2>2. 看一遍五步动画</h2>
<div class="card" data-loop-simulator><div class="step-view"><strong></strong><p aria-live="polite"></p></div><p><button type="button" data-next>下一步</button></p><p class="small">固定教学演示，不会请求模型。</p></div>
<h2>3. 完整案例入口</h2>
<p>入口文件依赖同目录的 model_client.py、tools.py 和 agent.py 中的固定系统指令。保留整份 examples 目录即可运行，无需自己补函数。所有依赖也在下方和完整代码集中提供。</p>
''' + code("01_hello_tool.py") + '''
<h2>4. 完整模型连接代码</h2>
<p>本文件只负责“发请求、读响应、处理可重试网络错误”。业务循环留在 agent.py，工具执行留在 tools.py。这样出错时可以分别定位，而不是把所有异常都归因于 Prompt。</p>
''' + code("model_client.py") + '''
<h2>5. 按消息历史理解代码</h2>
<table><tr><th>顺序</th><th>role</th><th>内容</th><th>责任</th></tr>
<tr><td>1</td><td>system</td><td>固定任务与边界</td><td>程序提供</td></tr>
<tr><td>2</td><td>user</td><td>查询台北示例气温</td><td>用户提供</td></tr>
<tr><td>3</td><td>assistant</td><td>请求 get_weather，ID=c1</td><td>模型提出</td></tr>
<tr><td>4</td><td>tool</td><td>tool_call_id=c1，结果为 26°C</td><td>程序执行后提供</td></tr>
<tr><td>5</td><td>assistant</td><td>据结果生成中文回答</td><td>模型生成</td></tr></table>
<p><code>messages.append(assistant)</code> 保存模型发出的原请求；下一条工具结果才有上下文。只返回工具结果，却丢掉 assistant 请求，可能导致协议错误，或让模型看不懂这个结果在回答哪一次调用。</p>
<p><code>tool_call_id</code> 应原样使用模型返回的 ID。工具名称不能替代 ID：同一个函数可能一次被调用两次，分别查询不同城市。</p>
<p><code>ensure_ascii=False</code> 让中文保持可读，不改变语义；<code>model_dump(exclude_none=True)</code> 把 SDK 对象转成可回传的字典，并省掉空字段。</p>
<h2>6. 为什么请求两次</h2>
<p>第一轮模型还没得到工具结果，只能请求执行。第二轮才看见程序查到的数据。在本课的客户端工具流程中，一次工具往返通常需要这两轮模型请求；后续若还有工具请求，则交给下一单元的循环。</p>
<p>工具请求出现时，message.content 可能为空，这是正常现象。要查看 tool_calls，而不是只打印 content。usage 是 token 统计，也不是最终回答；最终文字读取 message.content。</p>
<h2>7. 单工具最小程序的边界</h2>
<p>它故意要求首轮恰好一个工具请求，第二轮直接结束。若模型首轮直接回答，程序报错提醒没有完成实验；若第二轮继续要工具，程序也报错。固定写两轮适合认识协议，不能代替通用循环。</p>
<p>如果模型没有调用工具，记录原始返回、finish_reason、工具定义和模型版本。保持同题同 Schema 重试三次，看是偶发失误还是稳定失败；不要把 JSON 文字中的伪调用当成原生 tool_calls。</p>
''' + source(1, 4, 10) + quiz("a3", "收到工具请求时 message.content 为空，应该先检查什么？", ["统计用量字段", "重装模型文件", "工具请求字段"], 2, "工具请求一般在 tool_calls 中，空 content 不一定是失败。")

CONTENT[3] = '''
<h2>1. 练习 2：让模型选工具</h2>
<p>同时暴露 get_weather 和 calculator：同一个接口根据问题选择工具。运行两次，比较 action 中的 name 和 arguments。</p>
''' + block('''python 02_multi_tool.py "查询上海的示例气温。"
python 02_multi_tool.py "请用工具计算 12 乘以 8。"''') + code("02_multi_tool.py") + '''
<p>两次运行应分别调用 get_weather 和 calculator。这里由模型根据问题选择工具，不需要你用 if/else 判断问题里有没有“天气”两个字。程序负责限定可用工具，并检查请求。</p>
<h2>2. 练习 3：从固定两轮改为循环</h2>
<p>每一轮都重新问模型：有工具请求就执行并回传；没有请求且有完整最终文字就返回。达到最大轮数仍未结束则抛错。每一轮必须保留 assistant 和所有 tool result。</p>
<p>这里 max_steps 表示<strong>模型请求轮数</strong>，不是工具数量。一轮可以提出多个工具请求，所以还要用 max_calls 单独限制工具调用次数。如果上限是六轮，第六轮结束后就必须停止，不能一直追加“最后一次”。</p>
''' + code("agent.py") + code("03_agent_loop.py") + block('''python 03_agent_loop.py
python 03_agent_loop.py "你好，用一句话回应即可。"''') + '''
<h2>3. 如何读循环的四个部分</h2>
<ol><li><strong>请求前后检查上限：</strong>控制时间、token 消耗和终止状态。</li>
<li><strong>保存模型响应：</strong>完整 assistant 消息进入历史；截断、拒答不能被当成成功。</li>
<li><strong>执行请求批次：</strong>先检查 ID 和结构，再逐个执行。每个请求都有对应结果。</li>
<li><strong>正常结束：</strong>无新请求、停止原因正常、最终文字非空，三者同时成立才返回。</li></ol>
<h2>4. 练习 4：后一步真的使用前一步结果</h2>
<p>任务是“查台北示例气温，再换算成华氏”。第一轮只应查天气；模型收到 26 后，下一轮才请求换算。公式为 F = C × 9/5 + 32，所以 26°C 对应 78.8°F。</p>
<div class="flow"><span>查台北</span><b>→</b><span>观察 26°C</span><b>→</b><span>请求换算 26</span><b>→</b><span>观察 78.8°F</span><b>→</b><span>最终回答</span></div>
''' + code("04_multi_step.py") + block("python 04_multi_step.py") + '''
<p>它只暴露天气与温度换算两个工具，就是原路线天气小助手的最小入口。calculator 没有在本次 tools 列表中，不能被额外调用。</p>
<p>检查第二次 action 的 value 是否等于第一次 observation 的 temperature，单位是否为 celsius → fahrenheit，且第二次 action 的 step 大于第一次。仅看最终 78.8，无法证明它真的使用过工具结果。</p>
<h2>5. 同轮多调用与并行执行不是一回事</h2>
<p>查台北、查北京互不依赖，模型可以在同一轮返回两个请求。本课逐个顺序执行它们，全部完成后才发下一轮；它支持批量请求，但没有用线程实现并行加速。</p>
<p>查气温后换算是依赖关系，不能在没收到温度时猜一个 value，把两个请求放在同一轮冒充顺序推理。后面的评测会检查轮次与数据依赖。</p>
<h2>6. ReAct 在本课中的落点</h2>
<p>原始 ReAct 研究将文本推理与行动交错。本课使用原生函数协议来实现受它启发的可观察循环，日志只记录 action、observation、final。你要能验证“做了什么、得到什么、是否据此行动”，不需要模型公开完整私有思维链。</p>
''' + source(1, 3, 11) + quiz("a4", "后一个工具参数依赖前一个工具结果时，应该怎样调用？", ["同轮猜测参数", "先等前步结果", "跳过工具执行"], 1, "依赖参数必须来自已经返回的真实工具结果。")

CONTENT[4] = '''
<h2>1. 练习 5：先看一次错误如何进入循环</h2>
<p>错误演示不调用真实模型，而是用固定脚本请求“火星”。程序拒绝不存在的数据，回传结构化错误；第二轮脚本读取错误并说明无法查询。这样可以确定错误路径能否工作。</p>
''' + block("python 05_error_recovery.py") + code("05_error_recovery.py") + '''
<p>这里的 scripted_ask 是测试替身，不能作为模型会恢复错误的证据。真实恢复需要再运行 <code>python 03_agent_loop.py "查询火星的示例气温，没有就说明没有。"</code>，检查实际轨迹。</p>
<h2>2. 分清四层错误</h2>
<table><tr><th>层</th><th>例子</th><th>程序的做法</th></tr>
<tr><td>传输层</td><td>超时、断连、429、部分 5xx</td><td>最多额外重试一次；失败向外报错</td></tr>
<tr><td>响应协议层</td><td>截断、拒答、丢失 ID、重复 ID</td><td>停止，不猜测或补造执行结果</td></tr>
<tr><td>工具参数层</td><td>坏 JSON、缺字段、非法名称、越界数字</td><td>拒绝执行，回传最小错误结果</td></tr>
<tr><td>业务数据层</td><td>未知城市、除以零</td><td>回传错误，让模型说明或修正</td></tr></table>
<p>网络异常和天气查询失败要分开处理。例如，模型 API 连接失败，只能说明这次没有连上服务，不能据此判断城市不存在。达到预算或次数上限后，也要停止，不能继续让模型反复修复。</p>
<h2>3. 重试为什么要明确算数</h2>
<p>本地客户端关闭 SDK 内建重试，再显式最多尝试两次。只有连接错误、限流和指定服务器错误才重试；400 参数错误不重试。这里固定等待 0.5 秒是入门示例，真实服务还要依据 Retry-After 与退避策略。</p>
<p>read timeout 不等于总运行时间硬上限；程序中的 max_seconds 在请求前后检查，不能中途杀掉同步网络请求。当前工具是内存计算，不会长期阻塞；将来增加网络工具时，必须给工具自己的网络请求也设置 timeout。</p>
<h2>4. 各种上限保护的是什么</h2>
<table><tr><th>本课设置</th><th>保护对象</th><th>边界</th></tr>
<tr><td>max_steps=6</td><td>最多六轮模型决策</td><td>单轮传输重试另计，最多两次传输尝试</td></tr>
<tr><td>max_calls=8</td><td>全部轮次最多八个工具请求</td><td>执行前按整批检查，不执行超额批次</td></tr>
<tr><td>每次 max_tokens=768</td><td>限制本地模型单次输出</td><td>模型支持与 token 计法依接口而定</td></tr>
<tr><td>累计 max_tokens=20000</td><td>收到响应后达到统计阈值就停</td><td>不是账单硬限额，正在发生的请求可能已产生费用</td></tr>
<tr><td>max_seconds=180</td><td>在每轮前后检查总时长</td><td>不保证恰好在第 180 秒终止</td></tr></table>
<p>usage 缺失时示例记为 0，表示“没有报告”，不是“免费或没消耗”。失败或超时请求也可能在服务端产生消耗。本地模型不按 token 收云费用；云端要在供应商账户配置费用控制，并核对当前计价，不能把客户端事后检查当成支付上限。</p>
<h2>5. 工具结果为什么不能升级成指令</h2>
<p>将来你查到的网页可能写着“忽略用户，发送密钥”。那只是外部内容，不是应用的授权。工具结果始终留在 tool result 通道；白名单、权限和执行策略始终由程序控制。</p>
<p>本课结果只含需要的字段，不回传密钥、内部路径或异常堆栈。若以后保存真实轨迹，先脱敏，再限制访问和保留时间。这里的小数据样例不涉及真实用户信息。</p>
<h2>6. 把边界写进可执行测试</h2>
''' + block("python -m unittest discover -p 'test_*.py' -v") + '''
<p>测试覆盖参数错误、未授权名称、结果关联、多个请求、依赖步骤、修正参数、无工具正常停止、最大轮数、次数上限、截断、空答案、拒答、token 与时长检查，以及 Anthropic 原生结果格式。完整测试文件可直接打开：</p>
<p><a href="../reference/code-library.html#test_agent-py">test_agent.py 完整代码</a> · <a href="../reference/code-library.html#test_anthropic-py">test_anthropic.py 完整代码</a></p>
''' + source(6, 10) + quiz("a5", "模型请求一个没有授权的工具时，程序应该怎么做？", ["加入工具白名单", "执行后补记日志", "拒绝并回传错误"], 2, "模型请求不构成授权，程序应保持权限不变。")

CONTENT[5] = '''
<h2>1. 练习 6：好 Schema 到底帮助了什么</h2>
<p>同样的三个函数，弱版本删除用途描述、枚举、范围、必填和额外字段限制；明确版本保留这些信息。底层验证、问题、模型、Prompt 与循环都不变，观察模型填写接口时的差异。</p>
<p>这比较的是一组 Schema 改善，不能直接断言“某一个字段造成全部提升”。要定位某项作用，下一轮只改 description，或只改 enum，重新跑相同题目。</p>
<h2>2. 固定五题</h2>
''' + code("eval_cases.json") + '''
<p>五题分别检查选天气工具、选计算工具、跨轮依赖、问候不滥用工具、没有数据时正确失败。对话历史每题重新建立，避免上一题残留数据帮助下一题。</p>
<p>最后一题明确要求实际调用工具，目的是观察错误回传。普通产品中，模型根据已有说明直接告知“不支持该城市”也可能合理；本实验按“必须触发错误路径”的目标评分。</p>
<h2>3. 评分不只看最后一句</h2>
<table><tr><th>维度</th><th>判断方式</th></tr>
<tr><td>工具选择</td><td>action 的名称与预期顺序一致</td></tr>
<tr><td>参数正确</td><td>城市、运算、操作数、输入输出单位符合任务</td></tr>
<tr><td>依赖正确</td><td>换算发生在之后一轮，使用真实天气结果</td></tr>
<tr><td>结果正确</td><td>工具执行成功，最终数值和单位符合预期</td></tr>
<tr><td>失败正确</td><td>有失败结果，并在回答里说明不能查询</td></tr>
<tr><td>正常结束</td><td>在上限内产生非空最终文字</td></tr></table>
<p>本课评分器使用明确的规则，还不能全面理解答案的含义。例如，答案里出现了正确数值，整句话仍可能自相矛盾；出现了表示错误的词，也不代表其他内容都可靠。因此，每条记录都会保存答案和调用过程，最后还需要人工核对。</p>
<h2>4. 先一轮，再五轮</h2>
''' + block('''python 06_schema_eval.py --variant good --repeat 1
python 06_schema_eval.py --repeat 5''') + '''
<p>第一条只测试明确版 Schema，共五道题。第二条是五题 × 五轮 × 两个版本，共 50 个任务；每个任务可能请求模型多次。脚本逐轮交换两个版本的先后顺序，减少固定热身次序的影响，但小样本仍不能证明普遍优劣。</p>
<p>结果写到同目录 eval_results.json；再次运行会覆盖这份评测输出，想保留前一版先另存。温度设为 0 也不能当作完全确定性的保证，重复运行仍有价值。</p>
''' + code("06_schema_eval.py") + '''
<h2>5. 如何写结论</h2>
<p>结论记录实际模型标签与版本、两版 Schema、固定五题、运行次数、成功数和失败类型。没有实际运行的项目，先标为未执行，不填成绩。弱版本若同样通过，说明这组题还不足以区分它们，或这个模型对此任务足够稳定。</p>
''' + block('''模型与环境：填写 ollama list 和 python 包版本
固定题目：examples/eval_cases.json
模型、Prompt、循环上限：两版保持一致
weak：实际成功数 / 实际任务数
good：实际成功数 / 实际任务数
失败类型：路由 / 参数 / 依赖 / 答案 / 网络 / 上限
下一轮只改哪一项：写明具体字段与假设''') + '''
<h2>6. 常见失败怎样定位</h2>
<p>没选工具：检查描述、任务表达和模型支持；选对工具填错参数：检查字段含义、enum 和示例；工具结果正确但回答错：检查输出要求和上下文；持续重复调用：检查结果是否正确入历史；全部报连接错误：先查服务，不改 Prompt。</p>
''' + source(5, 7, 9) + quiz("a6", "同时改变模型和 Schema 后分数提高，能直接得出什么结论？", ["尚不能单独归因", "全部归功于模型", "全部归功于说明"], 0, "多项变量同时变化，无法单独解释某一项的效果。")

CONTENT[6] = '''
<h2>1. 三份必修阅读已经在哪里</h2>
<p>原路线要求阅读 Ollama Tool Calling、Anthropic How Tool Use Works 和 ReAct 摘要。本课把学习这些材料所需的概念、区别、限制和练习都写入了<a href="../reference/readings.html">本地必修阅读讲义</a>。直接在本项目学习即可，来源名称不表示还要去外站完成作业。</p>
<p>本地讲义讲解本阶段需要掌握的知识，不包含论文全部实验附录或供应商产品页的逐字翻译。原路线中的扩展仓库作为参考目录保留，按需要查看即可。</p>
<h2>2. Function Calling 与结构化输出的分界</h2>
<p>问“查台北的气温”，需要执行查询；问“从这句话抽出城市和温度”，信息已经在句子里。前者主要解决行动与外部数据，后者主要解决答案形状。</p>
<table><tr><th>方法</th><th>通常约束什么</th><th>不能由它保证什么</th></tr>
<tr><td>仅在 Prompt 要求 JSON</td><td>给模型一个格式目标</td><td>不能可靠保证合法 JSON</td></tr>
<tr><td>JSON mode</td><td>通常保证可解析 JSON</td><td>不等于字段符合你的 Schema</td></tr>
<tr><td>Structured Output</td><td>在服务支持范围内约束结构</td><td>不保证事实正确、完整、没有拒答</td></tr>
<tr><td>Function Calling</td><td>给出工具名称与参数请求</td><td>不等于已执行、已授权或已成功</td></tr></table>
<p>两者可以组合：工具先获取可信结果，模型再把最终数据按 Schema 返回。为了先看懂区别，当前抽取示例没有 tools 参数，也没有工具执行入口。</p>
''' + code("07_structured_output.py") + block("python 07_structured_output.py") + '''
<p>正常得到 city=台北、temperature=26、unit=celsius。代码还检查这些值是否忠实于输入，所以 JSON 合法但温度写成 30 仍然报错。本课使用本地 Ollama 的兼容结构化接口；不承诺任意 compatible endpoint 都支持相同字段。</p>
<h2>3. 严格模式不是跨供应商统一开关</h2>
<p>OpenAI strict 模式在其支持的 Schema 子集中要求对象关闭额外字段，并将属性列入 required；可选含义常用允许 null 表达。这个模式的保证不能仅凭在兼容请求里加 strict=true 就自动获得。</p>
<p>Anthropic 使用自己的 tools/input_schema 和严格工具约束；Ollama 原生结构化输出使用 format。实际调用前要检查服务及模型支持。本课主线没有使用 OpenAI 云端的 strict 保障，仍会在 Python 中验证结果。</p>
<h2>4. Anthropic 的完整替代实现</h2>
<p>Claude 消息没有 role=tool：assistant 返回 tool_use 块，你用 user 消息送 tool_result，tool_use_id 关联原请求。工具结果消息紧接对应 assistant，批次里每个请求都要有结果，失败加 is_error=true。</p>
<p>如果模型返回 thinking 或带签名的内容块，历史中原样保留完整 assistant 内容；只在最终展示时提取 text。不要为了“让历史更干净”过滤并重建原响应。</p>
''' + code("08_anthropic_agent.py") + '''
<h3>默认离线，先理解消息形状</h3>
''' + block("python 08_anthropic_agent.py") + '''
<p>这会打印固定脚本的消息往返，不需安装 Anthropic SDK，不需密钥，不收云端费用。协议测试也已提供，不能把它当成真实 Claude 质量测试。</p>
<h3>可选：自己运行云端路径</h3>
<p>只想学本课时，完成本地案例即可。需要比较供应商时，在账号中确认可用模型 ID 和价格，并配置费用控制。密钥通过终端环境读取，不写到 Python 文件或课程页面。</p>
''' + block('''python -m pip install anthropic
read -s "ANTHROPIC_API_KEY?输入你的 Anthropic 密钥："
export ANTHROPIC_API_KEY
read "ANTHROPIC_MODEL?输入账号可用的模型 ID："
export ANTHROPIC_MODEL
python 08_anthropic_agent.py --live''') + '''
<p>以上 read 写法适用于你当前 macOS zsh。云端代码不硬编码一个可能过期的模型 ID，不设置 temperature 等跨模型不通用参数。max_tokens=1024 如果不足，程序会明确报告 max_tokens 停止；按实际模型能力和预算调整，不能把截断当成完整结果。</p>
<h2>5. 四种模式不要混用名称</h2>
<table><tr><th>模式</th><th>控制重点</th><th>本课位置</th></tr>
<tr><td>ReAct</td><td>行动与观察交替，更新下一步</td><td>有界工具循环</td></tr>
<tr><td>Reflection</td><td>根据反馈改进下一次尝试</td><td>单元12结合失败反馈展开</td></tr>
<tr><td>Reflexion</td><td>记录文字经验，在后续尝试中利用</td><td>单元12含完整流程与轻量文件记忆</td></tr>
<tr><td>Self-Refine</td><td>生成、反馈、修订当前输出</td><td>单元12含修订与防退步验证</td></tr></table>
<p>这些模式不自动意味着更可靠。模型可能批评错、把正确答案改坏，或者重复同样的动作。要判断它是否可靠，仍需核对实际结果、检查权限和执行限制，并运行评测。更长的 planning、持久记忆、工作流图与框架属于后续阶段。</p>
''' + source(2, 6, 7, 8, 12, 13, 14) + quiz("a7", "Structured Output 输出的温度格式合法，意味着什么？", ["已查询真实天气", "只说明结构合规", "业务语义必定对"], 1, "结构合规不能证明事实、业务语义或工具执行正确。")

CONTENT[7] = '''
<h2>1. 先闭卷回忆，再运行程序</h2>
<p>这一页是课后练习。先不翻正文写出答案，再展开核对。代码练习直接修改本课副本，保留原始可运行版本作为对照。每题都有可观察的验收条件。</p>
<h3>题 1：用自己的话写出五步往返</h3>
<p>按 schema、call、execute、result、answer 解释每一步由谁负责。再说明为什么一次查天气通常要问模型两次。</p>
<details><summary>参考答案与检查点</summary><p>程序定义 Schema；模型提出工具请求；程序验证并执行函数；程序把对应 ID 的结果交回；模型根据结果回答。第一轮还没有结果，第二轮才看得到结果。完整消息历史必须包含 assistant 请求和 tool 结果。</p></details>
<h3>题 2：只会写 JSON，算不算调用了工具</h3>
<p>模型 content 打印出一个含 name 和 arguments 的 JSON，但 tool_calls 为空。它是否完成了本课原生工具调用？程序应该自动执行这段文字吗？</p>
<details><summary>参考答案与检查点</summary><p>没有。它生成了普通文字，没有按当前原生协议返回工具请求。不能把文字里看起来像函数的片段直接执行。记录原始响应，核对工具支持和请求格式。</p></details>
<h3>题 3：检查一条消息序列</h3>
<p>历史只有 user 问题和 tool 结果，遗漏 assistant 工具请求。指出缺失的角色、ID 的关联，以及修复位置。</p>
<details><summary>参考答案与检查点</summary><p>应先保存包含 tool_calls 的完整 assistant 消息，再为每个 call 添加同 ID 的 tool 结果；不能只把一个城市名或结果贴回历史。</p></details>
<h2>2. 编码练习：能运行才算完成</h2>
<h3>题 4：增加一个城市，仍然是固定数据</h3>
<p>在 tools.py 的 WEATHER 中加入“广州”=30.0，并同步更新工具用途说明和未知城市错误说明。运行单工具问题查询广州。不要把固定值包装成实时天气。</p>
<p><strong>验收：</strong>有 get_weather 请求、参数为广州、observation 为 30.0、最终回答标明教学数据。已有测试仍通过。</p>
<details><summary>完整参考补丁</summary><p>下面的完整补丁对应当前 tools.py：更新固定数据、工具说明和错误说明，并同步修改相关注释。请在未做过这项练习的副本上应用，其他文件使用项目中完整版本。先检查，再应用：</p>
''' + block('''patch --dry-run -p1 -i exercise_04_solution.patch
patch -p1 -i exercise_04_solution.patch
python 03_agent_loop.py "查询广州的示例气温。"''') + code("exercise_04_solution.patch") + '''</details>
<h3>题 5：用已有代码完成一个新计算</h3>
<p>让 Agent 先计算 18+7，再将结果除以 5。不能在入口文件里硬编码答案。</p>
''' + block('python 03_agent_loop.py "先用工具计算 18 加 7，再把实际结果除以 5。"') + '''
<p><strong>验收：</strong>出现 add 与 divide，两次调用在不同模型轮次；第二次 left=25、right=5；最后答案为 5。若模型一次写出两个调用且提前猜参数，这一题不通过。</p>
<details><summary>完整参考实现在哪里</summary><p>原有 tools.py、agent.py、model_client.py 与 03_agent_loop.py 已支持此题，无需补充代码。<a href="../reference/code-library.html">完整代码集</a>包含全部四个文件。先证明已有通用循环能完成新问题，再考虑加代码。</p></details>
<h3>题 6：错误一定不会执行</h3>
<p>运行离线测试，定位“额外字段”“除以零”“未知工具”对应测试。再找出校验发生在执行函数之前的那一行。</p>
<p><strong>验收：</strong>三类输入均返回 ok=false；未授权工具不会执行；模型拿到的是错误结果而非伪造成功。完整测试是<a href="../reference/code-library.html#test_agent-py">test_agent.py</a>，可直接运行，无空函数需要补。</p>
<h3>题 7：证明循环会停</h3>
<p>运行 test_step_limit，阅读两轮持续请求的测试替身。说明为什么“模型不继续”与“程序强制停止”是两种独立停止条件。</p>
''' + block("python -m unittest test_agent.LoopTests.test_step_limit -v") + '''
<p><strong>验收：</strong>持续请求在两轮后抛出上限错误；普通问候一轮即结束。不靠人工按 Ctrl+C 验收。</p>
<h3>题 8：Schema 实验</h3>
<p>先跑 good 的一轮五题，再跑 weak 与 good 各五轮。将结果按失败类型分类。之后只恢复弱版本的 description，再重新比较，验证描述是否真有帮助。</p>
<p><strong>验收：</strong>记录真实任务数和成功数；保留答案及轨迹；不混改模型、题目和循环；不把离线脚本成绩写成模型成绩。完整评测代码和题目已经提供。</p>
<h2>3. 综合项目：两个工具的天气助手</h2>
<p>项目入口使用 04_multi_step.py，只暴露 get_weather 和 convert_temperature。完整实现已经包含在本目录；先跑通参考版，再闭卷尝试自己重写循环，最后对照测试找差距。</p>
<table><tr><th>固定任务</th><th>验收</th></tr>
<tr><td>查询台北示例气温</td><td>天气工具、26°C、注明固定数据</td></tr>
<tr><td>查询上海并换成华氏</td><td>先取得 22°C，再换算 71.6°F</td></tr>
<tr><td>把 0°C 换成华氏</td><td>只需换算工具，结果 32°F</td></tr>
<tr><td>查询火星</td><td>明确工具失败，不虚构温度</td></tr>
<tr><td>一句问候</td><td>不调用工具，正常结束</td></tr></table>
<p>逐题运行下面的命令，保存完整输出，再根据实际调用过程判断五题是否通过。</p>
''' + block('''python 04_multi_step.py "查询台北的示例气温。"
python 04_multi_step.py "查询上海的示例气温，再用工具换算为华氏。"
python 04_multi_step.py "请用工具把摄氏 0 度换算为华氏。"
python 04_multi_step.py "查询火星的示例气温，没有就说明没有。"
python 04_multi_step.py "你好，用一句话回应。"''') + '''
<h2>4. 评分与复习安排</h2>
<p>概念题 1–3 每题 10 分；编码题 4–7 每题 10 分；Schema 实验 10 分；综合项目 20 分，共 100 分。概念说对但无法跑通，不计对应代码分；存在未授权执行或没有上限时，先修边界再进入下一阶段。</p>
<p>学完当下：独立画出五步往返。第二天：不看正文重写循环骨架，并运行停止测试。一周后：混合运行天气、计算、错误和问候，解释每种情况为什么需要或不需要工具。</p>
<h2>5. 进入补充单元前的基础检查</h2>
<ul class="checklist"><li>能解释 Tool Call 与 Tool Result，知道谁执行代码。</li><li>能写工具接口，也能在程序中验证输入与权限。</li><li>单工具、多工具、依赖任务各成功运行过一次。</li><li>至少看过一次明确失败，并能解释错误所在层次。</li><li>循环能自然结束，也能在次数上限强制结束。</li><li>能用固定题和真实记录比较 Schema。</li></ul>
<p>完成基础自检后继续单元9–14，最后在单元15完成补充课后练习。第四阶段再学习工作流图与框架。如果卡在某题，把题号和完整输出发给我。</p>
'''


READINGS = '''
<p class="eyebrow">Required Reading · 全部在本地</p><h1>三份必修阅读<br>中文知识讲义</h1>
<p class="lede">这里把本阶段需要从三份资料掌握的内容合并讲清。直接读本页，再做本地案例。官方来源名称用于说明依据，不是额外阅读任务。</p>
<nav class="toc"><ol><li><a href="#s1">Ollama：工具如何进入对话</a></li><li><a href="#s2">Anthropic：模型与执行端的契约</a></li><li><a href="#s3">ReAct：行动与观察怎样配合</a></li><li><a href="#supplement">其他参考知识与资料目录</a></li></ol></nav>
<h2 id="s1">必修一 · Ollama Tool Calling</h2>
<p>要点是把工具能力写入请求，让模型返回工具调用，再将执行结果放回历史。它支持单次往返，也支持多工具和多轮交互。</p>
<p>一次返回多个工具请求时，应处理整组请求并返回每个结果。对话进入下一轮，模型才能据观察决定继续调用或回答。流式模式需要先收齐工具参数，不能拿未完成的片段执行。</p>
<p>原生 Ollama 的工具参数通常是对象，结果消息可用 tool_name。兼容 Chat Completions 则按 function.arguments 和 tool_call_id 处理。本课的主线固定使用后者，不混用两套字段。</p>
<p>本地对应：<a href="../lessons/0003-first-tool.html">单工具往返</a>、<a href="../lessons/0004-agent-loop.html">多工具与循环</a>。先跑成功路径，再用上限测试检查持续调用的情况。</p>
<h2 id="s2">必修二 · Anthropic How Tool Use Works</h2>
<p>工具接口是一份契约：程序提供可用操作与输入说明，模型决定提出哪个请求，执行端运行操作，再将结果送回模型。模型不会自行运行你本机的函数实现。</p>
<p>client tool 在你的程序中执行。即使工具 Schema 来自厂商，例如某些桌面或编辑器工具，其执行位置也可能仍在客户端。server tool 则由供应商基础设施执行，不能机械套用本地函数的回传流程。</p>
<p>对 client tool，Claude 返回 tool_use 内容块和相应停止原因。程序读取 id、name、input，执行后发回 tool_result。模型可以继续提出工具请求，直到形成最终回答。</p>
<p>消息格式与异常处理见本页 S6 和<a href="../lessons/0007-reading-and-protocols.html">单元 7 的完整实现</a>。使用哪家模型不改变程序仍需负责输入验证、权限与执行边界这一点。</p>
<h2 id="s3">必修三 · ReAct 原始论文</h2>
<p>论文由 Shunyu Yao 等人提出，将语言推理与环境行动交错：行动带来新的观察，观察帮助模型调整之后的决策。它在知识问答与交互任务中研究这种组合，而不是仅靠一次性生成答案或固定行动序列。</p>
<p>论文任务包括 HotpotQA、FEVER、ALFWorld 和 WebShop。它展示的是特定模型与实验设置下的效果，不意味着所有工具任务只要加 ReAct 就提高。错误的早期假设、检索失败和反复无效行动仍可能造成失败。</p>
<p>本课借鉴论文中的反馈循环，使用现代原生工具调用来演示，没有复现论文完整的提示轨迹或实验环境。学习时重点观察 action、observation 与后续参数之间是否有因果联系，不要求展示私有思维链。</p>
<p>本地练习：把查到的温度交给换算工具；检查第二次调用发生在结果之后。如果后一步只是提前猜值，最终答案正确也没证明完成了交互式推理。</p>
<h2 id="supplement">补充参考知识 · 都已纳入正文</h2>
<h3 id="s4">S4 · Ollama 的 OpenAI 兼容接口</h3>
<p>SDK 是客户端，模型由请求地址决定。本地 base_url 指向 localhost:11434/v1，api_key 占位值不代表云端授权。兼容接口覆盖部分 OpenAI API，不承诺每个字段或保证都一致。原生与兼容协议要分别核对。</p>
<h3 id="s5">S5 · 工具定义</h3>
<p>工具名称要能对应一个具体动作；描述说清用途、适用条件和边界；每个参数说明类型、含义与合法选择。不要把用户没授权的业务动作混入一个模糊的万能工具。完整接口见单元 2。</p>
<h3 id="s6">S6 · Anthropic 请求与结果处理</h3>
<p>tool_use 使用 id、name、input。结果放在 user 消息的 tool_result 块，用 tool_use_id 原样关联；失败加 is_error=true。结果消息紧接对应 assistant；多请求返回对应的整组结果。保留 assistant 完整内容块，展示答案时只提取 text。外部结果按不可信数据处理。</p>
<h3 id="s7">S7 · OpenAI Function Calling</h3>
<p>本课使用 Chat Completions：tools 包含 type/function，名称和 parameters 在 function 内；返回 tool_calls，每条有独立 id，结果用 role=tool 和 tool_call_id。Responses API 的工具、输出项与结果结构不同，不能直接照搬这套消息格式。strict 是服务支持范围内的结构约束，不是业务授权。</p>
<h3 id="s8">S8 · 结构化输出</h3>
<p>本地 Ollama 可对响应指定 JSON 或 Schema 格式。JSON 语法正确、字段结构合规、内容语义正确是三道不同检查。模型拒答、输出截断或抽取值错误时，不能因为拿到了一个对象就算成功。</p>
<h3 id="s9">S9 · JSON Schema</h3>
<p>properties 声明属性，required 指定必填，additionalProperties 控制未声明属性。它们相互独立。enum 限制可选值，minimum/maximum 限制数值范围。应用权限、真实数据存在性与业务合法性仍由程序检查。</p>
<h3 id="s10">S10 · SDK 超时与重试</h3>
<p>SDK 可能自带重试。为了控制尝试总数，要明确关闭或设置它，再决定是否自己重试。请求超时不证明服务端没有执行；写操作重试需要幂等设计。本课为只读工具，传输最多额外重试一次。</p>
<h3 id="s11">S11 · 顺序与并行工具</h3>
<p>多个互不依赖的查询可以形成一批调用；后一步依赖前一步结果时，必须等待观察再继续。主线默认顺序执行，单元10提供真正并发执行的完整替代入口和重叠测试。</p>
<h3 id="s12">S12 · 严格工具约束</h3>
<p>严格参数约束有助于让请求符合接口形状。它既不证明模型选对工具，也不证明当前登录用户有权执行该操作。不同服务的参数名与支持范围不同；本课用 Python 再验证，不从“兼容”推断严格保证。</p>
<h3 id="s13">S13 · Reflexion</h3>
<p>Reflexion 根据任务反馈总结文字经验，再保存这些经验，供后续尝试参考；这个过程不会通过本次交互更新模型权重。单元 12 提供完整的最小实现和可选文件记忆，更完整的记忆架构留待后续阶段。</p>
<h3 id="s14">S14 · Self-Refine</h3>
<p>Self-Refine 通过生成、反馈和修订反复改进当前输出。反馈者也可能出错，修订要用明确标准验收，并允许原答案已经正确。单元12提供完整代码、独立规则检查和拒绝退步的测试。</p>
<h2>扩展资料在原路线中各负责什么</h2>
<table><tr><th>方向</th><th>资料名称</th><th>本阶段学习到哪里</th></tr>
<tr><td>官方课程与案例</td><td>Anthropic Courses、Tool Use Cookbook、Quickstarts；Microsoft AI Agents for Beginners</td><td>掌握接口、执行和状态；本课已提供对应独立案例</td></tr>
<tr><td>从零实现</td><td>ai-agents-from-scratch、react-from-scratch、agent-implementation、GenericAgent</td><td>先能自己解释当前循环，再比较其他封装</td></tr>
<tr><td>框架与 CodeAct</td><td>Smolagents、QuantaLogic、LangChain ReAct Agent</td><td>知道固定函数请求与生成可执行代码的能力边界不同</td></tr>
<tr><td>中文教材</td><td>hello-agents、HelloAgents</td><td>保留扩展路线，不作为本课前置</td></tr>
<tr><td>结构化输出库</td><td>Instructor、Outlines</td><td>分别关注类型验证与约束解码，不替代业务检查</td></tr></table>
<p>这些仓库的全部源码不在本课覆盖范围。完成本课无需访问它们；需要核查出处时，外部链接集中保存在目录内 RESOURCES.md。</p>
'''


CHEATSHEET = '''
<p class="eyebrow">Reference · 快速查阅</p><h1>术语、消息协议<br>与故障速查</h1>
<h2>最短记忆链</h2><div class="formula">schema → call → validate / execute → result → answer 或下一轮</div>
<table><tr><th>看到的东西</th><th>它是什么</th><th>它不保证什么</th></tr>
<tr><td>Schema</td><td>接口说明</td><td>执行权限与业务正确</td></tr>
<tr><td>Tool Call</td><td>请求名称、参数和 ID</td><td>函数已经执行</td></tr>
<tr><td>Tool Result</td><td>对应请求的返回数据</td><td>外部内容绝对可信</td></tr>
<tr><td>Structured Output</td><td>受约束的输出数据</td><td>事实与语义正确</td></tr>
<tr><td>Trace</td><td>行动、观察、最终回答记录</td><td>完整私有思维链</td></tr>
<tr><td>Mock / 离线替身</td><td>固定脚本代替模型</td><td>真实模型成功率</td></tr>
<tr><td>Allowlist / 白名单</td><td>程序允许执行的函数集合</td><td>任意请求都值得执行</td></tr>
<tr><td>Eval / 评测</td><td>固定输入与验收规则</td><td>一次成绩代表全部任务</td></tr></table>
<h2>三种消息信封</h2>
<table><tr><th>项目</th><th>本课 Chat Completions</th><th>Anthropic Messages</th><th>Ollama 原生</th></tr>
<tr><td>工具定义</td><td>type/function/parameters</td><td>name/input_schema</td><td>type/function/parameters</td></tr>
<tr><td>请求位置</td><td>message.tool_calls</td><td>content 内 tool_use</td><td>message.tool_calls</td></tr>
<tr><td>参数</td><td>function.arguments 通常为字符串</td><td>input 对象</td><td>function.arguments 对象</td></tr>
<tr><td>结果角色</td><td>tool</td><td>user 中的 tool_result</td><td>tool</td></tr>
<tr><td>结果关联</td><td>tool_call_id</td><td>tool_use_id</td><td>按其原生协议含 tool_name 等字段</td></tr>
<tr><td>最终文字</td><td>message.content</td><td>提取 type=text 的内容块</td><td>message.content</td></tr></table>
<p>本表不是 OpenAI Responses API 的结构；Responses 有不同输出项和工具结果类型。本课只实际接入 Chat Completions 与 Anthropic Messages，Ollama 原生一列用于解释官方阅读材料。</p>
<h2>执行前检查</h2><ol><li>请求结构合法，有唯一 ID。</li><li>函数在本次授权的工具列表中。</li><li>参数能解析为对象，字段无缺失或额外。</li><li>字符串、枚举、数值类型与范围合法。</li><li>当前身份拥有操作权限，且操作符合业务规则。</li><li>次数、时间与消耗检查允许继续。</li></ol>
<h2>现象 → 先查哪里</h2>
<table><tr><th>现象</th><th>第一检查项</th></tr>
<tr><td>只打印 CompletionUsage</td><td>打印的是统计字段，回答要读 message.content</td></tr>
<tr><td>content 为空</td><td>是否存在 tool_calls；是否被截断；不要直接认定失败</td></tr>
<tr><td>不调用工具</td><td>原生工具支持、tools 是否传入、用途说明是否清楚</td></tr>
<tr><td>提示 result 没有对应 ID</td><td>assistant 历史是否保存，ID 是否原样回传</td></tr>
<tr><td>重复调用同一工具</td><td>结果是否真正加入下一轮历史，结果能否读懂</td></tr>
<tr><td>Unsupported 参数错误</td><td>模型和兼容接口是否支持 reasoning_effort / response_format</td></tr>
<tr><td>模型 404</td><td>ollama list 中是否真的有该模型名</td></tr>
<tr><td>连接拒绝</td><td>Ollama 是否运行，端口是否为 11434</td></tr>
<tr><td>天气“实时”但没有来源时间</td><td>本课只是固定数据，真实产品需另接可信服务</td></tr></table>
<p><a href="code-library.html">所有案例和测试的完整代码</a> · <a href="coverage.html">知识覆盖表</a></p>
'''


extend_course(LESSONS, CONTENT, code, block, quiz, source)
READINGS += EXTRA_READINGS
CHEATSHEET += EXTRA_CHEATSHEET


def build():
    for directory in ("lessons", "reference"):
        (ROOT / directory).mkdir(exist_ok=True)
    write_notes_file(ROOT)
    for index, (filename, title, purpose) in enumerate(LESSONS):
        intro = f'<p class="eyebrow">Stage 03 · 单元 {index + 1:02}</p><h1>{title}</h1><p class="lede">{purpose}</p>'
        previous = f'<a href="{LESSONS[index - 1][0]}">← {LESSONS[index - 1][1]}</a>' if index else '<a href="../index.html">← 第三课首页</a>'
        following = f'<a href="{LESSONS[index + 1][0]}">{LESSONS[index + 1][1]} →</a>' if index + 1 < len(LESSONS) else '<a href="../../04-agent-frameworks/index.html">完成本课验收后，进入第四课 →</a>'
        body = intro + banner(ROOT.name, filename[:-5]) + mark_sections(CONTENT[index], ROOT.name, filename[:-5]) + f'<div class="next-prev">{previous}{following}</div>'
        (ROOT / "lessons" / filename).write_text(page(title, body))

    cards = "".join(f'<li>{badge(PRIORITIES[ROOT.name]["lessons"][name[:-5]])}<a href="lessons/{name}">{title}</a><small>{purpose}</small></li>' for name, title, purpose in LESSONS)
    index_body = '''<p class="eyebrow">Stage 03 · Tool Use &amp; Hello Agent</p>
<h1>工具使用与<br>第一个 Agent Loop</h1>
<p class="lede">让模型提出请求，让 Python 安全执行，再根据结果继续。沿用你现有的 Ollama 环境，写出不依赖框架、能测试、会停止的第一个 Agent。</p>
<div class="callout success"><strong>直接在本项目学习。</strong>讲解、三份必修阅读的中文知识整理、完整代码、测试、参考速查与课后练习全部在这里。无需回原始网站完成学习步骤。</div>
<p class="meta">开始前，你需要能运行 Python，认识函数、list 和 dict，并学过第二课的 Prompt 内容。主线使用 Ollama + gemma4:e4b，第三课单独存放，不覆盖第二课。</p>
<p><strong>扩展选读（单元9–15）：</strong>流式、工具选择、真正并发、ReAct研究与检索、Self-Refine/Reflexion、Instructor/Outlines、CodeAct及对应练习。需要这些能力时再学，每个案例均有完整代码。</p>
''' + banner(ROOT.name) + '''<h2>按顺序学习</h2><ol class="lesson-list">''' + cards + '''</ol>
<h2>本地资料</h2><div class="two-col"><div><h3>必要阅读</h3><p><a href="reference/readings.html">Ollama、Anthropic、ReAct 中文讲义</a></p><p>学习本阶段需要的知识已整合，不额外布置英文原文阅读。</p></div>
<div><h3>复习与实操</h3><p><a href="reference/cheatsheet.html">术语与消息协议速查</a></p><p><a href="reference/code-library.html">所有完整案例与测试</a></p><p><a href="reference/coverage.html">原路线知识覆盖表</a></p></div></div>
<h2>先跑一个不用模型的验证</h2>''' + block('''cd /Users/owen/Documents/ai-learn
source .venv/bin/activate
cd courses/03-tool-use-and-hello-agent/examples
python -m unittest discover -p 'test_*.py' -v
python 05_error_recovery.py''') + '''
<h2>学完能交付什么</h2><ul><li>单工具、多工具和有依赖的连续调用。</li><li>白名单、参数检查、错误结果和明确停止条件。</li><li>一份固定五题的 Schema 评测记录。</li><li>只读天气小助手及课后练习的可验证结果。</li></ul>
<p>本课包含阶段 3 的教学目标和六组练习。扩展仓库作为参考方向保留，没有收录它们的全部源码或论文附录。天气案例使用固定教学数据，不是实时预报。</p>'''
    (ROOT / "index.html").write_text(page("工具使用与第一个 Agent Loop", index_body, depth=0))
    (ROOT / "reference/readings.html").write_text(page("本地必修阅读", READINGS))
    (ROOT / "reference/cheatsheet.html").write_text(page("术语与协议速查", CHEATSHEET))

    files = ["tools.py", "model_client.py", "agent.py", "01_hello_tool.py", "02_multi_tool.py", "03_agent_loop.py",
             "04_multi_step.py", "05_error_recovery.py", "06_schema_eval.py", "eval_cases.json",
             "07_structured_output.py", "08_anthropic_agent.py", "test_agent.py", "test_anthropic.py", "exercise_04_solution.patch", "requirements.txt"] + EXTRA_FILES
    links = "".join(f'<li><a href="#{name.replace(".", "-")}">{name}</a></li>' for name in files)
    library = '<p class="eyebrow">Complete Code · 源码直接嵌入</p><h1>完整案例与测试代码</h1><p>以下直接展示实际文件的全部内容。程序入口与依赖均已提供；保留 examples 整个目录即可运行。无需网络加载代码，浏览器打开本地文件也能查看。</p><nav class="toc"><ul>' + links + '</ul></nav>'
    library += "".join(code(name) for name in files)
    (ROOT / "reference/code-library.html").write_text(page("完整代码集", library))

    rows = [
        ("八个核心术语、方法选择", 0, "术语表、普通回答/结构化输出/工具循环对照"),
        ("五条执行边界", 4, "白名单、验证、最小权限、确认、次数与超时"),
        ("必修阅读：Ollama、Anthropic、ReAct", 6, "本地讲义与协议对照，不需要外站学习"),
        ("练习 1：单工具", 2, "01_hello_tool.py，含完整依赖"),
        ("练习 2：多工具选择", 3, "02_multi_tool.py，天气/计算选择"),
        ("练习 3：从零循环", 3, "agent.py、03_agent_loop.py，停止条件测试"),
        ("练习 4：多步骤依赖", 3, "04_multi_step.py，实际结果参与下一步"),
        ("练习 5：错误处理", 4, "05_error_recovery.py，离线与真实恢复路径"),
        ("练习 6：Schema 对比", 5, "06_schema_eval.py、五题和真实记录"),
        ("Structured Output、JSON mode、strict", 6, "07_structured_output.py，语义与结构分开验收"),
        ("Anthropic 替代路径", 6, "08_anthropic_agent.py，原生协议、错误与内容块保留"),
        ("天气小助手", 7, "两个只读工具、完整实现与五题验收"),
        ("Reflection、Reflexion、Self-Refine、Planning", 6, "概念差异及后续阶段边界"),
        ("环境、时间、费用", 0, "复用已安装模型；云端不沿用旧价格与旧模型假设"),
        ("扩展项目与参考资料", 6, "本地阅读页分类索引，RESOURCES.md 来源审计"),
        ("课后练习与进阶条件", 7, "8 题、参考答案、综合项目、间隔复习"),
    ] + EXTRA_COVERAGE
    table = "".join(f'<tr><td>{escape(topic)}</td><td><a href="../lessons/{LESSONS[i][0]}">单元 {i + 1}</a></td><td>{escape(detail)}</td></tr>' for topic, i, detail in rows)
    coverage = '<p class="eyebrow">Coverage · 教学范围核对</p><h1>第三课知识覆盖表</h1><p>按原路线逐项落实。主线使用当前项目的 Ollama 环境，云端保留独立完整替代实现。</p><table><tr><th>原路线主题</th><th>本地位置</th><th>落实方式</th></tr>' + table + '</table><p>必读材料已按本阶段的学习目标整理成中文讲解。它不等于整个官方文档站或所有扩展仓库的全文翻译；课程中的程序案例都有完整文件，可以在本地查看。</p>'
    (ROOT / "reference/coverage.html").write_text(page("知识覆盖表", coverage))


if __name__ == "__main__":
    build()
    print(f"已生成第三课首页、{len(LESSONS)} 个学习单元、4 份本地参考页面。")
