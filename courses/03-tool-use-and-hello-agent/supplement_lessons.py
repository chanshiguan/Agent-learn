"""第三课补充单元：每个知识点都配本地讲解、完整代码与验收。"""

EXTRA_FILES = [
    "09_streaming_tools.py", "10_tool_choice.py", "11_parallel_tools.py", "learning_client.py",
    "12_self_refine.py", "13_reflexion.py", "14_instructor.py", "15_outlines.py",
    "16_codeact.py", "17_react_retrieval.py", "test_advanced.py", "verify_libraries.py", "requirements-libraries.txt",
]

EXTRA_COVERAGE = [
    ("流式调用与片段组装", 8, "完整收集器、断流/截断处理、真实往返"),
    ("工具选择控制", 9, "auto、none、required、指定名称；后续恢复auto"),
    ("真正并发执行", 9, "线程池、结果顺序、ID关联、并发重叠测试"),
    ("ReAct研究方法、实验与局限", 10, "基线、任务、指标、原始结果、原创两跳检索案例"),
    ("Self-Refine与Reflexion完整流程", 11, "生成/反馈/修订、Actor/Evaluator/记忆，离线与真实模型路径"),
    ("Instructor与Outlines", 12, "兼容环境、完整抽取代码、验证与重试、约束解码边界"),
    ("CodeAct与执行边界", 13, "受限Python解释器、多工具组合、攻击语法拒绝测试"),
    ("补充课后练习", 14, "7题、完整参考实现、跨主题综合验收"),
]

EXTRA_READINGS = '''
<h2 id="supplement-full">扩展主题的本地学习入口</h2>
<p>流式、工具选择、并发、论文方法、反思、类型化生成和代码行动分别有独立单元。下面列出知识来源，点击本地链接即可进入相应讲解。</p>
<h3 id="s15">S15 · Instructor：类型验证与有限重试</h3>
<p>Instructor 在模型客户端上增加 response_model 与验证失败后的重新尝试。Pydantic 定义可检查的数据契约；程序仍需决定哪些业务规则必须满足、允许几次尝试。完整教学在<a href="../lessons/0013-instructor-and-outlines.html">单元13</a>。</p>
<h3 id="s16">S16 · Outlines：输出类型与生成约束</h3>
<p>Outlines 用输出类型组织结构化生成。连接 Ollama 时，本例将 JSON Schema 交给后端，而非在 Python 客户端逐token控制远端模型。不同后端支持的 Schema、正则或文法范围不同。完整代码在单元13。</p>
<h3 id="s17">S17 · CodeAct：把代码作为行动</h3>
<p>CodeAct 将可执行代码作为行动表示，便于表达变量、计算和多个工具的组合，并通过执行反馈继续处理。完整 Python 执行器需要独立隔离策略。本课用原创受限解释器展示关键流程，见<a href="../lessons/0014-codeact.html">单元14</a>。</p>
<h3 id="s18">S18 · Python AST</h3>
<p>ast.parse 将源码变成语法树，不会因为解析就运行代码。本课只解释明确列出的节点；解析成功本身不代表代码安全。未实现的语法统一拒绝。</p>
<h3 id="s19">S19 · Python线程池</h3>
<p>submit 提交函数并返回 Future，result 取得对应结果。线程池可以重叠等待型工作；超时等待不等于停止已开始的线程。完整并发案例在<a href="../lessons/0010-choice-and-concurrency.html">单元10</a>。</p>
<h3 id="s20">S20 · 代码执行隔离</h3>
<p>本课解释器没有文件、网络、导入或任意宿主函数入口，只适合教学中的有限任务。要运行完整Python，应另外配置进程/容器或远程隔离、资源限制和凭证边界，不能靠删除builtins或一段提示词获得完整隔离。</p>
'''

