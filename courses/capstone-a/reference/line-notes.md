# 多行字符串与数据文件的逐行说明

Python、JavaScript、命令与配置语句的注释直接写在相应文件中。以下内容不能在原值内部插入注释，行号对应 examples 中的实际文件。JSON 保持合法格式；提示词正文和换行保持原样。

## examples/reference-draft.json

[打开对应文件](../examples/reference-draft.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | {&quot;actions&quot;:[{&quot;task&quot;:&quot;准备报名表草稿，不发布；整理报名字段&quot;,&quot;owner&quot;:&quot;小林&quot;,&quot;due&quot;:&quot;周五，具体日期待确认&quot;,&quot;source&quot;:&quot;M1,M2&quot;}],&quot;needs_confirmation&quot;:[&quot;会议日期与周五对应的年月日&quot;,&quot;预算&quot;]} | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
