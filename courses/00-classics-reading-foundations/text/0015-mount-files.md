# 把讲稿交给容器，把结果带回来

本单元预计 **25—35 分钟**。上一节的容器只打印了一句话；现在让它运行第一章同一个读取程序。先确认终端位于练习目录，运行 `pwd` 和 `ls`，应看到 `read_docx.py` 与 `data/input/`。

## 先画清楚文件在哪

| 主机上的位置 | 容器里的位置 | 用途 |
|---|---|---|
| `read_docx.py` | `/app/read_docx.py` | 要运行的程序，只读 |
| `data/input/` | `/input/` | 五份讲稿，只读 |
| `data/output/` | `/output/` | 接收新结果，可写 |

这叫[绑定挂载](../courses/00-classics-reading-foundations/knowledge/docker-boundaries.html)：把主机的一处文件或目录接到容器内的指定位置。这里没有复制整个知识库，也没有让镜像永久包含讲稿。

先创建输出目录：

```bash
# 准备接收结果的主机目录；已存在时保留原文件，成功通常没有输出。
mkdir -p data/output
```

## 第一次在容器里读讲稿

```bash
# 将主机输入只读挂载、输出可写挂载，再运行读稿程序；预期 JSON 出现在主机 data/output 中。
docker run --rm \
  --mount "type=bind,src=$(pwd)/read_docx.py,dst=/app/read_docx.py,readonly" \
  --mount "type=bind,src=$(pwd)/data/input,dst=/input,readonly" \
  --mount "type=bind,src=$(pwd)/data/output,dst=/output" \
  --workdir /app \
  python:3.12-slim \
  sh -c 'python -m pip install python-docx==1.2.0 && python read_docx.py "/input/06 《狂人日记》第一讲两种叙述声音.docx" /output/container.json'
```

`$(pwd)` 由主机终端展开为当前目录的完整路径，所以必须先进入练习目录。外层双引号保留路径里的空格，`sh -c` 后的单引号让整段命令交给容器执行。里面的 `&&` 表示只有依赖安装成功，才继续读取讲稿。

这次把安装依赖也写在运行命令里，是为了看清容器需要自己的依赖。第三章会把安装移到构建阶段，避免每次运行都重复做。不要把这里的临时做法直接当成最终部署方式。

## 检查结果落在何处

命令成功后，在主机打开 `data/output/container.json`。虽然 Python 在容器中写的是 `/output/container.json`，你仍能在主机看到它，因为这两个位置通过挂载连接在一起。

如果提示 `No such file or directory`，先区分是挂载源不存在，还是程序在容器里找错位置。程序的输入必须使用 `/input/` 下的完整文件名，不能把主机个人目录的路径原样当作容器路径。

## 动手验证只读挂载

下面这次故意把输出指向只读输入目录。它应该失败；该目录中不应新增 `should-fail.json`。

```bash
# 故意向只读挂载目录写文件；预期权限错误，并且输入目录不新增 should-fail.json。
docker run --rm \
  --mount "type=bind,src=$(pwd)/data/input,dst=/input,readonly" \
  python:3.12-slim \
  python -c "from pathlib import Path; Path('/input/should-fail.json').write_text('test')"
```

只读挂载限制程序对该位置的写入。它并不代表整个容器已经拥有完整安全隔离；本章只是明确输入和输出的职责。

**本单元完成条件：**主机能找到容器生成的 JSON；你能解释 `/input` 和 `/output` 分别对应哪里；只读写入实验按预期失败。

## 本单元验收与参考答案

先完成上面的操作，再用自己的话回答。下面是核对思路和结果的参考，不要求背原句。

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**输入输出分别在哪？** 主机 `data/input/` 对应容器 `/input/`；主机 `data/output/` 对应容器 `/output/`。所以容器写 `/output/container.json` 后，主机能在 `data/output/container.json` 读到它。

**只读实验应该成功吗？** 应失败。写 `/input/should-fail.json` 会被只读挂载拒绝；主机输入目录中不应新增这个文件。这次错误恰好是实验的预期结果。

**通过证据：**主机能打开 `container.json` 并核对第一讲来源；保留只读写入的报错，确认输入没有被改写。输入用容器路径 `/input/...`，不能直接照搬主机路径。

</details>

## 资料依据

[部署练习](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/examples/stage-7/05-deploy/README.zh-Hans.md)说明运行参数与文件系统限制；本节将文件输入输出拆成可观察实验，供后面知识库服务复用。
