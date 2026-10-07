"""Offline collection overlay: preserve current app; never make network requests."""
from pathlib import Path
import json,sys,datetime,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));from build_teaching import parse_all
CACHE=ROOT/'sources/teaching';data=json.loads((ROOT/'dist/bible-teaching.json').read_text());bible=json.loads((ROOT/'dist/bible.json').read_text());catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
p=CACHE/'series-attribution.json';attrs=json.loads(p.read_text())
attrs['PLGk636nvuNgRWPRzrKc2I7Yo9Qe512oVp']={'teacher':'Dennis Murray','source':'https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-for-2016-t35853.html','basis':'Inferred by matching all eight official Ezra lesson ranges to the December 2016 Series 142 broadcast record explicitly naming Dennis Murray. Playback untested.','series':'142, June 2012 rebroadcast','matchingRanges':8,'totalLessons':8}
attrs['PLGk636nvuNgTsXzEqaNPdoeiqIzRHSM7F']={'teacher':'Dennis Murray','source':'https://www.tapatalk.com/groups/theseason/new-shepherds-daily-broadcast-record-for-2017-t42682.html','basis':'Inferred by matching all nine official Nehemiah lesson ranges to the January 2017 broadcast record naming Dennis Murray, corroborated by seven individually named cached official descriptions. Archive inconsistently prints series 255/225 and revision year; do not normalize those errors into video titles. Playback untested.','matchingRanges':9,'totalLessons':9}
attrs['PLGk636nvuNgRqdqzEmB7fDvALJ6RbPKDv']={'teacher':'Arnold Murray','source':'https://www.tapatalk.com/groups/theseason/new-shepherds-daily-broadcast-record-for-2017-t42682.html','basis':'Inferred by matching the official 25-lesson Job sequence to the February–March 2017 Arnold Murray Series 187 record. Twenty-four ranges match; archive lesson 14 erroneously starts chapter 22 versus video chapter 27. Published video endpoints retained; full playback untested.','series':'187, May 1999 rebroadcast','matchingRanges':24,'totalLessons':25}
pl=next(p for p in catalog if p['id']=='PLiA6kuKpn0D1xjUIgzIt82iwWPEh6UUx8')
for vid in pl['videos']:assert 'Dennis Murray' in json.loads((CACHE/('video-'+vid+'.json')).read_text())['description']
attrs['PLGk636nvuNgQ6m-9LT1PzyqrxK3DfLEb9']={'teacher':'Dennis Murray','bookScope':[13],'source':'https://www.tapatalk.com/groups/theseason/shepherd-s-chapel-daily-broadcast-record-for-2014-t23147.html','basis':'Series-level inference for 2 Chronicles only: matches the Dennis Series 105 archival sequence and the parallel student playlist with 24 individually credited Dennis descriptions. Published ranges differ at several archive endpoints; retain video titles. First/second book resolved by dated June 15, 2023 sequence restart. Full playback untested.','corroboratingPlaylist':pl['url'],'corroboratingVideos':list(pl['videos']),'series':'105, 2 Chronicles portion'}
p.write_text(json.dumps(attrs,indent=2))
publicTeachers={}
BATCH=[13,14,15,16,17]
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
    if att and att.get('bookScope') and b not in att['bookScope']:att=None
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
report['discrepancies']=[{'passage':'Esther, all 167 verses','issue':'Six saved book/part candidates lack a valid published passage range and confirmed individual teacher credit; preserve for later review without verse-coverage claims.'},{'passage':'2 Chronicles 22:10–24:5 and chapters 30–36','issue':'Student playlist missing lesson 19 and closing chapters. Official series-inferred Dennis titles supply these ranges; no student endpoints extended.'},{'passage':'Job 27:7–28:28','issue':'Archive erroneously starts chapter 22; published video starts 27:7, retained.'},{'passage':'Nehemiah alternate final title','issue':'oiqm1TdUMvo says 13:32, but KJV chapter ends 13:31. Invalid title not clamped or promoted; official valid END supplies ending.'},{'passage':'Ezra alternate ending','issue':'Student END title explicitly ends 10:20 while KJV ends 10:44; retain published numerical endpoint. Official lesson supplies remainder.'}]
# Save unparsed book-level candidates separately, including Esther and invalid endpoints.
for b in BATCH:
 file=CACHE/(data['books'][b]['name'].lower().replace(' ','-')+'-search-candidates.json');queue=json.loads(file.read_text());unmapped=[]
 for pl in catalog:
  for vid,title in pl['videos'].items():
   if data['books'][b]['name'].lower() in title.lower() and not ranges(vid,title):unmapped.append({'id':vid,'title':title,'url':'https://www.youtube.com/watch?v='+vid,'playlist':pl['url'],'teacher':None,'playbackChecked':False,'status':'Published verse range missing or invalid; teacher confirmation also required'})
 queue['unmappedCandidates']=unmapped;queue['summary']['unmappedCandidateVideos']=len({r['id'] for r in unmapped});file.write_text(json.dumps(queue,indent=2));report['books'][data['books'][b]['name']]['unmappedCandidateVideos']=len({r['id'] for r in unmapped})
for b in range(66):
 if b not in BATCH:assert data['books'][b]==before['books'][b],b
report['scopePreserved']=True
import hashlib
report['kjvSha256']=hashlib.sha256((ROOT/'dist/bible.json').read_bytes()).hexdigest()
assert report['kjvSha256']==json.loads((ROOT/'verification/seventh-five-book-collection.json').read_text())['kjvSha256']
report['kjvUnchanged']=True
report['reviewShortlistLimit']=3
report['addedLessonsThisBatch']=sum(r['addedLessons'] for r in report['books'].values())
report['linkedVersesAddedThisBatch']=sum(data['books'][b]['coverage']['matched']-before['books'][b]['coverage']['matched'] for b in BATCH)
(ROOT/'dist/bible-teaching.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
p=ROOT/'verification/new-testament-progress.json';state=json.loads(p.read_text());state['updated']=report['updated'];state['activeBook']='Job';state['nextBook']='Psalms, Proverbs, Ecclesiastes, Song of Solomon, Isaiah';state['newTestamentCollectionPassComplete']=True
for name,row in report['books'].items():
 state['books'][name]=row
 if row['coverage']['matched']==row['coverage']['total'] and name not in state['completedBooks']:state['completedBooks'].append(name)
p.write_text(json.dumps(state,indent=2));(ROOT/'verification/eighth-five-book-collection.json').write_text(json.dumps(report,indent=2));print(json.dumps({name:{k:v for k,v in row.items() if k not in ['unmatched','candidateUnmatched']} for name,row in report['books'].items()},indent=2))
