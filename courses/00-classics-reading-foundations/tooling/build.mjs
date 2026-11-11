// 教材、答案与拓展正文由源文件生成；相对链接让课程可以换电脑离线阅读。
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {createRequire} from "node:module";
const require = createRequire(import.meta.url);
const {marked} = await import(require.resolve("marked"));
const course = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const root = path.resolve(course, "../..");
const read = name => fs.readFileSync(path.join(course, name), "utf8");
const units = JSON.parse(read("units.json"));
const topics = JSON.parse(read("knowledge/topics.json"));
const escape = s => s.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;");
const rel = (from,to) => path.relative(path.dirname(from),to).split(path.sep).join("/");
const home = path.join(course,"index.html");
const library = path.join(course,"knowledge/index.html");
const lesson = id => path.join(root,"lessons",`${id}.html`);
const titles = ["导学 · 认识项目与资料","第 1 章 · 用 Python 读取讲稿","第 2 章 · 第一次运行 Docker","第 3 章 · 制作自己的镜像","第 4 章 · 接通一种真实模型"];
const times = ["55—75 分钟","75—110 分钟","65—95 分钟","70—100 分钟","本地 75—115 分钟 / 线上 70—105 分钟"];
const outcomes = ["明确项目边界，准备五份样本和首批问题。","把 Word 正文存成有来源的 JSON，并回查原文件。","在容器中运行同一程序，知道输入和输出在哪里。","封装程序与依赖，验证镜像结果与主机一致。","两条路线任选其一，保存真实响应并练习连接排错。"];
const chapterTopics = [["rag-map"],["python-environments","rag-context"],["docker-boundaries"],["docker-boundaries"],["model-interfaces","rag-map"]];
const extraChapters = JSON.parse(read("chapters-extra.json"));
for (const ch of extraChapters) { titles[ch.chapter]=ch.title; times[ch.chapter]=ch.time; outcomes[ch.chapter]=ch.outcome; chapterTopics[ch.chapter]=ch.topics; }
const stages = [
  {name:"阶段一 · 准备程序、容器与模型",start:0,end:4},
  {name:"阶段二 · 做出有据问答",start:5,end:8},
  {name:"阶段三 · 改善检索质量",start:9,end:12},
  {name:"阶段四 · 做成伴读产品",start:13,end:16},
  {name:"阶段五 · 加入可控 Agent",start:17,end:20},
  {name:"阶段六 · 验证账号与可靠性",start:21,end:24},
  {name:"阶段七 · 部署、恢复与上线评审",start:25,end:29}
];
// 用单元的真实带写用时汇总；模型配置单元为二选一。
for (let ch=0; ch<=29; ch++) {
  const group=units.filter(u=>u.chapter===ch);
  let low=0,high=0;
  for(const u of group) {const values=u.minutes.split("—").map(Number); low+=values[0];high+=values[1];}
  if(ch===4) {const a=group.find(u=>u.file==="0020-local-model").minutes.split("—").map(Number); const b=group.find(u=>u.file==="0021-cloud-model").minutes.split("—").map(Number);low-=Math.max(a[0],b[0]);high-=Math.min(a[1],b[1]);}
  times[ch]=`${low}—${high} 分钟`;
}
const totalLow=Math.floor(times.reduce((n,t)=>n+Number(t.split("—")[0]),0)/60);
const totalHigh=Math.ceil(times.reduce((n,t)=>n+Number(t.split("—")[1].split(" ")[0]),0)/60);
const writtenFiles = new Set(Object.values(JSON.parse(read("writing/plan.json"))).flatMap(unit=>unit.edits.map(edit=>edit.file)));
const render = source => marked.parse(source.replace(/\{\{code:([^}]+)\}\}/g,(_,name)=>"\n```"+(name.endsWith(".py")?"python":"text")+"\n"+read(`examples/${name}`)+"\n```\n"));
function headings(html) {
  const toc=[];
  const body=html.replace(/<h2>(.*?)<\/h2>/g,(_,label)=>{
    const id=`section-${toc.length+1}`;
    toc.push(`<li><a href="#${id}">${label}</a></li>`);
    return `<h2 id="${id}">${label}</h2>`;
  });
  return {body,toc:`<nav class="page-toc" aria-label="本页目录"><p class="rail-label">本页目录</p><ol>${toc.join("")}</ol></nav>`};
}
function page(target,title,body,{kind="resources",rail="",unit=""}={}) {
  const link=to=>rel(target,to);
  const nav=[["home",home,"课程地图"],["knowledge",library,"知识拓展 · 选读"],["resources",path.join(course,"resources.html"),"资料与工具"]].map(([key,url,label])=>`<a href="${link(url)}"${kind===key?' aria-current="page"':""}>${label}</a>`).join("");
  const crumb=kind==="home"?"":`<nav class="breadcrumbs" aria-label="当前位置"><a href="${link(home)}">课程首页</a><span>/</span><span>${kind==="lesson"?"主线学习":kind==="knowledge"?"知识拓展 · 选读":"资料与工具"}</span><span>/</span><span>${escape(title)}</span></nav>`;
  const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)} · 名著伴读实战</title><link rel="stylesheet" href="${link(path.join(root,"assets/classics.css"))}"></head><body class="page-${kind}"${unit?` data-current-unit="${unit}"`:""}>
