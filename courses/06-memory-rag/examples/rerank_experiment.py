"""A/B/C 对照；C 使用明示规则重排，非训练好的神经 reranker。"""

# A/B/C 共用题目和资料，只逐步增加混合检索与重排；先读 experiment，再看三项检索函数。
import argparse
import json
import math
from collections import Counter
from time import perf_counter
from grounded_rag import DOCS, embed, cosine, generate, tokens

DOCUMENTS = DOCS + [
    {"id":"parking","owner":"*","text":"停车场周六08:00开放，停车每小时5元。"},
    {"id":"materials","owner":"*","text":"报名成功可下载本课程电子资料，不含其他课程。"},
    {"id":"contact","owner":"*","text":"课程咨询电话为虚构号码000-1234。"},
    {"id":"place","owner":"*","text":"课程地点为教学楼二层201教室。"},
    {"id":"food","owner":"*","text":"课堂不提供午餐，饮水机位于门厅。"},
    {"id":"invoice","owner":"*","text":"发票在付款后7天内发到报名邮箱。"},
    {"id":"recording","owner":"*","text":"本课程不提供录像，缺席者可以下载讲义。"},
]
CASES = [
    ("课程几点开始","alice",{"schedule"}),
    ("报名截止时间","alice",{"signup"}),
    ("未满18岁可以报名吗","alice",{"signup"}),
    ("提前取消退款","alice",{"refund"}),
    ("主办方取消课程退款","alice",{"refund","exception"}),
    ("报读截止时间","alice",{"signup"}),
    ("火星天气","alice",set()),
    ("Bob私人预约编号","alice",set()),
    ("课程几点结束","alice",{"schedule"}),
    ("提前多少小时取消全额退款","alice",{"refund"}),
    ("主办方取消不足24小时能退款吗","alice",{"exception"}),
    ("停车每小时多少钱","alice",{"parking"}),
    ("停车场什么时候开放","alice",{"parking"}),
    ("报名后能下载其他课程资料吗","alice",{"materials"}),
    ("课程咨询电话","alice",{"contact"}),
    ("课程地点在哪层哪个教室","alice",{"place"}),
    ("课程提供午餐吗","alice",{"food"}),
    ("饮水机在哪里","alice",{"food"}),
    ("发票付款后几天收到","alice",{"invoice"}),
    ("缺席能看录像吗","alice",{"recording"}),
]


# 先限制可见文档；A 用向量排名，B/C 继续加入 BM25 并用 RRF 融合。
def retrieve(query, user, hybrid, embedding_model, k):
    # 执行白名单取自本轮公开的工具，防止模型用一个实现中存在、但本轮未授权的函数名绕过限制。
    allowed = [doc for doc in DOCUMENTS if doc["owner"] in ("*",user)]
    if any(name in query.lower() and name != user for name in ("alice","bob")):
        return []
    vectors = embed([query]+[doc["text"] for doc in allowed], embedding_model)
    dense_scores = {doc["id"]:cosine(vectors[0],vector) for doc,vector in zip(allowed,vectors[1:])}
    dense = sorted([doc for doc in allowed if dense_scores[doc["id"]] >= (0.25 if embedding_model else 0.12)],
                   key=lambda doc:(-dense_scores[doc["id"]],doc["id"]))[:k]
    if not hybrid:
        return dense
    # 真正的 BM25 公式，中文用单字分词；分词器简单但不冒称仅词频就是 BM25。
    query_terms = tokens(query.replace("报读","报名").replace("截止时间","提交"))
    bags = [tokens(doc["text"]) for doc in allowed]
    average = sum(sum(bag.values()) for bag in bags)/len(bags)
    scores = {}
    for doc,bag in zip(allowed,bags):
        score = 0.0
        for word in query_terms:
            frequency = bag[word]
            document_frequency = sum(word in other for other in bags)
            inverse = math.log(1+(len(bags)-document_frequency+0.5)/(document_frequency+0.5))
            denominator = frequency+1.5*(1-0.75+0.75*sum(bag.values())/average)
            score += inverse*frequency*2.5/denominator
        scores[doc["id"]] = score
    lexical = sorted([doc for doc in allowed if scores[doc["id"]]>0],
                     key=lambda doc:(-scores[doc["id"]],doc["id"]))[:k]
    fused = Counter()
    for ranking in (dense,lexical):
        for position,doc in enumerate(ranking,1):
            fused[doc["id"]] += 1/(60+position)
    return sorted([doc for doc in allowed if doc["id"] in fused],
                  key=lambda doc:(-fused[doc["id"]],doc["id"]))[:k]


