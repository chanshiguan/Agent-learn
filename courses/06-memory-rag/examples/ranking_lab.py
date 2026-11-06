"""离线排名实验：演示 RRF 与指标，不冒充真实 embedding 模型。"""

# 固定排名实验不调用语义模型；用小列表先核对融合和指标的计算。


# 同一 ID 在不同列表的倒数排名贡献相加；不要求各路原始分数同尺度。
def reciprocal_rank_fusion(rankings, k=60):
    scores = {}
    for ranking in rankings:
        if len(set(ranking)) != len(ranking):
            raise ValueError("单路排名不能有重复 ID")
        for rank, item in enumerate(ranking, 1):
            scores[item] = scores.get(item, 0) + 1 / (k + rank)
    return sorted(scores, key=lambda item: (-scores[item], item))


# 根据相关 ID 集合计算命中与召回；返回数量 k 不是召回率的分母。
def metrics(ranking, relevant, k):
    selected = ranking[:k]
    hits = set(selected) & set(relevant)
    first = next((i for i, item in enumerate(selected, 1) if item in relevant), None)
    return {"hit": int(bool(hits)), "recall": len(hits) / len(relevant) if relevant else 0,
            "reciprocal_rank": 1 / first if first else 0}


if __name__ == "__main__":
    dense = ["d2", "d1", "d3"]
    keyword = ["d1", "d3", "d2"]
    fused = reciprocal_rank_fusion([dense, keyword])
    for name, ranking in [("向量排名（固定输入）", dense), ("词法排名（固定输入）", keyword), ("RRF", fused)]:
        print(name, ranking, metrics(ranking, {"d1"}, 1))
