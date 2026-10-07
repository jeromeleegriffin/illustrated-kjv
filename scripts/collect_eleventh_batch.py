"""Offline collection overlay: preserve current app; never make network requests."""
from pathlib import Path
import json,sys,datetime,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));from build_teaching import parse_all
CACHE=ROOT/'sources/teaching';data=json.loads((ROOT/'dist/bible-teaching.json').read_text());bible=json.loads((ROOT/'dist/bible.json').read_text());catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
p=CACHE/'series-attribution.json';attrs=json.loads(p.read_text())
attrs['PLGk636nvuNgRpAOU97FpH665uymk_FkyG']={'teacher': 'Arnold Murray', 'bookScope': [28, 29, 30, 31, 32, 33, 34, 35, 36, 37], 'source': 'https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-for-2016-t35853.html', 'basis': 'Series-level inference for Joel through Zechariah: 2016 broadcast record explicitly credits Arnold Murray for Minor Prophets Series 243 and matches official lesson sequence. Thirty-eight cached official playlist descriptions individually credit Arnold, with no Dennis credit found. Playlist contains alternate rebroadcast copies and a few shortened endpoints; preserve original titles/ranges. Full playback untested.', 'series': '243, Minor Prophets', 'individuallyNamedCachedLessons': 38, 'totalPlaylistVideos': 85}
p.write_text(json.dumps(attrs,indent=2))
publicTeachers={}
BATCH=list(range(28,38))
report={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directYouTubeRequests':0,'books':{},'discrepancies':[]};before=json.loads(json.dumps(data))
def points(b):return [[c,v] for c,vs in enumerate(bible['books'][b]['chapters'],1) for v in range(1,len(vs)+1)]
def uncovered(b,rs):return [p for p in points(b) if not any(r['start']<=p<=r['end'] for r in rs)]
def ranges(vid,title):
 # Combined passages resolved from title plus explicit Series 243 book-boundary record.
 if vid in ['t99U5NMuJYk','Y9Vw8_i1BWc']:return [(29,[9,7],[9,15]),(30,[1,1],[1,11])]
 if vid in ['kSSjNuJQKD4','RvwUuir5irc']:return [(30,[1,12],[1,21]),(31,[1,1],[1,17])]
 return parse_all(title)
priorBoundaryMappings=[l.copy() for l in data['books'][31]['lessons'] if l['id']=='RvwUuir5irc' and l['start']==[1,12]]
data['books'][31]['lessons']=[l for l in data['books'][31]['lessons'] if not (l['id']=='RvwUuir5irc' and l['start']==[1,12])]
report['correctedPriorMappings']=priorBoundaryMappings
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
report['discrepancies']=[{'passage': 'Amos 5:11–27', 'issue': 'Prior 17-verse gap now supplied by attributed official 5:11–6:10 titles.'}, {'passage': 'Zephaniah 1:1–2:15', 'issue': 'Prior 33-verse gap supplied by official titles; student Zephaniah playlist actually contains Habakkuk 3:6–19, so map by published passage, never playlist name.'}, {'passage': 'Zechariah 3:1–2', 'issue': 'Prior two-verse gap supplied by official 2:5–3:10 title.'}, {'passage': 'Amos–Obadiah and Obadiah–Jonah boundaries', 'issue': 'Four combined titles resolved from explicit archival book transition record, preserving original titles and URLs. RvwUuir5irc previous narrow Jonah 1:12–17 mapping corrected to Jonah 1:1–17, with old record retained in report. No playback transition timestamp guessed.'}, {'passage': 'Minor Prophets archive endpoints', 'issue': 'Archive Joel 3:31 invalid (KJV ends 21); Haggai first ending 2:16 differs from published 2:6. Use original valid video endpoints.'}, {'passage': 'Duplicate official rebroadcast lessons', 'issue': 'Preserve alternatives for later maximum-three-choice owner review; one primary link in reader, no newest-date assumption.'}]
# Save unparsed book-level candidates separately, including Esther and invalid endpoints.
for b in BATCH:
 file=CACHE/(data['books'][b]['name'].lower().replace(' ','-')+'-search-candidates.json');queue=json.loads(file.read_text());unmapped=[]
 for pl in catalog:
  for vid,title in pl['videos'].items():
   if (data['books'][b]['name'].lower() in title.lower()) and not ranges(vid,title):unmapped.append({'id':vid,'title':title,'url':'https://www.youtube.com/watch?v='+vid,'playlist':pl['url'],'teacher':None,'playbackChecked':False,'status':'Published verse range missing or invalid; teacher confirmation also required'})

 queue['unmappedCandidates']=unmapped;queue['summary']['unmappedCandidateVideos']=len({r['id'] for r in unmapped});file.write_text(json.dumps(queue,indent=2));report['books'][data['books'][b]['name']]['unmappedCandidateVideos']=len({r['id'] for r in unmapped})
for b in range(66):
 if b not in BATCH:assert data['books'][b]==before['books'][b],b
report['scopePreserved']=True
import hashlib
report['kjvSha256']=hashlib.sha256((ROOT/'dist/bible.json').read_bytes()).hexdigest()
assert report['kjvSha256']==json.loads((ROOT/'verification/tenth-five-book-collection.json').read_text())['kjvSha256']
report['kjvUnchanged']=True
report['reviewShortlistLimit']=3
report['correctedMappingsCount']=len(priorBoundaryMappings)
report['addedLessonsThisBatch']=sum(r['addedLessons'] for r in report['books'].values())
report['linkedVersesAddedThisBatch']=sum(data['books'][b]['coverage']['matched']-before['books'][b]['coverage']['matched'] for b in BATCH)
(ROOT/'dist/bible-teaching.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
p=ROOT/'verification/new-testament-progress.json';state=json.loads(p.read_text());state['updated']=report['updated'];state['activeBook']='Zechariah';state['nextBook']='Malachi, then unresolved teacher/range and duplicate review';state['newTestamentCollectionPassComplete']=True
for name,row in report['books'].items():
 state['books'][name]=row
 if row['coverage']['matched']==row['coverage']['total'] and name not in state['completedBooks']:state['completedBooks'].append(name)
p.write_text(json.dumps(state,indent=2));(ROOT/'verification/eleventh-ten-book-collection.json').write_text(json.dumps(report,indent=2));print(json.dumps({name:{k:v for k,v in row.items() if k not in ['unmatched','candidateUnmatched']} for name,row in report['books'].items()},indent=2))
