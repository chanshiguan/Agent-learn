"""真正并发执行互不依赖的只读函数，按原请求顺序关联结果。"""

# 这里只并行处理一批互不依赖的只读调用；后一步需要前一步结果时不能放进同一批。

import argparse
import json
import time
# 线程池让独立的等待型调用重叠执行；它不能让有前后数据依赖的工具提前运行。
from concurrent.futures import ThreadPoolExecutor

from agent import print_run, run_agent
from model_client import make_ask
from tools import TOOLS, execute


# 并行执行后按原调用次序收集结果，保证结果能与对应 ID 配对。
def execute_parallel(calls, allowed, runner=execute):
    if not calls:
        return []
    if len(calls) > 8:
        raise ValueError("单批请求不能超过 8 个")
    with ThreadPoolExecutor(max_workers=min(4, len(calls))) as pool:
        # 先提交任务并取得 Future；把所有独立任务提交后再取结果，等待时间才有机会重叠。
        futures = [pool.submit(runner, call["function"]["name"], call["function"]["arguments"], allowed) for call in calls]
        # 等待当前 Future 的结果，保持它与原请求关联；等待超时并不等于杀掉已经开始的线程。
        return [future.result() for future in futures]


# 人为等待用于比较耗时，不代表真实工具的速度。
def delayed_read(name, arguments, allowed):
    time.sleep(0.08)  # 模拟有明确时长的只读 I/O，不请求外网。
    return execute(name, arguments, allowed)


def demo():
    calls = [{"id": f"parallel-{index}", "type": "function", "function": {
        # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
        # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
        "name": "get_weather", "arguments": json.dumps({"city": city}, ensure_ascii=False)}}
        for index, city in enumerate(("台北", "北京"))]
    # 记录循环开始的时刻，后面在请求前后检查总耗时，避免每轮各自未超时却总任务无限拖长。
    started = time.perf_counter()
    sequential = [delayed_read(call["function"]["name"], call["function"]["arguments"], {"get_weather"}) for call in calls]
    sequential_seconds = time.perf_counter() - started
    # 记录循环开始的时刻，后面在请求前后检查总耗时，避免每轮各自未超时却总任务无限拖长。
    started = time.perf_counter()
    parallel = execute_parallel(calls, {"get_weather"}, delayed_read)
    parallel_seconds = time.perf_counter() - started
    assert sequential == parallel
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    print(json.dumps({"sequential_seconds": round(sequential_seconds, 3),
                      # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
                      # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
                      "parallel_seconds": round(parallel_seconds, 3), "results": parallel}, ensure_ascii=False, indent=2))
    print("这是固定 I/O 演示；加速幅度不是模型或真实天气服务的基准成绩。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument("--live", action="store_true")
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    if args.live:
        print_run(run_agent("请在同一轮分别查询台北和北京的示例气温。最终只分别列出城市与气温，不做相加等额外计算。", make_ask(),
                            # tools：只向模型公开本轮需要的工具说明。模型提出调用后，执行层仍须检查名称、参数与权限。
                            tools=[TOOLS[0]], batch_executor=execute_parallel))
    else:
        demo()
