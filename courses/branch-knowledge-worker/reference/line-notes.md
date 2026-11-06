# 多行字符串与数据文件的逐行说明

Python、JavaScript、命令与配置语句的注释直接写在相应文件中。以下内容不能在原值内部插入注释，行号对应 examples 中的实际文件。JSON 保持合法格式；提示词正文和换行保持原样。

## examples/input.json

[打开对应文件](../examples/input.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;task&quot;: &quot;将会议资料整理为 Decision/ActionItem/Owner/DueDate/SourceSentence/NeedsConfirmation 行动表草稿，缺失不猜。&quot;, | 说明本次要完成的任务。 |
| 3 |   &quot;evidence&quot;: [ | 提供可用于核对断言的证据。 |
| 4 |     { | 开始一个对象，内部以字段名组织数据。 |
| 5 |       &quot;id&quot;: &quot;m1&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 6 |       &quot;text&quot;: &quot;会议决定先制作报名表原型，不发布正式版本。&quot; | 保存本条原始文字或断言文字。 |
| 7 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 8 |     { | 开始一个对象，内部以字段名组织数据。 |
| 9 |       &quot;id&quot;: &quot;m2&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 10 |       &quot;text&quot;: &quot;小林负责整理报名字段，周五前交给小周。&quot; | 保存本条原始文字或断言文字。 |
| 11 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 12 |     { | 开始一个对象，内部以字段名组织数据。 |
| 13 |       &quot;id&quot;: &quot;m3&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 14 |       &quot;text&quot;: &quot;预算待财务确认。会议记录未注明日期。&quot; | 保存本条原始文字或断言文字。 |
| 15 |     } | 结束当前对象或数组。 |
| 16 |   ] | 结束当前对象或数组。 |
| 17 | } | 结束当前对象或数组。 |

## examples/reference-answer.json

[打开对应文件](../examples/reference-answer.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;draft&quot;: &quot;Decision：先做原型、不发布。ActionItem：整理报名字段。Owner：小林。DueDate：周五，具体日期待确认。SourceSentence：m2。NeedsConfirmation：会议日期和预算。&quot;, | 保存待人工核对的草稿，不表示已执行外部动作。 |
| 3 |   &quot;claims&quot;: [ | 逐条列出需要核对的断言。 |
| 4 |     { | 开始一个对象，内部以字段名组织数据。 |
| 5 |       &quot;text&quot;: &quot;小林负责整理字段&quot;, | 保存本条原始文字或断言文字。 |
| 6 |       &quot;source_ids&quot;: [ | 记录支持断言的来源 ID。 |
| 7 |         &quot;m2&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 8 |       ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 9 |       &quot;status&quot;: &quot;supported&quot; | 区分通过、失败、待复核或支持性状态。 |
| 10 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 11 |     { | 开始一个对象，内部以字段名组织数据。 |
| 12 |       &quot;text&quot;: &quot;预算已获批准&quot;, | 保存本条原始文字或断言文字。 |
| 13 |       &quot;source_ids&quot;: [], | 记录支持断言的来源 ID。 |
| 14 |       &quot;status&quot;: &quot;unsupported&quot; | 区分通过、失败、待复核或支持性状态。 |
| 15 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 16 |     { | 开始一个对象，内部以字段名组织数据。 |
| 17 |       &quot;text&quot;: &quot;周五的具体年月日&quot;, | 保存本条原始文字或断言文字。 |
| 18 |       &quot;source_ids&quot;: [ | 记录支持断言的来源 ID。 |
| 19 |         &quot;m3&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 20 |       ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 21 |       &quot;status&quot;: &quot;uncertain&quot; | 区分通过、失败、待复核或支持性状态。 |
| 22 |     } | 结束当前对象或数组。 |
| 23 |   ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 24 |   &quot;needs_confirmation&quot;: [ | 保留缺失信息与待确认事项。 |
| 25 |     &quot;会议日期&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 26 |     &quot;周五对应的具体日期&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 27 |     &quot;预算确认人及结果&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 28 |   ] | 结束当前对象或数组。 |
| 29 | } | 结束当前对象或数组。 |

## examples/reference-work.json

[打开对应文件](../examples/reference-work.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;actions&quot;: [ | 保存当前对象的 actions 字段，按本例题目或配置读取。 |
| 3 |     { | 开始一个对象，内部以字段名组织数据。 |
| 4 |       &quot;Decision&quot;: &quot;先做原型、不发布正式版本&quot;, | 记录明确作出的决定。 |
| 5 |       &quot;ActionItem&quot;: &quot;整理报名字段&quot;, | 记录待执行的动作。 |
| 6 |       &quot;Owner&quot;: &quot;小林&quot;, | 记录明确的负责人。 |
| 7 |       &quot;DueDate&quot;: &quot;周五，具体年月日待确认&quot;, | 记录截止日期；资料不足时保留待确认。 |
| 8 |       &quot;SourceSentence&quot;: &quot;m1,m2,m3&quot;, | 保留支持此项的原句。 |
| 9 |       &quot;NeedsConfirmation&quot;: [ | 列出不能自行补造的信息。 |
| 10 |         &quot;会议日期&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 11 |         &quot;周五对应日期&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 12 |       ] | 结束当前对象或数组。 |
| 13 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 14 |     { | 开始一个对象，内部以字段名组织数据。 |
| 15 |       &quot;Decision&quot;: &quot;预算尚未确认&quot;, | 记录明确作出的决定。 |
| 16 |       &quot;ActionItem&quot;: &quot;确认预算结果&quot;, | 记录待执行的动作。 |
| 17 |       &quot;Owner&quot;: &quot;待确认&quot;, | 记录明确的负责人。 |
| 18 |       &quot;DueDate&quot;: &quot;待确认&quot;, | 记录截止日期；资料不足时保留待确认。 |
| 19 |       &quot;SourceSentence&quot;: &quot;m3&quot;, | 保留支持此项的原句。 |
| 20 |       &quot;NeedsConfirmation&quot;: [ | 列出不能自行补造的信息。 |
| 21 |         &quot;财务确认人&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 22 |         &quot;预算金额&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 23 |         &quot;完成时间&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 24 |       ] | 结束当前对象或数组。 |
| 25 |     } | 结束当前对象或数组。 |
| 26 |   ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 27 |   &quot;conflict_case&quot;: { | 保存当前对象的 conflict_case 字段，按本例题目或配置读取。 |
| 28 |     &quot;record_a&quot;: &quot;虚构补充 A：周五交付&quot;, | 保存当前对象的 record_a 字段，按本例题目或配置读取。 |
| 29 |     &quot;record_b&quot;: &quot;虚构补充 B：周四交付&quot;, | 保存当前对象的 record_b 字段，按本例题目或配置读取。 |
| 30 |     &quot;result&quot;: &quot;记录冲突，保留两条来源，请负责人确认；不根据文件名新旧决定&quot; | 保存当前对象的 result 字段，按本例题目或配置读取。 |
| 31 |   }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 32 |   &quot;review&quot;: [ | 保存当前对象的 review 字段，按本例题目或配置读取。 |
| 33 |     &quot;小林是负责人，小周是接收人，不能交换&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 34 |     &quot;未将预算写成已批准&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 35 |     &quot;没有发送或创建任务&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 36 |   ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 37 |   &quot;original_meeting&quot;: { | 保存当前对象的 original_meeting 字段，按本例题目或配置读取。 |
| 38 |     &quot;source&quot;: &quot;团队决定周五先发布说明页。小林会整理常见问题，但没有写期限。客服主管要在9月3日前确认回复范本。是否寄信给全部客户，会议后再决定。&quot;, | 保存当前对象的 source 字段，按本例题目或配置读取。 |
| 39 |     &quot;table&quot;: [ | 保存当前对象的 table 字段，按本例题目或配置读取。 |
| 40 |       { | 开始一个对象，内部以字段名组织数据。 |
| 41 |         &quot;Decision&quot;: &quot;周五先发布说明页&quot;, | 记录明确作出的决定。 |
| 42 |         &quot;ActionItem&quot;: &quot;准备发布说明页&quot;, | 记录待执行的动作。 |
| 43 |         &quot;Owner&quot;: &quot;未知&quot;, | 记录明确的负责人。 |
| 44 |         &quot;DueDate&quot;: &quot;周五，具体日期未知&quot;, | 记录截止日期；资料不足时保留待确认。 |
| 45 |         &quot;SourceSentence&quot;: &quot;团队决定周五先发布说明页。&quot;, | 保留支持此项的原句。 |
| 46 |         &quot;NeedsConfirmation&quot;: &quot;是：负责人、周五具体日期&quot; | 列出不能自行补造的信息。 |
| 47 |       }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 48 |       { | 开始一个对象，内部以字段名组织数据。 |
| 49 |         &quot;Decision&quot;: &quot;整理常见问题&quot;, | 记录明确作出的决定。 |
| 50 |         &quot;ActionItem&quot;: &quot;整理常见问题&quot;, | 记录待执行的动作。 |
| 51 |         &quot;Owner&quot;: &quot;小林&quot;, | 记录明确的负责人。 |
| 52 |         &quot;DueDate&quot;: &quot;未知&quot;, | 记录截止日期；资料不足时保留待确认。 |
| 53 |         &quot;SourceSentence&quot;: &quot;小林会整理常见问题，但没有写期限。&quot;, | 保留支持此项的原句。 |
| 54 |         &quot;NeedsConfirmation&quot;: &quot;是：期限&quot; | 列出不能自行补造的信息。 |
| 55 |       }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 56 |       { | 开始一个对象，内部以字段名组织数据。 |
| 57 |         &quot;Decision&quot;: &quot;确认回复范本&quot;, | 记录明确作出的决定。 |
| 58 |         &quot;ActionItem&quot;: &quot;确认回复范本&quot;, | 记录待执行的动作。 |
| 59 |         &quot;Owner&quot;: &quot;客服主管&quot;, | 记录明确的负责人。 |
| 60 |         &quot;DueDate&quot;: &quot;9月3日前，年份未知&quot;, | 记录截止日期；资料不足时保留待确认。 |
| 61 |         &quot;SourceSentence&quot;: &quot;客服主管要在9月3日前确认回复范本。&quot;, | 保留支持此项的原句。 |
| 62 |         &quot;NeedsConfirmation&quot;: &quot;是：年份与负责人身份&quot; | 列出不能自行补造的信息。 |
| 63 |       }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 64 |       { | 开始一个对象，内部以字段名组织数据。 |
| 65 |         &quot;Decision&quot;: &quot;是否全客户寄信尚未决定&quot;, | 记录明确作出的决定。 |
| 66 |         &quot;ActionItem&quot;: &quot;会议后确认是否寄信&quot;, | 记录待执行的动作。 |
| 67 |         &quot;Owner&quot;: &quot;未知&quot;, | 记录明确的负责人。 |
| 68 |         &quot;DueDate&quot;: &quot;未知&quot;, | 记录截止日期；资料不足时保留待确认。 |
| 69 |         &quot;SourceSentence&quot;: &quot;是否寄信给全部客户，会议后再决定。&quot;, | 保留支持此项的原句。 |
| 70 |         &quot;NeedsConfirmation&quot;: &quot;是：决定、负责人和期限&quot; | 列出不能自行补造的信息。 |
| 71 |       } | 结束当前对象或数组。 |
| 72 |     ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 73 |     &quot;human_review&quot;: [ | 保存当前对象的 human_review 字段，按本例题目或配置读取。 |
| 74 |       &quot;逐句核对来源&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 75 |       &quot;负责人未补猜&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 76 |       &quot;周五与年份未推断&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 77 |       &quot;无真实敏感资料&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 78 |       &quot;收件人未确定且未发送&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 79 |     ] | 结束当前对象或数组。 |
| 80 |   } | 结束当前对象或数组。 |
| 81 | } | 结束当前对象或数组。 |
