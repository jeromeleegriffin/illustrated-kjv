/* Optional published-range video links. Scripture and reading state are independent. */
window.BibleTeaching=(()=>{
 let source=null,failed=false,location={book:0,chapter:1,verse:1};
 const box=document.getElementById('bibleTeaching'),reference=document.getElementById('teachingReference'),links=document.getElementById('teachingLinks');
 const rank=x=>x[0]*1000+x[1];
 function link(url,label,className=''){const a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=label;a.className=className;return a}
 function render(){
  box.hidden=false;links.replaceChildren();
  const book=source?.books[location.book];
  reference.textContent=`· ${book?.name||''} ${location.chapter}:${location.verse}`;
  if(!source){links.textContent=failed?'Lesson links could not load. Scripture is still available. Refresh to try again.':'Loading lesson links…';return}
  const point=rank([location.chapter,location.verse]);
  const automatic=book.lessons.filter(x=>rank(x.start)<=point&&point<=rank(x.end)).sort((a,b)=>Number(a.teacher!=='Arnold Murray')-Number(b.teacher!=='Arnold Murray')||Number(!a.official)-Number(!b.official));
  const unique=automatic.filter((m,i)=>automatic.findIndex(x=>x.id===m.id)===i);
  const preferred=window.TeachingChoice?.preferred(location.book,[location.chapter,location.verse],unique);
  const matches=preferred?[preferred,...unique.filter(m=>m.id!==preferred.id)]:unique;

  if(matches.length){
   if(preferred){const chosen=document.createElement('p');chosen.className='teaching-credit';chosen.textContent='Your selected recording';links.append(chosen)}
   links.append(link(matches[0].url,`Watch ${matches[0].title} ↗`,'teaching-link'));
   const credit=document.createElement('p');credit.className='teaching-credit';credit.textContent=`Pastor ${matches[0].teacher} · ${matches[0].channel}${matches[0].teacher==='Dennis Murray'?' · secondary fallback':''}${matches[0].official?'':' (independent archive)'}`;links.append(credit);
   if(matches[0].playbackChecked===false){const note=document.createElement('p');note.className='teaching-credit';note.textContent=matches[0].ownerReview?'Owner-reviewed passage link; full playback has not been independently tested.':'Published passage link; playback has not been tested.';links.append(note)}
   if(matches[0].teacherAttribution){const evidence=document.createElement('p');evidence.className='teaching-credit';evidence.append('Teacher attribution is inferred: ',link(matches[0].teacherAttribution.source,'attribution source ↗'));links.append(evidence)}
   if(matches.length>1){const more=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Other matching recordings';more.append(summary);for(const m of matches.slice(1,3))more.append(link(m.url,`${m.title} · ${m.teacher} · ${m.channel} ↗`,'teaching-link'));links.append(more)}
  }else{const p=document.createElement('p');p.textContent='No confirmed Arnold or Dennis Murray lesson for this verse in the current index.';links.append(p)}
  links.append(link('./teaching-review.html?book='+location.book+'&chapter='+location.chapter+'&verse='+location.verse,'Choose your teaching recordings →','teaching-review-link'));
  if(book.bookStudies.length){const studies=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Book studies — verse range not specified';studies.append(summary);for(const s of book.bookStudies)studies.append(link(s.url,`${s.title} · ${s.teacher} · ${s.channel} ↗`,'teaching-link'));links.append(studies)}
  const browse=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Browse lessons and Bible coverage';browse.append(summary);
  for(const url of book.playlists)browse.append(link(url,`${book.name} lesson playlist ↗`,'teaching-link'));
  browse.append(link('https://www.youtube.com/results?search_query='+encodeURIComponent(`Arnold Murray Dennis Murray Shepherd's Chapel ${book.name} ${location.chapter}:${location.verse}`),'Search YouTube for this passage ↗','teaching-link'));
  const note=document.createElement('p');note.className='teaching-credit';note.textContent='Search results are suggestions, not verified matches. Counts below show verses with confirmed published-range links.';browse.append(note);
  const table=document.createElement('table');table.className='teaching-coverage';
  const head=document.createElement('thead');head.innerHTML='<tr><th scope="col">Book</th><th scope="col">Verses linked</th></tr>';table.append(head);
  const body=document.createElement('tbody');for(const b of source.books){const row=document.createElement('tr'),name=document.createElement('td'),count=document.createElement('td');const a=document.createElement('a');a.href='./bible.html?ref='+encodeURIComponent(`${b.name} 1:1`);a.textContent=b.name;name.append(a);count.textContent=`${b.coverage.matched.toLocaleString()} / ${b.coverage.total.toLocaleString()}`;row.append(name,count);body.append(row)}table.append(body);browse.append(table);links.append(browse);
 }
 function setLocation(book,chapter,verse){location={book,chapter,verse};render()}
 document.addEventListener('bible-verse-selected',e=>setLocation(e.detail.book,e.detail.chapter,e.detail.verse));
 fetch('./bible-teaching.json?v=012').then(r=>{if(!r.ok)throw Error('Unavailable');return r.json()}).then(d=>{if(!Array.isArray(d.books)||d.books.length!==66)throw Error('Invalid lesson index');source=d;render()}).catch(()=>{failed=true;render()});
 return {setLocation};
})();
