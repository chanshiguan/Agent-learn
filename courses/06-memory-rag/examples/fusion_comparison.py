"""说明相对分数融合与排名融合的不同；不是远端向量数据库客户端。"""

# 同一份排名分别按分数和名次融合；观察 b 的分数优势在两种方法里如何体现。
from ranking_lab import reciprocal_rank_fusion


# 每路先缩放分数，再按权重相加；这个权重不是答案正确的概率。
def relative_fusion(dense, lexical, alpha=0.5):
    if not 0 <= alpha <= 1:
        raise ValueError('alpha 必须在 0 到 1 之间')
    scores = {}
    for source, weight in [(dense, alpha), (lexical, 1-alpha)]:
        if not source:
            continue
        low, high = min(source.values()), max(source.values())
        for key, value in source.items():
            normalized = (value-low)/(high-low) if high>low else 1.0
            scores[key] = scores.get(key,0)+weight*normalized
    return sorted(scores, key=lambda key:(-scores[key],key))


if __name__ == '__main__':
    dense={'a':0.9,'b':0.89,'c':0.1}
    lexical={'a':1.0,'b':10.0,'c':0.0}
    print('相对分数融合:',relative_fusion(dense,lexical))
    print('排名融合:',reciprocal_rank_fusion([['a','b','c'],['b','a','c']]))
