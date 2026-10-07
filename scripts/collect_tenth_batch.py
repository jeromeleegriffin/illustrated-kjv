"""Offline collection overlay: preserve current app; never make network requests."""
from pathlib import Path
import json,sys,datetime,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));from build_teaching import parse_all
CACHE=ROOT/'sources/teaching';data=json.loads((ROOT/'dist/bible-teaching.json').read_text());bible=json.loads((ROOT/'dist/bible.json').read_text());catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
p=CACHE/'series-attribution.json';attrs=json.loads(p.read_text())
attrs['PLGk636nvuNgS830lZaaKbCW5SkQWwyECv']={'teacher': 'Arnold Murray', 'source': 'https://www.tapatalk.com/groups/theseason/1-3-24-the-book-of-jeremiah-by-pastor-arnold-murra-t63958.html', 'basis': 'Series-level inference: public record explicitly names Arnold Murray and lists 48 matching official Jeremiah lesson ranges. Saved official playlist also includes penultimate 51:52–52:17 lesson in same series, absent from that public list; retain its published title. Full playback untested.', 'matchingRanges': 48, 'totalLessons': 49, 'corroboratingSource': 'https://www.tapatalk.com/groups/theseason/book-of-jeremiah-by-pastor-arnold-murray-cd-30173-t55581.html'}
attrs['PLGk636nvuNgSEnf6nvUattQiKk7jkgVOk']={'teacher': 'Arnold Murray', 'source': 'https://www.tapatalk.com/groups/theseason/lamentations-by-pastor-arnold-murray-t56283.html', 'basis': 'Series-level inference: public January 2020 record explicitly names Arnold Murray and matches all five official Lamentations ranges. Archive has mixed 2019/2020 dates; do not use these as upload dates. Full playback untested.', 'matchingRanges': 5, 'totalLessons': 5}
attrs['PLGk636nvuNgRV-97CaSB9GQXXrmT7uoJB']={'teacher': 'Arnold Murray', 'source': 'https://www.tapatalk.com/groups/theseason/whole-book-of-ezekiel-series-131-by-pastor-arnold--t39695.html', 'basis': 'Series-level inference: public Ezekiel Series 131 record explicitly names Arnold Murray and matches official sequence; seventeen cached official descriptions individually name Arnold. Archive has omissions and transcription errors including 7:22–18:23 and 32:11 start. Published video titles retained. Full playback untested.', 'series': '131, Ezekiel', 'totalLessons': 36, 'individuallyNamedCachedLessons': 17}
attrs['PLGk636nvuNgSdUMOHMc82P2J8sYwya_5Z']={'teacher': 'Arnold Murray', 'source': 'https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-for-2015-t30599.html', 'basis': 'Series-level inference: August–September 2015 record explicitly names Arnold Murray for Daniel Series 116 and matches all thirteen official lesson ranges. Full playback untested.', 'series': '116, May 2010 rebroadcast', 'matchingRanges': 13, 'totalLessons': 13}
p.write_text(json.dumps(attrs,indent=2))
publicTeachers={}
BATCH=[23,24,25,26,27]
report={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directYouTubeRequests':0,'books':{},'discrepancies':[]};before=json.loads(json.dumps(data))
def points(b):return [[c,v] for c,vs in enumerate(bible['books'][b]['chapters'],1) for v in range(1,len(vs)+1)]
def uncovered(b,rs):return [p for p in points(b) if not any(r['start']<=p<=r['end'] for r in rs)]
def ranges(vid,title):return parse_all(title)
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
report['discrepancies']=[{'passage': 'Jeremiah 51:52–52:17', 'issue': 'Saved penultimate official lesson absent from public 2024 list. Teacher visibly inferred at series level; range taken only from original saved title. Overlap 52:8–17 with final lesson retained.'}, {'passage': 'Jeremiah alternate series', 'issue': 'Student playlist stops at chapter 40 despite END label. Do not extend numerical 40:16 endpoint or assume coverage to chapter 52; teacher unconfirmed.'}, {'passage': 'Lamentations alternate first lesson', 'issue': 'Individually Arnold-credited 0tbFtVKya2U has malformed title -1:1 1:17; retain unmapped for review, no parser guess. Official first lesson supplies passage.'}, {'passage': 'Lamentations alternate final lesson', 'issue': 'Singular Lamentation title retained unmapped by parser; official ending supplies chapter 5.'}, {'passage': 'Ezekiel archive', 'issue': 'Archive 7:22–18:23 and 32:11 start conflict with official published ranges; archive also omits 20:13–38. Retain video titles, corroborated by seventeen individually named descriptions.'}, {'passage': 'Hosea', 'issue': 'Existing fourteen attributed links already cover all 197 verses; preserve them and retained alternatives without needless replacements.'}]
# Save unparsed book-level candidates separately, including Esther and invalid endpoints.
for b in BATCH:
 file=CACHE/(data['books'][b]['name'].lower().replace(' ','-')+'-search-candidates.json');queue=json.loads(file.read_text());unmapped=[]
 for pl in catalog:
  for vid,title in pl['videos'].items():
   if (data['books'][b]['name'].lower() in title.lower() or (b==24 and 'lamentation' in title.lower())) and not ranges(vid,title):unmapped.append({'id':vid,'title':title,'url':'https://www.youtube.com/watch?v='+vid,'playlist':pl['url'],'teacher':None,'playbackChecked':False,'status':'Published verse range missing or invalid; teacher confirmation also required'})

 for item in unmapped:
  if item['id']=='0tbFtVKya2U':item['teacher']='Arnold Murray';item['status']='Cached description names Arnold; malformed published range requires review'
 queue['unmappedCandidates']=unmapped;queue['summary']['unmappedCandidateVideos']=len({r['id'] for r in unmapped});file.write_text(json.dumps(queue,indent=2));report['books'][data['books'][b]['name']]['unmappedCandidateVideos']=len({r['id'] for r in unmapped})
for b in range(66):
 if b not in BATCH:assert data['books'][b]==before['books'][b],b
report['scopePreserved']=True
import hashlib
report['kjvSha256']=hashlib.sha256((ROOT/'dist/bible.json').read_bytes()).hexdigest()
assert report['kjvSha256']==json.loads((ROOT/'verification/ninth-five-book-collection.json').read_text())['kjvSha256']
report['kjvUnchanged']=True
report['reviewShortlistLimit']=3
report['addedLessonsThisBatch']=sum(r['addedLessons'] for r in report['books'].values())
report['linkedVersesAddedThisBatch']=sum(data['books'][b]['coverage']['matched']-before['books'][b]['coverage']['matched'] for b in BATCH)
(ROOT/'dist/bible-teaching.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
p=ROOT/'verification/new-testament-progress.json';state=json.loads(p.read_text());state['updated']=report['updated'];state['activeBook']='Hosea';state['nextBook']='Joel, Amos, Obadiah, Jonah, Micah';state['newTestamentCollectionPassComplete']=True
for name,row in report['books'].items():
 state['books'][name]=row
 if row['coverage']['matched']==row['coverage']['total'] and name not in state['completedBooks']:state['completedBooks'].append(name)
p.write_text(json.dumps(state,indent=2));(ROOT/'verification/tenth-five-book-collection.json').write_text(json.dumps(report,indent=2));print(json.dumps({name:{k:v for k,v in row.items() if k not in ['unmatched','candidateUnmatched']} for name,row in report['books'].items()},indent=2))
