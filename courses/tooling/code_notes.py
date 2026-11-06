"""为不能直接加注释的数据正文提供逐行说明，并解释终端命令。"""
import ast
import io
import re
import shlex
import tokenize
from html import escape
from pathlib import Path

FIELD_PURPOSES = {
    'task': '说明本次要完成的任务', 'evidence': '提供可用于核对断言的证据',
    'id': '标识当前条目，供引用或关联结果使用', 'text': '保存本条原始文字或断言文字',
    'draft': '保存待人工核对的草稿，不表示已执行外部动作', 'claims': '逐条列出需要核对的断言',
    'source_ids': '记录支持断言的来源 ID', 'source_id': '记录该条内容对应的来源 ID',
    'status': '区分通过、失败、待复核或支持性状态', 'needs_confirmation': '保留缺失信息与待确认事项',
    'supported': '表示给定资料支持的内容', 'unsupported': '表示给定资料不支持的内容',
    'uncertain': '表示证据不足，不能确定', 'role': '声明消息属于系统、用户、助手或工具',
    'content': '保存消息正文，供接收方读取', 'tool_call_id': '把工具结果对应到原始请求',
    'tool_calls': '列出模型提出的工具请求', 'function': '描述请求的函数和参数',
    'arguments': '提供函数参数，执行前仍需校验', 'name': '给条目、工具或配置设置名称',
    'type': '声明此处的数据或消息类型', 'description': '说明字段或工具的用途',
    'properties': '定义对象允许包含的字段', 'required': '列出必须提供的字段',
    'additionalProperties': '决定是否接受未声明的字段', 'items': '约束数组中每项的数据结构',
    'enum': '限定可接受的取值', 'model': '记录选用的模型；null 表示未知或未记录',
    'provider': '记录服务提供方；null 不能解释为已实际调用', 'input_tokens': '记录输入用量，未知时保留 null',
    'output_tokens': '记录输出用量，未知时保留 null', 'cost': '记录费用；未取得真实依据时不能填造',
    'cost_usd': '以美元记录费用；null 表示未知', 'skill_version': '记录任务所用 Skill 的版本',
    'reason': '说明当前判断或限制的依据', 'limitation': '说明程序能验证的范围和未能证明的部分',
    'question': '提供待回答的问题', 'query': '提供检索或模型输入', 'expected': '给出验收时应核对的结果',
    'answer': '保存答案内容，仍需按本题规则判断', 'reference': '提供参考答案或基线',
    'sources': '列出来源及其定位', 'cases': '列出独立验收题', 'split': '区分开发题与保留题',
    'version': '标识资料或题集版本，保证比较条件一致', 'category': '标识题目类别，便于分别统计',
    'grader': '选择当前题目的评分规则', 'must_include': '列出必须包含的内容',
    'must_not_include': '列出不能出现的内容', 'forbidden': '列出需要拒绝的内容或行为',
    'steps': '记录步骤或轮数，便于复核实际流程', 'trace': '保存运行过程，不能由最终答案代替',
    'command': '指定启动命令', 'args': '列出启动参数', 'env': '配置当前进程的环境变量',
    'mcpServers': '声明宿主可以连接的 MCP 服务', 'hooks': '声明事件发生时运行的处理器',
    'matcher': '筛选哪些事件匹配当前处理规则', 'timeout': '设置等待时间上限',
    'url': '记录来源或服务地址', 'retrieved_at': '记录实际取得资料的时间',
    'Decision': '记录明确作出的决定', 'ActionItem': '记录待执行的动作', 'Owner': '记录明确的负责人',
    'DueDate': '记录截止日期；资料不足时保留待确认', 'SourceSentence': '保留支持此项的原句',
    'NeedsConfirmation': '列出不能自行补造的信息', 'Draft': '保存草稿',
    'FactsCopied': '列出从原资料复制的事实', 'PASS': '表示本项限定范围的检查通过',
}

