"""生成自包含的虚构资料练习。参考答案明确区分于模型实际输出。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = {
    "branch-researcher": (
        "对三个问题逐一核对：Transformer 是否去掉循环和卷积作为其主要序列架构；论文评测哪些翻译任务；它是否证明所有任务都优于所有方法。",
        [("p1", "Attention Is All You Need 的模型架构章节提出以注意力机制构建 Transformer，不采用循环或卷积作为其主要序列建模架构。"), ("p2", "论文报告 WMT 2014 英德与英法翻译任务结果，实验有具体模型和训练条件。"), ("p3", "这是论文相关段落的教学概述，不是所有任务、所有模型的普遍比较；正式引用应回到原论文对应章节与表格。")],
        "前两项在给定概述中有支持；“所有任务都最优”没有证据。正式研究需核对论文架构章节与实验表格。",
        [("主要序列架构不使用循环与卷积", ["p1"], "supported"), ("评测包含英德和英法翻译", ["p2"], "supported"), ("证明所有任务都优于所有方法", [], "unsupported")],
        ["概述不是原始实验数据；复现前需核对论文具体训练设置与表格"]),
    "branch-developer": (
        "只读检查演示 README 改动计划，指出允许范围、验证与尚缺证据，不修改文件。",
        [("d1", "任务只允许修改 README.md，增加运行检查的说明。"), ("d2", "现有检查命令为 python check.py；不得删除。"), ("d3", "尚未执行检查，也没有产生 diff。")],
        "计划：只补 README 中的检查说明，保留 python check.py；得到具体修改授权后实施，随后展示 diff 与真实检查输出。",
        [("修改范围只有 README.md", ["d1"], "supported"), ("检查已经通过", [], "unsupported")],
        ["实际 diff", "实际检查结果"]),
    "branch-teacher": (
        "为虚构课堂设计15分钟影子活动草稿：目标、材料、步骤、两层提示、形成性检查、两题exit ticket；区分给定事实和教学建议。",
        [("t1", "活动主题是观察光源、物体和屏幕的相对位置与影子的关系。"), ("t2", "可用材料为纸笔、手电筒、不透明小卡片和白纸屏幕；不照射眼睛。"), ("t3", "学生年龄、已学内容和个别支持需求尚未提供。")],
        "草稿：0–2分钟预测，2–7分钟用卡片挡住手电光并观察屏幕，7–11分钟一次只改一个位置，11–13分钟画图解释，13–15分钟完成离堂题。提示一：先保持两个位置不变；提示二：比较卡片靠近光源前后的影子。离堂题：你改变了什么？证据是什么？教师需根据年龄调整。",
        [("材料包含手电筒和不透明卡片", ["t2"], "supported"), ("已知全部学生年龄", [], "unsupported")],
        ["年龄与先修", "安全和可及性调整", "三条科学事实的教师核查"]),
    "branch-knowledge-worker": (
        "将会议资料整理为 Decision/ActionItem/Owner/DueDate/SourceSentence/NeedsConfirmation 行动表草稿，缺失不猜。",
        [("m1", "会议决定先制作报名表原型，不发布正式版本。"), ("m2", "小林负责整理报名字段，周五前交给小周。"), ("m3", "预算待财务确认。会议记录未注明日期。")],
        "Decision：先做原型、不发布。ActionItem：整理报名字段。Owner：小林。DueDate：周五，具体日期待确认。SourceSentence：m2。NeedsConfirmation：会议日期和预算。",
        [("小林负责整理字段", ["m2"], "supported"), ("预算已获批准", [], "unsupported"), ("周五的具体年月日", ["m3"], "uncertain")],
        ["会议日期", "周五对应的具体日期", "预算确认人及结果"]),
    "branch-everyday-users": (
        "把虚构消息整理为提醒草稿，分别给 Draft、FactsCopied、NeedsConfirmation；不得发送、创建真实提醒或猜日期。",
        [("e1", "小雨请你在周五前交海报初稿。"), ("e2", "海报需包含活动名称、时间、地点。"), ("e3", "消息未提供活动名称、具体日期、地点和提交渠道。")],
        "Draft：周五前准备海报初稿，核对活动名称、时间、地点。FactsCopied：任务和字段来自 e1/e2。NeedsConfirmation：具体日期、活动资料、提交渠道。此内容仅为草稿。",
        [("需交海报初稿", ["e1"], "supported"), ("已发送提醒", [], "unsupported")],
        ["周五的具体日期", "活动名称与时间地点", "提交渠道"]),
}


def main():
    code = Path(__file__).with_name("evidence_example.py").read_text()
    for slug, (task, evidence, draft, claims, pending) in DATA.items():
        directory = ROOT / slug / "examples"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "exercise.py").write_text(code)
        (directory / "input.json").write_text(json.dumps({"task": task, "evidence": [{"id": key, "text": value} for key, value in evidence]}, ensure_ascii=False, indent=2))
        (directory / "reference-answer.json").write_text(json.dumps({"draft": draft, "claims": [{"text": text, "source_ids": refs, "status": status} for text, refs, status in claims], "needs_confirmation": pending}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
