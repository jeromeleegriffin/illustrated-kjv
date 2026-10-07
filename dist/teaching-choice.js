/* Recording choices stay in this browser, independently of reading progress. */
(function(root){
 const key='illustrated-kjv-teaching-choices-v1',rank=p=>p[0]*1000+p[1];
 function read(){try{const x=JSON.parse(root.localStorage.getItem(key)||'{}');return x&&typeof x==='object'&&!Array.isArray(x)?x:{}}catch{return {}}}
 function candidates(book,point){const seen=new Set();return book.lessons.filter(l=>rank(l.start)<=rank(point)&&rank(point)<=rank(l.end)).sort((a,b)=>Number(a.teacher!=='Arnold Murray')-Number(b.teacher!=='Arnold Murray')||Number(!a.official)-Number(!b.official)).filter(l=>{if(seen.has(l.id))return false;seen.add(l.id);return true})}
 function preferred(book,point,matches){for(const c of Object.values(read()).reverse()){if(c&&c.book===book&&Array.isArray(c.start)&&Array.isArray(c.end)&&rank(c.start)<=rank(point)&&rank(point)<=rank(c.end)){const m=matches.find(l=>l.id===c.id);if(m)return m}}return null}
 function shortlist(matches,selected){const list=matches.slice(0,3);if(selected&&!list.some(x=>x.id===selected.id))list[list.length-1]=selected;return list}
 function save(group,id){const state=read();if(id)state[group.key]={book:group.book,start:group.start,end:group.end,id};else delete state[group.key];try{root.localStorage.setItem(key,JSON.stringify(state));return true}catch{return false}}
 function groups(data,bible){const result=[];data.books.forEach((book,b)=>{let previous=null;bible.books[b].chapters.forEach((vs,ci)=>vs.forEach((_,vi)=>{const point=[ci+1,vi+1],matches=candidates(book,point),signature=matches.map(l=>l.id).join('|');if(matches.length<2){previous=null;return}if(previous&&previous.signature===signature){previous.end=point;previous.verses++}else{previous={book:b,name:book.name,start:point,end:point,matches,signature,verses:1};result.push(previous)}}))});return result.map(g=>({...g,key:`${g.book}:${g.start.join(':')}-${g.end.join(':')}`}))}
 root.TeachingChoice={key,rank,read,candidates,preferred,shortlist,save,groups};
})(typeof window==='undefined'?globalThis:window);
