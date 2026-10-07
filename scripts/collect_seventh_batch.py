"""Offline collection overlay: preserve current app; never make network requests."""
from pathlib import Path
import json,sys,datetime,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));from build_teaching import parse_all
CACHE=ROOT/'sources/teaching';data=json.loads((ROOT/'dist/bible-teaching.json').read_text());bible=json.loads((ROOT/'dist/bible.json').read_text());catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
p=CACHE/'series-attribution.json';attrs=json.loads(p.read_text())
samuel=next(pl for pl in catalog if pl['id']=='PLGk636nvuNgReITdZIZc5H75GBas-g69K');namedDennis=[]
for vid in samuel['videos']:
 fp=CACHE/('video-'+vid+'.json')
 if fp.exists() and 'Pastor Dennis Murray' in json.loads(fp.read_text()).get('description',''):namedDennis.append(vid)
assert len(namedDennis)==23
attrs[samuel['id']]={'teacher':'Dennis Murray','source':'https://www.youtube.com/watch?v='+namedDennis[0],'basis':'Inferred for this official Samuel sequence from 23 individually named cached official descriptions across both books. Unnamed recordings are series-level inference, not playback confirmation.','corroboratingVideos':namedDennis}
attrs['PLGk636nvuNgTPZuQTwPex6XimdPQqfMs9']={'teacher':'Dennis Murray','source':'https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-for-2015-t30599.html','basis':'Inferred by matching the official 49-lesson Kings sequence to Dennis Murray Series 210 in the 2015–2016 broadcast archives, including the explicitly titled cross-book lesson. Published video ranges retained where archive transcription differs. Full playback untested.','additionalSource':'https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-for-2016-t35853.html','series':'210, July 2011 rebroadcast','totalLessons':49}
p.write_text(json.dumps(attrs,indent=2))
publicTeachers={}
BATCH=[8,9,10,11,12]
report={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directYouTubeRequests':0,'books':{},'discrepancies':[]};before=json.loads(json.dumps(data))
def points(b):return [[c,v] for c,vs in enumerate(bible['books'][b]['chapters'],1) for v in range(1,len(vs)+1)]
def uncovered(b,rs):return [p for p in points(b) if not any(r['start']<=p<=r['end'] for r in rs)]
def ranges(vid,title):
 if vid=='bL0F1PJXovw':return [(8,[30,23],[31,13]),(9,[1,1],[1,9])]
 if vid=='JVWXCW1Cvb8':return [(10,[22,43],[22,53]),(11,[1,1],[1,18])]
 # Dated combined Chronicles playlist explicitly restarts at June 15, 2023.
 # Resolve book only, preserving every published verse endpoint and title.
 if 'I & II Chronicles' in title or 'I & I I Chronicles' in title:
  m=re.search(r'(\d+)/(\d+)/23',title)
  if not m:return []
  month,day=map(int,m.groups());prefix='I Chronicles' if (month,day)<(6,15) else 'II Chronicles'
  title=re.sub(r'I & I ?I Chronicles',prefix,title)
 return parse_all(title)
for b in BATCH:
 book=data['books'][b];candidates=[];seen=set();added=0
 for pl in catalog:
  for vid,title in pl['videos'].items():
   for bookid,start,end in ranges(vid,title):
    if bookid!=b or (vid,tuple(start),tuple(end)) in seen:continue
    seen.add((vid,tuple(start),tuple(end)))
    for c,v in (start,end):assert bible['books'][b]['chapters'][c-1][v-1],(title,c,v)
    evp=CACHE/('video-'+vid+'.json');ev=json.loads(evp.read_text()) if evp.exists() else {}
    text=title+'\n'+ev.get('description','')[:600];named=[t for t in ['Arnold Murray','Dennis Murray'] if re.search(re.escape(t),text,re.I)]
    who=named[0] if len(named)==1 and not re.search(r'Arnold\s*(?:&|and)\s*Dennis\s+Murray',text,re.I) else None
    att=attrs.get(pl['id']);direct=publicTeachers.get(vid)
    if att:who=att['teacher']
    elif direct:who=direct['teacher']
    unavailable=bool(ev.get('playability') and ev['playability']!='OK')
    entry={'id':vid,'title':title,'book':b,'start':start,'end':end,'url':'https://www.youtube.com/watch?v='+vid,'teacher':who,'channel':ev.get('author') or ("The Shepherd’s Chapel Official Channel" if pl['id'].startswith('PLGk') else 'Shepherds Student'),'official':pl['id'].startswith('PLGk'),'playlist':pl['url'],'timestampSeconds':None,'playbackChecked':False,'checked':ev.get('checked'),'mappingBasis':'Published passage range in saved playlist','status':'Teacher confirmation pending' if not who else 'Attributed lesson; full playback untested'}
    if att:entry['teacherAttribution']=att
    if direct:entry['teacherEvidence']=direct
    if unavailable:entry['status']='Saved video metadata reports unavailable; review replacement needed'
    candidates.append(entry)
    if who and not unavailable and not any(l['id']==vid and l['start']==start and l['end']==end for l in book['lessons']):
     book['lessons'].append(entry.copy());added+=1
     if pl['url'] not in book['playlists']:book['playlists'].append(pl['url'])
 book['lessons'].sort(key=lambda l:(l['teacher']!='Arnold Murray',not l['official'],l['start'],l['end'],l['id']))
 missing=uncovered(b,book['lessons']);book['coverage']={'matched':len(points(b))-len(missing),'total':len(points(b))}
 candidateMissing=uncovered(b,candidates)
 row={'coverage':book['coverage'],'linkedVideos':len({l['id'] for l in book['lessons']}),'addedLessons':added,'candidateVideos':len({l['id'] for l in candidates}),'candidateRangeCoverage':len(points(b))-len(candidateMissing),'unmatched':missing,'candidateUnmatched':candidateMissing,'teacherPendingVideos':len({r['id'] for r in candidates if r['teacher'] is None})}
 report['books'][book['name']]=row
 slug=book['name'].lower().replace(' ','-');(CACHE/(slug+'-search-candidates.json')).write_text(json.dumps({'book':book['name'],'summary':row,'candidates':candidates},indent=2))
report['discrepancies']=[{'passage':'1 Samuel 30:23–2 Samuel 1:9','issue':'Explicit combined title split into two book ranges; no timestamp guessed.'},{'passage':'1 Kings 22:43–2 Kings 1:18','issue':'Explicit combined title split into two book ranges; no timestamp guessed.'},{'passage':'1 Chronicles official candidates','issue':'Combined I & II label resolved using dated sequence restart June 15, 2023. Teachers remain unconfirmed; do not promote official candidates. Individually credited Dennis student recordings provide coverage.'},{'passage':'1 Chronicles 11:26–47','issue':'Official title ends 11:25; attributed student lesson ends 11:47. Official range not extended.'},{'passage':'Kings archival records','issue':'Archive endpoints sometimes differ from official titles; video endpoints retained. Unknown student recordings remain candidates.'}]
for b in range(66):
 if b not in BATCH:assert data['books'][b]==before['books'][b],b
report['scopePreserved']=True
import hashlib
report['kjvSha256']=hashlib.sha256((ROOT/'dist/bible.json').read_bytes()).hexdigest()
assert report['kjvSha256']==json.loads((ROOT/'verification/sixth-five-book-collection.json').read_text())['kjvSha256']
report['kjvUnchanged']=True
report['reviewShortlistLimit']=3
report['addedLessonsThisBatch']=sum(r['addedLessons'] for r in report['books'].values())
report['linkedVersesAddedThisBatch']=sum(data['books'][b]['coverage']['matched']-before['books'][b]['coverage']['matched'] for b in BATCH)
(ROOT/'dist/bible-teaching.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
p=ROOT/'verification/new-testament-progress.json';state=json.loads(p.read_text());state['updated']=report['updated'];state['activeBook']='1 Chronicles';state['nextBook']='2 Chronicles, Ezra, Nehemiah, Esther, Job';state['newTestamentCollectionPassComplete']=True
for name,row in report['books'].items():
 state['books'][name]=row
 if row['coverage']['matched']==row['coverage']['total'] and name not in state['completedBooks']:state['completedBooks'].append(name)
p.write_text(json.dumps(state,indent=2));(ROOT/'verification/seventh-five-book-collection.json').write_text(json.dumps(report,indent=2));print(json.dumps({name:{k:v for k,v in row.items() if k not in ['unmatched','candidateUnmatched']} for name,row in report['books'].items()},indent=2))
