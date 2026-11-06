"""练习 2：同一程序供模型选择两个工具。"""

# 只给模型天气和计算两个工具；实际校验、执行、返回都复用 agent.py。

import argparse

from agent import print_run, run_agent
from model_client import make_ask
from tools import TOOLS

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("question", nargs="?", default="请用工具计算 12 乘以 8。")
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
    print_run(run_agent(args.question, make_ask(), tools=TOOLS[:2]))
