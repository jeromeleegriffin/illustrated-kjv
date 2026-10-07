"""Second five-book offline overlay. No requests, deletion, push or deployment."""
from pathlib import Path
import json,sys,datetime,re,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_teaching import parse_all
CACHE=ROOT/'sources/teaching';target=ROOT/'dist/bible-teaching.json'
data=json.loads(target.read_text());before=json.loads(target.read_text());biblepath=ROOT/'dist/bible.json';biblehash=hashlib.sha256(biblepath.read_bytes()).hexdigest();bible=json.loads(biblepath.read_text())
catalog=json.loads((CACHE/'catalog.json').read_text())+json.loads((CACHE/'student-catalog.json').read_text())
archive='https://www.tapatalk.com/groups/theseason/shepherds-chapel-daily-broadcast-record-for-2016-t35853.html'
attrs=json.loads((CACHE/'series-attribution.json').read_text())
attrs.update({
 'PLGk636nvuNgTPCbZQZEn75wo9T8MflS0M':{'teacher':'Arnold Murray','source':archive,'basis':'Inferred by matching all four official Colossians lesson ranges and sequence to the archival Arnold Murray Series 110 broadcast record. Playback untested.','series':'110, April 2011','matchingRanges':4,'totalLessons':4},
 'PLGk636nvuNgTg_s0PGiELUGqMJp7AG0W6':{'teacher':'Arnold Murray','source':archive,'basis':'Inferred by matching the ten official Timothy lesson ranges and sequence to the archival Arnold Murray Series 307 broadcast record. Only 1 Timothy updated in this pass; playback untested.','series':'307, December 2011','matchingRanges':10,'totalLessons':10},
 'PLGk636nvuNgS-aRhlzMMW5Pw6zrKQY9M8':{'teacher':'Arnold Murray','source':'https://www.tapatalk.com/groups/theseason/1-8-19-philippians-by-pastor-arnold-murray-t56297.html','basis':'Inferred from a public search index of the January 2020 Philippians broadcast record naming Pastor Arnold Murray, matching the opening two published ranges and broadcast dates. The full source page returned HTTP 429 and was not retried. Later lessons are series-level inference, not individual playback confirmation.','series':'Philippians, January 2020 rebroadcast','matchingRanges':2,'totalLessons':5}
})
(CACHE/'series-attribution.json').write_text(json.dumps(attrs,indent=2))
publicTeachers={'QIlakAYBkMY':{'teacher':'Arnold Murray','source':'https://www.youtube.com/watch?v=QIlakAYBkMY','basis':'Public search result describes this Colossians 1:1–1:20 recording as Shepherds Chapel with Pastor Arnold Murray. Playback untested.'}}
(CACHE/'next-batch-public-evidence.json').write_text(json.dumps(publicTeachers,indent=2))
report={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directYouTubeRequests':0,'books':{},'discrepancies':[],'sourceBlocker':'Philippians archive page HTTP 429; no retry. Public search index used with explicit series-level inference.'}
invalid={'Y23KJsx-Kqc':(52,'Published end 2:26 is invalid: chapter 2 ends at verse 17. Do not clamp or infer actual endpoint.'),'r7qujVCi8TQ':(53,'Published end 6:22 is invalid: chapter 6 ends at verse 21. Saved playability also LOGIN_REQUIRED.'),'XYj1mSYTCSA':(51,'Cross-book title ends 1:1; archive says 2 Thessalonians 1:12. Unresolved endpoint and teacher; no mapping added.')}
normalized={'eNh1KKBNNSM':[(51,[1,1],[2,15])],'fiuSZaZzq7k':[(51,[2,16],[4,11])],'FlyyliNFhLI':[(51,[4,12],[5,10])]}
def points(b):return [[c,v] for c,vs in enumerate(bible['books'][b]['chapters'],1) for v in range(1,len(vs)+1)]
def uncovered(b,rs):return [p for p in points(b) if not any(r['start']<=p<=r['end'] for r in rs)]
for b in range(49,54):
 book=data['books'][b];candidates=[];excluded=[];seen=set();added=0
 for pl in catalog:
  for vid,title in pl['videos'].items():
   if vid in invalid:
    ib,reason=invalid[vid]
    if ib==b or (vid=='XYj1mSYTCSA' and b==52):
     entry={'id':vid,'title':title,'url':'https://www.youtube.com/watch?v='+vid,'playlist':pl['url'],'reason':reason,'status':'Owner review required; excluded from runtime'};excluded.append(entry)
    continue
   for bookid,start,end in normalized.get(vid,parse_all(title)):
    if bookid!=b or (vid,tuple(start),tuple(end)) in seen:continue
    seen.add((vid,tuple(start),tuple(end)))
    assert start<=end
    for c,v in (start,end):assert bible['books'][b]['chapters'][c-1][v-1]
    evp=CACHE/('video-'+vid+'.json');ev=json.loads(evp.read_text()) if evp.exists() else {}
    text=title+'\n'+ev.get('description','')[:600];named=[t for t in ['Arnold Murray','Dennis Murray'] if re.search(re.escape(t),text,re.I)]
    who=named[0] if len(named)==1 and not re.search(r'Arnold\s*(?:&|and)\s*Dennis\s+Murray',text,re.I) else None
    att=attrs.get(pl['id']);direct=publicTeachers.get(vid);who=att['teacher'] if att else (direct['teacher'] if direct else who)
    unavailable=bool(ev.get('playability') and ev['playability']!='OK')
    entry={'id':vid,'title':title,'book':b,'start':start,'end':end,'url':'https://www.youtube.com/watch?v='+vid,'teacher':who,'channel':ev.get('author') or ('The Shepherd’s Chapel Official Channel' if pl['id'].startswith('PLGk') else 'Shepherds Student'),'official':pl['id'].startswith('PLGk'),'playlist':pl['url'],'timestampSeconds':None,'playbackChecked':False,'checked':ev.get('checked'),'mappingBasis':'Published passage range in saved playlist','status':'Teacher confirmation pending' if not who else 'Attributed lesson; full playback untested'}
    if att:entry['teacherAttribution']=att
    if direct:entry['teacherEvidence']=direct
    if vid in normalized:entry['mappingBasis']='First Thessalonians identified from combined playlist sequence; original range retained; teacher unconfirmed'
    if unavailable:
     entry['status']='Saved video metadata reports unavailable; replacement review required'
     excluded.append({'id':vid,'title':title,'url':entry['url'],'reason':'Saved playability '+ev['playability']+'; valid range retained only as candidate; replacement review required.'})
    candidates.append(entry)
    if who and not unavailable and not any(l['id']==vid and l['start']==start and l['end']==end for l in book['lessons']):
     book['lessons'].append(entry.copy());added+=1
     if pl['url'] not in book['playlists']:book['playlists'].append(pl['url'])
 book['lessons'].sort(key=lambda l:(l['teacher']!='Arnold Murray',not l['official'],l['start'],l['end'],l['id']))
 missing=uncovered(b,book['lessons']);book['coverage']={'matched':len(points(b))-len(missing),'total':len(points(b))};cm=uncovered(b,candidates)
 row={'coverage':book['coverage'],'linkedVideos':len({l['id'] for l in book['lessons']}),'addedLessons':added,'candidateVideos':len({l['id'] for l in candidates}),'candidateRangeCoverage':len(points(b))-len(cm),'unmatched':missing,'candidateUnmatched':cm,'teacherPendingVideos':len({r['id'] for r in candidates if r['teacher'] is None}),'excludedCandidates':len(excluded)}
 report['books'][book['name']]=row;report['discrepancies']+=excluded
 slug=book['name'].lower().replace(' ','-');(CACHE/(slug+'-search-candidates.json')).write_text(json.dumps({'book':book['name'],'summary':row,'candidates':candidates,'excludedCandidates':excluded},indent=2))
report['discrepancies'].append({'id':'2J-JLzemPDo','reason':'Philippians final lesson date says 2019 in January 2020 sequence. Title retained; valid Bible range unaffected.'})
for b in list(range(49))+list(range(54,66)):assert data['books'][b]==before['books'][b],b
assert hashlib.sha256(biblepath.read_bytes()).hexdigest()==biblehash
report['scopePreserved']=True;report['scriptureSha256']=biblehash
target.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
p=ROOT/'verification/new-testament-progress.json';state=json.loads(p.read_text());state['updated']=report['updated'];state['activeBook']='1 Timothy';state['nextBook']='2 Timothy; unresolved teachers and verse gaps remain for later owner review.'
for name,row in report['books'].items():
 state['books'][name]=row
 if row['coverage']['matched']==row['coverage']['total'] and name not in state['completedBooks']:state['completedBooks'].append(name)
p.write_text(json.dumps(state,indent=2));(ROOT/'verification/nt-next-five-book-collection.json').write_text(json.dumps(report,indent=2))
print(json.dumps({n:{k:v for k,v in r.items() if k not in ['unmatched','candidateUnmatched']} for n,r in report['books'].items()},indent=2))