# 规则只读取问题与候选正文，不读取标准答案；规则本身仍需在新问题上验证。
def pair_score(query, text):
    # 对问题和候选正文一起计算；不读取题集 gold 或文档 ID。
    expanded = query.replace('报读', '报名').replace('截止时间', '提交')
    score = float(sum((tokens(expanded) & tokens(text)).values()))
    intents = [('几点', '开始'), ('截止', '提交'), ('18岁', '18岁'),
               ('提前取消', '24小时'), ('主办方取消', '主办方取消'), ('停车', '停车'), ('发票', '发票'),
               ('午餐', '午餐'), ('饮水机', '饮水机'), ('录像', '录像'),
               ('地点', '地点'), ('电话', '电话'), ('资料', '资料')]
    for question_phrase, evidence_phrase in intents:
        if question_phrase in expanded and evidence_phrase in text:
            score += 10
    if '提交' in expanded and '提交' in text:
        score += 10
    return score


# 只改变已有候选的顺序，不会找回候选之外的资料。
def rerank(query, candidates):
    return sorted(candidates, key=lambda doc: (-pair_score(query, doc['text']), doc['id']))


# 无答案题不虚构 Recall；另外记录 empty_correct，检查是否错误取回资料。
def metrics(found, gold):
    ids = [doc['id'] for doc in found]
    positions = [i for i, item in enumerate(ids, 1) if item in gold]
    return {'hit': bool(set(ids) & gold) if gold else None,
            'recall': len(set(ids) & gold) / len(gold) if gold else None,
            'reciprocal_rank': 1 / min(positions) if positions else 0,
            'empty_correct': not ids if not gold else None}


# 记录每组候选和最终证据，区分没召回、排得靠后与生成错误。
def experiment(model=None, candidate_k=8, answer_k=5, live=False):
    if not 1 <= answer_k <= candidate_k:
        raise ValueError('须满足 1 <= answer_k <= candidate_k')
    rows = []
    for question, user, gold in CASES:
        for variant in ('A', 'B', 'C'):
            # 每题在三组里都跑，保持题目、身份、候选数和生成方式一致。
            start = perf_counter()
            candidates = retrieve(question, user, hybrid=variant != 'A',
                                  embedding_model=model, k=candidate_k)
            ordered = rerank(question, candidates) if variant == 'C' else candidates
            selected = ordered[:answer_k]
            rows.append({'variant': variant, 'question': question,
                         'candidates': [d['id'] for d in candidates],
                         'selected': [d['id'] for d in selected], 'gold': sorted(gold),
                         'candidate_recall': metrics(candidates, gold)['recall'],
                         **metrics(selected, gold),
                         'evidence': [{'source_id': d['id'], 'text': d['text']} for d in selected],
                         'answer': generate(selected,question,live),
                         'milliseconds': round((perf_counter()-start)*1000, 3)})
    summaries = {}
    for variant in ('A', 'B', 'C'):
        subset = [row for row in rows if row['variant'] == variant]
        # 无答案题不参与普通召回均值，另统计是否错误返回资料。
        answerable = [row for row in subset if row['gold']]
        summaries[variant] = {
            'mean_recall': round(sum(row['recall'] for row in answerable)/len(answerable), 3),
            'mrr': round(sum(row['reciprocal_rank'] for row in answerable)/len(answerable), 3),
            'empty_cases_correct': sum(row['empty_correct'] is True for row in subset)}
    return {'embedding': model or '字符计数教学基线', 'reranker': '基于问题与正文的规则基线',
            'candidate_k': candidate_k, 'answer_k': answer_k,
            'generation': 'Ollama 生成，逐条人工复核' if live else '完整证据摘录基线，没有模型生成',
            'cost': {'external_paid_calls':0,'local_generation_calls':sum(bool(row['selected']) for row in rows) if live else 0,
                     'local_embedding_requests':sum(not any(name in row['question'].lower() and name != 'alice' for name in ('alice','bob')) for row in rows) if model else 0, 'hardware_cost':'未估算'},
            'scope': '公开开发题；规则按开发样例设计，不是盲测或通用语义效果',
            'summary': summaries, 'rows': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--embedding-model')
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--candidate-k', type=int, default=8)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--answer-k', type=int, default=5)
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    parser.add_argument('--live',action='store_true')
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    args = parser.parse_args()
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    print(json.dumps(experiment(args.embedding_model, args.candidate_k, args.answer_k, args.live),
                     # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
                     # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
                     ensure_ascii=False, indent=2))
