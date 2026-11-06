"""五种编排的可运行控制流样例；用固定函数隔离模型随机性。"""

# 五个函数分别演示五种控制流程；输入和检查均固定，便于先看懂步骤如何连接。
# 线程池让独立的等待型调用重叠执行；它不能让有前后数据依赖的工具提前运行。
from concurrent.futures import ThreadPoolExecutor
import json


# 前一步没有产物就停止，避免把空输入继续传给后面的步骤。
def chain(text):
    draft=text.strip()
    if not draft:
        return {'status':'blocked','reason':'第一阶段没有产物'}
    return {'status':'done','summary':draft[:30]}


# 只处理已登记的任务类别；未知类别返回澄清信息。
def route(task):
    handlers={'事实核对':lambda:{'expert':'证据检查','result':'必须附来源'},
              '格式核对':lambda:{'expert':'格式检查','result':'必须有标题'}}
    if task not in handlers:
        return {'expert':None,'result':'未支持的任务，请澄清'}
    return handlers[task]()


# 两项检查彼此独立，分别返回不同字段，再合并结果。
def parallel(text):
    checks=[lambda:{'format':text.startswith('# ')},lambda:{'source':'[d1]' in text}]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda fn:fn(),checks))
    return {key:value for result in results for key,value in result.items()}


# 先限制任务数并去重，再给每项任务分配来源标识。
def orchestrate(topics):
    if len(topics)>3 or len(topics)!=len(set(topics)):
        raise ValueError('任务最多三个且不能重复')
    jobs=[{'topic':topic,'source':'d'+str(i+1)} for i,topic in enumerate(topics)]
    return [{'topic':job['topic'],'draft':'需核对 '+job['topic'],'source':job['source']} for job in jobs]


# 每轮记录具体缺项，再补相应内容；轮数耗尽时返回 stopped。
def optimize(text, limit=2):
    history=[]
    for attempt in range(limit+1):
        missing=[]
        if not text.startswith('# '): missing.append('标题')
        if '[d1]' not in text: missing.append('引用')
        history.append({'attempt':attempt,'missing':missing})
        if not missing: return {'status':'done','text':text,'history':history}
        if attempt==limit: break
        if '标题' in missing: text='# 摘要\n'+text
        if '引用' in missing: text+=' [d1]'
    return {'status':'stopped','text':text,'history':history}


if __name__=='__main__':
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    print(json.dumps({'chain':chain('固定资料摘要'),'route':route('事实核对'),
        'parallel':parallel('# 摘要 [d1]'),'workers':orchestrate(['成本','来源']),
        # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
        # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
        'optimizer':optimize('固定资料')},ensure_ascii=False,indent=2))
