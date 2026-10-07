"""Offline collection overlay: preserve current app; never make network requests."""
from pathlib import Path
import json,sys,datetime,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));from build_teaching import parse_all
CACHE=ROOT/'sources/teaching';data=json.loads((ROOT/'dist/bible-teaching.json').read_text());bible=json.loads((ROOT/'dist/bible.json').read_text());catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
p=CACHE/'series-attribution.json';attrs=json.loads(p.read_text())
attrs['PLGk636nvuNgQm7u9f9ONyJixv9EZmLbCq']={'teacher':'Dennis Murray','source':'https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-for-2015-t30599.html','basis':'Inferred by matching the official 34-lesson Numbers sequence to Dennis Murray Series 256 in the 2015 broadcast record, corroborated by current TV listings of the closing ranges. Archive contains endpoint errors; published video ranges retained. Playback untested.','series':'256, August 2010 rebroadcast','totalLessons':34}
for pid,teacher,vids in [('PLGk636nvuNgSu6Ud8UBlcGUwtPNQ6UHaB','Arnold Murray',['4HgHsYjwhes','9BsQeAojykM','9ti_J5jq1T8','0iXsCzK9DkM','Bp2zvghlLaI','07JL-z0fMgY']),('PLGk636nvuNgQK_ZMH6FsOk7_Mec9Ydu1V','Dennis Murray',['QDKvsmyif9c','28bha5wTRz8','OU8esDxE0LE','Bw1aqR3ChnY','Hz6o5dZA38I','F2er8j-9T6I','Oot0pyne6EU','K29AYa7KZQc','IiZctrIcMBo','H-rzFpNzYFs','UZxEMs1F-kw','KMOsi7PsOxc']),('PLGk636nvuNgTH6qDcScIhN1XKzOLIvk7t','Arnold Murray',['LMEN5JhKAwE','Va9JWNwp2qo'])]:
 for vid in vids:assert teacher in json.loads((CACHE/('video-'+vid+'.json')).read_text())['description']
 attrs[pid]={'teacher':teacher,'source':'https://www.youtube.com/watch?v='+vids[0],'basis':f'Inferred for this official playlist from {len(vids)} individually named cached official video descriptions in the same book sequence. Unnamed recordings remain series-level inference; full playback untested.','corroboratingVideos':vids}
p.write_text(json.dumps(attrs,indent=2))
publicTeachers={'f3_aywKN6Lk':{'teacher':'Arnold Murray','source':'https://www.mytvguide.org/tv-listings/kcpm-dt-tv-guide/','basis':'Published TV listing names Arnold Murray for exact Deuteronomy 1:1–1:42 range. This is a range-level attribution inference, not video playback or an attribution of the entire playlist.'}}
(CACHE/'sixth-batch-public-evidence.json').write_text(json.dumps(publicTeachers,indent=2))
BATCH=[3,4,5,6,7]
report={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directYouTubeRequests':0,'books':{},'discrepancies':[]};before=json.loads(json.dumps(data))
def points(b):return [[c,v] for c,vs in enumerate(bible['books'][b]['chapters'],1) for v in range(1,len(vs)+1)]
def uncovered(b,rs):return [p for p in points(b) if not any(r['start']<=p<=r['end'] for r in rs)]
def ranges(vid,title):
 return parse_all(title)
for b in BATCH:
 book=data['books'][b];candidates=[];seen=set();added=0
 if b==3:
  report['numbersPriorLinksHeldForReview']=book['lessons'].copy();book['lessons']=[]
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
    if b==3 and not pl['id'].startswith('PLGk'):who=None
    if att:who=att['teacher']
    elif direct:who=direct['teacher']
    unavailable=bool(ev.get('playability') and ev['playability']!='OK')
    entry={'id':vid,'title':title,'book':b,'start':start,'end':end,'url':'https://www.youtube.com/watch?v='+vid,'teacher':who,'channel':ev.get('author') or ("The Shepherd’s Chapel Official Channel" if pl['id'].startswith('PLGk') else 'Shepherds Student'),'official':pl['id'].startswith('PLGk'),'playlist':pl['url'],'timestampSeconds':None,'playbackChecked':False,'checked':ev.get('checked'),'mappingBasis':'Published passage range in saved playlist','status':'Teacher confirmation pending' if not who else 'Attributed lesson; full playback untested'}
    if att:entry['teacherAttribution']=att
    if direct:entry['teacherEvidence']=direct
    if b==3 and not pl['id'].startswith('PLGk'):entry['status']='Teacher conflict: generic student Arnold credit versus matching Dennis Series 256; owner review needed'
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
report['discrepancies']=[{'passage':'Numbers student recordings','issue':'30 existing links have generic Arnold credit but closely match Dennis Series 256 sequence. Preserved all records in report and candidates, held out of runtime pending teacher review. Official Dennis fallback supplies published ranges.'},{'passage':'Numbers ending','issue':'2015 archive has 33:49, 35:9 and invalid 36:16; retain official titles 33:6, 35:7 and valid END.'},{'passage':'Deuteronomy','issue':'Only directly named saved alternatives and exact opening TV-range inference promoted. Remaining teacher-unknown candidates kept for later review; do not infer whole series from a single matching range.'},{'passage':'Joshua, Judges, Ruth','issue':'Unnamed official videos attributed as visible series-level inference from multiple individually named official descriptions, not individual playback.'}]
for b in range(66):
 if b not in BATCH:assert data['books'][b]==before['books'][b],b
report['scopePreserved']=True
import hashlib
report['kjvSha256']=hashlib.sha256((ROOT/'dist/bible.json').read_bytes()).hexdigest()
prior=json.loads((ROOT/'verification/fifth-five-book-collection.json').read_text())
assert report['kjvSha256']==prior['scriptureSha256']
report['kjvUnchanged']=True
report['reviewShortlistLimit']=3
report['addedLessonsThisBatch']=sum(r['addedLessons'] for r in report['books'].values())
report['linkedVersesAddedThisBatch']=sum(data['books'][b]['coverage']['matched']-before['books'][b]['coverage']['matched'] for b in BATCH)
(ROOT/'dist/bible-teaching.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
p=ROOT/'verification/new-testament-progress.json';state=json.loads(p.read_text());state['updated']=report['updated'];state['activeBook']='Ruth';state['nextBook']='1 Samuel, 2 Samuel, 1 Kings, 2 Kings, 1 Chronicles';state['newTestamentCollectionPassComplete']=True
for name,row in report['books'].items():
 state['books'][name]=row
 if row['coverage']['matched']==row['coverage']['total'] and name not in state['completedBooks']:state['completedBooks'].append(name)
p.write_text(json.dumps(state,indent=2));(ROOT/'verification/sixth-five-book-collection.json').write_text(json.dumps(report,indent=2));print(json.dumps({name:{k:v for k,v in row.items() if k not in ['unmatched','candidateUnmatched']} for name,row in report['books'].items()},indent=2))
