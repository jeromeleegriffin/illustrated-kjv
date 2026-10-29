#!/usr/bin/env python3
"""Incrementally scan private exports; publish only reviewed FAQ paraphrases/metadata.
Usage: python update_faq.py --library PRIVATE_LIBRARY --dist OUTPUT_DIST
A scan never approves an answer. Edit reviewed-occurrences.json after passage review.
"""
import argparse,collections,hashlib,json,re,sqlite3
from pathlib import Path
from datetime import datetime,timezone
VERSION='faq-scan-v2'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def frequency(sources):return len({s.get('recording_group',s['video_id']) for s in sources})
def confirmed_topical_teacher(doc,transcript_hash,evidence):
 """Require independently read, hash-bound program attribution, never import labels."""
 if not isinstance(evidence,dict) or evidence.get('teacher') not in ('Arnold Murray','Dennis Murray'):return None
 if evidence.get('transcript_sha256')!=transcript_hash or evidence.get('source_sha256')!=doc.get('source_sha256'):return None
 if evidence.get('basis') not in ('captioned_program_introduction','captioned_program_outro') or evidence.get('caption_passage_read') is not True:return None
 a=evidence.get('start_index');b=evidence.get('end_index')
 if type(a) is not int or type(b) is not int or not 0<=a<b<=len(doc['segments']):return None
 text=' '.join(s['text'] for s in doc['segments'][a:b]).casefold()
 if evidence['teacher'].casefold() not in text:return None
 return evidence['teacher']
