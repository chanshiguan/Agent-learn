# 目的：读取库替我们解析 Word 内部结构。此时只验证有没有读到正确文档，还不进行任何模型调用。
# 预期：运行 python peek_docx.py，公开第一讲应显示 1 个正文段落。
from pathlib import Path
from docx import Document

# 固定第一份输入，先确认程序和人打开的是同一份讲稿。
source = Path("data/input/06 《狂人日记》第一讲两种叙述声音.docx")
document = Document(source)
print("文件：", source.name)
print("正文段落数量：", len(document.paragraphs))

# 目的：段落数量对，并不代表选对了文件。打印少量原文，让你能在讲稿页面中逐字核对。
# 预期：再次运行会多显示位置 1 和开头 80 字；原文件没有改变。
# 保留原位置并限制预览长度，既能回查，也不会把全文刷满终端。
for position, paragraph in enumerate(document.paragraphs, start=1):
    print("段落位置：", position)
    print("开头文字：", paragraph.text[:80])
