"""Resume NT in book order. Serial, paced requests; preserve each verified addition."""
import sys,json,pathlib,re,time,datetime,urllib.request,urllib.error,collections
ROOT=pathlib.Path(__file__).resolve().parents[1];CACHE=ROOT/'sources/teaching'
sys.path.insert(0,str(ROOT/'scripts'));from build_teaching import parse_all
DATA=ROOT/'dist/bible-teaching.json';data=json.loads(DATA.read_text());bible=json.loads((ROOT/'dist/bible.json').read_text())
catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
if (CACHE/'nt-extra-catalog.json').exists():catalog+=json.loads((CACHE/'nt-extra-catalog.json').read_text())
STATE=ROOT/'verification/new-testament-progress.json'
progress={'teacherPolicy':'Arnold Murray first; Dennis Murray fallback per verse.','completedBooks':[],'books':{},'networkStopped':False}
if STATE.exists():progress=json.loads(STATE.read_text())
last_request=0;requested=set();stop=('--network' not in sys.argv or progress.get('networkStopped',False))
attributions=json.loads((CACHE/'series-attribution.json').read_text()) if (CACHE/'series-attribution.json').exists() else {}
def teacher(ev):
    text=(ev.get('title') or '')+'\n'+ev.get('description','')[:600]
    if re.search(r'Arnold\s*(?:&|and)\s*Dennis\s+Murray',text,re.I):return None
    found=[t for t in ['Arnold Murray','Dennis Murray'] if re.search(re.escape(t),text,re.I)]
    return found[0] if len(found)==1 else None
def cached(vid):
    p=CACHE/('video-'+vid+'.json')
    return json.loads(p.read_text()) if p.exists() else None
def points(b):return [[c,v] for c,vs in enumerate(bible['books'][b]['chapters'],1) for v in range(1,len(vs)+1)]
def gaps(b,who=None):return [p for p in points(b) if not any(l['start']<=p<=l['end'] and (who is None or l['teacher']==who) for l in data['books'][b]['lessons'])]
def add(b,ev,pl):
    attribution=attributions.get(pl['id'])
    who=teacher(ev) or (attribution['teacher'] if attribution and ev.get('channelId')=='UCwX0AEx-qIhQ9kgtlNhyIXw' else None)
    if ev.get('playability')!='OK' or not who:return False
    added=False
    for book,start,end in parse_all(ev.get('title') or '') or parse_all(ev.get('description','')[:600]):
        if book!=b:continue
        dest=data['books'][b]
        if any(l['id']==ev['id'] and l['start']==start and l['end']==end for l in dest['lessons']):continue
        dest['lessons'].append({'id':ev['id'],'title':ev['title'],'book':b,'start':start,'end':end,'url':'https://www.youtube.com/watch?v='+ev['id'],'teacher':who,'channel':ev.get('author'),'official':ev.get('channelId')=='UCwX0AEx-qIhQ9kgtlNhyIXw','playlist':pl['url'],'timestampSeconds':None,'checked':ev.get('checked'),'mappingBasis':'Published passage range'})
        if attribution:
            dest['lessons'][-1]['teacherAttribution']=attribution
        if pl['url'] not in dest['playlists']:dest['playlists'].append(pl['url'])
        added=True;print('LINK',dest['name'],who,ev['title'],flush=True)
    return added
def save(b):
    book=data['books'][b];book['lessons'].sort(key=lambda l:(l['teacher']!='Arnold Murray',not l['official'],l['start'],l['end'],l['id']))
    total=len(points(b));missing=gaps(b);book['coverage']={'matched':total-len(missing),'total':total}
    report={'coverage':book['coverage'],'videos':len({l['id'] for l in book['lessons']}),'unmatched':missing,'arnoldVerses':total-len(gaps(b,'Arnold Murray')),'dennisFallbackVerses':sum(any(l['teacher']=='Dennis Murray' and l['start']<=p<=l['end'] for l in book['lessons']) for p in gaps(b,'Arnold Murray'))}
    progress['books'][book['name']]=report
    progress['updated']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    if not missing and book['name'] not in progress['completedBooks']:progress['completedBooks'].append(book['name'])
    data['revision']='009';data['teacherPolicy']=progress['teacherPolicy'];DATA.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')));STATE.write_text(json.dumps(progress,indent=2))
