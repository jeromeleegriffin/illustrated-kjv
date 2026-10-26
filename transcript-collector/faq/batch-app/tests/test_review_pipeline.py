import json,sys,tempfile,unittest,zipfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import Store,windows,validate_result,sha
from review import ReviewQueue,check_candidate,build_review_package,fingerprint,named_teacher
from test_batch import document,archive

GOOD={'kind':'listener_question','question_supported':True,'answer_supported':True,'answer_complete':True,'qualification_preserved':True}
class Engine:
 model='test-only';hardware='cpu'
 def __init__(self,verdict=None):self.verdict=GOOD.copy() if verdict is None else verdict;self.calls=0
 def request(self,path,body):self.calls+=1;return {'done':True,'done_reason':'stop','response':json.dumps(self.verdict)}
def sample():
 d=document();d['segments'][0]['text']='And now here is Pastor Arnold Murray.'
 d['segments'][26]['text']='Arnold says rest is found in Christ, and encourages this listener to study.'
 q=validate_result(d,windows(d)[1],{'questions':[{'question_first_cue':25,'answer_first_cue':26,'answer_last_cue':26,'question':'What is rest?','answer':'Arnold encouraged the listener to find rest in Christ and study.','uncertainty':[]}],'notes':[]})[0]
 return d,q

