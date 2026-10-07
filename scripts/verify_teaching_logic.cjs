// Run the actual teaching renderer without a browser; this does not test layout.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.textContent=''}
 get textContent(){return this._text+this.children.map(e=>typeof e==='string'?e:e.textContent).join('')}
 set textContent(value){this._text=value;this.children=[]}
 append(...children){this.children.push(...children)}
 replaceChildren(){this.children=[];this.textContent=''}
}
(async()=>{
 const root=path.resolve(__dirname,'..'),data=JSON.parse(fs.readFileSync(path.join(root,'dist/bible-teaching.json'))),bible=JSON.parse(fs.readFileSync(path.join(root,'dist/bible.json')));
 const elements=Object.fromEntries(['bibleTeaching','teachingReference','teachingLinks'].map(id=>[id,new Element('div')]));
 const sandbox={window:{},document:{getElementById:id=>elements[id],createElement:tag=>new Element(tag),addEventListener:()=>{}},fetch:async()=>({ok:true,json:async()=>data})};
 vm.runInNewContext(fs.readFileSync(path.join(root,'dist/bible-teaching.js'),'utf8'),sandbox);await new Promise(resolve=>setImmediate(resolve));
 const batch=(process.argv[2]||'8,9,10,11,12').split(',').map(Number),label=process.argv[3]||'seventh';
 assert(/^[a-z]+$/.test(label));assert(batch.every(b=>Number.isInteger(b)&&b>=0&&b<66));
 let checked=0,arnold=0,dennis=0,gaps=0;
 for(const book of batch)for(let chapter=1;chapter<=bible.books[book].chapters.length;chapter++)for(let verse=1;verse<=bible.books[book].chapters[chapter-1].length;verse++){
  sandbox.window.BibleTeaching.setLocation(book,chapter,verse);
  const matches=data.books[book].lessons.filter(l=>l.start[0]*1000+l.start[1]<=chapter*1000+verse&&chapter*1000+verse<=l.end[0]*1000+l.end[1]).sort((a,b)=>Number(a.teacher!=='Arnold Murray')-Number(b.teacher!=='Arnold Murray')||Number(!a.official)-Number(!b.official));
  const primary=elements.teachingLinks.children.filter(e=>e.className==='teaching-link');
  if(!matches.length){assert.equal(primary.length,0);assert(elements.teachingLinks.textContent.includes('No confirmed'));gaps++;checked++;continue}
  assert.equal(primary.length,1);assert.equal(primary[0].href,matches[0].url);
  if(matches[0].teacher==='Arnold Murray')arnold++;else{dennis++;assert(elements.teachingLinks.children.some(e=>e.textContent.includes('secondary fallback')))}
  if(matches[0].teacherAttribution)assert(elements.teachingLinks.children.some(e=>e.textContent.includes('Teacher attribution is inferred')));
  checked++;
 }
 const result={status:'PASS',versesChecked:checked,arnoldPrimaryVerses:arnold,dennisFallbackVerses:dennis,unlinkedVerses:gaps,checks:['Actual renderer chooses one primary link for covered verses and an explicit gap otherwise','Arnold-first and official-source ordering','Dennis fallback credit','Inference notice for inferred records'],limitation:'DOM mock tests renderer logic only; browser layout and video playback are not tested.'};
 fs.writeFileSync(path.join(root,`verification/${label}-batch-renderer-logic.json`),JSON.stringify(result,null,2));console.log(result);
})().catch(e=>{console.error(e);process.exit(1)});
