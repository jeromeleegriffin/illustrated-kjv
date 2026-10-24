'use strict';
(() => {
 const data=window.GRIFFIN_FAQ;
 if(!data){document.getElementById('results-count').textContent='FAQ data could not load. Keep the page and its supporting files together.';return;}
 const $=id=>document.getElementById(id), make=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
 const clock=n=>`${Math.floor(n/60)}:${String(Math.floor(n%60)).padStart(2,'0')}`;
 const safeId=id=>/^[A-Za-z0-9_-]{11}$/.test(id);
 function watch(s){if(!safeId(s.video_id)||!Number.isFinite(s.start_seconds)||s.start_seconds<0)return null;const a=make('a',`▶ Hear the answer at ${clock(s.start_seconds)}`,'watch');a.href=`https://www.youtube.com/watch?v=${s.video_id}&t=${Math.floor(s.start_seconds)}s`;a.target='_blank';a.rel='noopener noreferrer';return a;}
 for(const topic of [...new Set(data.questions.map(q=>q.topic))].sort())$('topic').append(make('option',topic));
 function render(){
  const terms=$('query').value.toLowerCase().trim().split(/\s+/).filter(Boolean),teacher=$('teacher').value,topic=$('topic').value;let count=0;$('questions').replaceChildren();
  for(const q of data.questions){if(topic&&q.topic!==topic)continue;const answers=q.answers.filter(a=>!teacher||a.teacher===teacher);if(!answers.length)continue;const text=[q.question,q.topic,...answers.flatMap(a=>[a.teacher,a.summary,...a.scripture_mentions,...a.sources.map(s=>s.lesson)])].join(' ').toLowerCase();if(!terms.every(t=>text.includes(t)))continue;
   count++;const card=make('article',undefined,'question');card.id=q.id;card.append(make('p',q.topic,'topic'),make('h2',q.question));
   for(const a of [...answers].sort((x,y)=>(x.teacher==='Arnold Murray'?0:1)-(y.teacher==='Arnold Murray'?0:1))){const v=make('section',undefined,'variant');v.append(make('p',`Pastor ${a.teacher} · summary of teaching`,'pastor'),make('p',a.summary));if(a.scripture_mentions.length)v.append(make('p','Scripture mentioned: '+a.scripture_mentions.join('; '),'source'));
    for(const s of a.sources){const w=watch(s);if(w)v.append(w);v.append(make('p',`${s.lesson} · ${clock(s.start_seconds)}–${clock(s.end_seconds)}`,'source'));const details=make('details',undefined,'source-details');details.append(make('summary','Source and review details'),make('p',`Recording: ${s.video_id}. ${s.review_status==='source_changed_needs_review'?'Source changed or is missing: this answer needs review.':'Caption passage checked; audio verification pending.'}`,'status'));v.append(details);}
    if(a.relationship!=='initial_answer')v.append(make('p','Relationship to other answers: '+a.relationship,'status'));card.append(v);
   }
   if(q.conflict_status==='conflict_needs_review')card.append(make('p','Different answers require review. Both are preserved.','status'));$('questions').append(card);
  }
  $('results-count').textContent=`${count} of ${data.questions.length} questions shown. This is the first FAQ selection.`;$('empty').hidden=count!==0;
 }
 function review(){const q=$('review-query').value.toLowerCase();$('review-list').replaceChildren();for(const r of data.recordings||[]){if(!`${r.video_id} ${r.lesson} ${r.teacher} ${r.review_status}`.toLowerCase().includes(q))continue;const row=make('div',undefined,'review-row');row.append(make('b',r.lesson),make('span',`${r.teacher} · ${r.video_id}`),make('span',r.review_status.replaceAll('_',' ')));if(r.question_ids.length)row.append(make('span','Linked questions: '+r.question_ids.join(', ')));$('review-list').append(row);}}
 $('review-counts').textContent=`${data.review.available} transcripts tracked · ${data.review.partially_reviewed} partially reviewed · ${data.review.fully_reviewed} fully reviewed. All remaining Q&A work stays queued.`;
 $('filters').addEventListener('submit',e=>e.preventDefault());$('query').addEventListener('input',render);$('teacher').addEventListener('change',render);$('topic').addEventListener('change',render);$('filters').addEventListener('reset',()=>setTimeout(render,0));$('review-query').addEventListener('input',review);render();review();
})();
