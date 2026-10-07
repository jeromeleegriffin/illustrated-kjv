const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const data=JSON.parse(fs.readFileSync('dist/bible.json'));
const elements=new Map();let selection='',panel=false,modal=false,prevented=0,scrolls=0;
function el(id){if(!elements.has(id))elements.set(id,{listeners:{},disabled:false,focus(){this.focused=true},addEventListener(k,fn){this.listeners[k]=fn},classList:{contains:()=>panel}});return elements.get(id)}
const window={innerWidth:400,scrollY:0,getSelection:()=>({toString:()=>selection}),addEventListener(){},scrollTo(){scrolls++}};
const ctx={window,document:{getElementById:el,querySelector:s=>el(s.slice(1)),querySelectorAll:()=>[{hidden:!modal}]},fetch:()=>new Promise(()=>{}),console,URLSearchParams,location:{search:''},Date};vm.createContext(ctx);
vm.runInContext(fs.readFileSync('dist/chapter-navigation.js','utf8'),ctx);
vm.runInContext(fs.readFileSync('dist/app.js','utf8'),ctx);
ctx.data=data;vm.runInContext('state.data=data;render=()=>window.ReaderNavigation.update(state.data,state.book,state.chapter);window.ReaderNavigation.init(step);render()',ctx);
const position=()=>vm.runInContext('[state.book,state.chapter].join(":")',ctx);
const set=(b,c)=>vm.runInContext(`state.book=${b};state.chapter=${c};render()`,ctx);
assert(el('previousChapterBottom').disabled);el('previousChapterBottom').onclick();assert.equal(position(),'0:1');
let count=1;while(!el('nextChapterBottom').disabled){el('nextChapterBottom').onclick();count++;assert(count<1200)}
assert.equal(count,1189);assert.equal(position(),'65:22');assert(el('nextChapter').disabled);el('nextChapterBottom').onclick();assert.equal(position(),'65:22');
while(!el('previousChapterBottom').disabled)el('previousChapterBottom').onclick();assert.equal(position(),'0:1');
function touch(x,y,id=1){return {clientX:x,clientY:y,identifier:id}}
function event(touches,changedTouches=[],target={closest:()=>null}){return {touches,changedTouches,target,cancelable:true,preventDefault(){prevented++}}}
const emit=(k,e)=>el('scripture').listeners[k](e);
function swipe(dx,dy=0){emit('touchstart',event([touch(200,200)]));emit('touchmove',event([touch(200+dx,200+dy)]));emit('touchend',event([],[touch(200+dx,200+dy)]))}
swipe(-100);assert.equal(position(),'0:2');swipe(100);assert.equal(position(),'0:1');assert(el('chapterTitle').focused);
set(0,50);swipe(-100);assert.equal(position(),'1:1');swipe(100);assert.equal(position(),'0:50');
set(0,2);for(const [dx,dy] of [[-30,0],[-100,60],[15,100]]){swipe(dx,dy);assert.equal(position(),'0:2')}
selection='selected';swipe(-100);assert.equal(position(),'0:2');selection='';panel=true;swipe(-100);assert.equal(position(),'0:2');panel=false;modal=true;swipe(-100);assert.equal(position(),'0:2');modal=false;
emit('touchstart',event([touch(200,200)]));emit('touchmove',event([touch(100,200),touch(150,200,2)]));emit('touchend',event([],[touch(100,200)]));assert.equal(position(),'0:2');
emit('touchstart',event([touch(200,200)]));window.scrollY=20;emit('touchend',event([],[touch(100,200)]));assert.equal(position(),'0:2');window.scrollY=0;
emit('touchstart',event([touch(200,200)]));emit('touchcancel',event([]));emit('touchend',event([],[touch(100,200)]));assert.equal(position(),'0:2');
emit('touchstart',event([touch(200,200)],[],{closest:()=>({})}));emit('touchend',event([],[touch(100,200)]));assert.equal(position(),'0:2');
emit('touchstart',event([touch(10,200)]));emit('touchend',event([],[touch(150,200)]));assert.equal(position(),'0:2');
assert(prevented>=4);assert(scrolls>2300);
const report={status:'PASS',chapterCount:count,checks:['All 1189 chapters forward and backward using existing step function','Book boundaries and Bible endpoints','Bottom labels and disabled controls','Swipe left next; right previous','Heading focus after navigation','Short taps, vertical scrolling, selection, multi-touch, panels, modals, cancellation and edge gestures guarded'],limitations:['Synthetic DOM/touch events; physical mobile gestures and visual layout not verified']};fs.writeFileSync('verification/chapter-navigation-test.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
