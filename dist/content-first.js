/* Presentation-only enhancement; existing IDs, listeners and stored progress are retained. */
(()=>{'use strict';
function run(){
 const name=(location.pathname.split('/').pop()||'index.html').replace(/\.html$/,'');
 const page=name==='bible'?'index':name;document.body.dataset.compactPage=page;
 function fold(nodes,label){nodes=nodes.filter(Boolean);if(!nodes.length)return;const d=document.createElement('details');d.className='compact-help';const s=document.createElement('summary');s.textContent=label;d.append(s);nodes[0].before(d);nodes.forEach(n=>d.append(n));}
 if(page==='appendices'){
  const heading=document.querySelector('header h1');if(heading)heading.textContent='Bullinger’s Appendices';
  fold([document.querySelector('header>p')],'About these studies');
  const aside=document.querySelector('main>aside');if(aside&&!document.getElementById('appendixChooser')){const d=document.createElement('details');d.id='appendixChooser';const s=document.createElement('summary');s.textContent='Choose an appendix · number or title';d.append(s);while(aside.firstChild)d.append(aside.firstChild);aside.append(d);const mq=matchMedia('(min-width:701px)');const set=()=>{d.open=mq.matches;};set();mq.addEventListener('change',set);d.addEventListener('click',e=>{if(!mq.matches&&e.target.closest('[data-appendix]')){d.open=false;document.getElementById('appendixTitle')?.scrollIntoView({block:'nearest'});}});}
  const frame=document.getElementById('appendixFrame');frame?.addEventListener('load',()=>{try{const doc=frame.contentDocument;if(!doc||doc.getElementById('compact-appendix-text'))return;const style=doc.createElement('style');style.id='compact-appendix-text';style.textContent='h1{font-size:24px!important;line-height:1.25!important;margin:8px 0!important}h2{font-size:21px!important;line-height:1.3!important}body{margin:12px!important}';doc.head.append(style);}catch(e){/* The original study remains readable if not same-origin. */}});
 }
 if(page==='teaching-review')fold([document.querySelector('.review-shell>.intro'),document.querySelector('.review-shell>.muted')],'How recording choices work');
 if(page==='teaching-faq')fold([document.querySelector('.page-tools>.notice')],'About answers and review status');
 if(page==='topical-collection')fold(Array.from(document.querySelectorAll('main>p')).slice(0,3),'Catalog details and review status');
 if(page==='trivia'){const nav=document.querySelector('.app-navigation');if(nav){const links=nav.querySelectorAll('a');if(links[0])links[0].textContent='← Bible';if(links[1]){links[1].href='https://jeromegriffin.com/bible';links[1].textContent='Study home';}}}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();
})();
