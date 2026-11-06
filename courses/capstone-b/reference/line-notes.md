# 多行字符串与数据文件的逐行说明

Python、JavaScript、命令与配置语句的注释直接写在相应文件中。以下内容不能在原值内部插入注释，行号对应 examples 中的实际文件。JSON 保持合法格式；提示词正文和换行保持原样。

## examples/documents.json

[打开对应文件](../examples/documents.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | [ | 开始一个数组，内部按顺序保存各项。 |
| 2 |   {&quot;id&quot;:&quot;hours&quot;,&quot;keywords&quot;:[&quot;开放&quot;,&quot;几点&quot;,&quot;营业&quot;,&quot;周一&quot;,&quot;周日&quot;],&quot;text&quot;:&quot;虚构学习室周一至周六 09:00–18:00 开放，周日闭馆。&quot;}, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 3 |   {&quot;id&quot;:&quot;booking&quot;,&quot;keywords&quot;:[&quot;预约&quot;,&quot;预订&quot;,&quot;提前&quot;],&quot;text&quot;:&quot;预约座位至少提前 1 天，最多提前 7 天。&quot;}, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 4 |   {&quot;id&quot;:&quot;cancel&quot;,&quot;keywords&quot;:[&quot;取消&quot;,&quot;退款&quot;,&quot;退费&quot;],&quot;text&quot;:&quot;课程开始前 24 小时可取消预约并全额退款；不足 24 小时须人工确认。&quot;}, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 5 |   {&quot;id&quot;:&quot;quiet&quot;,&quot;keywords&quot;:[&quot;通话&quot;,&quot;安静&quot;,&quot;电话&quot;],&quot;text&quot;:&quot;安静区不得接打电话；通话请到门厅。&quot;}, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 6 |   {&quot;id&quot;:&quot;files&quot;,&quot;keywords&quot;:[&quot;资料&quot;,&quot;下载&quot;,&quot;教材&quot;],&quot;text&quot;:&quot;报名者可下载所报课程的电子资料，不包含其他课程。&quot;} | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 7 | ] | 结束当前对象或数组。 |

## examples/eval_cases.json

[打开对应文件](../examples/eval_cases.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;version&quot;:&quot;course-demo-v1&quot;, | 标识资料或题集版本，保证比较条件一致。 |
| 3 |   &quot;warning&quot;:&quot;公开教学题；读过答案后不能继续声称它是你的盲测保留集。&quot;, | 保存当前对象的 warning 字段，按本例题目或配置读取。 |
| 4 |   &quot;development&quot;:[ | 保存当前对象的 development 字段，按本例题目或配置读取。 |
| 5 |     {&quot;id&quot;:&quot;d1&quot;,&quot;question&quot;:&quot;周一几点开放？&quot;,&quot;required&quot;:[&quot;09:00&quot;,&quot;18:00&quot;],&quot;sources&quot;:[&quot;hours&quot;]}, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 6 |     {&quot;id&quot;:&quot;d2&quot;,&quot;question&quot;:&quot;预约至少提前几天？&quot;,&quot;required&quot;:[&quot;1&quot;],&quot;sources&quot;:[&quot;booking&quot;]}, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 7 |     {&quot;id&quot;:&quot;d3&quot;,&quot;question&quot;:&quot;课程开始前多久可以全额退款？&quot;,&quot;required&quot;:[&quot;24&quot;],&quot;sources&quot;:[&quot;cancel&quot;]}, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 8 |     {&quot;id&quot;:&quot;d4&quot;,&quot;question&quot;:&quot;哪里可以通话？&quot;,&quot;required&quot;:[&quot;门厅&quot;],&quot;sources&quot;:[&quot;quiet&quot;]}, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 9 |     {&quot;id&quot;:&quot;d5&quot;,&quot;question&quot;:&quot;报名者能下载哪些教材？&quot;,&quot;required&quot;:[&quot;所报&quot;],&quot;sources&quot;:[&quot;files&quot;]} | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 10 |   ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 11 |   &quot;holdout&quot;:[ | 保存当前对象的 holdout 字段，按本例题目或配置读取。 |
| 12 |     {&quot;id&quot;:&quot;h1&quot;,&quot;question&quot;:&quot;周日能去学习室吗？&quot;,&quot;required&quot;:[&quot;闭馆&quot;],&quot;sources&quot;:[&quot;hours&quot;]}, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 13 |     {&quot;id&quot;:&quot;h2&quot;,&quot;question&quot;:&quot;预约最多提前几天？&quot;,&quot;required&quot;:[&quot;7&quot;],&quot;sources&quot;:[&quot;booking&quot;]}, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 14 |     {&quot;id&quot;:&quot;h3&quot;,&quot;question&quot;:&quot;月球基地的地址是什么？&quot;,&quot;required&quot;:[&quot;资料不足，无法回答。&quot;],&quot;sources&quot;:[]} | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 15 |   ] | 结束当前对象或数组。 |
| 16 | } | 结束当前对象或数组。 |
