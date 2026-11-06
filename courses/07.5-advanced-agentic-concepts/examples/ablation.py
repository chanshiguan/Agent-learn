"""可复现的故障注入与删除实验：固定程序输出，不冒充模型评测。"""

# 每次只改变是否保留来源检查，用同一套正反例观察退步；不测模型能力。
import json

CASES=[{'id':'normal','refs':['d1'],'expected':'ok'},
       {'id':'bad_ref','refs':['invented'],'expected':'stop'},
       {'id':'empty','refs':[],'expected':'stop'},
       {'id':'timeout','refs':['d1'],'error':'timeout','expected':'stop'}]


# 本题既检查返回值，也检查异常是否符合预期；正确停止也可能是通过。
def trial(case, check_sources):
    if case.get('error'):
        return 'stop'
    if check_sources and (not case['refs'] or any(r!='d1' for r in case['refs'])):
        return 'stop'
    return 'ok'


# 逐题保存基线与删除后的差异，避免只看正常题掩盖故障。
def experiment():
    rows=[]
    for variant,check in [('baseline',True),('remove_source_check',False)]:
        for case in CASES:
            actual=trial(case,check)
            rows.append({'variant':variant,'case':case['id'],'actual':actual,'passed':actual==case['expected']})
    return {'mode':'确定性故障实验','rows':rows,'decision':'保留来源检查：删除后 bad_ref 与 empty 回退。该控制不是可随模型升级删除的措辞补丁。'}


if __name__=='__main__':
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(experiment(),ensure_ascii=False,indent=2))
