"""Offline collection overlay: preserve current app; never make network requests."""
from pathlib import Path
import json,sys,datetime,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));from build_teaching import parse_all
CACHE=ROOT/'sources/teaching';data=json.loads((ROOT/'dist/bible-teaching.json').read_text());bible=json.loads((ROOT/'dist/bible.json').read_text());catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
p=CACHE/'series-attribution.json';attrs=json.loads(p.read_text())
archive13='https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-2013-t19167.html'
archive17='https://www.tapatalk.com/groups/theseason/new-shepherds-daily-broadcast-record-for-2017-t42682.html'
def attribute(playlist,source,basis,scope=None):
 attrs[playlist]={'teacher':'Arnold Murray','source':source,'basis':basis+' Published video endpoints retained where archive differs; full playback untested.'}
 if scope:attrs[playlist]['bookScope']=scope
attribute('PLGk636nvuNgRkW8BJ8u2kosxhGSuaiGay',archive13,'Series-level inference: archive names Arnold for John Series 194, October 2009, and matches the official 24-lesson sequence.')
attribute('PLGk636nvuNgTaY0ijgEQDbmWIJkwMquZT',archive13,'Series-level inference: archive names Arnold for Hebrews and Jude Series 157, June 2010, and matches the official sequence.',[57])
for playlist in ['PLGk636nvuNgTeOzHIk0Lft_Kx0_d4y1uC','PLGk636nvuNgTQhLASSyaxvN3GtEVrQRw3']:
 attribute(playlist,archive13,'Series-level inference: archive names Arnold for 1 and 2 Peter Series 258, July 2007, and matches the seven-lesson sequence. Missing numeral and combined book titles resolved by this sequence.',[59,60])
attribute('PLGk636nvuNgRHwKIOk_NspOEaQBWCTMnO',archive17,'Series-level inference: archive explicitly credits Arnold for Romans Series 290, October 2012, matching the sixteen-lesson sequence.')
attribute('PLGk636nvuNgQN_crMbdxgjx2ciCDn2H3r',archive17,'Series-level inference: archive explicitly credits Arnold for Ephesians Series 123, November 2011, matching the seven-lesson sequence.')
attribute('PLGk636nvuNgQhfHMhRBneuDPQxlOa5uXY','https://www.tapatalk.com/groups/theseason/12-24-19-galatians-by-pastor-arnold-murray-1-1-2-7-t56246.html','Series-level inference from public search-index record naming Arnold and listing all five official Galatians ranges. Source opening failed; not retried.')
attribute('PLGk636nvuNgQ0HEqhI2GwizP70-wVDfof','https://www.tapatalk.com/groups/theseason/6-1-26-book-of-deuteronomy-by-pastor-arnold-murray-t65596.html','Series-level inference from indexed Deuteronomy broadcast record naming Arnold; the saved official sequence spans the book. Full source opening failed; lesson-by-lesson archive match not confirmed.')
attribute('PLGk636nvuNgQViHVSWoRCDPbitLGXU_zk','https://www.tapatalk.com/groups/theseason/5-10-23-book-of-philemon-by-pastor-arnold-murray-t63302.html','Public search-index record names Arnold for same May 10, 2023 Philemon broadcast and full-book range. Full source opening failed; not retried.')
attrs['PLGk636nvuNgRpAOU97FpH665uymk_FkyG']['bookScope']=list(range(28,39))
if 'Malachi extension' not in attrs['PLGk636nvuNgRpAOU97FpH665uymk_FkyG']['basis']:attrs['PLGk636nvuNgRpAOU97FpH665uymk_FkyG']['basis']+=' Malachi extension supported by same Series 243 archive and three official published titles.'
p.write_text(json.dumps(attrs,indent=2))
publicTeachers={}
BATCH=[4,16,38,40,42,44,45,47,48,50,52,56,57,59,60,61,65]
report={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directYouTubeRequests':0,'books':{},'discrepancies':[]};before=json.loads(json.dumps(data))
def points(b):return [[c,v] for c,vs in enumerate(bible['books'][b]['chapters'],1) for v in range(1,len(vs)+1)]
def uncovered(b,rs):return [p for p in points(b) if not any(r['start']<=p<=r['end'] for r in rs)]
def ranges(vid,title):
 if vid in ['soSFyASwbLs','iIMTsayr7VU']:return [(59,[5,1],[5,14]),(60,[1,1],[1,8])]
 if vid=='XSuuktzj8u0':return [(59,[1,20],[2,15])]
 if vid=='SO44pz-Cr6I':return [(59,[3,21],[4,19])]
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
report['discrepancies']=[{'issue':'Series attributions are visible in app; public metadata and archive inference, not full playback confirmation. Invalid endpoints and known unavailable recordings excluded.'}]
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
p=ROOT/'verification/new-testament-progress.json';state=json.loads(p.read_text());state['updated']=report['updated'];state['activeBook']='Whole-Bible audit';state['nextBook']='Unresolved passage review';state['wholeBibleCollectionPassComplete']=True;state['videoCoverageComplete']=all(b['coverage']['matched']==b['coverage']['total'] for b in data['books']);state['newTestamentCollectionPassComplete']=True
for name,row in report['books'].items():
 state['books'][name]=row
 if row['coverage']['matched']==row['coverage']['total'] and name not in state['completedBooks']:state['completedBooks'].append(name)
p.write_text(json.dumps(state,indent=2));(ROOT/'verification/twelfth-whole-bible-collection.json').write_text(json.dumps(report,indent=2));print(json.dumps({name:{k:v for k,v in row.items() if k not in ['unmatched','candidateUnmatched']} for name,row in report['books'].items()},indent=2))