TEXT_LINE_PURPOSES = {
    'from pathlib import Path': '导入路径工具，供生成后的检查脚本读取 README。',
    'for name in ("README.md", "docs/README.md")': '依次检查根目录和 docs 目录的两份 README。',
    'text = Path(name).read_text()': '读取当前 README 的文字，供后面的两项断言检查。',
    'assert "python3 run.py" in text': '检查是否写明正确运行命令；缺失时报告对应文件。',
    'assert "学习记录检查完成" in text': '检查是否写明运行后的预期输出；缺失时报告对应文件。',
    'print("PASS：两份 README': '仅在两份文件都通过断言后打印 PASS。',
    '# 台北旅行教学样本': '固定切分样本的一级标题；这是教学输入，不是实时旅行建议。',
    '## 饮食': '给饮食段设置二级标题，用于比较按结构切分的效果。',
    '台北以': '提供夜市与早餐的样本文段，让检索问题能命中饮食主题。',
    '台北有不少精品咖啡店': '提供同一主题的第二段，观察段落和切片边界如何影响检索。',
    '## 交通': '给交通段设置二级标题，和饮食主题分开。',
    '台北捷运': '提供交通方式和样本价格，作为检索与切分实验的固定文本。',
    'YouBike 是': '补充单车文段，检验是否能保留与问题相关的句子。',
    '## 天气': '给天气段设置二级标题。',
    '台北夏季': '提供季节、温度与天气的样本文段，供检索问题定位。',
    '# 公司入职教学样本': '固定知识库文档的一级标题；以下是虚构入职政策样本。',
    '## 休假政策': '标记休假政策章节，帮助按主题切分。',
    '全职员工': '提供休假天数、结转和申请条件，作为有条件答案的核对依据。',
    '## 远程办公': '标记远程办公政策章节。',
    '混合办公': '提供混合办公与全远程审批条件，供回答保留条件限制。',
    '## 费用报销': '标记费用报销政策章节。',
    '收据须在': '提供提交期限、预先批准和预订渠道，作为检索回答的证据。',
    '## 技术栈': '标记技术栈与代码审查要求章节。',
    '后端使用 Python': '提供技术版本和合并前审查要求，作为固定问答材料。',
    '你是具备长期记忆的助手': '要求模型使用下面检索到的相关记忆组织回答。',
    '相关记忆：': '标记相关记忆的开始位置，区分说明与记忆内容。',
    '{memory_text}': '把本次检索到的记忆文本填入提示，不等于允许记忆覆盖系统规则。',
    '只依据下面的资料用中文回答': '要求只依据给定上下文回答；找不到答案时明确表示没有信息。',
    '参考资料：': '标记检索上下文的开始位置。',
    '{context_text}': '把检索到的片段填入提示，作为本轮回答的证据。',
    '问题：{query}': '把当前问题填入提示，明确要从证据中回答什么。',
    '回答：': '标记模型应开始给出答案的位置，并结束多行提示文本。',
    'import sys': '让子进程读取测试传入的存储路径和操作模式。',
    'from starter import MemoryStore': '在子进程导入待测记忆存储实现。',
    'class TinyEmbeddingFunction:': '定义固定的微型向量函数，测试持久化时不下载或请求模型。',
    'def __call__(self, input):': '让替身对象能像函数一样接收文本列表。',
    "return [[float('python' in text.lower())": '按是否含 python 构造固定四维向量，提供可重复的测试输入。',
    '@staticmethod': '将下面方法声明为静态方法，调用时不接收 self。',
    'def name():': '提供向量函数的稳定名称，满足存储接口约定。',
    "return 'stage06-tiny-test'": '返回测试向量函数的固定标识。',
    'def get_config(self):': '提供持久化所需的向量函数配置接口。',
    'return {}': '该测试替身无额外配置，因此返回空对象。',
    'def build_from_config(config):': '声明根据配置重建测试向量函数的方法。',
    'return TinyEmbeddingFunction()': '重新创建同一种固定向量函数。',
    'memory = MemoryStore(path=sys.argv[1]': '使用命令行传入的目录创建记忆库，并注入固定向量函数。',
    "if sys.argv[2] == 'write':": '根据第二个参数选择写入阶段，模拟第一个进程。',
    "memory.remember('用户喜欢 Python。')": '把固定偏好写入持久化存储，供另一个进程读取。',
    'else:': '在另一次进程运行中进入读取与验证阶段。',
    "assert '用户喜欢 Python。' in memory.all()": '确认新进程仍能读到先前写入的偏好，证明数据跨进程保存。',
    '使用基线仓库': '指定使用可信基线中的审查方法，避免执行 PR 自带的规则。',
    '读取 ${{ runner.temp }}': '指定差异文件和审查范围，只报告本次改动引入的问题。',
    'diff 中的说明': '把差异里的文字和指令当作不可信数据，禁止据此执行命令。',
    '结合基线文件': '允许核对上下文，同时禁止修改和外部发布动作。',
    '输出中文：': '规定报告语言、发现问题时的证据字段，以及未发现问题时的写法。',
    '不能运行验证时': '要求如实标注未验证内容，防止把推测写成测试成功。',
}


