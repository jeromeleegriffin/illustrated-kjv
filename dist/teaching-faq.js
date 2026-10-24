'use strict';
(() => {
 const data=window.GRIFFIN_FAQ;
 if(!data){document.getElementById('results-count').textContent='FAQ data could not load. Keep the page and its supporting files together.';return;}
 const $=id=>document.getElementById(id),make=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
 const clock=n=>`${Math.floor(n/60)}:${String(Math.floor(n%60)).padStart(2,'0')}`;
 const safeId=id=>/^[A-Za-z0-9_-]{11}$/.test(id);
 const frequency=answers=>new Set(answers.flatMap(a=>a.sources.map(s=>s.recording_group||s.video_id))).size;
 function watch(s){if(!safeId(s.video_id)||!Number.isFinite(s.start_seconds)||s.start_seconds<0)return null;const a=make('a',`▶ Hear the answer at ${clock(s.start_seconds)}`,'watch');a.href=`https://www.youtube.com/watch?v=${s.video_id}&t=${Math.floor(s.start_seconds)}s`;a.target='_blank';a.rel='noopener noreferrer';return a;}
 function source(s){const box=make('div',undefined,'source-link'),w=watch(s);if(w)box.append(w);box.append(make('p',`${s.lesson} · ${s.video_id}`,'source'));return box;}
 for(const topic of [...new Set(data.questions.map(q=>q.topic))].sort())$('topic').append(make('option',topic));
 let page=0;
 const pagers=[make('nav',undefined,'faq-pager'),make('nav',undefined,'faq-pager')];
 pagers[0].setAttribute('aria-label','Question pages at top');pagers[1].setAttribute('aria-label','Question pages at bottom');
 $('questions').after(pagers[1]);
 function render(reset=false){
  if(reset)page=0;
  const terms=$('query').value.toLowerCase().trim().split(/\s+/).filter(Boolean),teacher=$('teacher').value,topic=$('topic').value;
  let list=data.questions.map(q=>({...q,shownAnswers:q.answers.filter(a=>!teacher||a.teacher===teacher)})).filter(q=>q.shownAnswers.length&&(!topic||q.topic===topic));
  list=list.filter(q=>{const text=[q.question,q.topic,...q.shownAnswers.flatMap(a=>[a.teacher,a.summary,...a.scripture_mentions,...a.sources.map(s=>s.lesson)])].join(' ').toLowerCase();return terms.every(t=>text.includes(t));});
  list.sort((a,b)=>$('sort').value==='alphabetical'?a.question.localeCompare(b.question):frequency(b.shownAnswers)-frequency(a.shownAnswers)||a.question.localeCompare(b.question));
  $('questions').replaceChildren();
  page=Math.max(0,Math.min(page,list.length-1));
  for(const nav of pagers){nav.replaceChildren();nav.hidden=!list.length;const prev=make('button','← Previous'),next=make('button','Next →'),label=make('span',list.length?`Page ${page+1} of ${list.length}`:'No results','page-label');prev.type=next.type='button';prev.disabled=page===0;next.disabled=page>=list.length-1;prev.onclick=()=>{page--;render();};next.onclick=()=>{page++;render();};nav.append(prev,label,next);}
  for(const q of list.slice(page,page+1)){
   const card=make('article',undefined,'question');card.id=q.id;card.dataset.count=frequency(q.shownAnswers);card.append(make('h2',`#${q.rank}. ${q.question}`),pagers[0],make('p',q.topic,'topic'));
   const count=frequency(q.shownAnswers);card.append(make('p',`Asked in ${count} reviewed recording${count===1?'':'s'}`,'frequency'));
   const answers=[...q.shownAnswers].sort((a,b)=>(a.teacher==='Arnold Murray'?0:1)-(b.teacher==='Arnold Murray'?0:1));
   for(const [i,a] of answers.entries()){
    const v=make('section',undefined,'variant');v.append(make('p',`Pastor ${a.teacher} · summary of this answer`,'pastor'),make('p',a.summary));
    if(a.scripture_mentions.length)v.append(make('p','Scripture mentioned in this answer: '+a.scripture_mentions.join('; '),'source'));
    if(a.sources[0])v.append(source(a.sources[0]));
    if(a.sources.length>1){const more=make('details',undefined,'source-details');more.append(make('summary',`${a.sources.length-1} more source link${a.sources.length===2?'':'s'} for this answer`));for(const s of a.sources.slice(1))more.append(source(s));v.append(more);}
    v.append(make('p','Caption passage reviewed; audio verification pending.','status'));
    if(i===0)card.append(v);else{const variant=make('details',undefined,'answer-variant');variant.append(make('summary',`Additional answer · Pastor ${a.teacher}`),v);card.append(variant);}
   }
   if(q.source_upload_count>q.asked_count)card.append(make('p','Alternate uploads are linked but counted once.','status'));
   if(q.conflict_status==='conflict_needs_review')card.append(make('p','Different answers require review. Both are preserved.','status'));
   $('questions').append(card);
  }
  $('results-count').textContent=`${list.length} matching questions · one question per page. Numbers show the overall frequency ranking; counts grow as review continues.`;$('empty').hidden=list.length!==0;
 }
 function review(){const q=$('review-query').value.toLowerCase();$('review-list').replaceChildren();for(const r of data.recordings||[]){if(!`${r.video_id} ${r.lesson} ${r.teacher} ${r.review_status}`.toLowerCase().includes(q))continue;const row=make('div',undefined,'review-row');row.append(make('b',r.lesson),make('span',`${r.teacher} · ${r.video_id} · ${r.kind||'passage'}`),make('span',r.review_status.replaceAll('_',' ')));if(r.question_ids.length)row.append(make('span','Linked questions: '+r.question_ids.join(', ')));$('review-list').append(row);}}
 $('review-counts').textContent=`${data.review.available} transcripts tracked and scanned · ${data.review.partially_reviewed} partially reviewed · ${data.review.fully_reviewed} complete caption Q&A reviews (audio pending) · ${data.review.teacher_pending||0} awaiting teacher confirmation.`;
 $('filters').addEventListener('submit',e=>e.preventDefault());$('query').addEventListener('input',()=>render(true));$('teacher').addEventListener('change',()=>render(true));$('topic').addEventListener('change',()=>render(true));$('sort').addEventListener('change',()=>render(true));$('filters').addEventListener('reset',()=>setTimeout(()=>render(true),0));$('review-query').addEventListener('input',review);render();review();
})();

