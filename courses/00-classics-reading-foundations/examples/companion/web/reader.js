// 模型与讲稿输出只当文本显示；访问令牌保存在内存中，刷新后重新登录。
const $ = id => document.getElementById(id);
let token='', config={}, selected=null, activeRequest=null, lastTrace='', viewVersion=0;
const id = () => crypto.randomUUID().replaceAll('-','');
const status = message => { $('status').textContent=message; };
async function api(path, method='GET', body) {
  const headers={'Content-Type':'application/json'};
  if(token)headers.Authorization='Bearer '+token;
  if(config.mode==='lab')headers['X-Lab-Reader']=$('reader').value;
  const response=await fetch(path,{method,headers,body:body===undefined?undefined:JSON.stringify(body)});
  const result=await response.json();
  if(!response.ok)throw new Error(typeof result.detail==='string'?result.detail:'请求未完成，请检查输入或重新登录。');
  return result;
}
async function refresh(){
  const expectedView=viewVersion;const sessions=await api('/api/sessions');if(viewVersion!==expectedView)return;$('sessions').replaceChildren();
  for(const session of sessions){const button=document.createElement('button');button.textContent=session.book+' · '+session.id.slice(0,6);button.onclick=()=>choose(session.id).catch(e=>status(e.message));$('sessions').append(button);}
  if(config.chapter>=19)await refreshNotes();
}
async function choose(identity){
  const expectedView=++viewVersion;selected=null;$('result').hidden=true;
  const session=await api('/api/sessions/'+identity);if(viewVersion!==expectedView)return;selected=session;$('selected').textContent='当前阅读：'+selected.book+' · '+identity.slice(0,6);
  $('progress').value=selected.progress;$('strict').checked=Boolean(selected.strict);$('result').hidden=true;lastTrace='';
  status('已打开阅读记录，可以继续提问。');
}
function reset(){viewVersion++;selected=null;lastTrace='';activeRequest=null;$('ask').disabled=false;$('cancel').hidden=true;$('sessions').replaceChildren();$('selected').textContent='先选择或创建一次阅读。';$('result').hidden=true;$('drafts').replaceChildren();$('notes').replaceChildren();$('family-result').textContent='';}
function requireSession(){if(!selected)throw new Error('请先创建或选择一次阅读。');}
async function enter(){
  const expectedView=viewVersion;
  $('login-panel').hidden=true;$('workspace').hidden=false;$('logout').hidden=config.mode==='lab';
  const books=await api('/api/books');if(viewVersion!==expectedView)return;$('book').replaceChildren();
  for(const book of books){const option=document.createElement('option');option.textContent=book;$('book').append(option);}
  await refresh();
}
function display(result){
  $('answer').textContent=result.answer;lastTrace=result.trace_id||'';$('sources').replaceChildren();
  for(const source of result.sources||[]){const details=document.createElement('details'),summary=document.createElement('summary'),text=document.createElement('p');summary.textContent=source.file+' · '+source.parent+' · 片段 '+source.start+'—'+source.end;text.className='source-text';text.textContent=source.text;details.append(summary,text);$('sources').append(details);}
  if(!(result.sources||[]).length)$('sources').textContent='本次没有给出可引用片段。';
  $('result').hidden=false;
}
async function refreshNotes(){
  // 每次异步返回都核对视图，防止 A 的迟到私密内容出现在已经切换为 B 的页面。
  const expectedView=viewVersion;const drafts=await api('/api/drafts');if(viewVersion!==expectedView)return;$('drafts').replaceChildren();
  for(const draft of drafts.filter(x=>x.status==='pending')){
    const box=document.createElement('div');box.className='draft';const label=document.createElement('p'),text=document.createElement('textarea'),edit=document.createElement('button'),approve=document.createElement('button');
    label.textContent='待确认草稿 · 版本 '+draft.revision;text.value=draft.body;text.setAttribute('aria-label','编辑草稿内容');edit.textContent='保存修改，重新预览';approve.textContent='确认保存这一版';
    edit.onclick=async()=>{const actionView=viewVersion;try{await api('/api/drafts/'+draft.id,'PATCH',{body:text.value});if(viewVersion!==actionView)return;await refreshNotes();if(viewVersion===actionView)status('草稿已修改，请重新阅读后确认。');}catch(e){if(viewVersion===actionView)status(e.message);}};
    approve.onclick=async()=>{const actionView=viewVersion;try{if(text.value!==draft.body)throw new Error('内容已编辑，请先保存修改并重新预览。');await api('/api/drafts/'+draft.id+'/approve','POST',{revision:draft.revision,digest:draft.digest,confirmed:true});if(viewVersion!==actionView)return;await refreshNotes();if(viewVersion===actionView)status('当前草稿已保存。');}catch(e){if(viewVersion===actionView)status(e.message);}};
    box.append(label,text,edit,approve);$('drafts').append(box);
  }
  const notes=await api('/api/notes');if(viewVersion!==expectedView)return;$('notes').replaceChildren();
  for(const note of notes){const paragraph=document.createElement('p');paragraph.textContent=note.body;$('notes').append(paragraph);}
}
function on(button,action){$(button).addEventListener('click',()=>{const expectedToken=token,expectedReader=$('reader').value;action().catch(e=>{if(token===expectedToken&&$('reader').value===expectedReader)status(e.message);});});}
$('login-form').onsubmit=async event=>{event.preventDefault();const expectedView=++viewVersion;try{const values=Object.fromEntries(new FormData(event.target));const result=await api('/api/login','POST',values);if(viewVersion!==expectedView)return;token=result.access_token;event.target.password.value='';$('family-panel').hidden=result.role!=='parent';await enter();if(viewVersion===expectedView)status('已登录。');}catch(e){if(viewVersion===expectedView)status(e.message);}};
$('ask-form').onsubmit=async event=>{
  event.preventDefault();const expectedView=viewVersion,requestId=id();try{requireSession();activeRequest=requestId;$('result').hidden=true;lastTrace='';$('ask').disabled=true;$('cancel').hidden=false;status('正在查资料并组织回答……');
    const result=await api('/api/ask','POST',{session_id:selected.id,question:$('question').value,request_id:requestId,mode:$('mode').value});if(viewVersion!==expectedView)return;selected.revision=result.session_revision;display(result);status('回答已完成，可以对照依据。');
  }catch(e){if(viewVersion===expectedView)status(e.message);}finally{if(activeRequest===requestId){activeRequest=null;$('ask').disabled=false;$('cancel').hidden=true;}}
};
on('new-session',async()=>{const expectedView=viewVersion;const result=await api('/api/sessions','POST',{book:$('book').value});if(viewVersion!==expectedView)return;await refresh();if(viewVersion===expectedView)await choose(result.id);});
on('refresh',refresh);
on('logout',async()=>{const request=api('/api/logout','POST');token='';reset();const expectedView=viewVersion;$('workspace').hidden=true;$('login-panel').hidden=false;$('logout').hidden=true;await request;if(viewVersion===expectedView)status('已退出登录。');});
$('reader').onchange=()=>{reset();const expectedView=viewVersion;refresh().catch(e=>{if(viewVersion===expectedView)status(e.message);});};
on('save-progress',async()=>{requireSession();const expectedView=++viewVersion;const current=await api('/api/sessions/'+selected.id,'PATCH',{progress:Number($('progress').value),strict:$('strict').checked,revision:selected.revision});if(viewVersion!==expectedView)return;selected=current;$('result').hidden=true;status('阅读范围已更新，旧上下文已清空。');});
on('delete-session',async()=>{requireSession();if(!confirm('删除当前阅读记录？这不会删除讲稿。'))return;const expectedView=viewVersion;await api('/api/sessions/'+selected.id,'DELETE');if(viewVersion!==expectedView)return;reset();const refreshedView=viewVersion;await refresh();if(viewVersion===refreshedView)status('阅读记录已删除。');});
on('cancel',async()=>{if(activeRequest){const expectedView=viewVersion;const result=await api('/api/cancel/'+activeRequest,'POST');if(viewVersion===expectedView)status(result.message);}});
on('feedback',async()=>{if(!lastTrace)throw new Error('请先获得一次回答。');const expectedView=viewVersion;const result=await api('/api/feedback','POST',{category:$('category').value,trace_id:lastTrace});if(viewVersion===expectedView)status('反馈已记录，回执 '+result.receipt.slice(0,8));});
for(const [button,kind] of [['draft-note','note'],['draft-plan','review_plan']])on(button,async()=>{requireSession();const expectedView=viewVersion;status('正在整理草稿，尚未保存……');await api('/api/drafts','POST',{session_id:selected.id,kind,request_id:id()});if(viewVersion!==expectedView)return;await refreshNotes();if(viewVersion===expectedView)status('草稿已生成，请检查后决定是否保存。');});
on('family',async()=>{const expectedView=viewVersion;const result=await api('/api/family/'+encodeURIComponent($('child').value));if(viewVersion===expectedView)$('family-result').textContent=JSON.stringify(result,null,2);});
on('erase',async()=>{if(!confirm('删除当前业务库中自己的阅读记录、笔记和待确认草稿，并退出登录？'))return;const expectedView=viewVersion;const result=await api('/api/personal-data','DELETE');if(viewVersion!==expectedView)return;token='';reset();$('workspace').hidden=true;$('login-panel').hidden=false;$('logout').hidden=true;status(result.scope);});
(async()=>{config=await api('/api/config');document.querySelectorAll('[data-chapter]').forEach(e=>{e.hidden=Number(e.dataset.chapter)>config.chapter;});$('lab-notice').hidden=config.mode!=='lab';$('lab-picker').hidden=config.mode!=='lab';if(config.mode==='lab')await enter();else $('login-panel').hidden=false;})().catch(e=>status(e.message));