def text_line_purpose(line, fallback):
    stripped=line.strip()
    if not stripped:
        return '保留空行，分隔提示或样本文档中的段落。'
    for fragment, purpose in TEXT_LINE_PURPOSES.items():
        if fragment in stripped:
            return purpose
    if stripped in {'"""', "'''"}:
        return '多行字符串的边界标记；不属于传给模型或子进程的正文。'
    return fallback


def shell_note(line):
    """解释现有命令，不执行、不改参数。"""
    text = line.strip()
    try:
        parts = shlex.split(text)
    except ValueError:
        return '这是上一行命令的续行；与前后行一起构成完整参数。'
    if not parts:
        return ''
    command = Path(parts[0]).name
    if command == 'cd':
        return '切换到 '+ ' '.join(parts[1:])+'，让后面的相对路径从这里开始计算；已在该目录时可跳过。'
    if command == 'source':
        return '在当前终端激活指定虚拟环境，让后面的 python 使用该环境中的解释器与依赖。'
    if ' -m venv ' in ' '+text+' ':
        return '用指定 Python 创建独立虚拟环境，避免本例依赖与其他课程互相影响。'
    if '-m pip' in text or command in {'pip','pip3','uv'}:
        if ' install ' in ' '+text+' ':
            return '将列出的依赖安装到所用 Python 环境；-r 表示从指定清单读取包名与版本。' if '-r' in parts else '在所用环境中安装本例列出的依赖及版本；这不会下载课程正文。'
        return '查看所用环境的包信息，核对实际版本与依赖是否满足本例。'
    if '-m unittest' in text or command == 'pytest':
        return '运行指定测试；discover 会查找匹配的测试文件，-v 会逐项显示结果。'
    if command.startswith('python'):
        if '-c' in parts:
            return '执行引号内的固定 Python 代码，按本行内容检查环境或演示指定操作。'
        script = next((p for p in parts[1:] if p.endswith('.py')), None)
        if script:
            mode = '；--live 会进入真实服务路径，需先满足本章环境要求' if '--live' in parts else ''
            purpose = {
                '01_hello_tool.py':'观察一次完整的天气工具调用往返', '02_multi_tool.py':'观察模型在多个工具中选择',
                '03_agent_loop.py':'运行有界工具循环', '04_multi_step.py':'检验有依赖的多步骤工具任务',
                '05_error_recovery.py':'观察坏参数、失败结果与恢复行为', '06_schema_eval.py':'比较工具说明在固定题集上的表现',
                '07_structured_output.py':'验证结构化结果与业务约束', '08_anthropic_agent.py':'观察 Anthropic 消息与工具结果往返',
                '09_streaming_tools.py':'观察流式片段组装与完整性检查', '10_tool_choice.py':'检验本行选择的工具调用模式',
                '11_parallel_tools.py':'验证并发执行及请求结果关联', '12_self_refine.py':'比较反馈前后的草稿',
                '13_reflexion.py':'检验经验如何影响下一次尝试', '14_instructor.py':'运行带类型验证和有限重试的抽取',
                '15_outlines.py':'运行结构约束生成示例', '16_codeact.py':'验证受限代码行动及语法边界',
                '17_react_retrieval.py':'通过两次检索取得回答所需证据',
            }.get(Path(script).name, '运行 '+script+'，按本行参数完成当前案例并核对输出')
            return purpose+mode+'。'
        return '用本行指定的 Python 运行模块或查看解释器信息。'
    if command == 'ollama':
        return {'list':'列出本机已安装的模型，不会下载新模型。','serve':'启动本地模型服务，供示例通过接口请求。','pull':'下载本行指定的模型；已有且未更新时无需重复下载。'}.get(parts[1] if len(parts)>1 else '', '按本行参数操作本地模型服务。')
    if command == 'read':
        return '从终端读取输入；-s 隐藏密钥输入，值只保存在当前 shell 变量中。' if '-s' in parts else '从终端读取本次配置值，保存到本行指定的变量。'
    if command == 'export':
        return '将本行变量传给随后启动的子进程；不会把它自动写入课程文件。'
    if command == 'patch':
        return '预演补丁是否能应用，不修改文件；-p1 去掉补丁路径的首级目录。' if '--dry-run' in parts else '将已检查的答案补丁应用到当前目录的对应文件。'
    if command == 'docker':
        return '按指定 Dockerfile 构建本地示例镜像。' if 'build' in parts else '按本行挂载、网络、用户和资源参数运行隔离案例；这些限制由命令实际落实。'
    if command == 'git':
        action = parts[1] if len(parts)>1 else ''
        return {'diff':'查看或保存实际改动，核对是否仅涉及授权范围。','init':'在本例独立演示目录初始化版本记录。','add':'把明确列出的演示文件加入暂存区。','commit':'为演示创建可比较的版本基线。','status':'查看演示目录中已改动和未跟踪的文件。','show':'读取指定提交或文件的实际内容。','restore':'按本行范围恢复演示文件；执行前先核对自己的未保存修改。','worktree':'按本行参数管理独立工作目录。'}.get(action,'执行本行指定的 Git 操作，范围以当前演示目录和参数为准。')
    if command in {'claude','codex'}:
        return '以本行指定的目录、规则或插件参数启动 CLI 会话；实际权限仍由宿主配置决定。'
    if command in {'mkdir','cp','cat','ls','pwd','chmod','curl','npm','npx','dvc','node','open'}:
        return {'mkdir':'创建本例需要的目录。','cp':'将指定文件复制到本例目录，供后续操作。','cat':'显示指定文本文件，核对其内容。','ls':'列出指定目录的文件或工具安装位置。','pwd':'显示当前目录，确认相对路径的起点。','chmod':'设置本例文件所需的执行权限。','curl':'按指定 URL 和参数发起请求，核对接口实际返回。','npm':'执行本行明确指定的包管理操作。','npx':'运行指定的 Node 工具；首次使用可能需要下载包。','dvc':'按本行参数管理数据版本或重跑实验阶段。','node':'运行指定的 JavaScript 离线演示，观察实际输出。','open':'打开本例指定的文件或页面。'}[command]
    if re.match(r'^[A-Za-z_][\w]*=',text):
        return '为本次命令设置明确的环境变量；后面的程序使用这些值运行。'
    return '执行本行指定的工具与参数，完成当前小节对应操作。'


