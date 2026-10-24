// Illustrated KJV public assets only. Private transcripts/audio are never routed here.
const RELEASE='9d798a5172b52b003c255d6122b29387e9fe4dab';
const ORIGIN=`https://raw.githubusercontent.com/jeromeleegriffin/illustrated-kjv/${RELEASE}/dist`;
const TYPES={html:'text/html; charset=utf-8',js:'text/javascript; charset=utf-8',css:'text/css; charset=utf-8',json:'application/json; charset=utf-8',svg:'image/svg+xml',png:'image/png',jpg:'image/jpeg',jpeg:'image/jpeg',webp:'image/webp',ico:'image/x-icon',txt:'text/plain; charset=utf-8',woff2:'font/woff2'};
export default {
 async fetch(request,env,ctx){
  const url=new URL(request.url);
  if(!['GET','HEAD'].includes(request.method))return new Response('Method Not Allowed',{status:405,headers:{Allow:'GET, HEAD'}});
  if(url.pathname==='/health')return Response.json({app:'Illustrated KJV',release:RELEASE,faq:'initial-seven-answers',private_transcripts_published:false});
  let path;
  try{path=decodeURIComponent(url.pathname);}catch{return new Response('Bad path',{status:400});}
  if(path==='/')path='/index.html';
  if(!/^\/[A-Za-z0-9_./-]+$/.test(path)||path.includes('..')||path.split('/').some(s=>s.startsWith('.')))return new Response('Not Found',{status:404});
  const ext=path.split('.').pop().toLowerCase();if(!TYPES[ext])return new Response('Not Found',{status:404});
  const key=new Request(url.origin+path+'?release='+RELEASE);
  try{
   const cache=caches.default;let response=await cache.match(key);
   if(!response){
    const upstream=await fetch(ORIGIN+path,{headers:{'Accept':'*/*'},redirect:'manual'});
    if(!upstream.ok)return new Response(upstream.status===404?'Not Found':'The Bible files are temporarily unavailable. Please try again.',{status:upstream.status===404?404:503,headers:{'Cache-Control':'no-store'}});
    const headers=new Headers({'Content-Type':TYPES[ext],'Cache-Control':'public, max-age=300, s-maxage=3600','X-Content-Type-Options':'nosniff','X-Bible-Release':RELEASE,'Referrer-Policy':'strict-origin-when-cross-origin'});
    response=new Response(upstream.body,{status:200,headers});
    ctx.waitUntil(cache.put(key,response.clone()));
   }
   return request.method==='HEAD'?new Response(null,{status:response.status,headers:response.headers}):response;
  }catch(error){console.error(JSON.stringify({event:'bible_asset_unavailable',path,reason:error.name,message:error.message}));return new Response('The Bible is temporarily unavailable. Please try again.',{status:503,headers:{'Cache-Control':'no-store'}});}
 }
};
