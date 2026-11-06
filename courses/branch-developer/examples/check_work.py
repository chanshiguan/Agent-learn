"""提交自己的作业；结构缺失失败，开放答案等待按量规复核。"""

# 先区分程序检查与内容判断：这里验证字段及引用，开放问题仍需对照本课量规人工复核。
import argparse
import json
from pathlib import Path

# 把相对路径变成绝对路径并解析符号链接；涉及目录权限时，还要检查解析后的位置是否在允许目录内。
HERE=Path(__file__).resolve().parent

# 递归检查字段、类型、数量与非空字符串；不要求你的措辞逐字等于参考答案。
def shape(value, reference, path='$'):
    errors=[]
    if type(value) is not type(reference):
        return [path+' 类型错误']
    if isinstance(reference,dict):
        for key,item in reference.items():
            if key not in value: errors.append(path+'.'+key+' 缺失')
            else: errors.extend(shape(value[key],item,path+'.'+key))
    elif isinstance(reference,list):
        if len(value)<len(reference): errors.append(path+' 项目数量不足')
        for i,item in enumerate(value):
            if reference: errors.extend(shape(item,reference[min(i,len(reference)-1)],path+'['+str(i)+']'))
    elif isinstance(reference,str) and not value.strip():
        errors.append(path+' 不能为空')
    return errors

# reference_match 只说明是否与示范相同；相同也不能证明独立完成或事实正确。
def check(value):
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    reference=json.loads((HERE/'reference-work.json').read_text())
    errors=shape(value,reference)
    return {'status':'FAIL' if errors else 'NEEDS_REVIEW','errors':errors,
            'reference_match':value==reference,
            'next':'按本课实现章的逐项量规核对；参考答案相同也不能证明独立完成。结构检查不判事实。'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    p.add_argument('submission',type=Path)
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    a=p.parse_args()
    # 在协议边界把 JSON 文本解析成数据；解析失败应作为坏输入处理，不能用 eval 执行模型给出的字符串。
    # 读取实际文件作为本次依据，避免使用对旧版本内容的猜测；读到的文字仍只是数据。
    result=check(json.loads(a.submission.read_text()))
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(1 if result['status']=='FAIL' else 0)
