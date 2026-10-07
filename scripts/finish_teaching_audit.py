"""Finish the whole-Bible audit using cached and indexed evidence; no network calls."""
from pathlib import Path
import json,re,hashlib,sys,datetime
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_teaching import parse_all
cache=ROOT/'sources/teaching';data=json.loads((ROOT/'dist/bible-teaching.json').read_text());before=json.loads(json.dumps(data));bible=json.loads((ROOT/'dist/bible.json').read_text())
attrs=json.loads((cache/'series-attribution.json').read_text())
attrs['PLiA6kuKpn0D3WvNRgOfNsiPFJmajMuR3p']={'teacher':'Arnold Murray','source':'https://www.youtube.com/watch?v=0vH9radWFtI','basis':'Series-level inference from six individually credited cached descriptions in the same 35-lesson Revelation playlist, corroborated by indexed lecture 7 and 11 titles naming Arnold. Closing two recordings not individually confirmed; full playback untested.','corroboratingVideos':['0vH9radWFtI','1BdiOlem4EE','3rLho65LPZc','5Y3N_TT5L_o','41vJyKctqic','0--R0yx2XSs']}
attrs['PLiA6kuKpn0D0OD4RlseMQkX7pUYXJBv8D']={'teacher':'Arnold Murray','bookScope':[61],'source':'https://www.youtube.com/watch?v=kEtbuGmwePQ','basis':'Series-level inference from individually credited cached opening lesson of this same numbered 1 John sequence. Lesson 5 is not individually teacher-confirmed. Retain published ranges; full playback untested.','corroboratingVideos':['kEtbuGmwePQ']}
public={v:{'teacher':'Arnold Murray','source':'https://www.youtube.com/watch?v='+v,'basis':'Public search index of this exact title and video ID credits Pastor Arnold Murray. Source page opening was throttled and not retried; full playback untested.'} for v in ['8Z3J_NHMOhk','9tVOaQGov2U']}
selected={50:['8Z3J_NHMOhk','9tVOaQGov2U'],61:['2LQVXernBlQ'],65:['j7h2HFjUKD8','JTBJ6X3euYU']}
catalog=json.loads((cache/'student-catalog.json').read_text());added=[]
for b,ids in selected.items():
 for pl in catalog:
  for vid,title in pl['videos'].items():
   if vid not in ids:continue
   for bi,start,end in parse_all(title):
    if bi!=b or any(l['id']==vid and l['start']==start and l['end']==end for l in data['books'][b]['lessons']):continue
    evfile=cache/('video-'+vid+'.json');ev=json.loads(evfile.read_text()) if evfile.exists() else {}
    assert not ev.get('playability') or ev['playability']=='OK'
    att=public.get(vid) or attrs[pl['id']]
    l={'id':vid,'title':title,'book':b,'start':start,'end':end,'url':'https://www.youtube.com/watch?v='+vid,'teacher':att['teacher'],'channel':'Shepherds Student','official':False,'playlist':pl['url'],'timestampSeconds':None,'playbackChecked':False,'checked':ev.get('checked'),'mappingBasis':'Published passage range in saved playlist','status':'Attributed lesson; full playback untested','teacherAttribution':att}
    data['books'][b]['lessons'].append(l);added.append(l)
    if pl['url'] not in data['books'][b]['playlists']:data['books'][b]['playlists'].append(pl['url'])
    qfile=cache/(data['books'][b]['name'].lower().replace(' ','-')+'-search-candidates.json');q=json.loads(qfile.read_text())
    for c in q['candidates']:
     if c['id']==vid:c.update(l)
    qfile.write_text(json.dumps(q,indent=2))
