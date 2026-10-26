const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(__dirname+'/../../../dist/teaching-faq.js','utf8');
const memory=new Map();let unavailable=false;
function open(order){
 const ids={};
 class Element{constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.classList={add(){}};this.value='';this.options=[];this.events={};}append(...es){this.children.push(...es);if(this.tag==='select')this.options.push(...es);}setAttribute(){}before(){}after(){}replaceChildren(){this.children=[];}addEventListener(n,f){this.events[n]=f;}}
 for(const id of ['query','teacher','topic','sort','questions','results-count','empty','review-query','review-list','review-counts','filters'])ids[id]=new Element(['teacher','topic','sort'].includes(id)?'select':'div');
 ids.sort.value='frequency';ids.sort.options=[{value:'frequency'},{value:'alphabetical'}];ids.teacher.options=[{value:''},{value:'Arnold Murray'}];
 const q=id=>({id,rank:1,question:'Question '+id,topic:'Study',answers:[{teacher:'Arnold Murray',summary:'Answer',scripture_mentions:[],sources:[]}],source_upload_count:0,asked_count:0});
 const context={window:{GRIFFIN_FAQ:{questions:order.map(q),recordings:[],review:{available:0,partially_reviewed:0,fully_reviewed:0}},addEventListener(){},scrollTo(){}},document:{getElementById:id=>ids[id],createElement:tag=>new Element(tag),addEventListener(){}},localStorage:{getItem:k=>{if(unavailable)throw Error();return memory.get(k)||null},setItem:(k,v)=>{if(unavailable)throw Error();memory.set(k,v)}},setTimeout,clearTimeout};
 vm.runInNewContext(source,context);return ids;
}
const key='griffin-faq-reading-position-v1';
open(['a','b']);assert.equal(JSON.parse(memory.get(key)).questionId,'a');
memory.set(key,JSON.stringify({version:1,questionId:'b',page:1,filters:{query:'',teacher:'',topic:'',sort:'frequency'}}));
let ids=open(['b','a']);assert.equal(ids.questions.children[0].id,'b');assert.equal(JSON.parse(memory.get(key)).page,1); // Alphabetical sorting still puts b second.
ids=open(['0','a','b']);assert.equal(ids.questions.children[0].id,'b');assert.equal(JSON.parse(memory.get(key)).page,2);
memory.set(key,'broken JSON');assert.doesNotThrow(()=>open(['a','b']));
memory.set(key,JSON.stringify({version:1,questionId:'removed',page:99999,filters:{query:'',teacher:'bogus',topic:'',sort:'bogus'}}));ids=open(['a','b']);assert.equal(ids.questions.children[0].id,'b');
unavailable=true;assert.doesNotThrow(()=>open(['a','b']));
console.log('PASS: save, reopen, stable question identity after list changes, corrupt data, removed question, invalid filters, unavailable storage');