EXTRA_CHEATSHEET = '''
<h2>补充术语与调用路径</h2>
<table><tr><th>术语</th><th>快速解释</th><th>本地单元</th></tr>
<tr><td>Delta / 流式片段</td><td>一次增量，不等于完整消息或完整参数</td><td><a href="../lessons/0009-streaming-tools.html">9</a></td></tr>
<tr><td>index / call ID</td><td>前者分组片段，后者关联调用结果</td><td>9</td></tr>
<tr><td>tool_choice</td><td>控制模型生成哪种请求，不授予执行权限</td><td><a href="../lessons/0010-choice-and-concurrency.html">10</a></td></tr>
<tr><td>Concurrency / 并发</td><td>任务在时间上重叠；需要保持结果关联</td><td>10</td></tr>
<tr><td>Future</td><td>已提交任务的结果句柄，不保证立刻完成</td><td>10</td></tr>
<tr><td>EM / 精确匹配</td><td>答案是否匹配标准，不是过程观感评分</td><td><a href="../lessons/0011-react-paper.html">11</a></td></tr>
<tr><td>Self-Refine</td><td>生成、反馈、修订当前输出</td><td><a href="../lessons/0012-feedback-and-memory.html">12</a></td></tr>
<tr><td>Reflexion</td><td>依据任务反馈形成经验，供下一次尝试使用</td><td>12</td></tr>
<tr><td>Instructor</td><td>类型化抽取、验证与有限重试的封装</td><td><a href="../lessons/0013-instructor-and-outlines.html">13</a></td></tr>
<tr><td>Outlines</td><td>用输出类型组织不同后端的结构化生成</td><td>13</td></tr>
<tr><td>Constrained Decoding / 约束解码</td><td>在生成时限制不符合结构的候选；支持范围依后端</td><td>13</td></tr>
<tr><td>CodeAct</td><td>用代码表示行动，通过执行观察继续处理</td><td><a href="../lessons/0014-codeact.html">14</a></td></tr>
<tr><td>AST / 抽象语法树</td><td>源码的语法结构；解析成功不表示安全</td><td>14</td></tr></table>
<p>完整验收顺序：先跑离线边界测试，再跑本机模型；有副作用的能力需另行设计执行策略。本课的只读和受限代码能力不自动扩展为生产权限。</p>
'''