class ReviewTests(unittest.TestCase):
 def test_positive_is_still_not_public_approval(self):
  d,q=sample();e=Engine();r=check_candidate(e,d,q)
  self.assertEqual(e.calls,1);self.assertEqual(r['status'],'machine_checked_for_final_review');self.assertFalse(r['public_approved'])
 def test_rhetorical_rejected_by_second_pass(self):
  d,q=sample();r=check_candidate(Engine({**GOOD,'kind':'rhetorical_teaching'}),d,q)
  self.assertEqual(r['status'],'held_for_review')
 def test_any_unsupported_claim_or_missing_qualification_holds(self):
  d,q=sample()
  for flag in ['question_supported','answer_supported','answer_complete','qualification_preserved']:
   self.assertEqual(check_candidate(Engine({**GOOD,flag:False}),d,q)['status'],'held_for_review')
 def test_presenter_conflict_holds_without_calling_model(self):
  d,q=sample();d['teacher']='Dennis Murray';e=Engine();r=check_candidate(e,d,q)
  self.assertEqual(e.calls,0);self.assertIn('caption_catalog_conflict',r['reasons'])
 def test_generic_arnold_intro_does_not_override_named_dennis(self):
  d,q=sample();d['teacher']='Dennis Murray';d['segments'][0]['text']='Family Bible Study Hour with Pastor Arnold Murray. And now here is Dennis Murray.'
  self.assertEqual(named_teacher(d),('Dennis Murray','named_caption_introduction'))
 def test_unknown_teacher_holds(self):
  d,q=sample();d['segments'][0]['text']='Welcome to Bible study.';e=Engine();r=check_candidate(e,d,q)
  self.assertEqual(e.calls,0);self.assertIn('named_presenter_unconfirmed',r['reasons'])
 def test_altered_evidence_and_extractor_flags_hold(self):
  d,q=sample();q['evidence']['answer']=[{'start':0,'end':1,'text':'fabricated'}];e=Engine();r=check_candidate(e,d,q)
  self.assertIn('evidence_does_not_match_source',r['reasons']);self.assertEqual(e.calls,0)
  d,q=sample();q['uncertainty']=['uncertain_word'];self.assertEqual(check_candidate(e,d,q)['status'],'held_for_review')
 def test_model_boolean_string_not_accepted(self):
  d,q=sample()
  with self.assertRaises(ValueError):check_candidate(Engine({**GOOD,'answer_supported':'true'}),d,q)
 def test_sync_resume_and_hash_change(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);d,q=sample();z=root/'in.zip';archive(z,d);s=Store(root/'data');s.import_zip(z);j=s.next_job();s.finish(j,[q],{})
   review=ReviewQueue(s);self.assertEqual(review.sync(),1);self.assertEqual(review.sync(),0)
   first=review.next();self.assertIsNotNone(first);reopened=ReviewQueue(s);self.assertEqual(reopened.next()['key'],first['key'])
   reopened.finish(first,{'status':'held_for_review','reasons':['test']});self.assertIsNone(reopened.next());self.assertEqual(reopened.status()['held_for_review'],1)
   d['segments'][0]['text']='Changed';archive(z,d);s.import_zip(z);reopened.sync();self.assertEqual(reopened.status(),{})
   with s.connect() as db:self.assertEqual(db.execute("SELECT count(*) FROM candidate_checks WHERE state='stale'").fetchone()[0],1)
 def test_grouping_retains_variants_without_auto_merge(self):
  d,q=sample();rows=[]
  for i in range(2):
   proposal={**q,'answer':q['answer']+str(i)};rows.append({'candidate_key':str(i),'video_id':d['id'],'transcript_sha256':'a'*64,'proposal':proposal,'state':'machine_checked_for_final_review'})
  r=build_review_package(rows,{'questions':[{'id':'rest','question':'What is rest?'}]})
  self.assertEqual(r['question_start_clusters'],1);g=r['groups'][0];self.assertEqual(len(g['variants']),2);self.assertFalse(g['public_approved']);self.assertEqual(g['likely_existing_groups'][0]['status'],'suggestion_not_approved_merge')
 def test_new_check_rules_invalidate_previous_automatic_decision(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);d,q=sample();z=root/'in.zip';archive(z,d);s=Store(root/'data');s.import_zip(z);j=s.next_job();s.finish(j,[q],{});v=ReviewQueue(s);v.sync();job=v.next();v.finish(job,{'status':'machine_checked_for_final_review'})
   with s.connect() as db:db.execute("UPDATE candidate_checks SET version='older-check-rules'")
   v=ReviewQueue(s);self.assertEqual(v.status()['pending'],1);self.assertIsNone(v.next()['result'])
 def test_self_contained_export_and_hash_guard(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);d,q=sample();z=root/'in.zip';archive(z,d);s=Store(root/'data');s.import_zip(z);j=s.next_job();s.finish(j,[q],{});v=ReviewQueue(s);v.sync();job=v.next();v.finish(job,check_candidate(Engine(),d,q))
   s.export(root/'out.zip')
   with zipfile.ZipFile(root/'out.zip') as out:
    raw=out.read('sources/'+d['id']+'.json');self.assertEqual(sha(raw),j['source_hash']);p=json.loads(out.read('publication-review.json'));self.assertEqual(p['counts']['machine_checked_for_final_review'],1);self.assertFalse(p['public_approved']);self.assertIsNone(out.testzip())
   Path(j['source_path']).write_text('{}')
   with self.assertRaises(ValueError):s.export(root/'bad.zip')
 def test_controller_checks_legacy_saved_work_before_new_extraction(self):
  from app import Controller
  from unittest.mock import patch
  import app
  class CheckOnly(Engine):
   def __init__(self,*a):super().__init__()
   def extract(self,*a):raise AssertionError('Should pause before any new extraction')
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);d,q=sample();z=root/'in.zip';archive(z,d);s=Store(root/'data');s.import_zip(z);j=s.next_job();s.finish(j,[q],{})
   with patch.object(app,'Ollama',CheckOnly):
    c=Controller(root/'data');original=c.review.finish
    def finish(job,result):original(job,result);c.mode='paused'
    c.review.finish=finish
    try:
     c.mode='running';deadline=time.time()+5
     while c.mode!='paused' and time.time()<deadline:time.sleep(.02)
     self.assertEqual(c.review.status().get('machine_checked_for_final_review'),1);self.assertEqual(c.store.status()['windows']['saved'],1)
    finally:c.close()

if __name__=='__main__':unittest.main()