def annotate_shell(text):
    lines=text.splitlines(keepends=True)
    out=[]
    for i,line in enumerate(lines):
        stripped=line.strip()
        if stripped and not stripped.startswith('#'):
            previous=lines[i-1].strip() if i else ''
            if not (previous.startswith('#') and re.search('[\u4e00-\u9fff]',previous)):
                out.append('# '+shell_note(line)+'\n')
        out.append(line)
    return ''.join(out)


def is_shell(text):
    first=next((line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith('#')), '')
    return bool(re.match(r'(?:cd |source |python\S* |[^ ]*/python[\d.]* |ollama |patch |read |export )',first))


def data_line_notes(text, kind):
    """行号对应实际文件；只在注释会改变数据时使用附表。"""
    lines=text.splitlines()
    selected={}
    if kind == 'python':
        tree=ast.parse(text)
        doclines=set()
        for n in ast.walk(tree):
            if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):
                doclines.update(range(n.lineno,n.end_lineno+1))
        tokens=list(tokenize.generate_tokens(io.StringIO(text).readline))
        spans=[];stack=[]
        for token in tokens:
            if token.type==tokenize.STRING and token.end[0]>token.start[0]:
                spans.append((token.start[0],token.end[0]))
            name=tokenize.tok_name.get(token.type,'')
            if name in {'FSTRING_START','TSTRING_START'}:stack.append(token.start[0])
            if name in {'FSTRING_END','TSTRING_END'} and stack:
                start=stack.pop()
                if token.end[0]>start:spans.append((start,token.end[0]))
        for start,end in spans:
            if start in doclines:continue
            owners=[n for n in ast.walk(tree) if isinstance(n,(ast.Assign,ast.AnnAssign,ast.Call)) and n.lineno<=start and n.end_lineno>=end]
            owners.sort(key=lambda n:n.end_lineno-n.lineno)
            context='当前语句中的文本数据'
            if owners:
                owner=owners[0]
                if isinstance(owner,ast.Assign):context='赋给 '+', '.join(ast.unparse(t) for t in owner.targets)+' 的文本'
                elif isinstance(owner,ast.AnnAssign):context='赋给 '+ast.unparse(owner.target)+' 的文本'
                else:context='传给 '+ast.unparse(owner.func)+' 的文本参数'
            for number in range(start,end+1):
                selected[number]=text_line_purpose(lines[number-1], context+'；'+('开始多行字符串。' if number==start else '结束多行字符串，保留正文和插值。' if number==end else '这一行是字符串正文，内容和换行原样保留，不是 Python 指令。'))
        for index, line in enumerate(lines):
            if index and lines[index-1].rstrip().endswith('\\'):
                selected[index+1] = ('继续同一条 with 语句，替换日志函数并保存替身，供后续断言核对。'
                                     if 'patch(' in line else '提供上一行断言失败时的错误消息，保留实际结果供排错。')
    elif kind in {'yaml','yml'}:
        inblock=False;indent=0;key=''
        for number,line in enumerate(lines,1):
            spaces=len(line)-len(line.lstrip())
            if inblock and line.strip() and spaces<=indent:inblock=False
            if inblock and line.strip() and not line.lstrip().startswith('#'):
                selected[number]=text_line_purpose(line, '给审查助手的任务要求；作为 prompt 正文传入，不在这里执行。' if key=='prompt' else '多行文本内容；保持原值，不能当作 YAML 字段或注释。')
            if re.search(r':\s*[|>]\s*$',line):
                inblock=True;indent=spaces;key=line.strip().split(':')[0]
    elif kind=='json':
        for number,line in enumerate(lines,1):
            stripped=line.strip()
            if not stripped:continue
            match=re.match(r'"([^"\\]+)"\s*:',stripped)
            if match:
                key=match[1]
                purpose=FIELD_PURPOSES.get(key,'保存当前对象的 '+key+' 字段，按本例题目或配置读取')
                selected[number]=purpose+'。'
            elif stripped in {'{','['}:selected[number]='开始一个'+('对象，内部以字段名组织数据。' if stripped=='{' else '数组，内部按顺序保存各项。')
            elif re.fullmatch(r'[\]\}, ]+',stripped):selected[number]='结束当前对象或数组；逗号表示同一层还有下一项。' if stripped.endswith(',') else '结束当前对象或数组。'
            else:selected[number]='提供当前数组中的一项；顺序和值按本行保存，供题目、参考答案或配置读取。'
    return [(number,lines[number-1],note) for number,note in sorted(selected.items())]


