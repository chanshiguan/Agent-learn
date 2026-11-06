"""练习 3：模型可以继续调用，也可以直接结束。"""

# 先看命令行参数，再到 agent.py 的 run_agent 看循环；max_steps 限制模型请求轮数。

import argparse

from agent import print_run, run_agent
from model_client import make_ask

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("question", nargs="?", default="先用工具算 12 加 8，再把结果乘以 3。")
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--max-steps", type=int, default=6)
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    # max_steps：限制循环最多执行多少步；它是程序的停止条件，不能只在提示词里写“不要无限循环”。
    print_run(run_agent(args.question, make_ask(), max_steps=args.max_steps))
