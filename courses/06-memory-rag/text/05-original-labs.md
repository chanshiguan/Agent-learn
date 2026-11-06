# 原练习逐题运行与验收

> 本课教学副本使用简体中文问题与资料。本地向量案例统一使用 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`，这是支持多语言的编码模型；首次运行会下载权重。旧的英文模型缓存不能替代这份权重。默认长期记忆目录改为 `.stage06-memory-zh`，避免混用旧模型的向量；如果自行指定旧目录，也应新建集合并重新入库。模型资料见 [Sentence Transformers 官方说明](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)，学习所需用法已在本课说明。
>
> 离线测试用固定向量或字词重叠替身检查入库、召回、提示拼接和持久化，不能证明新模型的中文检索质量。实际运行时仍要按各实验标准核对排名与证据；关键词基线只做子串匹配，不提供完整中文分词。


以下命令从 ai-learn 根目录运行。每题有独立 Python 3.11 环境；创建和安装只在首次需要，日常直接用对应环境解释器。requirements.txt 列依赖，不是课程正文。不要将这些依赖安装进主环境或第二、三课环境。

原始代码完整保留在源码页，标为 upstream；补充参考解在本课实作章。原材料中的云价格与产品状态是来源快照，实际开销以账户和用量为准。

这些练习共用同一套排错方法：如果出现 ModuleNotFoundError，核对运行解释器与安装解释器是否相同；模型不存在先用 ollama list 核对名字；模型返回格式不符则保留实际输出，不伪造成功。原包版本与本地模型支持情况会影响结果，mock 测试和真实调用分开记录。

## 01-embeddings：Embedding

首次运行会下载 sentence-transformers 权重。记录实际模型、向量维度与相似度。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-06-01
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-06-01/bin/python -m pip install -r courses/06-memory-rag/examples/upstream/01-embeddings/requirements.txt
# 运行 courses/06-memory-rag/examples/upstream/01-embeddings/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-06-01/bin/python courses/06-memory-rag/examples/upstream/01-embeddings/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-06-01/bin/python courses/06-memory-rag/examples/upstream/01-embeddings/starter.py
```

验收：同义与无关句对照；相反句也可能相似，不能据相似度判事实。


## 02-vector-db：向量数据库

看 collection 的 ID、文段、metadata 与 query 返回值；判断临时或持久存储。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-06-02
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-06-02/bin/python -m pip install -r courses/06-memory-rag/examples/upstream/02-vector-db/requirements.txt
# 运行 courses/06-memory-rag/examples/upstream/02-vector-db/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-06-02/bin/python courses/06-memory-rag/examples/upstream/02-vector-db/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-06-02/bin/python courses/06-memory-rag/examples/upstream/02-vector-db/starter.py
```

验收：正确题能取回依据，未知题不要把任意近邻当答案。


## 03-chunking-comparison：切分比较

比较固定长度、段落、标题；检查关键条件与例外有没有断开。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-06-03
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-06-03/bin/python -m pip install -r courses/06-memory-rag/examples/upstream/03-chunking-comparison/requirements.txt
# 运行 courses/06-memory-rag/examples/upstream/03-chunking-comparison/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-06-03/bin/python courses/06-memory-rag/examples/upstream/03-chunking-comparison/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-06-03/bin/python courses/06-memory-rag/examples/upstream/03-chunking-comparison/starter.py
```

验收：不能只比较片段数量，要检查支持同一问题的证据是否完整。


## 04-full-rag-pipeline：原始 RAG 基线

原例只把文本传给模型；它用于理解检索生成，不满足逐事实引用的新综合要求。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-06-04
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-06-04/bin/python -m pip install -r courses/06-memory-rag/examples/upstream/04-full-rag-pipeline/requirements.txt
# 运行 courses/06-memory-rag/examples/upstream/04-full-rag-pipeline/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-06-04/bin/python courses/06-memory-rag/examples/upstream/04-full-rag-pipeline/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-06-04/bin/python courses/06-memory-rag/examples/upstream/04-full-rag-pipeline/starter.py
```

验收：先看检索，再看回答；本课 grounded_rag 才是完整引用参考。


## 05-long-term-memory：原始记忆基线

原实现使用 Chroma PersistentClient，数据写到指定目录；测试包含两个新进程一写一读，使用固定假向量避免下载权重。它能证明持久化，但尚未完整实现用户同意、更新、删除、期限和用户隔离。

```bash
# 用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。
python3.11 -m venv courses/.venv-lab-06-05
# 将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。
courses/.venv-lab-06-05/bin/python -m pip install -r courses/06-memory-rag/examples/upstream/05-long-term-memory/requirements.txt
# 运行 courses/06-memory-rag/examples/upstream/05-long-term-memory/test.py，按本行参数完成当前案例并核对输出。
courses/.venv-lab-06-05/bin/python courses/06-memory-rag/examples/upstream/05-long-term-memory/test.py
# 为本次命令设置明确的环境变量；后面的程序使用这些值运行。
MODEL=gemma4:e4b courses/.venv-lab-06-05/bin/python courses/06-memory-rag/examples/upstream/05-long-term-memory/starter.py
```

验收：原题用 test.py 的真实 Chroma 持久化测试证明重启读回；更新/删除/隔离/期限与“改表格”使用 memory_lifecycle.py 的补充完整参考。

