// Illustrated KJV public assets only. Private transcripts/audio are never routed here.
const RELEASE='320bff9c70e15333e38aaa0b0d5885d0682f6ccf';
const FAQ_RELEASE='30be3d28915605f509b673cc760ad7b36558ed46';
const FAQ_PATHS=new Set(['/teaching-faq.html','/teaching-faq.js','/teaching-faq.css','/teaching-faq.json','/teaching-faq-review.json','/teaching-faq-data.js']);
const TOPICAL_RELEASE='c5e32d109510e30c22bb377626ab84540f204ca2';
const TOPICAL_PATHS=new Set(['/topical-studies.html','/topical-studies.js','/topical-studies.css','/topical-studies.json','/topical-studies-data.js','/topical-collection.html','/topical-transcript-urls.txt','/topical-grok-request.txt','/topical-batch008.json','/topical-batch008-grok-request.txt']);
const READER_RELEASE='9811a95d9b8ad918994e36aebac5130f61a77397';
const READER_PATHS=new Set(['/index.html','/app.js','/reading.js']);
const COMPACT_RELEASE='04c13f07ff07ceace5646b7546737cbbbd907932';
const COMPACT_ASSETS=new Set(['/content-first.css','/content-first.js','/app.js']);
const COMPACT_PAGES=new Set(['/index.html','/bible.html','/appendices.html','/trivia.html','/teaching-review.html','/topical-studies.html','/teaching-faq.html','/topical-collection.html']);
const ORIGIN=`https://raw.githubusercontent.com/jeromeleegriffin/illustrated-kjv/${RELEASE}/dist`;
const TYPES={html:'text/html; charset=utf-8',js:'text/javascript; charset=utf-8',css:'text/css; charset=utf-8',json:'application/json; charset=utf-8',svg:'image/svg+xml',png:'image/png',jpg:'image/jpeg',jpeg:'image/jpeg',webp:'image/webp',ico:'image/x-icon',txt:'text/plain; charset=utf-8',woff2:'font/woff2'};
export default {
 async fetch(request,env,ctx){
  const url=new URL(request.url);
  if(!['GET','HEAD'].includes(request.method))return new Response('Method Not Allowed',{status:405,headers:{Allow:'GET, HEAD'}});
  if(url.pathname==='/health')return Response.json({app:'Illustrated KJV',release:RELEASE,faq:'frequency-ranked-reviewed-passages',faq_release:FAQ_RELEASE,private_transcripts_published:false});
  let path;
  try{path=decodeURIComponent(url.pathname);}catch{return new Response('Bad path',{status:400});}
  if(path==='/')path='/index.html';
  if(!/^\/[A-Za-z0-9_./-]+$/.test(path)||path.includes('..')||path.split('/').some(s=>s.startsWith('.')))return new Response('Not Found',{status:404});
  const ext=path.split('.').pop().toLowerCase();if(!TYPES[ext])return new Response('Not Found',{status:404});
  const assetRelease=COMPACT_ASSETS.has(path)?COMPACT_RELEASE:FAQ_PATHS.has(path)?FAQ_RELEASE:TOPICAL_PATHS.has(path)?TOPICAL_RELEASE:READER_PATHS.has(path)?READER_RELEASE:RELEASE;
  const assetOrigin=(COMPACT_ASSETS.has(path)||FAQ_PATHS.has(path)||TOPICAL_PATHS.has(path)||READER_PATHS.has(path))?`https://raw.githubusercontent.com/jeromeleegriffin/illustrated-kjv/${assetRelease}/dist`:ORIGIN;
  const key=new Request(url.origin+path+'?release='+assetRelease);
  try{
   const cache=caches.default;let response=await cache.match(key);
   if(!response){
    const upstream=await fetch(assetOrigin+path,{headers:{'Accept':'*/*'},redirect:'manual'});
    if(!upstream.ok)return new Response(upstream.status===404?'Not Found':'The Bible files are temporarily unavailable. Please try again.',{status:upstream.status===404?404:503,headers:{'Cache-Control':'no-store'}});
    const headers=new Headers({'Content-Type':TYPES[ext],'Cache-Control':ext==='html'?'no-store':'public, max-age=300, s-maxage=3600','X-Content-Type-Options':'nosniff','X-Bible-Release':assetRelease,'Referrer-Policy':'strict-origin-when-cross-origin'});
    response=new Response(upstream.body,{status:200,headers});
    ctx.waitUntil(cache.put(key,response.clone()));
   }
   if(request.method==='GET'&&COMPACT_PAGES.has(path)&&response.ok){const page=path==='/bible.html'?'index':path.slice(1,-5);response=new HTMLRewriter().on('head',{element(e){e.append('<link rel="stylesheet" href="/content-first.css?v='+COMPACT_RELEASE+'"><script defer src="/content-first.js?v='+COMPACT_RELEASE+'"></script>',{html:true});}}).on('script[src]',{element(e){if((e.getAttribute('src')||'').split('?')[0].replace(/^\.\//,'/')==='/app.js')e.setAttribute('src','/app.js?v='+COMPACT_RELEASE);}}).on('body',{element(e){e.setAttribute('data-compact-page',page);}}).transform(response);}
   return request.method==='HEAD'?new Response(null,{status:response.status,headers:response.headers}):response;
  }catch(error){console.error(JSON.stringify({event:'bible_asset_unavailable',path,reason:error.name,message:error.message}));return new Response('The Bible is temporarily unavailable. Please try again.',{status:503,headers:{'Cache-Control':'no-store'}});}
 }
};
