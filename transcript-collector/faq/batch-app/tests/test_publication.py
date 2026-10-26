import copy,json,sys,unittest,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from publication import prepare_publication,render_preview,slim_registry
from review import CHECK_VERSION
from test_review_pipeline import sample,GOOD

def fixture():
 d,q=sample();h='a'*64
 check={'check_version':CHECK_VERSION,'verdict':GOOD.copy(),'public_approved':False}
 v={'candidate_key':'k1','video_id':d['id'],'transcript_sha256':h,'proposal':q,'check':check,'state':'machine_checked_for_final_review'}
 review={'groups':[{'video_id':d['id'],'transcript_sha256':h,'question_first_cue':q['question_first_cue'],'variants':[v]}]}
 reference={'questions':[{'id':'rest','question':'What is rest?','topic':'Christian living'}],'occurrences':[]}
 def source(video,digest):
  assert video==d['id'] and digest==h
  return d
 return d,q,review,reference,source

class PublicationTests(unittest.TestCase):
 def test_existing_exact_group_staged_without_approval(self):
  d,q,r,ref,src=fixture();out,report=prepare_publication(r,ref,src)
  self.assertEqual(report['prepared_proposals'],1);p=out['proposals'][0];self.assertEqual(p['question_id'],'rest');self.assertFalse(p['public_approved']);self.assertFalse(report['public_approved']);self.assertIn('&t=250s',p['source_url']);self.assertEqual(ref['occurrences'],[])
 def test_matching_prior_source_overlap_not_counted_again(self):
  d,q,r,ref,src=fixture();ref['occurrences']=[{'video_id':d['id'],'teacher':d['teacher'],'transcript_sha256':'a'*64,'question_id':'rest','start':249,'end':270}]
  out,report=prepare_publication(r,ref,src);self.assertEqual(report['prepared_proposals'],0);self.assertEqual(out['held'][0]['reason'],'overlaps_previously_reviewed_source_answer');self.assertEqual(out['held'][0]['existing_question_ids'],['rest'])
 def test_changed_prior_hash_does_not_hide_new_source(self):
  d,q,r,ref,src=fixture();ref['occurrences']=[{'video_id':d['id'],'teacher':d['teacher'],'transcript_sha256':'b'*64,'question_id':'rest','start':249,'end':270}]
  out,report=prepare_publication(r,ref,src);self.assertEqual(report['prepared_proposals'],1)
 def test_different_checked_variants_preserved_for_reconciliation(self):
  d,q,r,ref,src=fixture();v=copy.deepcopy(r['groups'][0]['variants'][0]);v['candidate_key']='k2';v['proposal']['answer']='A different answer.';r['groups'][0]['variants'].append(v)
  out,report=prepare_publication(r,ref,src);self.assertEqual(report['prepared_proposals'],0);self.assertEqual(len(out['held'][0]['candidate_keys']),2)
 def test_bad_timestamps_and_altered_captions_held(self):
  for kind in ('timestamp','evidence'):
   d,q,r,ref,src=fixture()
   if kind=='timestamp':q['start']=251
   else:q['evidence']['answer']=[{'start':260,'end':269,'text':'fabricated'}]
   out,report=prepare_publication(r,ref,src);self.assertEqual(report['prepared_proposals'],0);self.assertIn('anchor_mismatch',out['held'][0]['reason'])
 def test_punctuation_variants_not_silently_collapsed(self):
  d,q,r,ref,src=fixture();v=copy.deepcopy(r['groups'][0]['variants'][0]);v['candidate_key']='other';v['proposal']['answer']=q['answer'].rstrip('.')+'?';r['groups'][0]['variants'].append(v)
  self.assertEqual(prepare_publication(r,ref,src)[0]['held'][0]['reason'],'different_checked_answer_variants_need_reconciliation')
 def test_unknown_presenter_never_prepared(self):
  d,q,r,ref,src=fixture();d['segments'][0]['text']='Welcome.';out,report=prepare_publication(r,ref,src);self.assertEqual(report['prepared_proposals'],0)
 def test_outdated_check_rules_and_failed_verdict_held(self):
  for change in ('version','verdict'):
   d,q,r,ref,src=fixture();c=r['groups'][0]['variants'][0]['check']
   if change=='version':c['check_version']='older'
   else:c['verdict']['answer_supported']=False
   self.assertEqual(prepare_publication(r,ref,src)[1]['prepared_proposals'],0)
 def test_missing_source_is_specific_hold(self):
  d,q,r,ref,src=fixture()
  def missing(*args):raise FileNotFoundError()
  out,report=prepare_publication(r,ref,missing);self.assertEqual(out['held'][0]['reason'],'source_missing_or_hash_mismatch')
 def test_ambiguous_group_not_forced(self):
  d,q,r,ref,src=fixture();ref['questions'].append({'id':'rest2','question':'What is rest?'})
  self.assertEqual(prepare_publication(r,ref,src)[0]['held'][0]['reason'],'ambiguous_existing_question_group')
 def test_unknown_exact_wording_group_is_stable_provisional(self):
  d,q,r,ref,src=fixture();ref['questions']=[];a=prepare_publication(r,ref,src)[0]['proposals'][0];b=prepare_publication(r,ref,src)[0]['proposals'][0];self.assertEqual(a['question_id'],b['question_id']);self.assertEqual(a['grouping_basis'],'provisional_exact_wording_group')
 def test_known_alternate_upload_requires_alignment(self):
  d,q,r,ref,src=fixture();ref['duplicate_recording_aliases']={d['id']:'0123456789_'};ref['occurrences']=[{'video_id':'0123456789_'}]
  self.assertEqual(prepare_publication(r,ref,src)[0]['held'][0]['reason'],'alternate_upload_requires_alignment')
 def test_preview_escapes_user_text_and_has_fixed_navigation(self):
  d,q,r,ref,src=fixture();q['answer']='Arnold says <img src=x onerror=alert(1)>.';out,report=prepare_publication(r,ref,src);page=render_preview(out,report);self.assertIn('&lt;img',page);self.assertNotIn('<img',page);self.assertIn('position:fixed',page);self.assertEqual(page.count('class="next"'),2);self.assertIn('not approved or published',page)
 def test_slim_reference_never_includes_private_evidence(self):
  r=slim_registry({'questions':[],'occurrences':[{'video_id':'abcdefghijk','summary':'long prose','evidence':'private captions','transcript_sha256':'a'*64}]})
  self.assertNotIn('evidence',r['occurrences'][0]);self.assertNotIn('summary',r['occurrences'][0])
 def test_canonical_upload_with_reviewed_alias_also_held(self):
  d,q,r,ref,src=fixture();ref['duplicate_recording_aliases']={'0123456789_':d['id']};ref['occurrences']=[{'video_id':'0123456789_','recording_group':d['id']}]
  self.assertEqual(prepare_publication(r,ref,src)[0]['held'][0]['reason'],'alternate_upload_requires_alignment')
 def test_repeat_preparation_is_idempotent(self):
  d,q,r,ref,src=fixture();a=prepare_publication(r,ref,src);b=prepare_publication(r,ref,src);self.assertEqual(a,b)

if __name__=='__main__':unittest.main()
