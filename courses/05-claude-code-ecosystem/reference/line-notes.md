# 多行字符串与数据文件的逐行说明

Python、JavaScript、命令与配置语句的注释直接写在相应文件中。以下内容不能在原值内部插入注释，行号对应 examples 中的实际文件。JSON 保持合法格式；提示词正文和换行保持原样。

## examples/course-plugin/.claude-plugin/plugin.json

[打开对应文件](../examples/course-plugin/.claude-plugin/plugin.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;name&quot;: &quot;course-readme&quot;, | 给条目、工具或配置设置名称。 |
| 3 |   &quot;version&quot;: &quot;1.0.0&quot;, | 标识资料或题集版本，保证比较条件一致。 |
| 4 |   &quot;description&quot;: &quot;教学用 README 完整性检查；只读，不安装或执行文档中的命令。&quot; | 说明字段或工具的用途。 |
| 5 | } | 结束当前对象或数组。 |

## examples/settings.demo.json

[打开对应文件](../examples/settings.demo.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;hooks&quot;: { | 声明事件发生时运行的处理器。 |
| 3 |     &quot;PreToolUse&quot;: [{ | 保存当前对象的 PreToolUse 字段，按本例题目或配置读取。 |
| 4 |       &quot;matcher&quot;: &quot;Edit&#124;Write&quot;, | 筛选哪些事件匹配当前处理规则。 |
| 5 |       &quot;hooks&quot;: [{ | 声明事件发生时运行的处理器。 |
| 6 |         &quot;type&quot;: &quot;command&quot;, | 声明此处的数据或消息类型。 |
| 7 |         &quot;command&quot;: &quot;python3 \&quot;$CLAUDE_PROJECT_DIR/observe_hook.py\&quot;&quot; | 指定启动命令。 |
| 8 |       }] | 结束当前对象或数组。 |
| 9 |     }] | 结束当前对象或数组。 |
| 10 |   } | 结束当前对象或数组。 |
| 11 | } | 结束当前对象或数组。 |

## examples/upstream/tool-calling-tutor/evals/evals.json

