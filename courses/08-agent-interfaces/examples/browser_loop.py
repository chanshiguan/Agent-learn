"""本地虚构表单：观察→提议→策略→人工决定→执行→外部状态验证。无发送。"""

# 先读 observe/propose/policy，再看 run；固定提议用于隔离执行器问题，不代表模型规划。
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


# 读取页面真实值和版本，既用于执行前检查，也用于执行后验收。
def observe(page):
    return {'title':page.title(),'draft':page.locator('#draft').input_value(),
            'version':page.locator('#version').inner_text()}


# 按场景返回固定请求；请求携带观察快照，便于发现批准后页面变化。
def propose(observation, scenario):
    if scenario == 'offsite':
        return {'type':'navigate','url':'https://evil.test','expected':observation}
    if scenario == 'send':
        return {'type':'send','expected':observation}
    return {'type':'fill','value':'课程学习草稿','expected':observation}


# 填写需要操作者批准；发送和跳转都不属于本题允许的动作。
def policy(action):
    if action['type'] == 'fill':
        return 'ASK'
    return 'BLOCK'


# 只有策略允许、操作者接受、页面未变三项都满足，才调用浏览器填写。
def run(output, decision='reject', scenario='normal'):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page()
        # 演示页不需要网络，所有页面请求都阻断。
        page.route('**/*',lambda route:route.abort())
        page.set_content('<title>本地虚构表单</title><label>草稿<input id="draft"></label><span id="version">1</span>')
        before=observe(page)
        action=propose(before,scenario)
        verdict=policy(action)
        record={'before':before,'proposal':action,'policy':verdict,'executed':False}
        if verdict == 'BLOCK':
            record['status']='BLOCKED'
        else:
            # 只允许操作者通过 CLI 明确选择；提议无法自行给出批准。
            record['decision']=decision
            if decision != 'accept':
                record['status']='REJECTED'
            else:
                if scenario == 'stale':
                    page.locator('#version').evaluate('(e) => e.textContent = "2"')
                # 批准后再读一次当前页面；状态变化就停止，旧批准不能用于新状态。
                if observe(page) != action['expected']:
                    record['status']='STALE_REQUIRES_NEW_REVIEW'
                else:
                    try:
                        if scenario == 'failure':
                            raise RuntimeError('教学注入：执行器不可用')
                        page.locator('#draft').fill(action['value'])
                        record['executed']=True
                        # 执行后独立读取输入框，核对真正写进去的内容，而不是相信执行器口头报告。
                        after=observe(page)
                        if after['draft'] != action['value']:
                            raise RuntimeError('实际页面值与提议不一致')
                        record['status']='VERIFIED'
                    except Exception as error:
                        record['status']='FAILED'
                        record['error']=str(error)
        record['after']=observe(page)
        page.screenshot(path=str(output/'state.png'),full_page=True)
        browser.close()
    # 将当前产物保存到明确文件，供另一次运行或人工复核；保存成功本身不代表内容已通过验收。
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    (output/'receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
    return record


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    p.add_argument('--decision',choices=['accept','reject'],default='reject')
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    p.add_argument('--scenario',choices=['normal','offsite','send','stale','failure'],default='normal')
    # 为运行者提供明确的选项与默认值；这里的限制让同一实验可以按相同条件重跑。
    p.add_argument('--output',type=Path,default=Path('/tmp/ai-learn-action-loop'))
    # 先把命令行输入转为受约束的参数，防止错误模式或缺少参数到执行一半才暴露。
    a=p.parse_args()
    # 以 JSON 保留字段和类型，便于重跑比较或人工核对；不能只保存对象的调试显示。
    # ensure_ascii：设为 False 时直接保留中文，方便阅读日志与工具结果；JSON 结构和字段含义不变。
    # indent：给本地 JSON 产物增加缩进，方便人工逐字段检查；不会改变数据内容。
    print(json.dumps(run(a.output,a.decision,a.scenario),ensure_ascii=False,indent=2))
