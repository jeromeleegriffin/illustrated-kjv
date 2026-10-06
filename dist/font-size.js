/* Reading size is independent of scripture content and reading/quiz progress. */
(()=>{
 const KEY='illustrated-kjv-font-size-v1',MIN=16,MAX=32,DEFAULT=20;
 const decrease=document.getElementById('fontDecrease'),increase=document.getElementById('fontIncrease'),reset=document.getElementById('fontReset'),label=document.getElementById('fontSizeLabel'),status=document.getElementById('fontStatus');
 let size=DEFAULT;try{const value=Number(localStorage.getItem(KEY));if(Number.isInteger(value)&&value>=MIN&&value<=MAX)size=value}catch{}
 function apply(save=false){document.documentElement.style.setProperty('--reading-font-size',size+'px');document.documentElement.style.setProperty('--study-font-size',Math.max(14,size-6)+'px');label.textContent=size+' px';decrease.disabled=size<=MIN;increase.disabled=size>=MAX;if(save){try{localStorage.setItem(KEY,String(size));status.textContent=''}catch{status.textContent='Size changed for this visit; browser storage unavailable.'}}}
 decrease.onclick=()=>{size=Math.max(MIN,size-2);apply(true)};increase.onclick=()=>{size=Math.min(MAX,size+2);apply(true)};reset.onclick=()=>{size=DEFAULT;apply(true)};apply();
})();
