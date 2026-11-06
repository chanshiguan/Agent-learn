# AI Learn

这是一个用于学习 OpenAI Python SDK 的项目。

## 课程目录

- [全部课程](courses/index.html)
- [第二课：Prompt Engineering](lessons/index.html)
- [第三课：工具使用与第一个 Agent Loop](courses/03-tool-use-and-hello-agent/index.html)
- [第四课：Workflow Graph 与 Agent 框架](courses/04-agent-frameworks/index.html)
- [A/B 后续主线、五条身份分支与结业专题](courses/index.html)

后续新增 16 个独立课程目录：B 线 4、5、6、7、7.5、8；A 线 A1、A2、A3；五条身份分支；双轨结业专题。第五、八课为两线共用，保留原课程的选修和先修关系。每课最后都有练习章、验收标准和折叠参考答案。

课程文字、必读知识、原课核对资料和完整案例均可在本地阅读。实际运行验证和未验证范围见 [验证记录](courses/VERIFICATION.md)。

新增阶段放在 `courses/阶段编号-主题/`，包含自己的讲义、案例、参考资料与课后练习。第二课保留原有目录。

## 首次安装

打开终端并进入项目目录：

```bash
cd ~/Documents/ai-learn
```

创建 Python 虚拟环境：

```bash
python3 -m venv .venv
```

激活虚拟环境：

```bash
source .venv/bin/activate
```

激活成功后，终端提示符前通常会出现 `(.venv)`。

安装 OpenAI Python SDK：

```bash
python -m pip install openai
```

检查是否安装成功：

```bash
python -c "import openai; print(openai.__version__)"
```

## 平时进入项目

以后每次开始开发时，执行：

```bash
cd ~/Documents/ai-learn
source .venv/bin/activate
```

然后运行项目中的 Python 文件，例如：

```bash
python example.py
```

## 退出虚拟环境

完成开发后执行：

```bash
deactivate
```

终端提示符前的 `(.venv)` 消失，就表示已经退出虚拟环境。
