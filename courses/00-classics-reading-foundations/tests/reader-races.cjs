// 使用真实页面函数和可控的响应顺序；合成私密文字仅用于边界测试，不代表模型结果。
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(path.join(__dirname, '../examples/companion/web/reader.js'), 'utf8');
function between(start,end) {
  const a=start.exec(source),b=end.exec(source);
  assert(a && b && b.index>a.index, '页面函数定位失败');
  return source.slice(a.index,b.index);
}
const element = () => ({children:[], textContent:'', replaceChildren(){this.children=[];}, append(...items){this.children.push(...items);}, setAttribute(){}});
const tick = () => new Promise(resolve => setImmediate(resolve));

async function lateNotes(){
  const nodes={drafts:element(),notes:element()}, requests=[];
  const context={viewVersion:0,document:{createElement:element},$:id=>nodes[id],status(){},api:url=>new Promise(resolve=>requests.push({version:context.viewVersion,url,resolve}))};
  vm.createContext(context);
  vm.runInContext(between(/async function refreshNotes\s*\(/,/function on\s*\(/),context);
  const first=context.refreshNotes();
  requests.find(r=>r.version===0&&r.url==='/api/drafts').resolve([]);await tick();
  context.viewVersion++;nodes.notes.replaceChildren();nodes.drafts.replaceChildren();
  const second=context.refreshNotes();
  requests.find(r=>r.version===1&&r.url==='/api/drafts').resolve([]);await tick();
  requests.find(r=>r.version===1&&r.url==='/api/notes').resolve([{body:'B_NOTE'}]);await second;
  requests.find(r=>r.version===0&&r.url==='/api/notes').resolve([{body:'A_PRIVATE_NOTE'}]);await first;
  assert.deepEqual(nodes.notes.children.map(n=>n.textContent),['B_NOTE']);
}

async function lateSession(){
  const nodes={selected:element(),progress:element(),strict:element(),result:element()}, requests=[];
  const context={viewVersion:0,selected:null,lastTrace:'',$:id=>nodes[id],status(){},api:url=>new Promise(resolve=>requests.push({url,resolve}))};
  vm.createContext(context);
  vm.runInContext(between(/async function choose\s*\(/,/function reset\s*\(/),context);
  const first=context.choose('A');const second=context.choose('B');
  requests[1].resolve({id:'B',book:'公开样本',progress:2,strict:0});await second;
  requests[0].resolve({id:'A',book:'A_PRIVATE_BOOK',progress:9,strict:0});await first;
  assert.equal(context.selected.id,'B');assert.equal(nodes.progress.value,2);
  assert(!nodes.selected.textContent.includes('A_PRIVATE_BOOK'));
}

async function draftAfterSessionChange(){
  const nodes={drafts:element(),notes:element()};let row={id:'draft',status:'pending',body:'旧正文',revision:1,digest:'a'.repeat(64)};
  const context={viewVersion:0,document:{createElement:element},$:id=>nodes[id],status(){},api:async(url,method,body)=>{
    if(method==='PATCH'){row={...row,body:body.body,revision:2};return row;}
    if(url==='/api/drafts')return [row];
    if(url==='/api/notes')return [];
    throw new Error('意外请求');
  }};
  vm.createContext(context);
  vm.runInContext(between(/async function refreshNotes\s*\(/,/function on\s*\(/),context);
  await context.refreshNotes();context.viewVersion++;
  const card=nodes.drafts.children[0];card.children[1].value='修改后的正文';
  await card.children[2].onclick();
  assert.equal(nodes.drafts.children[0].children[0].textContent,'待确认草稿 · 版本 2');
}

async function lateLogin(){
  const nodes={'login-form':element(),'family-panel':element()},requests=[];let entered=0;
  const context={viewVersion:0,token:'',$:id=>nodes[id],status(){},FormData:class extends Map{constructor(form){super(form.values);}},enter:async()=>{entered++;},api:()=>new Promise(resolve=>requests.push(resolve))};
  vm.createContext(context);
  vm.runInContext(between(/\$\('login-form'\)\.onsubmit\s*=/,/\$\('ask-form'\)\.onsubmit\s*=/),context);
  const event=name=>({preventDefault(){},target:{values:[['username',name]],password:{value:'synthetic'}}});
  const first=nodes['login-form'].onsubmit(event('A'));const second=nodes['login-form'].onsubmit(event('B'));
  requests[1]({access_token:'B_TOKEN',role:'reader'});await second;
  requests[0]({access_token:'A_TOKEN',role:'reader'});await first;
  assert.equal(context.token,'B_TOKEN');assert.equal(entered,1);
}

(async()=>{await lateNotes();await lateSession();await draftAfterSessionChange();await lateLogin();console.log('4 个页面回归通过：读者笔记、会话选择、草稿更新与登录顺序。');})().catch(error=>{console.error(error);process.exitCode=1;});
