"""用固定实验结果演示决策门槛；数字是教学数据，不是模型评测结果。"""

# 质量、延迟和禁止动作分别比较；省 token 不能抵消越权。
def decide(baseline, candidate):
    required = {"pass_rate", "unsafe_actions", "latency", "tokens"}
    if set(baseline) != required or set(candidate) != required:
        raise ValueError("缺少同口径的四项指标")
    if candidate["unsafe_actions"]:
        return "拒绝：出现禁止动作"
    if candidate["pass_rate"] < baseline["pass_rate"]:
        return "拒绝：质量回退"
    if candidate["latency"] > baseline["latency"] * 1.2:
        return "暂不采用：超过事前延迟门槛"
    if candidate["tokens"] > baseline["tokens"] * 1.5:
        return "暂不采用：超过事前用量门槛"
    return "可继续验证：还须多次试跑、人工校准和保留集检查"


if __name__ == "__main__":
    # 保留原方案表现，改进后在同一题集和配置上比较，避免只展示新方案成功的个例。
    baseline = {"pass_rate": 0.8, "unsafe_actions": 0, "latency": 10, "tokens": 1000}
    candidate = {"pass_rate": 0.9, "unsafe_actions": 0, "latency": 11, "tokens": 1300}
    print("固定教学数据：", decide(baseline, candidate))
