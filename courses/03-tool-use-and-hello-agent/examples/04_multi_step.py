"""练习 4，同时也是天气小助手的最小项目入口：仅暴露两个只读工具。"""

# 温度换算依赖天气查询结果；模型必须先读到摄氏值，才有第二步的输入。

import argparse

from agent import print_run, run_agent
from model_client import make_ask
from tools import TOOLS

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("question", nargs="?", default="查询台北的示例气温，再用温度工具换算成华氏。")
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
    print_run(run_agent(args.question, make_ask(), tools=[TOOLS[0], TOOLS[2]]))
