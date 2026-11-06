# 多行字符串与数据文件的逐行说明

Python、JavaScript、命令与配置语句的注释直接写在相应文件中。以下内容不能在原值内部插入注释，行号对应 examples 中的实际文件。JSON 保持合法格式；提示词正文和换行保持原样。

## examples/diff_lab.py

[打开对应文件](../examples/diff_lab.py)

| 行 | 原内容 | 目的 |
|---|---|---|
| 14 | CHECK = &#x27;&#x27;&#x27;from pathlib import Path | 导入路径工具，供生成后的检查脚本读取 README。 |
| 15 | for name in (&quot;README.md&quot;, &quot;docs/README.md&quot;): | 依次检查根目录和 docs 目录的两份 README。 |
| 16 |     text = Path(name).read_text() | 读取当前 README 的文字，供后面的两项断言检查。 |
| 17 |     assert &quot;python3 run.py&quot; in text, name + &quot; 缺少正确命令&quot; | 检查是否写明正确运行命令；缺失时报告对应文件。 |
| 18 |     assert &quot;学习记录检查完成&quot; in text, name + &quot; 缺少预期输出&quot; | 检查是否写明运行后的预期输出；缺失时报告对应文件。 |
| 19 | print(&quot;PASS：两份 README 都有命令与预期输出&quot;) | 仅在两份文件都通过断言后打印 PASS。 |
| 20 | &#x27;&#x27;&#x27; | 多行字符串的边界标记；不属于传给模型或子进程的正文。 |
