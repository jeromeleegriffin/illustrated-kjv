'use strict';
const studies=window.GRIFFIN_TOPICAL.studies,PAGE_SIZE=50;
const query=document.getElementById('query'),teacher=document.getElementById('teacher'),topic=document.getElementById('topic'),batch=document.getElementById('batch');let activeLetter='',page=0;
function sortKey(s){return s.title.trim().replace(/^[^A-Za-z0-9]+/,'').replace(/^(the|an|a)\s+/i,'')}
function firstLetter(s){const c=sortKey(s).charAt(0).toUpperCase();return /^[A-Z]$/.test(c)?c:'#'}
function subject(s){const t=s.title.toLowerCase();if(/prophe|trump|seal|beast|tribulation|rapture|antichrist|millennium|end time|latter rain|world ages/.test(t))return 'Prophecy & end times';if(/prayer|worship|praise|gratitude|thank|faith|glorify/.test(t))return 'Faith & prayer';if(/christ|jesus|immanuel|messiah|passover|communion/.test(t))return 'Christ & Passover';if(/study|scripture|knowledge|discern|parable/.test(t))return 'Bible study';return s.topic==='Special studies'?'Other topics':s.topic}
for(const label of [...new Set(studies.map(subject))].sort()){const o=document.createElement('option');o.value=o.textContent=label;topic.append(o)}
for(const n of [...new Set(studies.map(s=>s.batch))].sort((a,b)=>a-b)){const o=document.createElement('option');o.value=String(n);o.textContent='Batch '+n+' · '+studies.filter(s=>s.batch===n).length+' links';batch.append(o)}
function selectStudies(q='',pastor='',category='',selectedBatch='',letter=''){q=q.trim().toLowerCase();return studies.filter(s=>(!pastor||(pastor==='pending'?!s.teacher:s.teacher===pastor))&&(!category||subject(s)===category)&&(!selectedBatch||String(s.batch)===selectedBatch)&&(!letter||firstLetter(s)===letter)&&(!q||[s.title,s.published_title].join(' ').toLowerCase().includes(q))).sort((a,b)=>sortKey(a).localeCompare(sortKey(b),'en',{numeric:true,sensitivity:'base'})||a.id.localeCompare(b.id))}
const letterButtons=[];for(const [label,value] of [['All',''],['0–9','#'],...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').map(c=>[c,c])]){const b=document.createElement('button');b.type='button';b.textContent=label;b.setAttribute('aria-pressed',String(!value));b.addEventListener('click',()=>{activeLetter=value;resetPage()});letterButtons.push([b,value]);document.getElementById('letters').append(b)}
function render(){const rows=selectStudies(query.value,teacher.value,topic.value,batch.value,activeLetter),pages=Math.max(1,Math.ceil(rows.length/PAGE_SIZE));page=Math.min(page,pages-1);const start=page*PAGE_SIZE,visible=rows.slice(start,start+PAGE_SIZE),list=document.getElementById('questions');list.replaceChildren();for(const s of visible){const li=document.createElement('li'),a=document.createElement('a'),title=document.createElement('span'),arrow=document.createElement('span');a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';title.textContent=s.title;if(s.transcript_status==='saved_private_captions'){const status=document.createElement('small');status.className='caption-status';status.textContent='Captions saved · review pending';title.append(status)}if(s.media_kind){const status=document.createElement('small');status.className='caption-status';status.textContent=s.media_kind==='archive_audio_listing'?'Archive audio listing · playback unverified':'Video listing · playback unverified';title.append(status)}arrow.textContent='↗';arrow.className='arrow';arrow.setAttribute('aria-hidden','true');a.append(title,arrow);li.append(a);list.append(li)}document.getElementById('results-count').textContent=rows.length?(start+1)+'–'+(start+visible.length)+' of '+rows.length+' matches · '+studies.length+' links total':'0 matches · '+studies.length+' links total';document.getElementById('empty').hidden=rows.length>0;for(const suffix of ['', '-top']){document.getElementById('page-count'+suffix).textContent='Page '+(page+1)+' of '+pages;document.getElementById('previous'+suffix).disabled=page===0;document.getElementById('next'+suffix).disabled=page>=pages-1;}for(const [b,v] of letterButtons)b.setAttribute('aria-pressed',String(v===activeLetter))}
 let stopPagingHold=()=>{};
 function holdToPage(button,direction){
  let timer=null,pointer=null,repeated=false;
  const stop=()=>{clearTimeout(timer);timer=null;pointer=null;};
  const step=()=>{if(button.disabled)return false;page+=direction;render();window.scrollTo(0,0);return true;};
  button.title='Tap for one page; hold to keep turning pages';
  button.addEventListener('pointerdown',e=>{
   if(!e.isPrimary||e.button!==0||button.disabled)return;
   stopPagingHold();stopPagingHold=stop;pointer=e.pointerId;repeated=false;
   button.setPointerCapture(e.pointerId);
   const repeat=()=>{if(pointer===null||button.disabled){stop();return;}repeated=true;step();timer=setTimeout(repeat,180);};
   timer=setTimeout(repeat,450);
  });
  for(const event of ['pointerup','pointercancel','lostpointercapture','pointerleave'])button.addEventListener(event,stop);
  button.addEventListener('contextmenu',e=>e.preventDefault());
  button.addEventListener('click',()=>{stop();if(repeated){repeated=false;return;}step();});
  button.addEventListener('keydown',()=>{repeated=false;});
 }
 window.addEventListener('blur',()=>stopPagingHold());
 document.addEventListener('visibilitychange',()=>{if(document.hidden)stopPagingHold();});

function resetPage(){stopPagingHold();page=0;render()}
query.addEventListener('input',resetPage);teacher.addEventListener('change',resetPage);topic.addEventListener('change',resetPage);batch.addEventListener('change',resetPage);for(const suffix of ['', '-top']){holdToPage(document.getElementById('previous'+suffix),-1);holdToPage(document.getElementById('next'+suffix),1);}document.getElementById('filters').addEventListener('reset',()=>{query.value='';teacher.value='';topic.value='';batch.value='';activeLetter='';resetPage()});render();


