'use strict';
const $ = id => document.getElementById(id);
const demo = new URLSearchParams(location.search).get('demo') === '1';
const todayJST = () => new Intl.DateTimeFormat('sv-SE', {timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const state = {issues:[], request:0};
function preference(key,value){try{if(value===undefined)return localStorage.getItem(key);localStorage.setItem(key,value);}catch{}return null;}
function setTheme(value){if(value==='auto')delete document.documentElement.dataset.theme;else document.documentElement.dataset.theme=value;preference('brief-theme',value);}
$('theme').value=preference('brief-theme')||'auto';setTheme($('theme').value);
$('theme').addEventListener('change',e=>setTheme(e.target.value));
let large=preference('brief-large')==='true';
function size(){document.documentElement.style.setProperty('--body-size',large?'20px':'17px');$('font-size').setAttribute('aria-pressed',String(large));$('font-size').textContent=large?'标准字号':'大字阅读';}
size();$('font-size').onclick=()=>{large=!large;size();preference('brief-large',String(large));};
function message(text){$('notice').textContent=text;}
async function json(url){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw new Error('文件无法读取');return r.json();}
function latest(){return state.issues.find(x=>x.date<=todayJST());}
function dateURL(date){const u=new URL(location);u.searchParams.set('date',date);u.hash='';return u;}
async function show(date,push=false){
 const token=++state.request;
 const issue=state.issues.find(x=>x.date===date);
 if(!issue){message('这个日期还没有简报。可以选择已有日期，或返回今日 / 最新。');$('issue-title').textContent='该日期尚未发布';$('issue-meta').textContent='';$('article').replaceChildren();$('toc').replaceChildren();$('dates').selectedIndex=-1;return;}
 $('dates').value=date;
 if(push)history.pushState({},'',dateURL(date));
 $('issue-title').textContent=issue.title;$('issue-meta').textContent='正在读取…';$('article').replaceChildren();$('toc').replaceChildren();
 message(demo?'版式预览 · 以下为演示内容，不是当日新闻；日期仅用于演示历史浏览。':date===todayJST()?'今日简报已发布。':`正在阅读 ${date}。${latest()?.date===date?'今日尚未发布，已显示最近一期。':''}`);
 try{
  const data=await json(`./data/${demo?'demo/':''}${date}.json`);if(token!==state.request)return;
  // Only the allowlisted output of build.py enters this element.
  $('article').innerHTML=data.html;
  $('issue-label').textContent=demo?'LAYOUT PREVIEW / 版式预览':'DAILY EDITION / 每日综合简报';
  $('issue-meta').textContent=`${date} · 日本时间${data.importedAt?' · 入库 '+new Date(data.importedAt).toLocaleString('zh-CN',{timeZone:'Asia/Tokyo',hour12:false}):''}`;
  $('article').querySelectorAll('h1,h2').forEach((h,i)=>{if(!h.id)h.id=`section-${i}`;const a=document.createElement('a');a.href='#'+encodeURIComponent(h.id);a.textContent=h.textContent;$('toc').append(a);});
  $('article').querySelectorAll('img').forEach(img=>{const fallback=()=>{const p=document.createElement('p');p.className='image-error';p.textContent='图片暂不可用：'+(img.alt||'请查看原文来源');img.replaceWith(p);};img.addEventListener('error',fallback,{once:true});if(img.complete&&img.naturalWidth===0)fallback();});
 }catch{if(token!==state.request)return;message('简报加载失败，请刷新重试。其他日期仍可选择。');$('issue-meta').textContent='加载失败';}
}
$('dates').onchange=e=>show(e.target.value,true);
$('latest').onclick=()=>{const current=latest();if(current)show(current.date,true);};
window.addEventListener('popstate',()=>show(new URLSearchParams(location.search).get('date')||latest()?.date));
async function init(){
 $('clock-date').textContent=todayJST().replaceAll('-',' / ');
 try{
  const manifest=await json(`./data/${demo?'demo/':''}index.json`);
  state.issues=manifest.issues.sort((a,b)=>b.date.localeCompare(a.date));
  $('dates').replaceChildren();for(const issue of state.issues){const o=document.createElement('option');o.value=issue.date;o.textContent=issue.date;$('dates').append(o);}
  if(!state.issues.length){message('第一份简报尚未导入。发布后，首页会自动显示当天或最近一期。');$('dates').disabled=true;$('latest').disabled=true;return;}
  const requested=new URLSearchParams(location.search).get('date');await show(requested||latest()?.date);
 }catch{message('暂时无法读取简报目录，请稍后刷新。');}
}
init();
