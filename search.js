(function(root){
'use strict';
const aliases=[['gen','ge'],['ex','exo','exod'],['lev','lv'],['num','nu'],['deut','dt'],['josh','jos'],['judg','jdg'],['ru'],['1sam','1sa'],['2sam','2sa'],['1ki','1kgs'],['2ki','2kgs'],['1chron','1chr','1ch'],['2chron','2chr','2ch'],['ezr'],['neh'],['est'],[],['psalm','ps','psa'],['prov','pr'],['eccl','ecc'],['song','songofsongs','sos','canticles'],['isa'],['jer'],['lam'],['ezek','eze'],['dan'],['hos'],[],['am'],['obad'],['jon'],['mic'],['nah'],['hab'],['zeph'],['hag'],['zech'],['mal'],['matt','mt'],['mk','mrk'],['lk'],['jn','jhn'],['ac'],['rom'],['1cor','1co'],['2cor','2co'],['gal'],['eph'],['phil','php'],['col'],['1thess','1th'],['2thess','2th'],['1tim','1ti'],['2tim','2ti'],['tit'],['phlm','phm'],['heb'],['jas','jam'],['1pet','1pe'],['2pet','2pe'],['1jn','1jhn'],['2jn','2jhn'],['3jn','3jhn'],[],['rev','re']];
const bookKey=s=>s.toLowerCase().replace(/\bfirst\b/g,'1').replace(/\bsecond\b/g,'2').replace(/\bthird\b/g,'3').replace(/[^a-z0-9]/g,'');
const normalize=s=>s.toLowerCase().replace(/[’‘]/g,"'").replace(/\s+/g,' ').trim();
function search(data,names,query,limit=75){
 const q=String(query||'').trim(); if(!q)return {kind:'empty',message:'Enter a word, phrase, or Bible reference.'};
 const findBook=s=>names.findIndex((name,i)=>bookKey(name)===bookKey(s)||(aliases[i]||[]).includes(bookKey(s)));
 const match=q.match(/^(.+?)\s+(\d+)(?:\s*[:.]\s*(\d+))?$/);
 let bi=match?findBook(match[1]):findBook(q);
 if(bi>=0){const chapter=match?Number(match[2]):1,verse=match&&match[3]?Number(match[3]):1,book=data.books[bi];
  if(chapter<1||chapter>book.chapters.length)return {kind:'error',message:`${names[bi]} has ${book.chapters.length} chapters. Choose a chapter from 1 to ${book.chapters.length}.`};
  const count=book.chapters[chapter-1].length;
  if(verse<1||verse>count)return {kind:'error',message:`${names[bi]} ${chapter} has ${count} verses. Choose a verse from 1 to ${count}.`};
  return {kind:'reference',target:{book:bi,chapter,verse}};
 }
 const needle=normalize(q),results=[];let total=0;
 data.books.forEach((book,bi)=>book.chapters.forEach((verses,ci)=>verses.forEach((text,vi)=>{if(normalize(text).includes(needle)){total++;if(results.length<limit)results.push({book:bi,chapter:ci+1,verse:vi+1,text})}})));
 return {kind:'text',results,total,limit};
}
const api={search};root.BibleSearch=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof window==='object'?window:globalThis);