def build(library,dist,registry_path):
 registry=json.loads(registry_path.read_text());private=library/'faq-review';private.mkdir(exist_ok=True);dist.mkdir(parents=True,exist_ok=True)
 db=sqlite3.connect(private/'faq-progress.sqlite');db.execute('create table if not exists sources(id text primary key, hash text, scanner text, candidate_count integer, scanned_at text, kind text)')
 docs={};paths={};kinds={}
 for kind,folder in [('passage',library/'search-library/transcripts'),('topical',library/'topical-library/search-library/transcripts'),('supplement',library/'recovery006/supplement-search/transcripts')]:
  for p in sorted(folder.glob('*.json')):
   d=json.loads(p.read_text());id=d['id'];assert id not in docs;docs[id]=d;paths[id]=p;kinds[id]=kind
 now=datetime.now(timezone.utc).isoformat();new=changed=unchanged=0
 candidate_dir=private/'scan-candidates';candidate_dir.mkdir(exist_ok=True)
 anchors=re.compile(r'\?|\b(?:question time|question is|from (?:Texas|California|Georgia|Florida|Tennessee|Arkansas)|what is|can you explain|will we|is it a sin)\b',re.I)
 for id,d in docs.items():
  h=digest(paths[id]);previous=db.execute('select hash,scanner from sources where id=?',(id,)).fetchone()
  if previous==(h,VERSION):unchanged+=1;continue
  if previous:changed+=1
  else:new+=1
  candidates=[]
  for i,s in enumerate(d['segments']):
   if s['start']<1800:continue
   if anchors.search(s['text']):candidates.append(dict(start=s['start'],end=s['end'],text=s['text'],segment_index=i,status='candidate_not_reviewed'))
  (candidate_dir/(id+'.json')).write_text(json.dumps(dict(video_id=id,transcript_sha256=h,candidates=candidates)))
  with db:db.execute('insert or replace into sources values(?,?,?,?,?,?)',(id,h,VERSION,len(candidates),now,kinds[id]))
 confirmed={id:teacher for id,d in docs.items() if kinds[id]=='topical' and (teacher:=confirmed_topical_teacher(d,digest(paths[id]),registry.get('teacher_confirmations',{}).get(id)))}
 teachers={id:confirmed.get(id,d['teacher']) for id,d in docs.items()}
 questions={q['id']:{**q,'answers':[]} for q in registry['questions']};records={};invalid=[]
 oldp=private/'teaching-faq-review.json';old={r['video_id']:r for r in json.loads(oldp.read_text()).get('recordings',[])} if oldp.exists() else {}
 for id,d in docs.items():
  scanned=db.execute('select hash,candidate_count,scanned_at from sources where id=?',(id,)).fetchone();refs=d.get('catalog',{}).get('references',[]);lesson='; '.join(x.get('title','') for x in refs) or d.get('catalog_title') or d.get('catalog',{}).get('title',id)
  records[id]=dict(video_id=id,teacher=teachers[id],catalog_teacher=d.get('catalog_teacher'),lesson=lesson,kind=kinds[id],transcript_sha256=scanned[0],source_sha256=d['source_sha256'],scan_status='scanned_candidates_only',candidate_count=scanned[1],scanned_at=scanned[2],review_status='teacher_confirmation_pending' if kinds[id]=='topical' and id not in confirmed else 'pending',question_ids=[],reviewed_ranges=[],stale_question_ids=[],present=True,history=old.get(id,{}).get('history',[]))
  if old.get(id,{}).get('transcript_sha256') not in (None,scanned[0]):records[id]['history'].append(dict(event='source_changed',previous_hash=old[id]['transcript_sha256'],at=now))
 for id,r in old.items():
  if id not in records:records[id]={**r,'present':False,'review_status':'source_missing_needs_review'}
 for o in registry['occurrences']:
  id=o['video_id'];q=questions[o['question_id']];r=records.get(id)
  if id not in docs or not r or r['transcript_sha256']!=o['transcript_sha256'] or teachers[id]!=o['teacher']:
   invalid.append(dict(video_id=id,question_id=q['id'],reason='source_missing_changed_or_teacher_mismatch'))
   if r:r['review_status']='source_changed_needs_review';r['stale_question_ids'].append(q['id'])
   continue
  if (kinds[id]=='topical' and id not in confirmed) or o['teacher'] not in ['Arnold Murray','Dennis Murray']:continue
  assert 0<=o['start']<o['end']<=docs[id]['duration']+.01
  source=dict(video_id=id,teacher=o['teacher'],lesson=r['lesson'],start_seconds=o['start'],end_seconds=o['end'],transcript_sha256=r['transcript_sha256'],source_sha256=r['source_sha256'],review_status=o['review_status'],recording_group=o['recording_group'])
  answer=next((a for a in q['answers'] if a['id']==o['variant'] and a['summary']==o['summary']),None)
  if answer is None:
   answer_id=o['variant'] if not any(a['id']==o['variant'] for a in q['answers']) else o['variant']+'-'+hashlib.sha256(o['summary'].encode()).hexdigest()[:10]
   answer=dict(id=answer_id,teacher=o['teacher'],summary=o['summary'],kind='editorial_paraphrase',scripture_mentions=o['scripture_mentions'],relationship='initial_answer' if not q['answers'] else 'additional_reviewed_answer',sources=[]);q['answers'].append(answer)
  if not any(s['video_id']==id and s['start_seconds']==o['start'] and s['end_seconds']==o['end'] for s in answer['sources']):answer['sources'].append(source)
  if q['id'] not in r['question_ids']:r['question_ids'].append(q['id'])
  r['reviewed_ranges'].append(dict(question_id=q['id'],start_seconds=o['start'],end_seconds=o['end'],review='caption_passage_checked_audio_pending'));r['review_status']='partially_reviewed'
 # Explicit, hash-bound recording review evidence is independent of occurrences.
 # A complete caption Q&A review does not imply independent audio verification.
 for evidence in registry.get('recording_reviews',[]):
  id=evidence['video_id'];r=records.get(id)
  if not r or id not in docs or (kinds[id]=='topical' and id not in confirmed):continue
  if evidence.get('transcript_sha256')!=r['transcript_sha256'] or evidence.get('teacher')!=r['teacher']:
   r['review_status']='source_changed_needs_review';r['stale_recording_review']=True;continue
  start=evidence.get('qa_start');end=evidence.get('qa_end');cursor=evidence.get('cursor_seconds')
  if not isinstance(start,(int,float)) or not isinstance(end,(int,float)) or not 0<=start<end<=docs[id]['duration']+.01:continue
  if not isinstance(cursor,(int,float)) or not start<=cursor<=end:continue
  ranges=sorted(evidence.get('reviewed_ranges',[]),key=lambda x:x['start']);covered=start
  for span in ranges:
   if not start<=span['start']<span['end']<=end or span['start']>covered+.01:break
   covered=max(covered,span['end'])
  r['recording_review']=evidence;r['cursor_seconds']=cursor
  complete=(evidence.get('qa_boundaries_confirmed') is True and evidence.get('all_listener_questions_reviewed') is True and not evidence.get('unresolved_ranges') and covered>=end-.01 and cursor>=end-.01)
  r['review_status']='fully_reviewed' if complete else 'partially_reviewed'
 questions=list(questions.values())
 for q in questions:
  sources=[s for a in q['answers'] for s in a['sources']];q['asked_count']=frequency(sources);q['source_upload_count']=len({s['video_id'] for s in sources});q['count_basis']='distinct_recording_groups_in_reviewed_passages';q['frequency_scope']='lower_bound_not_full_archive_frequency'
 questions.sort(key=lambda q:(-q['asked_count'],q['question'].casefold()))
 for i,q in enumerate(questions,1):q['rank']=i
 counts=collections.Counter(r['review_status'] for r in records.values());review=dict(available=len(records),partially_reviewed=counts['partially_reviewed'],fully_reviewed=counts['fully_reviewed'],completion_basis='complete_caption_QA_review_not_audio_verification',scanned=len(records),teacher_pending=counts['teacher_confirmation_pending'],pending=counts['pending'],source_changed=len(invalid),question_occurrences=sum(q['asked_count'] for q in questions))
 data=dict(schema='griffin-faq-v2',updated=now,authority_policy='Arnold Murray primary; Dennis Murray clearly attributed secondary. Preserve variants; never combine different claims as a quotation.',frequency_policy='Most asked among reviewed passages. One count per question per distinct recording group. Alternate uploads count once. These are lower bounds while review continues.',questions=questions)
 ledger=dict(schema='griffin-faq-review-v2',updated=now,policy='Scanned is not reviewed. Only listed time ranges were reviewed. Changed hashes invalidate linked approvals; new files enter candidate review. Full transcript text stays private.',recordings=list(records.values()),review=review)
 (dist/'teaching-faq.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));(dist/'teaching-faq-review.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2));(private/'teaching-faq-review.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
 browser={**data,'review':review,'recordings':[{k:r.get(k) for k in ['video_id','teacher','lesson','kind','review_status','question_ids']} for r in ledger['recordings']]};(dist/'teaching-faq-data.js').write_text('window.GRIFFIN_FAQ='+json.dumps(browser,ensure_ascii=False).replace('<','\\u003c')+';\n')
 report=dict(updated=now,sources=len(docs),new_scans=new,changed_scans=changed,unchanged_scans=unchanged,questions=len(questions),review=review,invalid_approvals=invalid,ranked_questions=[dict(id=q['id'],count=q['asked_count']) for q in questions]);(private/'faq-update-report.json').write_text(json.dumps(report,indent=2));db.close();return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--library',required=True,type=Path);p.add_argument('--dist',required=True,type=Path);p.add_argument('--registry',type=Path,default=(Path(__file__).resolve().parents[1]/'reviewed-occurrences.json' if (Path(__file__).resolve().parents[1]/'reviewed-occurrences.json').exists() else Path(__file__).resolve().parent/'reviewed-occurrences.json'));a=p.parse_args();print(json.dumps(build(a.library,a.dist,a.registry),indent=2))


