"""Offline collection overlay: preserve current app; never make network requests."""
from pathlib import Path
import json,sys,datetime,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));from build_teaching import parse_all
CACHE=ROOT/'sources/teaching';data=json.loads((ROOT/'dist/bible-teaching.json').read_text());bible=json.loads((ROOT/'dist/bible.json').read_text());catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
p=CACHE/'series-attribution.json';attrs=json.loads(p.read_text())
attrs.update({
'PLGk636nvuNgT_tdpvncvr2GlsP97sPR48':{'teacher':'Arnold Murray','source':'https://www.tapatalk.com/groups/theseason/shepherd-s-chapel-daily-broadcast-record-for-2014-t23147.html','basis':'Inferred by matching the official 23-lesson Revelation sequence to the archive’s re-aired 2010 Arnold Murray Series 284. The log mixes early 2014 reteaching with 2010 rebroadcasts and contains range errors; retain published video ranges. Full playback untested.','series':'284, January 2010 rebroadcast','totalLessons':23},
'PLGk636nvuNgQMT2_ywIxfUrqmycZNV-te':{'teacher':'Arnold Murray','source':'https://www.tapatalk.com/groups/theseason/1-23-23-the-book-of-exodus-by-pastor-arnold-murray-t62882.html','basis':'Inferred by matching all 24 published ranges to the January–March 2023 Exodus broadcast record naming Pastor Arnold Murray. Full playback untested.','series':'Exodus, January–March 2023 rebroadcast','matchingRanges':24,'totalLessons':24},
'PLGk636nvuNgSIdge6KkKtOxXb6RJUfD7x':{'teacher':'Dennis Murray','source':'https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-for-2016-t35853.html','basis':'Inferred by matching official Leviticus sequence to the archival Dennis Murray Series 217 broadcast record, corroborated by many individually named cached descriptions. Published video ranges retained where archive differs. Secondary fallback until a confirmed Arnold recording covers the verse; playback untested.','series':'217, June 2009 rebroadcast','totalLessons':26}
});p.write_text(json.dumps(attrs,indent=2))
publicTeachers={vid:{'teacher':'Arnold Murray','source':'https://www.youtube.com/watch?v='+vid,'basis':'Public search metadata explicitly names Pastor Arnold Murray with this exact published passage range; full playback untested.'} for vid in ['KetgVB2kG4o','DzaVNyMiE18']}
(CACHE/'fifth-batch-public-evidence.json').write_text(json.dumps(publicTeachers,indent=2))
BATCH=[64,65,0,1,2]
report={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directYouTubeRequests':0,'books':{},'discrepancies':[]};before=json.loads(json.dumps(data))
def points(b):return [[c,v] for c,vs in enumerate(bible['books'][b]['chapters'],1) for v in range(1,len(vs)+1)]
def uncovered(b,rs):return [p for p in points(b) if not any(r['start']<=p<=r['end'] for r in rs)]
def ranges(vid,title):
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
report['discrepancies']=[{'passage':'Revelation 21:16–27','issue':'Official chapter 21 lesson title ends 21:15 while archive ends 21:27. Do not extend video range. Alternative candidates await teacher confirmation.'},{'passage':'Revelation','issue':'2014 archive mixes early reteaching and 2010 rebroadcast ranges; several ranges differ from published playlist. Preserve video ranges and flag for later review.'},{'passage':'Leviticus 4:35','issue':'Official title ends 4:34; individually attributed Dennis alternate covers verse 35. Do not change official title.'},{'passage':'Leviticus 16:6–15 and 19:4–13','issue':'Alternative playlist title gaps preserved; official mapped lessons supply these verses.'},{'passage':'Genesis 35:27–29','issue':'Filled by search-named Arnold alternative DzaVNyMiE18; existing Genesis lessons preserved.'}]
for b in range(66):
 if b not in BATCH:assert data['books'][b]==before['books'][b],b
report['scopePreserved']=True
report['addedLessonsThisBatch']=sum(r['addedLessons'] for r in report['books'].values())
report['linkedVersesAddedThisBatch']=sum(data['books'][b]['coverage']['matched']-before['books'][b]['coverage']['matched'] for b in BATCH)
(ROOT/'dist/bible-teaching.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
p=ROOT/'verification/new-testament-progress.json';state=json.loads(p.read_text());state['updated']=report['updated'];state['activeBook']='Leviticus';state['nextBook']='Numbers, Deuteronomy, Joshua, Judges, Ruth; New Testament collection passes complete but unresolved links remain.';state['newTestamentCollectionPassComplete']=True
for name,row in report['books'].items():
 state['books'][name]=row
 if row['coverage']['matched']==row['coverage']['total'] and name not in state['completedBooks']:state['completedBooks'].append(name)
p.write_text(json.dumps(state,indent=2));(ROOT/'verification/fifth-five-book-collection.json').write_text(json.dumps(report,indent=2));print(json.dumps({name:{k:v for k,v in row.items() if k not in ['unmatched','candidateUnmatched']} for name,row in report['books'].items()},indent=2))