<a class="skip-link" href="#main-content">跳到正文</a><header class="site-header"><div class="header-inner"><a class="brand" href="${link(home)}"><span class="brand-mark" aria-hidden="true">读</span><span>名著伴读<span class="brand-caption">AI 开发实战课</span></span></a><nav class="global-nav" aria-label="课程主要入口">${nav}</nav></div></header>
<div class="site-shell">${crumb}<div class="${rail?"reading-layout":"wide-layout"}">${rail?`<aside class="reading-rail"><details class="rail-menu" open><summary>${kind === "knowledge" ? "本页目录与返回入口" : "本章导航与本页目录"}</summary>${rail}</details></aside>`:""}<main id="main-content" tabindex="-1">${body}</main></div>
<footer class="site-footer"><p>名著 AI 伴读助手 · 从基础练习到上线评审</p><p>主线按顺序练习，拓展按需阅读。用自己的操作和解释验收，阅读与打勾不代表已经掌握。</p><p><a href="${link(path.join(course,"sources.html"))}">资料来源</a><a href="${link(path.join(course,"verification.html"))}">验证范围</a><a href="${link(home)}">返回课程地图</a></p><p>卡住时，记录单元、预期结果和实际报错；分享命令前去掉密钥。课程以新准备的学习环境为起点。</p></footer></div><script src="${link(path.join(root,"assets/classics.js"))}"></script></body></html>`;
  fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,html);
}
for(const [i,u] of units.entries()) {
  const target=lesson(u.file),peers=units.filter(x=>x.chapter===u.chapter);
  const {body,toc}=headings(render(read(`text/${u.file}.md`)));
  const rail=`<a class="back-link" href="${rel(target,home)}#chapter-${u.chapter}">← 返回课程地图</a><p class="rail-label">${titles[u.chapter]}</p><nav aria-label="本章单元"><ol class="unit-list">${peers.map((p,j)=>`<li><a href="${p.file}.html"${p.file===u.file?' aria-current="page"':""}><span class="unit-number">${j+1}</span><span>${escape(p.title)}<small>${p.minutes} 分钟</small></span></a></li>`).join("")}</ol></nav>${toc}`;
  const optional=chapterTopics[u.chapter].map(slug=>{const t=topics.find(x=>x.slug===slug);return `<a href="${rel(target,path.join(course,`knowledge/${slug}.html`))}" data-knowledge-link>${t.title}<span>${t.minutes} 分钟 · ${t.description}</span></a>`;}).join("");
  // 本地路线跳过线上配置，直接汇入共用程序；避免把二选一教成两项必修。
  const prev=units[i-1],next=u.file==="0020-local-model"?units.find(x=>x.file==="0022-first-model-call"):units[i+1];
  const content=`<p class="eyebrow">主线学习 / ${u.chapter===0?"导学":`第 ${u.chapter} 章`} / 单元 ${peers.indexOf(u)+1} · 共 ${peers.length} 个</p>`+body.replace(/<\/h1>/,`</h1><div class="lesson-meta"><span>本单元 ${u.minutes} 分钟</span><span>本章 ${times[u.chapter]}</span><span>安装与下载等待另计</span><span>选读不计入用时</span></div>`);
  const end=`${u.chapter>=5?'<p class="reading-note">运行位置：你从导学开始创建的 <code>classics-reader/</code> 项目根目录。主机统一使用全局 Python 3.12；新终端核对版本，并重新设置所选模型路线的环境变量。</p>':""}<label class="study-check"><input type="checkbox" data-study-check="${u.file}"><span><strong>我已完成操作，并能解释结果</strong><small>手动标记保存在当前浏览器；换电脑后不自动同步。</small></span></label><section class="optional-box" id="optional-reading" aria-label="本单元选读"><span class="tag">选读</span><strong>想多了解一点</strong><p>现在跳过也能继续主线，不需要额外安装软件。</p><div class="optional-links">${optional}</div></section><nav class="next-prev" aria-label="相邻学习单元">${prev?`<a href="${prev.file}.html"><small>上一单元</small>${escape(prev.title)}</a>`:`<a href="${rel(target,home)}">返回课程地图</a>`}${next?`<a href="${next.file}.html"><small>${u.file==="0020-local-model"?"下一步 · 跳过线上配置":"下一单元"}</small>${escape(next.title)} →</a>`:`<a href="${rel(target,home)}"><small>全部主线完成后</small>回到课程地图 →</a>`}</nav>`;
  page(target,u.title,content+end,{kind:"lesson",rail,unit:u.file});
}
let overview=`<section class="home-hero"><div><p class="eyebrow">课程首页 / 学习地图</p><h1>做一个有据可查的<br>名著 AI 伴读助手</h1><p class="lede">新建一个空项目，只下载五份公开讲稿。跟着每节亲手写一小段代码，逐步做出有据问答、启发式伴读和可控 Agent，再准备公司上线需要的证据。这里是学习地图；第一次来，从导学开始。</p><div class="hero-actions"><a class="button primary" id="continue-learning" href="${rel(home,lesson(units[0].file))}">从导学开始 <span aria-hidden="true">→</span></a><a class="text-link" href="#learning-path">先看学习顺序 ↓</a></div><p id="resume-note" class="meta">第一次学习，建议从第一个单元开始。</p></div><aside class="milestone"><p class="rail-label">同一个项目，逐步长大</p><ol><li><span>01</span>从资料到有据问答</li><li><span>02</span>从伴读到可控 Agent</li><li><span>03</span>从可运行到可评审交付</li></ol><p>每一步说明写在哪里、为什么写、怎样运行，以及预期看到什么。代码由你逐步写成。</p></aside></section><div class="course-facts"><p><strong>导学 + 29 章</strong><span>每次一个短单元</span></p><p><strong>${units.length} 个连续练习单元</strong><span>任选一条生成模型路线，主线约 ${totalLow}—${totalHigh} 小时，等待与公司审核另计</span></p><p><strong>两条模型路线，任选其一</strong><span>汇合后使用同一个调用程序</span></p></div><section id="learning-path"><div class="section-heading"><div><p class="eyebrow">必修主线</p><h2>按这个顺序，一步步做出来</h2></div><p id="course-progress" class="meta">${units.length} 个单元，含本地与线上两个路线单元。</p></div><p class="section-intro">每章都有可检查的产出。先动手，再回答验收题，最后展开参考答案核对。</p>`;
overview+=`<nav class="stage-jumps" aria-label="按阶段定位">${stages.map((st,i)=>`<a href="#stage-${i+1}">${i+1}. ${st.name.split(" · ")[1]}</a>`).join("")}</nav>`;
for(const [si,stage] of stages.entries()) {
  overview+=`<details class="stage-group" id="stage-${si+1}"${si===0?" open":""}><summary><span>${stage.name}</span><small>${stage.start===0?"导学 + 第 1—4 章":`第 ${stage.start}—${stage.end} 章`} · 展开章节</small></summary>`;
for(let ch=stage.start;ch<=stage.end;ch++) {
  overview+=`<section class="chapter-row" id="chapter-${ch}"><div class="chapter-intro"><span class="chapter-number">${String(ch).padStart(2,"0")}</span><h3>${titles[ch]}</h3><p>${outcomes[ch]}</p><p class="meta">预计 ${times[ch]}</p>${ch===4?'<p class="route-note">本地与线上选一条，再进入“用同一个程序获得回答”。</p>':""}</div><ol class="chapter-lessons">`;
  for(const [j,u] of units.filter(x=>x.chapter===ch).entries()) {
    const badge=u.file.includes("local-model")?"本地路线":u.file.includes("cloud-model")?"线上路线":"";
    overview+=`<li><a href="${rel(home,lesson(u.file))}" data-unit-link="${u.file}"><span class="lesson-order">${j+1}</span><span class="lesson-name">${escape(u.title)}${badge?`<span class="route-tag">${badge} · 二选一</span>`:""}<small>${u.minutes} 分钟 <span data-unit-status>· 未标记</span></small></span><span class="link-arrow" aria-hidden="true">↗</span></a></li>`;
  }
  overview+="</ol></section>";
}
overview+="</details>";
}
overview+=`</section><section class="home-library"><div><p class="eyebrow">可选拓展</p><h2>做项目，也把知识连起来</h2><p>遇到好奇的概念，再进去读。每篇独立成页，有解释、取舍和原文链接，不增加主线验收任务。</p><a class="text-link" href="knowledge/index.html">浏览全部知识拓展 →</a></div><div class="featured-reading"><a href="knowledge/rag-map.html"><span class="tag">技术对比 · 12—15 分钟</span><strong>RAG 有哪些常见做法？</strong><span>基础 RAG、混合检索、重排序、GraphRAG、Agentic RAG……从问题出发看差别。</span></a></div></section><section><p class="eyebrow">随用随查</p><h2>需要资料时，来这里找</h2><div class="resource-grid"><a href="${rel(home,path.join(root,"reference/classics-foundations.html"))}"><strong>术语与命令速查 →</strong><span>忘了一个词或一条命令，用它快速回忆。</span></a><a href="code.html"><strong>课后参考代码 →</strong><span>完成本节后用于查错；主线在页面中逐段带写。</span></a><a href="resources.html"><strong>输入资料与使用说明 →</strong><span>只需五份讲稿；从空项目开始，不需要代码包。</span></a></div></section>`;
page(home,"课程首页 · 学习地图",overview,{kind:"home"});
let knowledge=`<p class="eyebrow">知识拓展 / 全部选读</p><h1>带着好奇来，读懂一点就回去练</h1><p class="lede">主线负责把项目做出来，这里解释背后的选择。可以随时跳过，不会影响章节进度；预计阅读时间不含外部文章。</p><div class="reading-note">选读解释主线里的技术取舍；无需先读完所有方法，再开始练习。资料查阅日期：2026-11-10；方法对比不是热度排名。</div>`;
for(const group of [...new Set(topics.map(t=>t.group))]) knowledge+=`<section><h2>${group}</h2><div class="knowledge-grid">${topics.filter(t=>t.group===group).map(t=>`<a href="${t.slug}.html"><span class="meta">选读 · ${t.minutes} 分钟</span><h3>${t.title}</h3><p>${t.description}</p><span class="text-link">打开说明 →</span></a>`).join("")}</div></section>`;
page(library,"知识拓展",knowledge,{kind:"knowledge"});
for(const t of topics) {
  const target=path.join(course,`knowledge/${t.slug}.html`),{body,toc}=headings(render(read(`knowledge/${t.slug}.md`)));
  const back=`<a href="${rel(target,lesson(t.unit))}" data-return-to-lesson>← 返回相关主线单元</a>`;
  const rail=`<a class="back-link" href="index.html">← 全部知识拓展</a>${toc}<div class="rail-return">${back}<p class="meta">从单元打开时，可返回刚才的阅读位置。</p></div>`;
  const content=`<p class="eyebrow">选读知识 / ${t.group}</p>`+body.replace(/<\/h1>/,`</h1><div class="lesson-meta"><span>预计 ${t.minutes} 分钟</span><span>不计入主线验收</span><span>无需额外安装</span></div>`);
  page(target,t.title,content+`<div class="knowledge-return">${back}<a href="rag-map.html">查看 RAG 技术地图 →</a></div><p class="meta">外部资料核对日期：2026-11-10。伴读例子为本课程设计的说明，不代表已在知识库上实测效果。</p>`,{kind:"knowledge",rail});
}
page(path.join(course,"resources.html"),"资料与工具",`<p class="eyebrow">资料与工具 / 随用随查</p><h1>练习材料与使用说明</h1><p class="lede">这些是学习时的辅助资料。第一次来，请先回到课程地图，从导学开始。</p><div class="resource-grid"><a href="${rel(home,path.join(root,"reference/classics-foundations.html"))}"><strong>术语与命令速查 →</strong><span>常见概念与命令的用途、预期结果。</span></a><a href="code.html"><strong>课后参考代码 →</strong><span>这是最后一个单元完成后的状态，用于课后对照。</span></a><a href="${rel(home,lesson("0009-samples"))}"><strong>逐份下载五个输入文件 →</strong><span>仅阅读材料；Python 程序和配置跟着主线亲手创建。</span></a><a href="public-materials/index.html"><strong>阅读五份公开样本 →</strong><span>新编正文、来源边界与原题参考答案。</span></a><a href="sources.html"><strong>资料来源 →</strong><span>区分指定仓库主线与新增选读材料。</span></a><a href="verification.html"><strong>验证范围 →</strong><span>哪些已检查，哪些需在学习设备运行。</span></a></div><h2>在实际学习电脑上，从空目录开始</h2><p>新建 <code>classics-reader/</code>，只把导学链接中的五份 DOCX 放进 <code>data/input/</code>。第一章开始亲手创建依赖清单、读取脚本；以后每节都在这个项目内增加或修改具体代码。</p><p>课程网站用浏览器阅读，练习项目放在你选择的学习电脑。没有需要解压的程序包，也不要求下载仓库。五份讲稿为课程新编材料，原著短引句与讲解观点分别标注。安装依赖、下载模型和线上调用需要网络。</p><h2>运行命令之前</h2><p>命令块里的 <code>#</code> 行说明用途与预期结果。“复制命令”只取可执行行；逐组操作，遇到输入提示先填完再继续，不要一次执行整页命令。程序代码的“复制代码”会保留解释性注释。</p><p>本版以 macOS 终端命令为主，不依赖课程编写电脑的环境。M1 16 GB 是本地路线参考设备，不保证速度或并发；原生 PowerShell 尚未提供。</p>`);
let code='<p class="eyebrow">资料与工具 / 示例文件</p><h1>课后参考代码</h1><p>下面是走完全课之后的文件，仅供查错与复盘。它们含有后续章节的功能，不应复制来替代当前单元。开始练习请回课程地图，每页会明确写出本次增量。</p><div class="code-file-list">';
const exampleFiles = fs.readdirSync(path.join(course,"examples"), {recursive:true,withFileTypes:true}).filter(f=>f.isFile()).map(f=>path.relative(path.join(course,"examples"),path.join(f.parentPath||f.path,f.name))).filter(name=>!name.split(path.sep).some(p=>["data","__pycache__",".venv"].includes(p)) && writtenFiles.has(name) && !path.basename(name).startsWith(".env")).sort();
for(const name of exampleFiles) {
  const slug=name.replace(/[^a-zA-Z0-9-]/g,"-");
  const target=path.join(course,"code",slug+".html");
  const language=name.endsWith(".py")?"python":name.endsWith(".js")?"javascript":"text";
  code+=`<a id="${slug}" href="code/${slug}.html"><strong>${escape(name)}</strong><span>查看完整文件与下载 →</span></a>`;
  page(target,name,`<div class="article-only"><p class="eyebrow">资料与工具 / 完整源码</p><h1>${escape(name)}</h1><p><a href="../code.html">← 返回文件索引</a> · <a href="../examples/${name}" download>下载此文件</a></p><pre><code class="language-${language}">${escape(read(`examples/${name}`))}</code></pre></div>`);
}
page(path.join(course,"code.html"),"课后参考代码",code+"</div>");
for(const [source,target,title] of [["RESOURCES.md","sources.html","资料来源"],["VERIFICATION.md","verification.html","验证范围"],["REVIEW.md","review.html","课程审查记录"]]) page(path.join(course,target),title,`<div class="article-only">${render(read(source))}</div>`);
page(path.join(root,"reference/classics-foundations.html"),"术语与命令速查",`<div class="article-only">${render(read("reference.md"))}</div>`);
console.log(`已生成 ${units.length} 个主线单元、${topics.length} 篇选读与课程入口。`);

// 阅读材料沿用教材的页面框架；Markdown 保留给 GitHub，HTML 方便离线阅读。
for (const [source, target, title] of [["README.md", "index.html", "公开阅读材料"], ["answers.md", "answers.html", "原题参考答案"], ...["06","07","08","09","10"].map(n => [`texts/${n}.md`, `texts/${n}.html`, `阅读材料 ${n}`])]) {
  const location = path.join(course, "public-materials", target);
  const text = read(`public-materials/${source}`).replaceAll("README.md)", "index.html)").replace(/(texts\/\d+|answers)\.md\)/g, "$1.html)");
  page(location, title, `<div class="article-only"><p class="eyebrow">资料与工具 / 课程自编讲解稿</p>${render(text)}<p><a href="${rel(location, path.join(course,"public-materials/index.html"))}">返回公开样本目录</a> · <a href="${rel(location, lesson("0009-samples"))}">回到导学：准备样本</a></p></div>`);
}