[打开对应文件](../examples/upstream/tool-calling-tutor/evals/evals.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;schema_version&quot;: 1, | 保存当前对象的 schema_version 字段，按本例题目或配置读取。 |
| 3 |   &quot;description&quot;: &quot;tool-calling-tutor 的简体中文离线行为验收题；只核对路由、检查要点和本地资料定位，不代表模型质量分数。&quot;, | 说明字段或工具的用途。 |
| 4 |   &quot;cases&quot;: [ | 列出独立验收题。 |
| 5 |     { | 开始一个对象，内部以字段名组织数据。 |
| 6 |       &quot;id&quot;: &quot;symptom_a_llm_not_calling&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 7 |       &quot;locale&quot;: &quot;zh-Hans&quot;, | 保存当前对象的 locale 字段，按本例题目或配置读取。 |
| 8 |       &quot;input&quot;: &quot;我写了 get_weather 工具，也传入了 tools，但模型只返回文字，没有调用工具。&quot;, | 保存当前对象的 input 字段，按本例题目或配置读取。 |
| 9 |       &quot;expected_route&quot;: &quot;a&quot;, | 保存当前对象的 expected_route 字段，按本例题目或配置读取。 |
| 10 |       &quot;reference&quot;: &quot;references/debug-flowchart.zh-Hans.md#section-a-symptom-allm-完全不触发-toolcalls&quot;, | 提供参考答案或基线。 |
| 11 |       &quot;must_cover&quot;: [ | 保存当前对象的 must_cover 字段，按本例题目或配置读取。 |
| 12 |         &quot;先确认当前 SDK、模型与工具调用支持情况&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 13 |         &quot;检查 tool description、边界、query 是否真的需要工具，以及 schema wrapper&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 14 |         &quot;不要捏造原因比例或保证换 model 就会成功&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 15 |       ] | 结束当前对象或数组。 |
| 16 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 17 |     { | 开始一个对象，内部以字段名组织数据。 |
| 18 |       &quot;id&quot;: &quot;symptom_b_wrong_args&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 19 |       &quot;locale&quot;: &quot;zh-Hans&quot;, | 保存当前对象的 locale 字段，按本例题目或配置读取。 |
| 20 |       &quot;input&quot;: &quot;工具被调用了，但 value 收到的是“32 摄氏度”这个字符串，而不是数字 32。&quot;, | 保存当前对象的 input 字段，按本例题目或配置读取。 |
| 21 |       &quot;expected_route&quot;: &quot;b&quot;, | 保存当前对象的 expected_route 字段，按本例题目或配置读取。 |
| 22 |       &quot;reference&quot;: &quot;references/schema-evolution.zh-Hans.md#iteration-0原始坏-schema&quot;, | 提供参考答案或基线。 |
| 23 |       &quot;must_cover&quot;: [ | 保存当前对象的 must_cover 字段，按本例题目或配置读取。 |
| 24 |         &quot;检查类型、必填字段、枚举，以及应用侧参数验证&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 25 |         &quot;按四次 Schema 改进逐步说明，不声称有固定成功率&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 26 |         &quot;不执行未经验证的模型参数&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 27 |       ] | 结束当前对象或数组。 |
| 28 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 29 |     { | 开始一个对象，内部以字段名组织数据。 |
| 30 |       &quot;id&quot;: &quot;symptom_c_loop_no_end&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 31 |       &quot;locale&quot;: &quot;zh-Hans&quot;, | 保存当前对象的 locale 字段，按本例题目或配置读取。 |
| 32 |       &quot;input&quot;: &quot;ReAct loop 一直调用同一个 tool，跑到最大轮数也没有结束。&quot;, | 保存当前对象的 input 字段，按本例题目或配置读取。 |
| 33 |       &quot;expected_route&quot;: &quot;c&quot;, | 保存当前对象的 expected_route 字段，按本例题目或配置读取。 |
| 34 |       &quot;reference&quot;: &quot;references/debug-flowchart.zh-Hans.md#section-c-symptom-creact-loop-跑不停&quot;, | 提供参考答案或基线。 |
| 35 |       &quot;must_cover&quot;: [ | 保存当前对象的 must_cover 字段，按本例题目或配置读取。 |
| 36 |         &quot;检查 assistant history、call ID、tool result 和停止条件&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 37 |         &quot;保留最大轮数并让失败清楚可见&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 38 |         &quot;只要求可检查的短计划，不索取隐藏推理&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 39 |       ] | 结束当前对象或数组。 |
| 40 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 41 |     { | 开始一个对象，内部以字段名组织数据。 |
| 42 |       &quot;id&quot;: &quot;symptom_d_design_from_scratch&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 43 |       &quot;locale&quot;: &quot;zh-Hans&quot;, | 保存当前对象的 locale 字段，按本例题目或配置读取。 |
| 44 |       &quot;input&quot;: &quot;我想做一个查询 GitHub 仓库资料的工具，但还没有写 Schema。&quot;, | 保存当前对象的 input 字段，按本例题目或配置读取。 |
| 45 |       &quot;expected_route&quot;: &quot;d&quot;, | 保存当前对象的 expected_route 字段，按本例题目或配置读取。 |
| 46 |       &quot;reference&quot;: &quot;references/schema-evolution.zh-Hans.md#iteration-0原始坏-schema&quot;, | 提供参考答案或基线。 |
| 47 |       &quot;must_cover&quot;: [ | 保存当前对象的 must_cover 字段，按本例题目或配置读取。 |
| 48 |         &quot;依次明确用途、描述、类型、取值约束与错误处理&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 49 |         &quot;先确认所用 SDK，再选择对应的 Schema 外形&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 50 |         &quot;加入工具白名单与参数验证&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 51 |       ] | 结束当前对象或数组。 |
| 52 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 53 |     { | 开始一个对象，内部以字段名组织数据。 |
| 54 |       &quot;id&quot;: &quot;route_away_langgraph&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 55 |       &quot;locale&quot;: &quot;zh-Hans&quot;, | 保存当前对象的 locale 字段，按本例题目或配置读取。 |
| 56 |       &quot;input&quot;: &quot;我的 LangGraph StateGraph 连线有问题，这个工具调用教学助手能修吗？&quot;, | 保存当前对象的 input 字段，按本例题目或配置读取。 |
| 57 |       &quot;expected_route&quot;: &quot;away&quot;, | 保存当前对象的 expected_route 字段，按本例题目或配置读取。 |
| 58 |       &quot;reference&quot;: &quot;&quot;, | 提供参考答案或基线。 |
| 59 |       &quot;must_cover&quot;: [ | 保存当前对象的 must_cover 字段，按本例题目或配置读取。 |
| 60 |         &quot;把框架特有的调试问题引导到第四课&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 61 |         &quot;MCP、上线运维与通用提示工程分别按对应课程处理&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 62 |       ] | 结束当前对象或数组。 |
| 63 |     } | 结束当前对象或数组。 |
| 64 |   ] | 结束当前对象或数组。 |
| 65 | } | 结束当前对象或数组。 |
