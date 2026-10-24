"""Track new/changed private transcripts without publishing transcript content.
python scripts/faq_review.py --transcripts PRIVATE/transcripts --faq dist/teaching-faq.json --ledger dist/teaching-faq-review.json
A scan queues review. It never declares a full lesson reviewed or invents answers.
"""
import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone

def sha(raw): return hashlib.sha256(raw).hexdigest()
def sync(folder, faq, previous):
    records = {r['video_id']:dict(r) for r in previous.get('recordings', [])}
    evidence = {}
    for q in faq['questions']:
        for answer in q['answers']:
            for s in answer['sources']: evidence.setdefault(s['video_id'], []).append((q['id'], s))
    seen=set()
    for path in sorted(Path(folder).glob('*.json')):
        raw=path.read_bytes();d=json.loads(raw);vid=d['id']
        if vid in seen: raise ValueError('Duplicate transcript ID: '+vid)
        if d['teacher'] not in ('Arnold Murray','Dennis Murray') or not d.get('segments'): raise ValueError('Invalid transcript: '+vid)
        seen.add(vid); fingerprint=sha(raw); old=records.get(vid,{}); changed=bool(old.get('transcript_sha256') and old['transcript_sha256']!=fingerprint)
        refs=evidence.get(vid,[])
        stale=[qid for qid,s in refs if s['transcript_sha256']!=fingerprint]
        history=list(old.get('history',[]))
        if changed: history.append({'previous_sha256':old['transcript_sha256'],'previous_status':old.get('review_status'),'changed_at':datetime.now(timezone.utc).isoformat()})
        status='changed_needs_review' if changed or stale else old.get('review_status','pending')
        if status=='pending' and refs and not stale:status='partially_reviewed'
        records[vid]={'video_id':vid,'teacher':d['teacher'],'lesson':'; '.join(x['title'] for x in d['catalog']['references']), 'transcript_sha256':fingerprint,'source_sha256':d.get('source_sha256'), 'review_status':status,'question_ids':sorted({qid for qid,_ in refs}),'reviewed_ranges':[{'question_id':qid,'start_seconds':source['start_seconds'],'end_seconds':source['end_seconds'],'review_status':source['review_status']} for qid,source in refs],'stale_question_ids':sorted(set(stale)),'present':True,'history':history}
    for vid,r in records.items():
        if vid not in seen:r['present']=False;r['review_status']='source_missing'
    return {'schema':'griffin-faq-review-v1','updated':datetime.now(timezone.utc).isoformat(),'policy':'Scan is not completed Q&A review. Changed/missing sources need review; original answer variants are preserved. Full review must be explicitly recorded after checking all Q&A. No private transcript text stored here.','recordings':sorted(records.values(),key=lambda r:r['video_id'])}

def write_atomic(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(path)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--transcripts',required=True);p.add_argument('--faq',required=True);p.add_argument('--ledger',required=True);a=p.parse_args()
    faq=json.loads(Path(a.faq).read_text());dest=Path(a.ledger);old=json.loads(dest.read_text()) if dest.exists() else {};ledger=sync(a.transcripts,faq,old);write_atomic(dest,ledger)
    bundle={'questions':faq['questions'],'review':{'available':len([r for r in ledger['recordings'] if r['present']]),'fully_reviewed':sum(r['review_status']=='fully_reviewed' for r in ledger['recordings']),'partially_reviewed':sum(r['review_status']=='partially_reviewed' for r in ledger['recordings']),'needs_review':sum(r['review_status'] not in ('fully_reviewed',) for r in ledger['recordings'])}}
    bundle['recordings']=ledger['recordings']
    tracked={r['video_id']:r for r in ledger['recordings']}
    for q in bundle['questions']:
        for answer in q['answers']:
            for source in answer['sources']:
                r=tracked.get(source['video_id'],{})
                if not r.get('present') or r.get('transcript_sha256')!=source['transcript_sha256']:source['review_status']='source_changed_needs_review'
    js=dest.parent/'teaching-faq-data.js';text='window.GRIFFIN_FAQ = '+json.dumps(bundle,ensure_ascii=False).replace('<','\\u003c')+';\n';tmp=js.with_suffix('.tmp');tmp.write_text(text,encoding='utf-8');tmp.replace(js)
    print(json.dumps(bundle['review']))
if __name__=='__main__':main()