def notes_html(text, kind):
    rows=data_line_notes(text,kind)
    if not rows:return ''
    return '<details class="line-notes"><summary>逐行说明：保留原值的数据与多行字符串</summary><p>行号对应上面的完整代码及实际文件。这里是提示词或结构化数据，在正文内加注释会改变程序输入，因此单独解释。</p><table><thead><tr><th>行</th><th>原内容</th><th>目的</th></tr></thead><tbody>'+''.join(f'<tr><td>{n}</td><td><code>{escape(line)}</code></td><td>{escape(note)}</td></tr>' for n,line,note in rows)+'</tbody></table></details>'


def file_kind(path):
    return {'.py':'python','.json':'json','.yaml':'yaml','.yml':'yaml'}.get(path.suffix,'')


def file_notes(path):
    return notes_html(path.read_text(),file_kind(path))


def write_notes_file(home):
    """为直接阅读源码的学习者保存同一份逐行数据说明。"""
    parts=['# 多行字符串与数据文件的逐行说明\n\nPython、JavaScript、命令与配置语句的注释直接写在相应文件中。以下内容不能在原值内部插入注释，行号对应 examples 中的实际文件。JSON 保持合法格式；提示词正文和换行保持原样。\n']
    for path in sorted((home/'examples').rglob('*')):
        if not path.is_file() or not file_kind(path):continue
        rows=data_line_notes(path.read_text(),file_kind(path))
        if not rows:continue
        relative=path.relative_to(home)
        parts.append('\n## '+str(relative)+'\n\n[打开对应文件](../'+str(relative)+')\n\n| 行 | 原内容 | 目的 |\n|---|---|---|\n')
        for number,line,note in rows:
            parts.append('| '+str(number)+' | '+escape(line).replace('|','&#124;')+' | '+escape(note).replace('|','&#124;')+' |\n')
    (home/'reference/line-notes.md').write_text(''.join(parts))
