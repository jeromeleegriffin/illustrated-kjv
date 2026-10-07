"""Targeted, serial Matthew verification; stop on a rate limit, never bulk retry."""
import sys,json,pathlib,re,time,datetime,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1];CACHE=ROOT/'sources/teaching'
sys.path.insert(0,str(ROOT/'scripts'));from build_teaching import parse_all
data=json.loads((ROOT/'dist/bible-teaching.json').read_text());book=data['books'][39]
catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
playlists=[p for p in catalog if 'Matthew' in p['title']]
def matches(c,v,teacher=None):return any(l['start']<=[c,v]<=l['end'] and (teacher is None or l['teacher']==teacher) for l in book['lessons'])
bible=json.loads((ROOT/'dist/bible.json').read_text())
def gaps(teacher=None):return [[c,v] for c,vs in enumerate(bible['books'][39]['chapters'],1) for v in range(1,len(vs)+1) if not matches(c,v,teacher)]
def add(ev,pl):
    text=(ev.get('title') or '')+'\n'+ev.get('description','')[:600]
    teachers=[t for t in ['Arnold Murray','Dennis Murray'] if re.search(re.escape(t),text,re.I)]
    if ev.get('playability')!='OK' or len(teachers)!=1:return
    teacher=teachers[0]
    ranges=parse_all(ev.get('title') or '') or parse_all(ev.get('description','')[:600])
    for b,start,end in ranges:
        if b!=39:continue
        if any(l['id']==ev['id'] and l['start']==start and l['end']==end for l in book['lessons']):continue
        lesson={'id':ev['id'],'title':ev['title'],'book':39,'start':start,'end':end,'url':'https://www.youtube.com/watch?v='+ev['id'],'teacher':teacher,'channel':ev.get('author'),'official':ev.get('channelId')=='UCwX0AEx-qIhQ9kgtlNhyIXw','playlist':pl['url'],'timestampSeconds':None,'checked':ev.get('checked'),'mappingBasis':'Published passage range'}
        book['lessons'].append(lesson)
        if pl['url'] not in book['playlists']:book['playlists'].append(pl['url'])
        print('Verified',teacher,ev['title'],flush=True)
def save():
    book['lessons'].sort(key=lambda l:(l['teacher']!='Arnold Murray',not l['official'],l['start'],l['end'],l['id']))
    book['coverage']={'matched':1071-len(gaps()),'total':1071}
    data['revision']='008';data['teacherPolicy']='Arnold Murray first; Dennis Murray fallback per verse.'
    (ROOT/'dist/bible-teaching.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
    report={'book':'Matthew','coverage':book['coverage'],'unmatched':gaps(),'lessons':len(book['lessons']),'teacherPolicy':data['teacherPolicy'],'checked':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (ROOT/'verification/matthew-coverage.json').write_text(json.dumps(report,indent=2))
for pl in playlists:
    for vid in pl['videos']:
        p=CACHE/('video-'+vid+'.json')
        if p.exists():
            ev=json.loads(p.read_text())
            if 'error' not in ev:add(ev,pl)
save();calls=0
for pl in playlists:
    for vid,title in pl['videos'].items():
        ranges=[r for r in parse_all(title) if r[0]==39]
        required=gaps('Arnold Murray') if pl['id'].startswith('PLGk') else gaps()
        if not any(any(start<=g<=end for g in required) for _,start,end in ranges):continue
        p=CACHE/('video-'+vid+'.json')
        if p.exists() and 'error' not in json.loads(p.read_text()):continue
        if calls:time.sleep(5)
        calls+=1
        try:
            s=urllib.request.urlopen(urllib.request.Request('https://www.youtube.com/watch?v='+vid,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read().decode()
            m=re.search(r'(?:var )?ytInitialPlayerResponse\s*=\s*',s)
            if not m:raise ValueError('Metadata unavailable')
            d=json.JSONDecoder().raw_decode(s[m.end():])[0];v=d.get('videoDetails',{})
            ev={'id':vid,'title':v.get('title'),'author':v.get('author'),'channelId':v.get('channelId'),'description':v.get('shortDescription',''),'playability':d.get('playabilityStatus',{}).get('status'),'checked':datetime.date.today().isoformat()}
            p.write_text(json.dumps(ev,indent=2));add(ev,pl);save();print('Matthew linked',book['coverage']['matched'],'/1071',flush=True)
        except urllib.error.HTTPError as e:
            print('Stopped HTTP',e.code,'— no retry',flush=True);save();sys.exit(2)
        except Exception as e:
            print('Could not confirm',vid,type(e).__name__,str(e),flush=True)
        if not gaps():break
    if not gaps():break
save();print('Matthew final',book['coverage'],'remaining',len(gaps()),flush=True)
