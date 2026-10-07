"""Offline collection overlay: preserve current app; never make network requests."""
from pathlib import Path
import json,sys,datetime,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));from build_teaching import parse_all
CACHE=ROOT/'sources/teaching';data=json.loads((ROOT/'dist/bible-teaching.json').read_text());bible=json.loads((ROOT/'dist/bible.json').read_text());catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
p=CACHE/'series-attribution.json';attrs=json.loads(p.read_text())
attrs['PLGk636nvuNgTWcG0AYaFwnR1r_mFdu3Ah']={'teacher': 'Dennis Murray', 'source': 'https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-2013-t19167.html', 'basis': 'Series-level inference: July 2013 broadcast record explicitly names Dennis Murray for Psalms Series 265; saved official 100-lesson sequence matches that sequence, with several different published endpoints. January 2014 closing sequence corroborates continuation. Retain saved video endpoints; full playback untested.', 'series': '265, Psalms', 'totalLessons': 100, 'corroboratingSource': 'https://www.tapatalk.com/groups/theseason/shepherd-s-chapel-daily-broadcast-record-for-2014-t23147.html'}
attrs['PLGk636nvuNgQl794CDjabzIvGHX1sS4QI']={'teacher': 'Arnold Murray', 'source': 'https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-for-2015-t30599.html', 'basis': 'Series-level inference: June–August 2015 archive explicitly names Arnold Murray for Proverbs Series 262. Official 30-lesson sequence matches the series; retain video endpoints where archive transcription differs. Full playback untested.', 'series': '262, Proverbs 2008 rebroadcast', 'totalLessons': 30}
attrs['PLGk636nvuNgQspUFYtMJK0_Z5tcffANJv']={'teacher': 'Arnold Murray', 'source': 'https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-2013-t19167.html', 'basis': 'Series-level inference: March–April 2013 archive explicitly names Arnold Murray for Ecclesiastes Series 121. Official eleven-lesson sequence matches; first two cached official descriptions also name Arnold. Archive chapter 5 endpoint 21 is invalid; retain published title ending 20. Full playback untested.', 'series': '121, Ecclesiastes', 'totalLessons': 11}
attrs['PLGk636nvuNgTdNhRfNKaDc7FyTWmrYqt9']={'teacher': 'Arnold Murray', 'source': 'https://www.tapatalk.com/groups/theseason/12-12-23-song-of-solomon-by-pastor-arnold-murray-t63897.html', 'basis': 'Public source explicitly credits Arnold Murray and embeds the same four official video IDs with matching published passage ranges. Audio and full playback untested.', 'corroboratingVideos': ['BOuoDp97QjY', 'gqMIckYNxdQ', 'Y5F5ITq761U', 'P9DYEhPaigo'], 'totalLessons': 4}
attrs['PLGk636nvuNgSuD5cucnHfhD6id7nwyFmF']={'teacher': 'Arnold Murray', 'source': 'https://www.tapatalk.com/groups/theseason/book-of-isaiah-by-pastor-arnold-murray-series-160-t58001.html', 'basis': 'Series-level inference: public 2020 Isaiah Series 160 record explicitly credits Arnold Murray and lists all 48 matching official passage ranges. Published first lesson begins 1:11; do not extend it. Full playback untested.', 'series': '160, Isaiah', 'matchingRanges': 48, 'totalLessons': 48}
p.write_text(json.dumps(attrs,indent=2))
publicTeachers={'alodZNb9h0o':{'teacher':'Arnold Murray','source':'https://www.youtube.com/watch?v=alodZNb9h0o','basis':'Public indexed listing explicitly names Pastor Arnold Murray for this video; playback untested.'}}
BATCH=[18,19,20,21,22]
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
report['discrepancies']=[{'passage': 'Psalms 136:13–26 and 145:1', 'issue': 'Existing Arnold series has these 15 verse gaps; official Dennis series supplies fallback only where Arnold is missing.'}, {'passage': 'Psalms official playlist', 'issue': 'Saved official playlist stops at 147:12 and has a few internal published-title gaps. Preserve endpoints; existing Arnold links cover remaining passages.'}, {'passage': 'Ecclesiastes 5', 'issue': 'Archive ends chapter at verse 21 but KJV ends 20. Use valid saved video title ending 20; do not change scripture.'}, {'passage': 'Isaiah 1:1–10', 'issue': 'Official title begins at 1:11. Existing Arnold student lesson supplies opening verses; official title not extended.'}, {'passage': 'Song of Solomon alternatives', 'issue': 'Only alodZNb9h0o has individually corroborated Arnold credit in public search. Other student alternatives remain teacher-pending; all four official IDs are credited by public source.'}, {'passage': 'Video availability', 'issue': 'Four public embed checks throttled. No retry, playback or audio timestamps; direct importer remains paused.'}]
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
assert report['kjvSha256']==json.loads((ROOT/'verification/eighth-five-book-collection.json').read_text())['kjvSha256']
report['kjvUnchanged']=True
report['reviewShortlistLimit']=3
report['addedLessonsThisBatch']=sum(r['addedLessons'] for r in report['books'].values())
report['linkedVersesAddedThisBatch']=sum(data['books'][b]['coverage']['matched']-before['books'][b]['coverage']['matched'] for b in BATCH)
(ROOT/'dist/bible-teaching.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
p=ROOT/'verification/new-testament-progress.json';state=json.loads(p.read_text());state['updated']=report['updated'];state['activeBook']='Isaiah';state['nextBook']='Jeremiah, Lamentations, Ezekiel, Daniel, Hosea';state['newTestamentCollectionPassComplete']=True
for name,row in report['books'].items():
 state['books'][name]=row
 if row['coverage']['matched']==row['coverage']['total'] and name not in state['completedBooks']:state['completedBooks'].append(name)
p.write_text(json.dumps(state,indent=2));(ROOT/'verification/ninth-five-book-collection.json').write_text(json.dumps(report,indent=2));print(json.dumps({name:{k:v for k,v in row.items() if k not in ['unmatched','candidateUnmatched']} for name,row in report['books'].items()},indent=2))
