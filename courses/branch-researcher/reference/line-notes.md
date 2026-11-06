# 多行字符串与数据文件的逐行说明

Python、JavaScript、命令与配置语句的注释直接写在相应文件中。以下内容不能在原值内部插入注释，行号对应 examples 中的实际文件。JSON 保持合法格式；提示词正文和换行保持原样。

## examples/input.json

[打开对应文件](../examples/input.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;task&quot;: &quot;对三个问题逐一核对：Transformer 是否去掉循环和卷积作为其主要序列架构；论文评测哪些翻译任务；它是否证明所有任务都优于所有方法。&quot;, | 说明本次要完成的任务。 |
| 3 |   &quot;evidence&quot;: [ | 提供可用于核对断言的证据。 |
| 4 |     { | 开始一个对象，内部以字段名组织数据。 |
| 5 |       &quot;id&quot;: &quot;p1&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 6 |       &quot;text&quot;: &quot;Attention Is All You Need 的模型架构章节提出以注意力机制构建 Transformer，不采用循环或卷积作为其主要序列建模架构。&quot; | 保存本条原始文字或断言文字。 |
| 7 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 8 |     { | 开始一个对象，内部以字段名组织数据。 |
| 9 |       &quot;id&quot;: &quot;p2&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 10 |       &quot;text&quot;: &quot;论文报告 WMT 2014 英德与英法翻译任务结果，实验有具体模型和训练条件。&quot; | 保存本条原始文字或断言文字。 |
| 11 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 12 |     { | 开始一个对象，内部以字段名组织数据。 |
| 13 |       &quot;id&quot;: &quot;p3&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 14 |       &quot;text&quot;: &quot;这是论文相关段落的教学概述，不是所有任务、所有模型的普遍比较；正式引用应回到原论文对应章节与表格。&quot; | 保存本条原始文字或断言文字。 |
| 15 |     } | 结束当前对象或数组。 |
| 16 |   ] | 结束当前对象或数组。 |
| 17 | } | 结束当前对象或数组。 |

## examples/paper-evidence.json

[打开对应文件](../examples/paper-evidence.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;paper&quot;: &quot;Attention Is All You Need&quot;, | 保存当前对象的 paper 字段，按本例题目或配置读取。 |
| 3 |   &quot;version&quot;: &quot;arXiv:1706.03762v7&quot;, | 标识资料或题集版本，保证比较条件一致。 |
| 4 |   &quot;source_url&quot;: &quot;https://arxiv.org/html/1706.03762v7&quot;, | 保存当前对象的 source_url 字段，按本例题目或配置读取。 |
| 5 |   &quot;checked_at&quot;: &quot;2026-11-04&quot;, | 保存当前对象的 checked_at 字段，按本例题目或配置读取。 |
| 6 |   &quot;scope&quot;: &quot;本课三问的有限证据片段与中文讲解；不替代研究投稿时的全文审读，不把论文授权变成 MIT。&quot;, | 保存当前对象的 scope 字段，按本例题目或配置读取。 |
| 7 |   &quot;evidence&quot;: [ | 提供可用于核对断言的证据。 |
| 8 |     { | 开始一个对象，内部以字段名组织数据。 |
| 9 |       &quot;id&quot;: &quot;q1-problem&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 10 |       &quot;location&quot;: &quot;1 Introduction，循环模型计算段落&quot;, | 保存当前对象的 location 字段，按本例题目或配置读取。 |
| 11 |       &quot;original_excerpt&quot;: &quot;precludes parallelization within training examples&quot;, | 保存当前对象的 original_excerpt 字段，按本例题目或配置读取。 |
| 12 |       &quot;explanation&quot;: &quot;这里的主语是前文讨论的序列计算依赖；批内并行受到限制。不能脱离主语解读为计算机无法并行。&quot; | 保存当前对象的 explanation 字段，按本例题目或配置读取。 |
| 13 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 14 |     { | 开始一个对象，内部以字段名组织数据。 |
| 15 |       &quot;id&quot;: &quot;q2-architecture&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 16 |       &quot;location&quot;: &quot;3 Model Architecture；3.1 Encoder&quot;, | 保存当前对象的 location 字段，按本例题目或配置读取。 |
| 17 |       &quot;original_excerpt&quot;: &quot;encoder-decoder structure; multi-head self-attention mechanism&quot;, | 保存当前对象的 original_excerpt 字段，按本例题目或配置读取。 |
| 18 |       &quot;explanation&quot;: &quot;分号连接两个非连续短摘录。架构由编码器和解码器组成，编码器子层包含多头自注意力；同节还说明前馈、残差和归一化。位置编码见3.5，解码器遮挡见3.1。&quot; | 保存当前对象的 explanation 字段，按本例题目或配置读取。 |
| 19 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 20 |     { | 开始一个对象，内部以字段名组织数据。 |
| 21 |       &quot;id&quot;: &quot;q3-experiments&quot;, | 标识当前条目，供引用或关联结果使用。 |
| 22 |       &quot;location&quot;: &quot;Abstract；6.1–6.3 Results&quot;, | 保存当前对象的 location 字段，按本例题目或配置读取。 |
| 23 |       &quot;original_excerpt&quot;: &quot;WMT 2014 English-to-German; WMT 2014 English-to-French; English constituency parsing&quot;, | 保存当前对象的 original_excerpt 字段，按本例题目或配置读取。 |
| 24 |       &quot;explanation&quot;: &quot;三项是非连续实验名称摘录；中文分别是英德翻译、英法翻译、英语成分句法分析。另有模型变体实验。跨任务普遍最优不是这些证据支持的结论。&quot; | 保存当前对象的 explanation 字段，按本例题目或配置读取。 |
| 25 |     } | 结束当前对象或数组。 |
| 26 |   ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 27 |   &quot;negative_example&quot;: { | 保存当前对象的 negative_example 字段，按本例题目或配置读取。 |
| 28 |     &quot;claim&quot;: &quot;论文证明所有领域的任务都最优。&quot;, | 保存当前对象的 claim 字段，按本例题目或配置读取。 |
| 29 |     &quot;citation&quot;: &quot;q3-experiments&quot;, | 保存当前对象的 citation 字段，按本例题目或配置读取。 |
| 30 |     &quot;judgment&quot;: &quot;未支持&quot;, | 保存当前对象的 judgment 字段，按本例题目或配置读取。 |
| 31 |     &quot;reason&quot;: &quot;该证据只列特定任务，不能支持全称断言；这是本教材的证据范围判断，不假造作者的限制原话。&quot; | 说明当前判断或限制的依据。 |
| 32 |   } | 结束当前对象或数组。 |
| 33 | } | 结束当前对象或数组。 |

## examples/reference-answer.json

[打开对应文件](../examples/reference-answer.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;draft&quot;: &quot;前两项在给定概述中有支持；“所有任务都最优”没有证据。正式研究需核对论文架构章节与实验表格。&quot;, | 保存待人工核对的草稿，不表示已执行外部动作。 |
| 3 |   &quot;claims&quot;: [ | 逐条列出需要核对的断言。 |
| 4 |     { | 开始一个对象，内部以字段名组织数据。 |
| 5 |       &quot;text&quot;: &quot;主要序列架构不使用循环与卷积&quot;, | 保存本条原始文字或断言文字。 |
| 6 |       &quot;source_ids&quot;: [ | 记录支持断言的来源 ID。 |
| 7 |         &quot;p1&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 8 |       ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 9 |       &quot;status&quot;: &quot;supported&quot; | 区分通过、失败、待复核或支持性状态。 |
| 10 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 11 |     { | 开始一个对象，内部以字段名组织数据。 |
| 12 |       &quot;text&quot;: &quot;评测包含英德和英法翻译&quot;, | 保存本条原始文字或断言文字。 |
| 13 |       &quot;source_ids&quot;: [ | 记录支持断言的来源 ID。 |
| 14 |         &quot;p2&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 15 |       ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 16 |       &quot;status&quot;: &quot;supported&quot; | 区分通过、失败、待复核或支持性状态。 |
| 17 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 18 |     { | 开始一个对象，内部以字段名组织数据。 |
| 19 |       &quot;text&quot;: &quot;证明所有任务都优于所有方法&quot;, | 保存本条原始文字或断言文字。 |
| 20 |       &quot;source_ids&quot;: [], | 记录支持断言的来源 ID。 |
| 21 |       &quot;status&quot;: &quot;unsupported&quot; | 区分通过、失败、待复核或支持性状态。 |
| 22 |     } | 结束当前对象或数组。 |
| 23 |   ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 24 |   &quot;needs_confirmation&quot;: [ | 保留缺失信息与待确认事项。 |
| 25 |     &quot;概述不是原始实验数据；复现前需核对论文具体训练设置与表格&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 26 |   ] | 结束当前对象或数组。 |
| 27 | } | 结束当前对象或数组。 |

## examples/reference-work.json

[打开对应文件](../examples/reference-work.json)

| 行 | 原内容 | 目的 |
|---|---|---|
| 1 | { | 开始一个对象，内部以字段名组织数据。 |
| 2 |   &quot;questions&quot;: [ | 保存当前对象的 questions 字段，按本例题目或配置读取。 |
| 3 |     { | 开始一个对象，内部以字段名组织数据。 |
| 4 |       &quot;question&quot;: &quot;主要架构是否去掉循环和卷积？&quot;, | 提供待回答的问题。 |
| 5 |       &quot;answer&quot;: &quot;在论文提出的 Transformer 主要序列建模架构中，是。不能推断所有注意力系统都不用卷积。&quot;, | 保存答案内容，仍需按本题规则判断。 |
| 6 |       &quot;source_ids&quot;: [ | 记录支持断言的来源 ID。 |
| 7 |         &quot;p1&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 8 |       ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 9 |       &quot;status&quot;: &quot;supported&quot;, | 区分通过、失败、待复核或支持性状态。 |
| 10 |       &quot;location&quot;: &quot;本地 input.json p1；论文架构章节的教学概述&quot; | 保存当前对象的 location 字段，按本例题目或配置读取。 |
| 11 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 12 |     { | 开始一个对象，内部以字段名组织数据。 |
| 13 |       &quot;question&quot;: &quot;评测哪些翻译任务？&quot;, | 提供待回答的问题。 |
| 14 |       &quot;answer&quot;: &quot;WMT 2014 英德与英法翻译。不能据此推断所有语言对的效果。&quot;, | 保存答案内容，仍需按本题规则判断。 |
| 15 |       &quot;source_ids&quot;: [ | 记录支持断言的来源 ID。 |
| 16 |         &quot;p2&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 17 |       ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 18 |       &quot;status&quot;: &quot;supported&quot;, | 区分通过、失败、待复核或支持性状态。 |
| 19 |       &quot;location&quot;: &quot;本地 input.json p2；实验章节的教学概述&quot; | 保存当前对象的 location 字段，按本例题目或配置读取。 |
| 20 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 21 |     { | 开始一个对象，内部以字段名组织数据。 |
| 22 |       &quot;question&quot;: &quot;是否证明所有任务最优？&quot;, | 提供待回答的问题。 |
| 23 |       &quot;answer&quot;: &quot;没有。给定证据没有穷尽任务、对照模型和训练条件。&quot;, | 保存答案内容，仍需按本题规则判断。 |
| 24 |       &quot;source_ids&quot;: [ | 记录支持断言的来源 ID。 |
| 25 |         &quot;p3&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 26 |       ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 27 |       &quot;status&quot;: &quot;unsupported&quot;, | 区分通过、失败、待复核或支持性状态。 |
| 28 |       &quot;location&quot;: &quot;本地 input.json p3&quot; | 保存当前对象的 location 字段，按本例题目或配置读取。 |
| 29 |     } | 结束当前对象或数组。 |
| 30 |   ], | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 31 |   &quot;comparison&quot;: { | 保存当前对象的 comparison 字段，按本例题目或配置读取。 |
| 32 |     &quot;paper_a&quot;: &quot;本地 Transformer 概述&quot;, | 保存当前对象的 paper_a 字段，按本例题目或配置读取。 |
| 33 |     &quot;paper_b&quot;: &quot;教学反例：另一研究只做情感分类，非真实论文&quot;, | 保存当前对象的 paper_b 字段，按本例题目或配置读取。 |
| 34 |     &quot;comparable&quot;: &quot;都可记录数据、指标和计算预算&quot;, | 保存当前对象的 comparable 字段，按本例题目或配置读取。 |
| 35 |     &quot;not_comparable&quot;: &quot;BLEU 与分类准确率不能直接相减，任务与数据不同&quot; | 保存当前对象的 not_comparable 字段，按本例题目或配置读取。 |
| 36 |   }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 37 |   &quot;reproduction&quot;: { | 保存当前对象的 reproduction 字段，按本例题目或配置读取。 |
| 38 |     &quot;status&quot;: &quot;未执行&quot;, | 区分通过、失败、待复核或支持性状态。 |
| 39 |     &quot;required&quot;: [ | 列出必须提供的字段。 |
| 40 |       &quot;代码版本&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 41 |       &quot;数据划分与许可&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 42 |       &quot;随机种子&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 43 |       &quot;训练配置&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 44 |       &quot;算力&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 45 |       &quot;原始指标&quot;, | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 46 |       &quot;失败日志&quot; | 提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。 |
| 47 |     ] | 结束当前对象或数组。 |
| 48 |   }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 49 |   &quot;review_record&quot;: { | 保存当前对象的 review_record 字段，按本例题目或配置读取。 |
| 50 |     &quot;date&quot;: &quot;2026-11-03&quot;, | 保存当前对象的 date 字段，按本例题目或配置读取。 |
| 51 |     &quot;tools&quot;: &quot;只读本地 input.json；无网络搜索&quot;, | 保存当前对象的 tools 字段，按本例题目或配置读取。 |
| 52 |     &quot;limit&quot;: &quot;本练习只考给定证据核对，不是全文复现&quot; | 保存当前对象的 limit 字段，按本例题目或配置读取。 |
| 53 |   }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 54 |   &quot;original_three_questions&quot;: [ | 保存当前对象的 original_three_questions 字段，按本例题目或配置读取。 |
| 55 |     { | 开始一个对象，内部以字段名组织数据。 |
| 56 |       &quot;question&quot;: &quot;论文解决什么问题？&quot;, | 提供待回答的问题。 |
| 57 |       &quot;answer&quot;: &quot;循环序列模型难在一个样本内并行计算，长距离依赖的连接路径也较长；论文探索用注意力为核心的序列转换架构。&quot;, | 保存答案内容，仍需按本题规则判断。 |
| 58 |       &quot;location&quot;: &quot;Introduction；Background&quot;, | 保存当前对象的 location 字段，按本例题目或配置读取。 |
| 59 |       &quot;evidence&quot;: &quot;教学转述：循环计算依赖前一位置状态，限制样本内并行。&quot;, | 提供可用于核对断言的证据。 |
| 60 |       &quot;judgment&quot;: &quot;支持；不是“此前所有模型都没有注意力”&quot;, | 保存当前对象的 judgment 字段，按本例题目或配置读取。 |
| 61 |       &quot;local_evidence_id&quot;: &quot;q1-problem&quot; | 保存当前对象的 local_evidence_id 字段，按本例题目或配置读取。 |
| 62 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 63 |     { | 开始一个对象，内部以字段名组织数据。 |
| 64 |       &quot;question&quot;: &quot;方法有哪些主要部分？&quot;, | 提供待回答的问题。 |
| 65 |       &quot;answer&quot;: &quot;编码器与解码器、多头注意力、位置前馈层、词嵌入与位置编码；解码器使用遮挡防止看到未来输出，并注意编码器结果；配合残差和归一化。&quot;, | 保存答案内容，仍需按本题规则判断。 |
| 66 |       &quot;location&quot;: &quot;Model Architecture 3.1–3.5&quot;, | 保存当前对象的 location 字段，按本例题目或配置读取。 |
| 67 |       &quot;evidence&quot;: &quot;短摘录：multi-head self-attention mechanism；其余为中文教学转述。&quot;, | 提供可用于核对断言的证据。 |
| 68 |       &quot;judgment&quot;: &quot;支持；注意力替代主要循环结构，不代表去掉位置信息&quot;, | 保存当前对象的 judgment 字段，按本例题目或配置读取。 |
| 69 |       &quot;local_evidence_id&quot;: &quot;q2-architecture&quot; | 保存当前对象的 local_evidence_id 字段，按本例题目或配置读取。 |
| 70 |     }, | 结束当前对象或数组；逗号表示同一层还有下一项。 |
| 71 |     { | 开始一个对象，内部以字段名组织数据。 |
| 72 |       &quot;question&quot;: &quot;实验支持与限制是什么？&quot;, | 提供待回答的问题。 |
| 73 |       &quot;answer&quot;: &quot;用WMT2014英德、英法翻译作比较，另有模型变体与英语成分句法分析实验。证据只支持所测任务和设置；不能推断所有任务优于所有方法。&quot;, | 保存答案内容，仍需按本题规则判断。 |
| 74 |       &quot;location&quot;: &quot;Results 6.1–6.3；Why Self-Attention&quot;, | 保存当前对象的 location 字段，按本例题目或配置读取。 |
| 75 |       &quot;evidence&quot;: &quot;短摘录：English-to-German and English-to-French；其余为中文教学转述。&quot;, | 提供可用于核对断言的证据。 |
| 76 |       &quot;judgment&quot;: &quot;支持实验范围；“所有任务最优”未支持。对泛化范围的限制是本教材推断，不伪装成作者专门限制段落原话。&quot;, | 保存当前对象的 judgment 字段，按本例题目或配置读取。 |
| 77 |       &quot;local_evidence_id&quot;: &quot;q3-experiments&quot; | 保存当前对象的 local_evidence_id 字段，按本例题目或配置读取。 |
| 78 |     } | 结束当前对象或数组。 |
| 79 |   ] | 结束当前对象或数组。 |
| 80 | } | 结束当前对象或数组。 |
