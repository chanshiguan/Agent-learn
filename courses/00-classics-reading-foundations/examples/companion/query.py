# 目的：把同一个问题及命中结果保存起来，下一章可以对照修改前后的检索表现。
# 预期：search.json 只有问题和片段，不会冒充模型答案。
import argparse
import json
from .files import save
from .rag import retrieve, answer, rerank, rewrite
from .files import load
from .corpus import visible


def main(kind="search"):
    parser = argparse.ArgumentParser(description="从讲稿中找资料")
    parser.add_argument("question")
    parser.add_argument("--method", default="keyword")
    parser.add_argument("--expand",action="store_true")
    parser.add_argument("--rerank",action="store_true")
    parser.add_argument("--rewrite",action="store_true")
    parser.add_argument("--tenant", default="demo")
    parser.add_argument("--book", default="狂人日记")
    args = parser.parse_args()
    query=rewrite(args.question) if args.rewrite else args.question
    if kind == "direct-vector":
        from .vectors import embed
        chunks=visible(load("corpus.json")["chunks"],args.tenant,args.book)
        vectors=embed([c["text"] for c in chunks])
        query_vector=embed([query])[0]
        hits=sorted([{**c,"score":sum(a*b for a,b in zip(v,query_vector))}
                     for c,v in zip(chunks,vectors)],key=lambda c:-c["score"])[:5]
    else:
        hits = retrieve(query,args.tenant,args.book,args.method,expand=args.expand)
    if args.rerank:
        hits=rerank(args.question,hits)
    result = answer(args.question,hits) if kind == "ask" else {"question":args.question,"query":query,"hits":hits}
    save(kind + ".json",result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
