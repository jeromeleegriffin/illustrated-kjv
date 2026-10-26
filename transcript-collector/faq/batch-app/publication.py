"""Prepare private FAQ proposals and a local preview; never grant public approval."""
import collections, hashlib, html, json, math, re
from core import ALLOWED_TEACHERS, finite
from review import CHECK_VERSION, named_teacher, normalize

def slim_registry(registry):
 fields=('question_id','video_id','teacher','start','end','transcript_sha256','recording_group')
 return {'schema':'griffin-approved-reference-index-v1','questions':registry.get('questions',[]),
  'occurrences':[{k:o[k] for k in fields if k in o} for o in registry.get('occurrences',[])],
  'duplicate_recording_aliases':registry.get('duplicate_recording_aliases',{}),
  'policy':'Reference snapshot only. Refresh against the current approved registry before publication.'}

def prepare_publication(review,reference,source_reader):
 question_index=collections.defaultdict(list)
 for q in reference.get('questions',[]):question_index[normalize(q['question'])].append(q)
 prior=collections.defaultdict(list)
 prior_groups=collections.defaultdict(list)
 aliases=reference.get('duplicate_recording_aliases',{})
 for o in reference.get('occurrences',[]):
  prior[o['video_id']].append(o)
  prior_groups[o.get('recording_group',aliases.get(o['video_id'],o['video_id']))].append(o)
 proposals=[];held=[];seen=set();baseline=hashlib.sha256(json.dumps(reference,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
 for group in review.get('groups',[]):
  video=group['video_id'];source_hash=group['transcript_sha256'];variants=group['variants']
  good=[v for v in variants if v.get('state')=='machine_checked_for_final_review']
  entry={'video_id':video,'transcript_sha256':source_hash,'question_first_cue':group['question_first_cue'],'candidate_keys':[v['candidate_key'] for v in variants],'public_approved':False}
  def hold(reason):held.append({**entry,'reason':reason})
  if not good:hold('no_candidate_passed_automatic_checks');continue
  checked_answers={' '.join(v['proposal'].get('answer','').split()).casefold() for v in good}
  if len(checked_answers)!=1:hold('different_checked_answer_variants_need_reconciliation');continue
  v=max(good,key=lambda x:len(x['proposal'].get('answer','')));q=v['proposal'];check=v.get('check') or {}
  verdict=check.get('verdict',{})
  if check.get('check_version')!=CHECK_VERSION or verdict.get('kind')!='listener_question' or any(verdict.get(k) is not True for k in ('question_supported','answer_supported','answer_complete','qualification_preserved')):
   hold('missing_or_outdated_check_evidence');continue
  try:d=source_reader(video,source_hash)
  except (ValueError,KeyError,OSError):hold('source_missing_or_hash_mismatch');continue
  teacher=d['teacher'];presenter,basis=named_teacher(d)
  if teacher not in ALLOWED_TEACHERS or presenter!=teacher or basis!='named_caption_introduction':hold('presenter_requires_confirmation');continue
  start=q.get('start');end=q.get('end')
  if not finite(start) or not finite(end) or not 0<=start<end<=d['duration']+.1:hold('invalid_timestamp_range');continue
  try:
   q0,q1,a0,a1=[q[k] for k in ('question_first_cue','question_last_cue','answer_first_cue','answer_last_cue')]
   if any(type(i) is not int for i in (q0,q1,a0,a1)) or not 0<=q0<=q1<=a0<=a1<len(d['segments']):raise ValueError()
   if q['evidence']['question']!=d['segments'][q0:q1+1] or q['evidence']['answer']!=d['segments'][a0:a1+1]:raise ValueError()
   if start!=d['segments'][q0]['start'] or end!=d['segments'][a1]['end']:raise ValueError()
  except (KeyError,ValueError,TypeError):hold('caption_evidence_or_timestamp_anchor_mismatch');continue
  if not re.fullmatch(r'[A-Za-z0-9_-]{11}',video) or not re.fullmatch(r'[a-f0-9]{64}',source_hash):hold('invalid_source_identity');continue
  if not q.get('question') or not q.get('answer') or len(q['answer'].split())>90 or q.get('uncertainty'):hold('incomplete_or_uncertain_paraphrase');continue
  matches=question_index.get(normalize(q['question']),[])
  if len(matches)>1:hold('ambiguous_existing_question_group');continue
  existing=matches[0] if matches else None
  overlaps=[]
  for old in prior.get(video,[]):
   if old.get('transcript_sha256')!=source_hash or old.get('teacher')!=teacher:continue
   overlap=max(0,min(end,old['end'])-max(start,old['start']))
   if overlap/max(.01,min(end-start,old['end']-old['start']))>=.8:overlaps.append(old)
  if overlaps:
   entry['existing_question_ids']=sorted({o['question_id'] for o in overlaps});hold('overlaps_previously_reviewed_source_answer');continue
  # Do not align timestamps between alternate uploads without evidence.
  alias=aliases.get(video,video)
  if any(o['video_id']!=video for o in prior_groups.get(alias,[])):hold('alternate_upload_requires_alignment');continue
  norm=normalize(q['question']);qid=existing['id'] if existing else 'proposal-'+hashlib.sha256(norm.encode()).hexdigest()[:16]
  key=(video,source_hash,q0,norm,normalize(q['answer']))
  if key in seen:hold('exact_duplicate_proposal');continue
  seen.add(key)
  proposals.append({**entry,'question_id':qid,'question':existing['question'] if existing else q['question'],
   'grouping_basis':'exact_existing_question_wording' if existing else 'provisional_exact_wording_group',
   'topic':existing.get('topic','Listener questions') if existing else 'Listener questions','teacher':teacher,
   'summary':q['answer'],'start':start,'end':end,'recording_group':alias,'preferred_candidate_key':v['candidate_key'],
   'source_url':f'https://www.youtube.com/watch?v={video}&t={math.floor(start)}s','status':'prepared_machine_proposal_requires_final_review'})
 counts=collections.defaultdict(set)
 for p in proposals:counts[p['question_id']].add(p['recording_group'])
 proposals.sort(key=lambda p:(-len(counts[p['question_id']]),p['question'].casefold(),p['teacher']!='Arnold Murray',p['video_id'],p['start']))
 for rank,p in enumerate(proposals,1):p['preview_number']=rank;p['provisional_recording_count']=len(counts[p['question_id']])
 report={'schema':'griffin-publication-preflight-v1','public_approved':False,'reference_snapshot_sha256':baseline,
  'reference_questions':len(reference.get('questions',[])),'reference_occurrences':len(reference.get('occurrences',[])),
  'input_question_clusters':len(review.get('groups',[])),'prepared_proposals':len(proposals),'held_clusters':len(held),
  'hold_reasons':dict(collections.Counter(h['reason'] for h in held)),
  'checks':['current typed second-pass verdict','named presenter matches catalog','original source hash','exact caption evidence and timestamps','bounded paraphrase','previous approved source overlap','retained variants','fixed HTTPS timestamp links'],
  'required_before_live':['final semantic review','reconcile provisional or changed groups against CURRENT registry','preserve answer differences and aliases','run official FAQ generator and tests','publish only the separate FAQ assets'],
  'policy':'Private preparation only. No approved registry or public assets were modified. Provisional counts are not published FAQ frequencies; a machine pass does not prove full Q&A coverage or audio verification.'}
 return {'schema':'griffin-prepared-faq-proposals-v1','public_approved':False,'proposals':proposals,'held':held},report

def render_preview(bundle,report):
 cards=[]
 for p in bundle['proposals']:
  cards.append('<article hidden><h2>'+html.escape(p['question'])+'</h2><p>'+html.escape(p['summary'])+'</p><p><a target="_blank" rel="noreferrer" href="'+html.escape(p['source_url'],quote=True)+'">'+html.escape(p['teacher']+' · '+p['video_id']+' · '+str(math.floor(p['start']))+'s')+'</a></p><small>Machine proposal — final review required. '+html.escape(p['grouping_basis'])+'.</small></article>')
 empty='<p>No proposals passed preparation yet. Pending checks and held material remain in the private results package.</p>' if not cards else ''
 return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Private FAQ publication preview</title><style>body{font:18px system-ui;margin:0;background:#f5f7fa;color:#172735}header,footer{position:fixed;left:0;right:0;padding:12px;background:#fff;border-bottom:1px solid #ccc;display:flex;gap:12px;justify-content:center;align-items:center}header{top:0}footer{bottom:0;border-top:1px solid #ccc}main{max-width:850px;margin:85px auto 100px;padding:0 20px}button{padding:10px 20px;font:inherit}h2{font-size:26px}article{background:white;border:1px solid #ddd;border-radius:8px;padding:20px}small{line-height:1.6}</style><header><button class="prev">Previous</button><span class="position"></span><button class="next">Next</button></header><main><p><strong>Private preview — not approved or published.</strong> Review the proposed answer and its source before publication. Counts and exact-wording groups are provisional.</p>'''+empty+''.join(cards)+'''</main><footer><button class="prev">Previous</button><span class="position"></span><button class="next">Next</button></footer><script>let page=0;const cards=[...document.querySelectorAll('article')];function show(){cards.forEach((c,i)=>c.hidden=i!==page);document.querySelectorAll('.position').forEach(x=>x.textContent=cards.length?(page+1)+' / '+cards.length:'0 / 0');document.querySelectorAll('.prev').forEach(x=>x.disabled=page===0);document.querySelectorAll('.next').forEach(x=>x.disabled=page+1>=cards.length);scrollTo(0,0)}document.querySelectorAll('.prev').forEach(b=>b.onclick=()=>{page--;show()});document.querySelectorAll('.next').forEach(b=>b.onclick=()=>{page++;show()});show();</script></html>'''
