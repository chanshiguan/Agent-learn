# 多行字符串与数据文件的逐行说明

Python、JavaScript、命令与配置语句的注释直接写在相应文件中。以下内容不能在原值内部插入注释，行号对应 examples 中的实际文件。JSON 保持合法格式；提示词正文和换行保持原样。

## examples/input.json

[打开对应文件](../examples/input.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;task&quot;: &quot;只读检查演示 README 改动计划，指出允许范围、验证与尚缺证据，不修改文件。&quot;, | 说明本次要完成的任务。 |
| 3 |   &quot;evidence&quot;: [ | 提供可用于核对断言的证据。 |
| 4 |     { | 开始一个对象，内部以字段名组织数据。 |
| 5 |       &quot;id&quot;: &quot;d1&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 6 |       &quot;text&quot;: &quot;任务只允许修改 README.md，增加运行检查的说明。&quot; | 保存本条原始文字或断言文字。 |
| 7 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 8 |     { | 开始一个对象，内部以字段名组织数据。 |
| 9 |       &quot;id&quot;: &quot;d2&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 10 |       &quot;text&quot;: &quot;现有检查命令为 python check.py；不得删除。&quot; | 保存本条原始文字或断言文字。 |
| 11 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 12 |     { | 开始一个对象，内部以字段名组织数据。 |
| 13 |       &quot;id&quot;: &quot;d3&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 14 |       &quot;text&quot;: &quot;尚未执行检查，也没有产生 diff。&quot; | 保存本条原始文字或断言文字。 |
| 15 |     } | 结束当前对象或数组。 |
| 16 |   ] | 结束当前对象或数组。 |
| 17 | } | 结束当前对象或数组。 |

## examples/reference-answer.json

[打开对应文件](../examples/reference-answer.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;draft&quot;: &quot;计划：只补 README 中的检查说明，保留 python check.py；得到具体修改授权后实施，随后展示 diff 与真实检查输出。&quot;, | 保存待人工核对的草稿，不表示已执行外部动作。 |
| 3 |   &quot;claims&quot;: [ | 逐条列出需要核对的断言。 |
| 4 |     { | 开始一个对象，内部以字段名组织数据。 |
| 5 |       &quot;text&quot;: &quot;修改范围只有 README.md&quot;, | 保存本条原始文字或断言文字。 |
| 6 |       &quot;source_ids&quot;: [ | 记录支持断言的来源 ID。 |
| 7 |         &quot;d1&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 8 |       ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 9 |       &quot;status&quot;: &quot;supported&quot; | 区分通过、失败、待复核或支持性状态。 |
| 10 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 11 |     { | 开始一个对象，内部以字段名组织数据。 |
| 12 |       &quot;text&quot;: &quot;检查已经通过&quot;, | 保存本条原始文字或断言文字。 |
| 13 |       &quot;source_ids&quot;: [], | 记录支持断言的来源 ID。 |
| 14 |       &quot;status&quot;: &quot;unsupported&quot; | 区分通过、失败、待复核或支持性状态。 |
| 15 |     } | 结束当前对象或数组。 |
| 16 |   ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 17 |   &quot;needs_confirmation&quot;: [ | 保留缺失信息与待确认事项。 |
| 18 |     &quot;实际 diff&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 19 |     &quot;实际检查结果&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 20 |   ] | 结束当前对象或数组。 |
| 21 | } | 结束当前对象或数组。 |

## examples/reference-work.json

[打开对应文件](../examples/reference-work.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;analysis&quot;: { | 保存当前对象的 analysis 字段，按本例题目或配置读取。 |
| 3 |     &quot;scope&quot;: &quot;只修改 README.md 的运行说明&quot;, | 保存当前对象的 scope 字段，按本例题目或配置读取。 |
| 4 |     &quot;baseline&quot;: &quot;先保留 python check.py，未知测试状态不能写通过&quot;, | 保存当前对象的 baseline 字段，按本例题目或配置读取。 |
| 5 |     &quot;excluded&quot;: [ | 保存当前对象的 excluded 字段，按本例题目或配置读取。 |
| 6 |       &quot;全仓格式化&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 7 |       &quot;改 check.py&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 8 |       &quot;安装无关包&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 9 |     ] | 结束当前对象或数组。 |
| 10 |   }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 11 |   &quot;plan&quot;: [ | 保存当前对象的 plan 字段，按本例题目或配置读取。 |
| 12 |     &quot;读 README.md 与 check.py&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 13 |     &quot;在隔离演示目录补运行说明&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 14 |     &quot;显示单文件 diff&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 15 |     &quot;执行 check.py 并保留真实输出&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 16 |     &quot;只撤回 README.md 本次改动&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 17 |   ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 18 |   &quot;before&quot;: &quot;# 演示项目\n用于练习文档修改。\n&quot;, | 保存当前对象的 before 字段，按本例题目或配置读取。 |
| 19 |   &quot;after&quot;: &quot;# 演示项目\n用于练习文档修改。\n\n## 运行\n在本目录执行：python check.py\n成功时输出 PASS。\n&quot;, | 保存当前对象的 after 字段，按本例题目或配置读取。 |
| 20 |   &quot;diff&quot;: &quot;--- README.md\n+++ README.md\n@@ -1,2 +1,6 @@\n # 演示项目\n 用于练习文档修改。\n+\n+## 运行\n+在本目录执行：python check.py\n+成功时输出 PASS。\n&quot;, | 保存当前对象的 diff 字段，按本例题目或配置读取。 |
| 21 |   &quot;verification&quot;: { | 保存当前对象的 verification 字段，按本例题目或配置读取。 |
| 22 |     &quot;status&quot;: &quot;示范预期，实际运行以 develop_demo.py 输出为准&quot;, | 区分通过、失败、待复核或支持性状态。 |
| 23 |     &quot;command&quot;: &quot;python check.py&quot;, | 指定启动命令。 |
| 24 |     &quot;expected&quot;: &quot;PASS&quot; | 给出验收时应核对的结果。 |
| 25 |   }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 26 |   &quot;rollback&quot;: &quot;先看 diff 确认只含本人改动，再在演示仓库执行 git restore -- README.md；有他人改动时逐块撤回。&quot;, | 保存当前对象的 rollback 字段，按本例题目或配置读取。 |
| 27 |   &quot;transfer&quot;: { | 保存当前对象的 transfer 字段，按本例题目或配置读取。 |
| 28 |     &quot;bug&quot;: &quot;取列表首项前未检查空列表&quot;, | 保存当前对象的 bug 字段，按本例题目或配置读取。 |
| 29 |     &quot;before&quot;: &quot;def first(xs): return xs[0]&quot;, | 保存当前对象的 before 字段，按本例题目或配置读取。 |
| 30 |     &quot;after&quot;: &quot;def first(xs): return xs[0] if xs else None&quot;, | 保存当前对象的 after 字段，按本例题目或配置读取。 |
| 31 |     &quot;cases&quot;: [ | 列出独立验收题。 |
| 32 |       { | 开始一个对象，内部以字段名组织数据。 |
| 33 |         &quot;input&quot;: [], | 保存当前对象的 input 字段，按本例题目或配置读取。 |
| 34 |         &quot;expected&quot;: null | 给出验收时应核对的结果。 |
| 35 |       }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 36 |       { | 开始一个对象，内部以字段名组织数据。 |
| 37 |         &quot;input&quot;: [ | 保存当前对象的 input 字段，按本例题目或配置读取。 |
| 38 |           7 | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 39 |         ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 40 |         &quot;expected&quot;: 7 | 给出验收时应核对的结果。 |
| 41 |       } | 结束当前对象或数组。 |
| 42 |     ] | 结束当前对象或数组。 |
| 43 |   } | 结束当前对象或数组。 |
| 44 | } | 结束当前对象或数组。 |
