# 构建镜像，再处理同一份讲稿

本单元预计 **25—35 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《把临时安装步骤写进 Dockerfile》](0017-dockerfile.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 构建


## 运行并观察

```bash
# 将当前目录中的构建说明和程序制成镜像；成功后可按 classics-reader:chapter3 运行。
docker build -t classics-reader:chapter3 .
```

最后的点表示当前目录是构建输入目录。`-t` 给镜像起名并加上标签，后面的 `docker run` 用这个名称找到它。若提示找不到 Dockerfile，先看 `pwd`，不要急着重装 Docker。

观察日志中安装依赖和复制程序的步骤。构建完成后可以运行：

```bash
# 确认镜像已构建；预期列表有 chapter3 标签，但仍需运行来验证读取结果。
docker image ls classics-reader
```

预期能找到 `chapter3` 标签。镜像存在说明构建完成，还不能证明读取结果正确。

## 运行

```bash
# 将主机输入只读挂载、输出可写挂载，再运行读稿程序；预期 JSON 出现在主机 data/output 中。
docker run --rm \
  --mount "type=bind,src=$(pwd)/data/input,dst=/input,readonly" \
  --mount "type=bind,src=$(pwd)/data/output,dst=/output" \
  classics-reader:chapter3 \
  "/input/06 《狂人日记》第一讲两种叙述声音.docx" \
  /output/image.json
```

现在不再挂载 `read_docx.py`，因为程序已复制到镜像里。也不再把安装命令写进 `docker run`，因为依赖已在构建时准备好。

`ENTRYPOINT` 已经指定 `python read_docx.py`，所以这里只追加输入和输出。重复写一次 `python read_docx.py` 会被当成脚本参数，通常导致参数数量错误。

## 用一条对照确认结果

在主机已启用的 Python 环境中运行：

```bash
# 比较主机与镜像读同一文件的完整 JSON；预期“结果一致：True”，否则先检查来源指纹。
python -c "import json; from pathlib import Path; a=json.loads(Path('data/output/first.json').read_text()); b=json.loads(Path('data/output/image.json').read_text()); print('结果一致：', a == b)"
```

预期为 `True`。读取同一个输入、使用同一程序时，JSON 应一致。若不一致，比较 `source_sha256`、文件名和正文，再检查镜像是否重新构建；不要先把差异归因于 Docker “不稳定”。

## 独立完成第二讲

保持镜像不变，处理第二讲并输出到 `image-second.json`。先自己写命令，再看参考。

<details><summary>完整参考命令</summary>

```bash
# 将主机输入只读挂载、输出可写挂载，再运行读稿程序；预期 JSON 出现在主机 data/output 中。
docker run --rm \
  --mount "type=bind,src=$(pwd)/data/input,dst=/input,readonly" \
  --mount "type=bind,src=$(pwd)/data/output,dst=/output" \
  classics-reader:chapter3 \
  "/input/07 《狂人日记》第二讲月光与平等.docx" \
  /output/image-second.json
```

</details>

**本单元完成条件：**你能构建镜像、读出两份讲稿，并用主机结果对照其中一份。日志与输出文件都保留，失败时也记录实际报错。

## 本单元验收与参考答案

先完成上面的操作，再用自己的话回答。下面是核对思路和结果的参考，不要求背原句。

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**构建后怎么确认？** 镜像列表中有 `classics-reader` 的 `chapter3` 标签。再实际运行，才知道读取任务是否成功。

**运行时要再写 `python read_docx.py` 吗？** 不用。镜像的 `ENTRYPOINT` 已指定程序，只追加输入和输出路径。

**预期输出和对照是什么？** 第一讲写入 `image.json`，第二讲写入 `image-second.json`；同一版本第一讲的主机 JSON 与镜像 JSON 比较应为 `True`。第二讲预期为 1 段、1,306 字符。

**通过证据：**保留构建日志、两份镜像输出及对照结果。若不同，先比较来源指纹、文件名和正文，再看镜像是否包含新代码；只看到镜像名称不算整节通过。

</details>

## 资料依据

[部署练习](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/examples/stage-7/05-deploy/README.zh-Hans.md)说明镜像构建与运行；本课用相同输入输出检查环境迁移有没有改变结果。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
