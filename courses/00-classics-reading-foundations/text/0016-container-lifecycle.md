# 程序退出后，容器和文件分别去哪了

本单元预计 **20—30 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《把讲稿交给容器，把结果带回来》](0015-mount-files.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 保留一个容器，观察它结束后的状态

这次不用 `--rm`，并给实验容器起一个明确的名字：


## 运行并观察

```bash
# 保留一个具名实验容器，分别写入容器内部与主机挂载目录；预期打印“两个文件已写入”。
docker run --name reading-lifecycle \
  --mount "type=bind,src=$(pwd)/data/output,dst=/output" \
  python:3.12-slim \
  python -c "from pathlib import Path; Path('/tmp/inside.txt').write_text('容器内部'); Path('/output/outside.txt').write_text('主机挂载目录'); print('两个文件已写入')"
# 把已停止的实验容器也列出来；预期可以观察到 Exited 状态及退出码。
docker ps -a --filter name=reading-lifecycle
# 读取指定实验容器的标准输出与错误；失败程序若没打印内容，日志也可能为空。
docker logs reading-lifecycle
```

预期容器显示已退出，退出码为 `0`；日志中能看到最后那句输出。`docker ps` 默认只显示正在运行的容器，`-a` 才包含已经停止的。若提示名字已占用，先用 `docker ps -a --filter name=reading-lifecycle` 确认是不是你之前的实验，不要清理其他任务的容器。

## 再次启动与删除

```bash
# 重新执行这个已停止容器原先的命令并显示输出；它不会创建新的容器。
docker start -a reading-lifecycle
# 删除本节已停止的具名实验容器；预期容器记录消失，主机挂载输出仍保留。
docker rm reading-lifecycle
# 从主机直接读取挂载输出；预期仍看到“主机挂载目录”，说明结果不依赖容器保留。
cat data/output/outside.txt
```

`start -a` 再次运行这个容器配置好的命令，并显示输出；`rm` 删除已经退出的实验容器。挂载在主机上的 `outside.txt` 仍在。容器内部 `/tmp/inside.txt` 属于被删除容器的文件层，新建容器不会继承它。

不要在这里运行全局清理命令。我们只删除自己命名并确认已经停止的实验容器。

## 观察一次失败

```bash
# 故意让主进程以状态 7 退出；用于验证无日志时也能从状态发现失败。
docker run --name reading-failure python:3.12-slim python -c "raise SystemExit(7)"
# 读取实验容器保存的退出码；本节故意失败的程序预期返回 7。
docker inspect reading-failure --format '{{.State.ExitCode}}'
# 读取指定实验容器的标准输出与错误；失败程序若没打印内容，日志也可能为空。
docker logs reading-failure
# 删除本节已停止的具名实验容器；预期容器记录消失，主机挂载输出仍保留。
docker rm reading-failure
```

预期退出码为 `7`，日志可能为空，因为这段程序没有打印文字。没有日志并不等于成功；要结合退出状态判断。日后资料读取失败，可以先看程序的错误输出，再看退出状态，而不是先重启整台服务器。

## 第 2 章验收

向我说明三件事：为什么读稿程序完成后容器停止；为什么删除容器后挂载结果仍存在；哪个位置应该只读。保留 `container.json`，下一章会拿它与镜像运行结果比较。

<details><summary>参考解释</summary>

容器中的主进程是一次性程序，任务完成就退出。绑定挂载的输出实际位于主机目录，因此删除容器不会同时删除主机文件。讲稿是输入，设为只读能避免本次读取程序误改原资料；结果另写到输出目录。

</details>

## 本单元验收与参考答案

先完成上面的操作，再用自己的话回答。下面是核对思路和结果的参考，不要求背原句。

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**停止和删除有什么不同？** 主进程结束后容器停止，但未用 `--rm` 时容器记录与内部文件层仍保留，可以查看日志或再次启动；`docker rm` 才删除这个已停止容器。

**删除后结果在哪？** `outside.txt` 位于主机 `data/output/`，仍能读取；容器内部 `/tmp/inside.txt` 随容器删除而丢失，新容器不会自动继承它。讲稿挂载应只读，结果目录可写。

**没有日志就成功了吗？** 不是。故意失败的实验没有打印内容，但退出码是 7。要同时看日志和状态。

**通过证据：**正常实验显示 `Exited (0)`，失败实验退出码为 7；删除两个具名实验容器后，主机挂载输出仍存在。

</details>

## 资料依据

[Stage 7 部署练习](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/examples/stage-7/05-deploy/README.zh-Hans.md)的容器运行示例是后续应用。本节增加了生命周期观察，不将运行成功等同于生产隔离已完成。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