def extend_course(lessons, content, code, block, quiz, source):
    lessons.extend([
        ("0009-streaming-tools.html", "流式工具调用", "把分片参数组装完整，验证完成后再执行。"),
        ("0010-choice-and-concurrency.html", "工具选择控制与并发执行", "控制模型何时调用工具，正确关联并发结果。"),
        ("0011-react-paper.html", "ReAct论文详解与检索实验", "理解研究方法、对照实验和失败类型，跑通两跳查询。"),
        ("0012-feedback-and-memory.html", "Self-Refine与Reflexion", "让反馈能修正输出、形成可复用经验，同时防止越改越错。"),
        ("0013-instructor-and-outlines.html", "Instructor与Outlines完整实战", "区分类型校验、失败重试与生成约束，运行同一抽取任务。"),
        ("0014-codeact.html", "CodeAct与代码执行边界", "用代码组合工具，在受限解释器中观察执行反馈。"),
        ("0015-extended-exercises.html", "补充课后练习与综合验收", "闭卷解释、运行新案例，用证据检验全部补充内容。"),
    ])

    content[8] = '''
<h2>1. 流式响应改变了什么</h2>
<p>非流式请求一次返回完整 message。流式请求逐块返回 delta，每个 delta 可能只有一段文字、一段工具名或参数片段。用户能更早看见文字，但程序此时未必拿到完整调用。</p>
<p>例如参数先到 <code>{"city":"</code>，下一块才到 <code>台北"}</code>。第一块不是坏 JSON，也不是可以执行的请求；它是尚未完成的参数。正确做法是按调用 index 收集片段，等整轮正常结束，再进入原有验证入口。</p>
<h2>2. index、id、arguments分别负责什么</h2>
<table><tr><th>字段</th><th>作用</th><th>处理方式</th></tr>
<tr><td>index</td><td>这块属于本轮第几个工具请求</td><td>分组收集，不能把不同调用的参数拼一起</td></tr>
<tr><td>id</td><td>请求与结果之间的关联标识</td><td>收集后原样用于tool_call_id</td></tr>
<tr><td>function.name</td><td>请求哪个函数</td><td>收齐后查白名单</td></tr>
<tr><td>function.arguments</td><td>JSON参数文本片段</td><td>按到达次序追加；完整后才解析</td></tr>
<tr><td>finish_reason</td><td>这轮是否正常结束</td><td>截断、缺少结束、拒答均不执行</td></tr></table>
<p>这里讲的是 Chat Completions 兼容流。Ollama 原生流的 message/tool_calls 形状不同，不能把同一个片段组装器不加核对地用于所有协议。</p>
<h2>3. 完整可运行代码</h2>
<p>收集器只组装响应，不运行工具；组装后的普通 message 继续交给 agent.py。因此原有的白名单、输入验证、错误结果、最大轮数都继续生效。</p>
''' + code("09_streaming_tools.py") + block('''python 09_streaming_tools.py
python 09_streaming_tools.py --live''') + '''
<p>第一条用固定片段演示参数怎样拆开、怎样重新合并。第二条会请求本机 Ollama，你应该能看到正确的 get_weather 请求、工具结果和最终回答。单个 delta 只是响应片段，不能直接当成完整答案。</p>
<h2>4. 断流时究竟做什么</h2>
<p>连接中断、finish_reason=length、缺少正常结束块时，当前不完整请求全部不执行。若打算重新请求，应从最后一个完整的对话状态重试，并明确预算；不能把上次的半段参数拼到新请求。</p>
<p>文本增量可以用于页面预览，工具副作用必须等验证完成。若未来要让用户取消请求，取消传输和撤销已经执行的工具动作是两件事；本例只读，不实现撤销。</p>
<h2>5. 本课的边界和验证</h2>
<p>本例每轮最多接收 8 个调用，组装后的内容最多 65536 字符。多个调用的片段交错到达时，先按 index 分组，组装完成后再按 index 排序。字符上限用于限制教学任务的规模，不能拿来估算 token 费用。流式响应的 usage 可能到最后才出现，也可能没有返回；没有 usage 不代表没有消耗。</p>
<p>离线测试专门覆盖交错分片、usage尾块、缺少结束、截断和超长响应。完整测试已纳入代码集。</p>
''' + source(1, 7) + quiz("s9", "工具参数只收到半段JSON时应该怎么做？", ["先运行部分参数", "等待完整再验证", "改用字符串执行"], 1, "片段必须完整组装并验证，之后才能执行工具。")

    content[9] = '''
<h2>1. tool_choice控制模型请求行为</h2>
<table><tr><th>意图</th><th>Chat Completions形状</th><th>用途</th></tr>
<tr><td>模型自行决定</td><td><code>"auto"</code></td><td>常规助手，可回答或调用</td></tr>
<tr><td>本轮不调用</td><td><code>"none"</code></td><td>只回答或只格式化已有结果</td></tr>
<tr><td>必须选一个或多个</td><td><code>"required"</code></td><td>检验是否经过工具路径</td></tr>
<tr><td>指定函数</td><td><code>{"type":"function","function":{"name":"get_weather"}}</code></td><td>验证特定接口，不再测试工具路由能力</td></tr></table>
<p>这些是当前接口对请求生成的控制，不会授予执行权限。程序依然根据本次白名单决定是否运行。none案例同时使用空执行白名单；若接口违反约束返回调用，程序直接停止。</p>
<p>Anthropic对应格式是type=auto/none/any/tool，指定函数用name；不是直接复制上表JSON。部分模型或思考设置不接受强制工具，需要按服务能力处理。兼容端点同样必须实测，不能只因为请求返回200就认为约束有效。</p>
''' + code("10_tool_choice.py") + block('''python 10_tool_choice.py auto
python 10_tool_choice.py none
python 10_tool_choice.py required
python 10_tool_choice.py specific''') + '''
<p>强制模式只用于首轮；收到结果后，下一轮恢复 auto，让模型可以直接回答。如果每轮都设为 required，模型就可能一直请求工具，无法自然结束。指定函数实验不应计入“模型自己选对工具”的评测分数。</p>
<h2>2. 多请求不等于真正并发</h2>
<p>模型同轮提出查台北和查北京，只说明两张请求单同时产生。原来的for循环仍然顺序执行。本节用ThreadPoolExecutor把独立只读调用交给不同工作线程，让它们的等待时间重叠。</p>
<p>如果两个查询各等80毫秒，顺序执行约160毫秒；并发可能接近80毫秒再加调度开销。这是理想示意，实际机器负载、限流和服务端串行都会改变效果，不能把理论值写成成绩。</p>
''' + code("11_parallel_tools.py") + block('''python 11_parallel_tools.py
python 11_parallel_tools.py --live''') + '''
<h2>3. 返回顺序和完成顺序可以不同</h2>
<p>本例先提交全部任务，得到代表待完成结果的 Future 对象，再按原请求顺序调用 result 取回结果。因此，即使北京先完成，也不会把它配给台北的请求 ID。每个成功或错误结果仍然对应原请求；一条查询失败不能被悄悄丢掉。</p>
<p>agent.py在任何任务开始前检查整批ID、请求结构与次数上限；并发函数内的每个调用仍经过execute验证。主线默认仍顺序执行，只有显式传入batch_executor才切换。</p>
<h2>4. 哪些调用可以并发</h2>
<table><tr><th>任务</th><th>能否并发</th><th>原因</th></tr>
<tr><td>查台北与查北京</td><td>可以</td><td>参数互不依赖，均只读</td></tr>
<tr><td>查气温后换算</td><td>不能提前并发</td><td>后一步需要前一步的结果</td></tr>
<tr><td>先扣款再发收据</td><td>不能照搬本例</td><td>有业务顺序、副作用、幂等与确认要求</td></tr></table>
<p>线程适合让多项 I/O 等待重叠，例如等待网络返回；不保证加速纯 Python 的密集计算。future.result 等待超时，也不会终止已经开始的线程。真实网络工具还需设置自身的超时和并发上限。</p>
''' + source(5, 7, 19) + quiz("s10", "并发查询中北京先完成，结果应关联什么？", ["北京的原请求ID", "台北的原请求ID", "最后那条用户消息"], 0, "关联始终取决于原请求ID，而不是完成先后。")

    content[10] = '''
<h2>1. 论文研究问题</h2>
<p>ReAct由Yao等人提出，研究语言决策与环境行动的交替。知识任务用HotpotQA、FEVER；交互任务用ALFWorld、WebShop。历史实验主要使用PaLM-540B，不能把结果直接移植到当前本地模型。</p>
<h2>2. 方法与对照如何读</h2>
<table><tr><th>方法</th><th>论文中的对照意图</th></tr><tr><td>Standard</td><td>直接生成答案</td></tr><tr><td>CoT / CoT-SC</td><td>文本推理；后者多次采样后聚合</td></tr><tr><td>Act</td><td>行动与观察，不加入相同形式的推理轨迹</td></tr><tr><td>ReAct</td><td>推理与行动交错</td></tr></table>
<p>论文检索环境包含search、lookup、finish。其提示通过少量任务轨迹提供示范。现代代码可以用原生工具协议实现反馈循环；本课不要求模型公开私有思维链，也不把当前API实现称为历史提示方法的逐字复现。</p>
<h2>3. 原始实验并不是全面领先</h2>
<table><tr><th>方法</th><th>HotpotQA EM</th><th>FEVER准确率</th></tr><tr><td>Standard</td><td>28.7</td><td>57.1</td></tr><tr><td>CoT</td><td>29.4</td><td>56.3</td></tr><tr><td>CoT-SC</td><td>33.4</td><td>60.4</td></tr><tr><td>Act</td><td>25.7</td><td>58.9</td></tr><tr><td>ReAct</td><td>27.4</td><td>60.9</td></tr></table>
<p class="reading-source">数据来自ReAct论文表1，百分数，属于当时固定实验条件；不是本课程运行成绩。原文也研究了组合方法与微调。</p>
<p>论文观察到检索无效、重复行动与推理错误等失败。可从中得到的工程问题是：你的循环能否识别无进展，证据是否足够，增加请求是否真的改变了结果？这些问题需要轨迹与评测回答。</p>
<h2>4. 看懂指标，才能读懂结论</h2>
<p>EM是最终答案与标准答案的精确匹配，不是“过程看起来合理”。准确率是被判定正确的样本比例；交互任务则看是否达成环境目标。不同任务的分数不能相加当作一个Agent通用能力分。</p>
<p>使用检索可能减少凭空编造，却增加查错资料、读错资料和重复调用的机会。你要同时检查最终答案、证据、请求数和失败类型。某题答对而没有用到工具结果，只能证明答案对，不能证明反馈链有效。</p>
<h2>5. 原创两跳检索实验</h2>
<p>我们虚构“青禾号由林遥设计，林遥出生于海城”两份记录。模型起初只知道问题和可查询实体；第一次查青禾号得到设计者，第二次按观察查林遥，最后回答海城。它与真实百科或现实人物无关。</p>
''' + code("17_react_retrieval.py") + block('''python 17_react_retrieval.py
python 17_react_retrieval.py --live''') + '''
<p>离线版固定展示无资料时回答不知道、取到两条资料后回答海城；这些不是模型实验分数。真实版分别跑无工具与有工具路径，输出答案、轮数和查询轨迹。无工具回答不知道是合理处理信息不足，并不等同于程序故障。</p>
<p>这个教学执行器会先检查证据：拿到 birth_city 以前只接受 search，拿到后才允许 final。模型负责选择查询哪个实体，程序负责阻止在没有证据时直接结束。因此它是受ReAct启发的受控小实验，不是没有约束的自主检索器。</p>
<h2>6. 怎样做自己的小实验</h2>
<p>保持问题、模型、参数、资料版本和评分规则一致，只改变是否允许查询。检查两次查询的实体是否来自前一步观察；将资料中的出生城市换成另一个虚构值后重跑，判断答案是否跟随证据变化。</p>
<p>一次成功不能复现论文结论。若要研究一般质量，应扩展多个两跳问题，避免题目答案泄漏进系统指令；记录搜索失败、错误拼接与最终输出错误，分别计算比例。</p>
''' + source(3) + quiz("s11", "ReAct在某个历史任务得分提高，可以推出什么？", ["所有任务必然更强", "本地模型必然更强", "结论依赖实验条件"], 2, "研究结论需要与其任务、模型、指标和对照条件一起理解。")

    content[11] = '''
<h2>1. 先区分三个反馈层次</h2>
<table><tr><th>名称</th><th>改变什么</th><th>本课实现</th></tr><tr><td>Reflection</td><td>依据反馈调整做法的广义动作</td><td>解释为何失败、下一次检查什么</td></tr><tr><td>Self-Refine</td><td>修订当前这份输出</td><td>草稿→批评→修订</td></tr><tr><td>Reflexion</td><td>让经验影响下一次尝试</td><td>Actor→Evaluator→经验记录→重试</td></tr></table>
<p>Self-Refine研究同一模型提供反馈并修订；Reflexion研究通过文字反馈与记忆帮助后续尝试。它们都不意味着这次调用更新了模型权重。本课分别提供受这些方法启发的完整最小流程，不复现论文全部评测。</p>
<h2>2. Self-Refine：改同一份答案</h2>
<p>任务是把给定事实写成一段中文温度说明。生成器先给草稿，批评器指出遗漏，再由模型修订。调用的是同一模型，职责由不同请求中的任务决定。</p>
<p>判断修改是否有效，不能只听模型说“更好了”。本例还用独立规则检查地点、78.8、华氏、固定示例和非实时说明。如果修改后的规则得分更低，就保留旧稿；最多修改两轮。</p>
''' + code("12_self_refine.py") + block('''python 12_self_refine.py
python 12_self_refine.py --live''') + '''
<p>看trace中的draft、feedback、revision和accepted。离线版故意从不完整草稿开始；真实模型可能一开始就写对，因此可能不产生revision，这同样是正常结果。</p>
<h2>3. Reflexion：经验用于后一次尝试</h2>
<p>Actor负责回答；Evaluator用确定的换算公式和来源类型判断；Reflector把具体失败提炼成一条可检查经验。下一次Actor会收到这些经验，但仍须服从原任务事实。</p>
<p>本例经验是“先乘9/5再加32，保留固定来源类型”。它指出可验证步骤，优于“下次认真一点”。也不能把一个样例答案当作普遍规则，例如把“永远输出78.8”写进经验。</p>
<p>实测曾出现模型反复输出F或Fahrenheit，而接口要求fahrenheit。代码为 unit 和 source_kind 设置了枚举；经验仍用于可改进的业务错误，不能替代接口约束。真实模型首轮通过时，经验提炼可能不会触发。</p>
''' + code("13_reflexion.py") + block('''python 13_reflexion.py
python 13_reflexion.py --live
python 13_reflexion.py --remember''') + '''
<p>默认情况下，记忆只保留到本次运行结束。加上 --remember 后，程序才会读写本课 examples 中的 reflection_memory.json，最多保存 3 条，每条最多 200 字符；下次运行时会更新这个文件。离线演示的经验与真实模型实验要分开记录，比较结果时还要注明是否加载了之前的经验。</p>
<h2>4. 为什么还要独立Evaluator</h2>
<p>模型可能一致地犯同一个错，Critic也可能误判。确定性检查给出可以复核的失败信号；没有标准答案的写作任务，可以用明确量表或人工审核，但不能声称这就获得了完全可靠的裁判。</p>
<p>Self-Refine的规则只检查部分内容，得分未降也不代表全文语义没退步；Reflexion的Evaluator只适用于这里的固定题。把案例改成新业务时，先更新判定依据，再谈反馈有效性。</p>
<h2>5. 成本和停止</h2>
<p>Self-Refine最多一次初稿加两轮“反馈/修订”，即最多5个模型请求；Reflexion最多3次回答和2次经验提炼，即最多5个请求。每次请求均有输出上限与网络超时。受限次数比“请反思直到正确”更容易测试。</p>
<p>外部经验是资料，不能升级成system指令；记忆也可能陈旧或错误。真实系统需要区分任务、模型和版本，记录经验来源，允许过期与删除，而不是把全部失败文本永久塞回Prompt。</p>
''' + source(13, 14) + quiz("s12", "Reflexion把经验存成文字后，真正改变的是什么？", ["后续请求的上下文", "基础模型全部权重", "执行程序授权范围"], 0, "经验通过上下文影响下一次决策，不自动修改权重或权限。")

    content[12] = '''
<h2>1. 三件不同的事</h2>
<table><tr><th>环节</th><th>解决的问题</th><th>例子</th></tr><tr><td>约束生成</td><td>尽量避免非法结构出现</td><td>后端按JSON Schema限制生成</td></tr><tr><td>结果验证</td><td>检查已经生成的数据</td><td>Pydantic检查字段、范围、枚举</td></tr><tr><td>失败重试</td><td>把错误反馈后再尝试</td><td>最多两次抽取</td></tr></table>
<p>Instructor提供类型化抽取和验证重试；Outlines围绕输出类型组织结构化生成。两者可服务相似目标，执行机制与后端支持不同。名字里有“约束”也不能保证抽取的城市或事实正确。</p>
<h2>2. 独立环境是本例的一部分</h2>
<p>本项目主环境使用 Python 3.14 和 OpenAI 3.37。核查时，Outlines 1.3.3 要求 Python 低于 3.14，Instructor 1.17 与主 SDK 要求的 jiter 版本范围也有冲突。因此，下面单独创建 Python 3.11 环境，避免反复降级主环境中的依赖。</p>
''' + block('''cd /Users/owen/Documents/ai-learn
/opt/homebrew/bin/python3.11 -m venv courses/03-tool-use-and-hello-agent/.venv-libraries311
courses/03-tool-use-and-hello-agent/.venv-libraries311/bin/python -m pip install -r courses/03-tool-use-and-hello-agent/examples/requirements-libraries.txt
cd courses/03-tool-use-and-hello-agent/examples
../.venv-libraries311/bin/python 14_instructor.py
../.venv-libraries311/bin/python 15_outlines.py''') + '''
<p>编写教材时，你的电脑已安装 /opt/homebrew/bin/python3.11，下面的案例使用这个解释器。它的固定依赖如下，与主线 requirements 分开使用。以后升级这些包时，需要重新运行案例确认兼容性。</p>
<p>独立环境同时安装httpx的SOCKS支持，避免Ollama包导入时因电脑已有代理配置而报错；实际案例客户端设置trust_env=False，数据请求直接发送到本机。</p>
''' + code("requirements-libraries.txt") + '''
<h2>3. Instructor完整代码</h2>
<p>BaseModel定义结果形状；Field给出长度和数值范围；Literal限定单位与来源类型；model_validator检查内容是否忠实于输入。extra=forbid拒绝额外字段，strict=True减少隐式类型转换。</p>
''' + code("14_instructor.py") + '''
<p>本例使用JSON模式，不通过天气工具查询，只从现成句子抽取。Instructor解析为WeatherRecord；在固定的1.17.0版本中，max_retries=1表示初次之后再允许一次，即最多两次抽取。底层SDK重试关闭，避免重试层数相乘。换版本后重新确认计数方式。</p>
<p>没有出现验证失败时，只发生一次抽取；运行成功并不证明重试路径被触发。Pydantic规则的错误输入可通过本课离线测试稳定检查。</p>
<p>独立库集成测试还用真实Instructor封装与固定HTTP响应验证“先错后对”和“失败两次后停止”，并检查Outlines确实把Schema交给Ollama。没有网络请求，完整测试代码也在本地代码集。</p>
''' + block("../.venv-libraries311/bin/python verify_libraries.py") + '''
<h2>4. Outlines完整代码</h2>
''' + code("15_outlines.py") + '''
<p>from_ollama连接本机原生接口；把WeatherRecord作为output_type交给模型。返回的JSON文本再次经model_validate_json验证，并用额外判断检查城市和温度。未声明为实时数据，也没有访问真实气象服务。</p>
<h2>5. 约束解码到底是什么</h2>
<p>可以把生成看作不断选下一个token。如果状态表明当前应产生一个数字，受约束的后端会限制不符合语法的候选；这与先自由生成、之后用正则修补不同。Schema通常会被转换为后端能执行的语法或状态约束。</p>
<p>本例远端Ollama负责实际生成约束；Python客户端不会读取远端logits。Outlines还支持其他后端，其正则、文法、类型支持范围不完全相同。不能因为某后端支持Literal或正则，就断言Ollama适配器也支持同样的全部输入。</p>
<h2>6. 怎样选择</h2>
<p>如果只需要在本地抽取 JSON，原生 Schema 加结果验证就能满足很多任务。需要类型模型和验证反馈时，Instructor 可以减少手动衔接这些步骤的代码；需要统一使用不同后端来生成结构化结果时，再考虑 Outlines。选择时比较实际失败率、延迟和依赖，不必为了功能多而叠加工具库。</p>
<p>完整测试覆盖语义不符、额外字段、布尔温度和错误来源；成功结果应是台北、26、celsius、fixed_example。两个库都不替代业务权限检查。</p>
''' + source(8, 15, 16) + quiz("s13", "JSON字段都合法，但城市被编造了，应该判断为什么？", ["可以直接入库使用", "属于结构完全失败", "属于业务语义失败"], 2, "结构与业务含义分开验收，合法JSON仍可能抽取错。")

    content[13] = '''
<h2>1. 从函数工作单到代码行动</h2>
<p>函数调用常用“工具名+参数”表示一个动作。CodeAct研究把可执行代码作为行动，允许变量、计算和多个工具组合，并用执行反馈继续后续步骤。本课用受限Python语法展示这种表示方式。</p>
<p>同一个任务可以表达为两条函数请求，也可以表达为：先把天气结果存进weather，再读取temperature换算，结果赋给answer。一次代码动作可以组合多个计算，但其中发生了多少工具访问，仍应计入自己的运行预算。</p>
<h2>2. 本课为什么用受限解释器</h2>
<p>直接exec模型生成的完整Python会把宿主环境暴露给代码。这里不调用eval或exec：先把源码解析成AST，再只解释明确支持的节点。解析源码不运行它，能否接受某种语法由解释器逐项决定。</p>
<table><tr><th>允许</th><th>拒绝</th></tr><tr><td>单变量赋值、有限数字、短字符串</td><td>import、文件读取、网络、属性访问</td></tr><tr><td>变量、加减乘除、工具结果字典取值</td><td>循环、类、函数定义、推导式、幂运算</td></tr><tr><td>白名单工具的显式关键字参数</td><td>任意宿主函数、动态参数展开</td></tr></table>
<p>这个解释器可以完整运行教学案例，但不支持完整 Python，也没有经过通用沙箱所需的安全审计。遇到它不支持的代码，应返回错误，不能改用 exec 执行来绕过限制。</p>
''' + code("16_codeact.py") + block('''python 16_codeact.py
python 16_codeact.py --live''') + '''
<h2>3. 代码的四层职责</h2>
<ol><li><strong>动作生成：</strong>模型返回kind=code、code源码；最后kind=final回答。</li><li><strong>语法解释：</strong>TinyPython仅处理白名单节点，变量只存在values字典里。</li><li><strong>工具执行：</strong>固定名称仍交给原有execute验证参数，不绕过工具检查。</li><li><strong>观察反馈：</strong>成功数据或明确错误回到下一轮；最多四轮。</li></ol>
<p>JSON中的code是待解释数据，不是宿主命令。外部观察在本例结构化决策协议中以明确的数据消息返回；它是原创教学协议，与原生tool_call_id协议不同，不能混用格式。</p>
<h2>4. 状态、失败与资源上限</h2>
<p>解释器会在多次代码动作之间保留 values，方便复用前一步的变量。每轮仍要重新给 answer 赋值，以免把旧结果当成这次的结果。代码执行失败后，可以根据错误修改再试；只有实际执行成功，才能报告完成。</p>
<p>最终文字还要说明台北、78.8华氏、固定示例与非实时性质。执行正确但文字只输出一个裸数时，程序回传格式反馈，请模型在剩余轮数内补全；不重新放宽执行权限。</p>
<p>本例限制源码为 2000 字符、AST 为 160 个节点，每次最多执行 10 条语句，总共最多四轮决策。工具只能读取固定数据和计算。这些限制用于控制教学任务，并不保证能安全执行任意恶意代码。执行完整 Python 还需要进程或远程隔离、CPU/内存/时长限制、网络策略、凭证保护和输出截断。</p>
<h2>5. 用测试证明拒绝路径</h2>
''' + block("python -m unittest test_advanced.CodeActionTests -v") + '''
<p>测试不会运行攻击代码，而是确认解释器拒绝import、属性访问、open、while、推导式和大幂。另有测试验证工具错误仍会被拒绝、状态保留、必须产生新answer，以及持续代码请求达到上限就停止。</p>
<h2>6. 选择函数调用还是代码行动</h2>
<p>接口固定、权限清晰、审计要求强时，函数调用通常更容易约束。任务需要大量中间变量和组合计算时，代码表示更灵活，但执行环境的责任更重。先解释清楚语法解释、工具验证和运行环境各自限制什么，再考虑使用 Smolagents 或其他 CodeAct 框架。</p>
''' + source(17, 18, 20) + quiz("s14", "AST解析成功后，可以立即认定模型代码安全么？", ["只能说明语法可读", "可以开放所有权限", "可以直接宿主执行"], 0, "解析、允许哪些语法、授予哪些能力是不同步骤。")

    content[14] = '''
<h2>1. 流式调用：不能只测成功</h2>
<p>运行09_streaming_tools.py的离线和真实模式。闭卷解释index和id的区别；再运行断流与截断测试，指出为什么工具调用次数必须为零。</p>
''' + block('''python 09_streaming_tools.py
python 09_streaming_tools.py --live
python -m unittest test_advanced.StreamingTests -v''') + '''
<details><summary>验收与完整参考</summary><p>参数碎片正确合并，同轮不同index不串线；没有结束原因时停止，不执行。完整实现见<a href="../reference/code-library.html#09_streaming_tools-py">09_streaming_tools.py</a>与<a href="../reference/code-library.html#test_advanced-py">test_advanced.py</a>。</p></details>
<h2>2. 选择模式：别把指定工具当路由能力</h2>
<p>分别运行auto、none、required、specific，记录首轮是否有tool_calls。解释specific成功为什么不能证明模型会自行选工具，以及后续为什么恢复auto。</p>
<details><summary>参考答案</summary><p>specific由程序明确指定工具；auto才保留模型的路由决定。持续强制每轮调用可能无法自然结束。none还需程序保持执行权限约束。完整代码为10_tool_choice.py。</p></details>
<h2>3. 并发：用重叠证据验收</h2>
<p>运行11_parallel_tools.py，比较实际输出时长。然后运行Barrier测试，解释两名工作线程必须同时到达Barrier才继续，为什么这比断言“耗时小于某个数字”更稳定。</p>
''' + block("python -m unittest test_advanced.ExecutionTests -v") + '''
<details><summary>参考答案</summary><p>两个任务并发执行时，都能到达 Barrier；如果顺序执行，第一个任务会一直等到超时。测试还会检查返回结果是否与原调用顺序对应，避免按完成顺序把 ID 配错。完整代码和测试都已提供。</p></details>
<h2>4. 研究理解：事实、指标、推断分开</h2>
<p>不翻正文写出Standard、CoT、Act、ReAct各改变了什么。解释为什么原论文中HotpotQA某项分数低于CoT，仍不否定工具反馈的全部价值。</p>
<p>再运行17_react_retrieval.py --live，检查查询青禾号后是否使用观察中的林遥去做第二跳。最终答对但没有两次查询，不通过本题的过程验收。</p>
<details><summary>参考答案</summary><p>一种方法是否有用，要结合具体任务和评价指标来看。不同方法在获取事实、灵活处理任务和错误恢复方面各有取舍。两跳案例不仅要答出“海城”，还要确认后一步确实使用了前一步取得的数据。</p></details>
<h2>5. 反馈：看得见被保留和被拒绝的修订</h2>
<p>运行Self-Refine与Reflexion离线版，分别找出revision与memory。再跑两个真实版；如果首轮已经正确，记录“无需修订”，不能虚构失败轨迹。</p>
''' + block('''python 12_self_refine.py
python 13_reflexion.py
python 12_self_refine.py --live
python 13_reflexion.py --live
python -m unittest test_advanced.FeedbackTests -v''') + '''
<details><summary>验收</summary><p>Self-Refine不接受规则得分更低的修订；Reflexion失败后生成可核对经验并在下一次尝试提供；连续失败在上限停止。完整实现12/13与反馈测试均在代码集。</p></details>
<h2>6. 结构与语义：两套库同题对照</h2>
<p>在独立环境分别运行14、15。比较最终字段；再阅读Pydantic失败测试，解释“城市不是台北”和“多了一个字段”分别由哪层拦截。</p>
<details><summary>参考答案</summary><p>额外字段由结构模型的extra=forbid拦截；城市或温度偏离输入由业务验证拦截。Instructor的重试与Outlines的生成约束不能代替这些规则。安装步骤和完整代码见单元13。</p></details>
<h2>7. CodeAct：组合能力与边界同时验收</h2>
<p>运行16的离线与真实模式，找到同一代码动作中的天气查询与换算。再运行CodeActionTests，解释为什么本课拒绝import，而不是悄悄为模型开放更多能力。</p>
<details><summary>参考答案</summary><p>代码表示能组合中间变量与工具，但只能使用解释器明确允许的能力。最终需要成功观察与78.8°F结果，禁止语法必须被拒绝。当前实现不承诺完整Python兼容。</p></details>
<h2>综合验收与复习</h2>
<ul class="checklist"><li>能解释基础单元 1–8，以及扩展单元 9–14 的案例。</li><li>每个主题至少检查一个成功路径和一个失败路径。</li><li>知道离线脚本、真实模型成绩与历史论文结果是三种证据。</li><li>能解释流、并发、重试、反思分别改变哪一层。</li><li>闭卷完成两跳查询、天气换算与执行边界的说明。</li></ul>
<p>当日做流式和并发，第二天闭卷区分Self-Refine与Reflexion，一周后混合验收JSON抽取、工具查询和CodeAct。同一问题用哪条路径更合适，要能说明依据。</p>
<p>全部案例可在本项目阅读和运行；外部来源仅保留供核查。把题号、运行命令和完整输出发给我，可以继续逐行拆解。</p>
'''