rows=[];gaps=[]
for b,book in enumerate(data['books']):
 if b in selected:book['lessons'].sort(key=lambda l:(l['teacher']!='Arnold Murray',not l['official'],l['start'],l['end'],l['id']))
 else:assert book==before['books'][b]
 missing=[];arnold=dennis=0;seen=set()
 for l in book['lessons']:
  assert l['teacher'] in ['Arnold Murray','Dennis Murray'];assert re.fullmatch('[A-Za-z0-9_-]{11}',l['id']);assert l['url']=='https://www.youtube.com/watch?v='+l['id'];assert l['start']<=l['end']
  for c,v in [l['start'],l['end']]:assert 1<=c<=len(bible['books'][b]['chapters']) and 1<=v<=len(bible['books'][b]['chapters'][c-1])
  key=(l['id'],tuple(l['start']),tuple(l['end']));assert key not in seen;seen.add(key)
 for c,vs in enumerate(bible['books'][b]['chapters'],1):
  for v in range(1,len(vs)+1):
   matches=[l for l in book['lessons'] if l['start']<=[c,v]<=l['end']]
   if any(l['teacher']=='Arnold Murray' for l in matches):arnold+=1
   elif matches:dennis+=1
   else:missing.append([c,v])
 total=sum(map(len,bible['books'][b]['chapters']));book['coverage']={'matched':arnold+dennis,'total':total}
 rows.append({'book':book['name'],'index':b,'coverage':book['coverage'],'arnoldPrimaryVerses':arnold,'dennisFallbackVerses':dennis,'linkedVideos':len({l['id'] for l in book['lessons']}),'lessonMappings':len(book['lessons'])})
 if missing:
  segments=[]
  for p in missing:
   if segments and p[0]==segments[-1]['end'][0] and p[1]==segments[-1]['end'][1]+1:segments[-1]['end']=p
   else:segments.append({'start':p,'end':p})
  gaps.append({'book':book['name'],'index':b,'missingVerses':len(missing),'ranges':segments})
base=json.loads((ROOT/'verification/twelfth-whole-bible-collection.json').read_text());updated=datetime.datetime.now(datetime.timezone.utc).isoformat()
report={'updated':updated,'status':'Collection pass complete; verse coverage partial','collectionPassComplete':True,'videoCoverageComplete':not gaps,'totalBooks':66,'fullyMappedBooks':66-len(gaps),'totalVerses':31102,'linkedVerses':sum(r['coverage']['matched'] for r in rows),'arnoldPrimaryVerses':sum(r['arnoldPrimaryVerses'] for r in rows),'dennisFallbackVerses':sum(r['dennisFallbackVerses'] for r in rows),'uniqueLinkedVideos':len({l['id'] for b in data['books'] for l in b['lessons']}),'lessonMappings':sum(r['lessonMappings'] for r in rows),'addedLessonsThisTurn':base['addedLessonsThisBatch']+len(added),'linkedVersesAddedThisTurn':sum(r['coverage']['matched'] for r in rows)-27848,'directImporterPaused':True,'directImporterRequestsThisTurn':0,'publicPageChecks':'Four public YouTube page checks failed: one disabled, three throttled. Stopped; no retries.','runtimeTests':'Pending renderer logic validation','visualTests':'Blocked: previously installed browser binary missing; no visual PASS claimed','kjvSha256':hashlib.sha256((ROOT/'dist/bible.json').read_bytes()).hexdigest(),'kjvUnchanged':True,'reviewShortlistLimit':3,'ownerReviewAppBuilt':False,'exactAudioSynchronization':False,'books':rows,'gaps':gaps,'supplementalLessons':added}
assert report['kjvSha256']==base['kjvSha256']
data['mappingBasis']='Published passage ranges; Arnold first, Dennis fallback per verse. Teacher attribution from publisher metadata or explicitly disclosed series inference. No exact audio synchronization; full playback untested.'
(cache/'series-attribution.json').write_text(json.dumps(attrs,indent=2));(cache/'whole-bible-public-evidence.json').write_text(json.dumps({'updated':updated,'indexedIndividualCredits':public,'note':'These are public index evidence, not successful full video page fetches.'},indent=2))
(ROOT/'dist/bible-teaching.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
(ROOT/'verification/whole-bible-teaching-audit.json').write_text(json.dumps(report,indent=2))
p=ROOT/'verification/new-testament-progress.json';state=json.loads(p.read_text());state.update({'updated':updated,'activeBook':'Whole-Bible audit complete','nextBook':'Manual review of unresolved passages','wholeBibleCollectionPassComplete':True,'videoCoverageComplete':not gaps,'remainingGaps':gaps})
for row in rows:
 name=row['book'];state['books'].setdefault(name,{})['coverage']=row['coverage']
 if row['coverage']['matched']==row['coverage']['total'] and name not in state['completedBooks']:state['completedBooks'].append(name)
state['completedBooks']=[row['book'] for row in rows if row['coverage']['matched']==row['coverage']['total']];p.write_text(json.dumps(state,indent=2))
for b in selected:
 qfile=cache/(data['books'][b]['name'].lower().replace(' ','-')+'-search-candidates.json');q=json.loads(qfile.read_text());q['summary']['coverage']=data['books'][b]['coverage'];q['summary']['teacherPendingVideos']=len({c['id'] for c in q['candidates'] if not c.get('teacher')});qfile.write_text(json.dumps(q,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['books','supplementalLessons']},indent=2))
