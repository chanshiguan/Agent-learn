# 虚构数据复现实验

先复制本目录到独立 demo。Python 标准库可执行 `python measure.py`，输出 count=3、accuracy=2/3。
选修 DVC 路径：在该副本初始化 Git 和 DVC，`dvc add data.csv` 保存数据版本，再 `dvc repro` 执行管线。
Git 保存代码、`.dvc` 元数据、`dvc.yaml`、`dvc.lock`，大数据保存在 cache 或另配置的 remote。
修改一行 correct 后再次运行，比较 metrics，保留失败与版本。此实验没有训练或验证论文模型。