def fetch(vid):
    global last_request,stop
    delay=10-(time.monotonic()-last_request)
    if delay>0:time.sleep(delay)
    last_request=time.monotonic();requested.add(vid)
    try:
        s=urllib.request.urlopen(urllib.request.Request('https://www.youtube.com/watch?v='+vid,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read().decode();m=re.search(r'(?:var )?ytInitialPlayerResponse\s*=\s*',s)
        if not m:raise ValueError('Video metadata unavailable')
        d=json.JSONDecoder().raw_decode(s[m.end():])[0];v=d.get('videoDetails',{})
        ev={'id':vid,'title':v.get('title'),'author':v.get('author'),'channelId':v.get('channelId'),'description':v.get('shortDescription',''),'playability':d.get('playabilityStatus',{}).get('status'),'checked':datetime.date.today().isoformat()}
        (CACHE/('video-'+vid+'.json')).write_text(json.dumps(ev,indent=2));return ev
    except urllib.error.HTTPError as e:
        print('NETWORK STOP',e.code,vid,flush=True);stop=True;progress['networkStopped']=True;progress['blocker']='HTTP '+str(e.code)+'; no retry';return None
    except Exception as e:
        print('UNCONFIRMED',vid,str(e),flush=True)
        if '403' in str(e) or '429' in str(e):stop=True;progress['networkStopped']=True;progress['blocker']=str(e)+'; no retry'
        return None
# Matthew is already complete. Continue from Mark through Revelation, in canonical order.
book_args=[a for a in sys.argv[1:] if a.isdigit()]
for b in range(int(book_args[0]) if book_args else 40,int(book_args[1])+1 if len(book_args)>1 else 66):
    name=data['books'][b]['name'];print('BOOK',name,flush=True)
    candidates=[];seen=set()
    for pl in catalog:
        for vid,title in pl['videos'].items():
            ranges=[(start,end) for book,start,end in parse_all(title) if book==b]
            if ranges and vid not in seen:candidates.append((vid,title,pl,ranges));seen.add(vid)
    for vid,title,pl,ranges in candidates:
        ev=cached(vid)
        if ev and 'error' not in ev:add(b,ev,pl)
    save(b)
    # Prefer sources with confirmed Arnold metadata; some official series omit the teacher.
    source_scores=collections.defaultdict(int)
    for vid,title,pl,ranges in candidates:
        ev=cached(vid)
        if ev and (teacher(ev)=='Arnold Murray' or attributions.get(pl['id'],{}).get('teacher')=='Arnold Murray'):source_scores[pl['id']]+=1
    candidates.sort(key=lambda x:(-source_scores[x[2]['id']],x[2]['id'].startswith('PLGk'),x[3][0][0]))
    # First seek Arnold for uncovered-by-Arnold passages. Dennis remains a fallback.
    for vid,title,pl,ranges in candidates:
        if stop or not gaps(b,'Arnold Murray'):break
        ev=cached(vid)
        if ev and 'error' not in ev:continue
        if not any(start<=p<=end for start,end in ranges for p in gaps(b,'Arnold Murray')):continue
        if vid in requested:continue
        ev=fetch(vid)
        if ev:add(b,ev,pl)
        save(b);print('PROGRESS',name,data['books'][b]['coverage'],flush=True)
    # Remaining sources can provide named Dennis matches if Arnold could not be verified.
    for vid,title,pl,ranges in candidates:
        if stop or not gaps(b):break
        if vid in requested:continue
        ev=cached(vid)
        if ev and 'error' not in ev:continue
        if not any(start<=p<=end for start,end in ranges for p in gaps(b)):continue
        ev=fetch(vid)
        if ev:add(b,ev,pl)
        save(b)
    save(b);print('BOOK RESULT',name,progress['books'][name]['coverage'],flush=True)
    if gaps(b):
        progress.setdefault('blocker','Book remains incomplete; preserve canonical order before advancing.');save(b);break
    if stop:print('Network paused; remaining books use saved evidence only.',flush=True)
print('FINISHED PASS',progress['completedBooks'],flush=True)
