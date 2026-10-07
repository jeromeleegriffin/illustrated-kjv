"""Collect published playlist ranges and per-video teacher evidence. No guessed links."""
import concurrent.futures as cf
import json, re, urllib.request, urllib.error, pathlib, datetime, threading

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / 'sources' / 'teaching'
CACHE.mkdir(parents=True, exist_ok=True)
BLOCKED=threading.Event()
def walk(x, key):
    if isinstance(x, dict):
        if key in x: yield x[key]
        for v in x.values(): yield from walk(v, key)
    elif isinstance(x, list):
        for v in x: yield from walk(v, key)
def get(url):
    if BLOCKED.is_set(): raise RuntimeError('Collection paused after rate limit; no further requests sent')
    try:return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=35).read().decode()
    except urllib.error.HTTPError as e:
        if e.code==429:BLOCKED.set()
        raise
def initial(s, name):
    m = re.search(r'(?:var )?' + name + r'\s*=\s*', s)
    if not m: raise ValueError('Missing '+name)
    return json.JSONDecoder().raw_decode(s[m.end():])[0]
def context(s):
    m = re.search(r'"INNERTUBE_CONTEXT":', s)
    return json.JSONDecoder().raw_decode(s[m.end():])[0]
def pages(s):
    d=initial(s,'ytInitialData');ctx=context(s);seen=set()
    for _ in range(30):
        yield d
        items=list(walk(d,'continuationItemRenderer'))
        if not items: return
        token=items[0]['continuationEndpoint']['continuationCommand']['token']
        if token in seen: return
        seen.add(token)
        req=urllib.request.Request('https://www.youtube.com/youtubei/v1/browse',json.dumps({'context':ctx,'continuation':token}).encode(),{'Content-Type':'application/json'})
        d=json.load(urllib.request.urlopen(req,timeout=35))
    raise ValueError('Pagination limit reached')
def playlists():
    file=CACHE/'playlists.json'
    if file.exists(): return json.loads(file.read_text())
    out={}
    for d in pages(get('https://www.youtube.com/@TheShepherdsChapel/playlists')):
        for z in walk(d,'lockupViewModel'):
            pid=z.get('contentId','')
            if pid.startswith('PLGk'):
                out[pid]=z['metadata']['lockupMetadataViewModel']['title']['content']
    file.write_text(json.dumps(out,indent=2));return out
def playlist(item):
    pid,title=item;file=CACHE/(pid+'.json')
    if file.exists(): return json.loads(file.read_text())
    out={}
    for d in pages(get('https://www.youtube.com/playlist?list='+pid)):
        for z in walk(d,'lockupViewModel'):
            vid=z.get('contentId','')
            if len(vid)==11 and z.get('contentType')=='LOCKUP_CONTENT_TYPE_VIDEO':
                out[vid]=z['metadata']['lockupMetadataViewModel']['title']['content']
        for z in walk(d,'playlistVideoRenderer'):
            if 'videoId' in z: out[z['videoId']]=''.join(t.get('text','') for t in z.get('title',{}).get('runs',[]))
    result={'id':pid,'title':title,'videos':out,'url':'https://www.youtube.com/playlist?list='+pid}
    file.write_text(json.dumps(result,indent=2));return result
def video(vid):
    file=CACHE/('video-'+vid+'.json')
    if file.exists(): return json.loads(file.read_text())
    try:
        d=initial(get('https://www.youtube.com/watch?v='+vid),'ytInitialPlayerResponse')
        z=d.get('videoDetails',{});desc=z.get('shortDescription','')
        result={'id':vid,'title':z.get('title'),'author':z.get('author'),'channelId':z.get('channelId'),'description':desc,'playability':d.get('playabilityStatus',{}).get('status'),'checked':datetime.date.today().isoformat()}
    except Exception as e: result={'id':vid,'error':str(e)}
    file.write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
    catalog=playlists();print('Playlists',len(catalog),flush=True)
    excluded=re.compile(r'Sunday|Pastor |Documentaries|Quiz|Fellowship|NEW STUDENTS|Communion|Passover|Single Studies|Christmas|Weekly Special|Welcome|Current Series',re.I)
    selected=[x for x in catalog.items() if not excluded.search(x[1])]
    results=[]
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        for r in pool.map(playlist,selected):
            results.append(r);print(r['title'],len(r['videos']),flush=True)
    (CACHE/'catalog.json').write_text(json.dumps(results,indent=2))
    vids={vid for r in results for vid in r['videos']}
    with cf.ThreadPoolExecutor(max_workers=2) as pool:
        for n,r in enumerate(pool.map(video,sorted(vids)),1):
            if n%50==0:print('Video evidence',n,'/',len(vids),flush=True)
    print('Finished',len(vids),flush=True)
