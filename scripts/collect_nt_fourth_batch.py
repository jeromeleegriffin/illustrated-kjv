"""Offline collection overlay: preserve current app; never make network requests."""
from pathlib import Path
import json,sys,datetime,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));from build_teaching import parse_all
CACHE=ROOT/'sources/teaching';data=json.loads((ROOT/'dist/bible-teaching.json').read_text());bible=json.loads((ROOT/'dist/bible.json').read_text());catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
p=CACHE/'series-attribution.json';attrs=json.loads(p.read_text())
attrs['PLGk636nvuNgSwJBaLQy3Ndce4SF7Ko1Lj']={'teacher':'Arnold Murray','source':'https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-for-2015-t30599.html','basis':'Inferred by matching official John epistle playlist sequence to the archival Arnold Murray Series 202 broadcast record: four exact opening ranges, final combined epistle lesson, and final 1 John chapter. Archive has erroneous 5:31; retain published video end 5:21. Full playback untested.','series':'202, March 2010','matchingRanges':4,'totalLessons':6}
p.write_text(json.dumps(attrs,indent=2))
report={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directYouTubeRequests':0,'books':{},'discrepancies':[]};before=json.loads(json.dumps(data))
def points(b):return [[c,v] for c,vs in enumerate(bible['books'][b]['chapters'],1) for v in range(1,len(vs)+1)]
def uncovered(b,rs):return [p for p in points(b) if not any(r['start']<=p<=r['end'] for r in rs)]
def ranges(vid,title):
 if vid=='knj97IaubCg':return [(62,[1,1],[1,13]),(63,[1,1],[1,14])]
 if vid=='XSuuktzj8u0':return [(59,[1,20],[2,15])]
 if vid=='SO44pz-Cr6I':return [(59,[3,21],[4,19])]
 if vid=='iIMTsayr7VU':return [(59,[5,1],[5,14]),(60,[1,1],[1,8])]
 return parse_all(title)
for b in range(59,64):
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
    att=attrs.get(pl['id'])
    if att:who='Arnold Murray'
    unavailable=bool(ev.get('playability') and ev['playability']!='OK')
    entry={'id':vid,'title':title,'book':b,'start':start,'end':end,'url':'https://www.youtube.com/watch?v='+vid,'teacher':who,'channel':ev.get('author') or ("The Shepherd’s Chapel Official Channel" if pl['id'].startswith('PLGk') else 'Shepherds Student'),'official':pl['id'].startswith('PLGk'),'playlist':pl['url'],'timestampSeconds':None,'playbackChecked':False,'checked':ev.get('checked'),'mappingBasis':'Published passage range in saved playlist','status':'Teacher confirmation pending' if not who else 'Attributed lesson; full playback untested'}
    if att:entry['teacherAttribution']=att
    if vid=='knj97IaubCg':entry['mappingBasis']='Both named short epistles mapped from 1:1 to their KJV endings using published END title and archival Series 202 lecture 6 context; transition timestamps untested'
    if vid in ['XSuuktzj8u0','SO44pz-Cr6I','iIMTsayr7VU']:entry['mappingBasis']='Peter book context resolved from seven-lesson playlist order and explicit parallel official playlist titles; teacher unconfirmed'
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
report['discrepancies']=[{'passage':'1 John 5:1–21','issue':'Archive says 5:31, which does not exist. Retain valid published video end 5:21.'},{'video':'knj97IaubCg','issue':'Joint second/third John title resolved with archive final-lesson context. Full playback and epistle transition timestamp untested.'},{'passage':'1 Peter and 2 Peter','issue':'Valid saved candidates cover both entire books; most lack confirmed teachers. Do not infer Arnold from channel name or generic series title.'},{'passage':'1 Peter 3:10–11','video':'ORyel4WlDb8','issue':'Short published range retained; possible typo needs later owner review.'},{'passage':'1 Peter 5:14 and 2 Peter 3:18','issue':'Alternative playlist endings omit the last verse of both Peter books; official candidate ranges retain those verses, pending teacher confirmation.'}]
for b in list(range(59))+list(range(64,66)):assert data['books'][b]==before['books'][b],b
report['scopePreserved']=True
report['addedLessonsThisBatch']=sum(r['addedLessons'] for r in report['books'].values())
report['linkedVersesAddedThisBatch']=sum(data['books'][b]['coverage']['matched']-before['books'][b]['coverage']['matched'] for b in range(59,64))
(ROOT/'dist/bible-teaching.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
p=ROOT/'verification/new-testament-progress.json';state=json.loads(p.read_text());state['updated']=report['updated'];state['activeBook']='3 John';state['nextBook']='Jude and Revelation; unresolved teachers and verse gaps remain for later owner review.'
for name,row in report['books'].items():
 state['books'][name]=row
 if row['coverage']['matched']==row['coverage']['total'] and name not in state['completedBooks']:state['completedBooks'].append(name)
p.write_text(json.dumps(state,indent=2));(ROOT/'verification/nt-fourth-five-book-collection.json').write_text(json.dumps(report,indent=2));print(json.dumps({name:{k:v for k,v in row.items() if k not in ['unmatched','candidateUnmatched']} for name,row in report['books'].items()},indent=2))
