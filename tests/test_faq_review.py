import sys,unittest,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from faq_review import sync,sha
class ReviewTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.path=self.root/'one.json';self.payload={'id':'abcdefghijk','teacher':'Arnold Murray','source_sha256':'abc','catalog':{'references':[{'title':'Genesis 1'}]},'segments':[{'start':0,'end':1,'text':'Original words'}]};self.path.write_text(json.dumps(self.payload));self.faq={'questions':[{'id':'q1','answers':[{'sources':[{'video_id':'abcdefghijk','transcript_sha256':sha(self.path.read_bytes()),'start_seconds':0,'end_seconds':1,'review_status':'caption_passage_checked_audio_pending'}]}]}]}
 def tearDown(self):self.tmp.cleanup()
 def test_new_then_repeat_scan(self):
  a=sync(self.root,self.faq,{});self.assertEqual(a['recordings'][0]['review_status'],'partially_reviewed');b=sync(self.root,self.faq,a);self.assertEqual(a['recordings'],b['recordings'])
 def test_new_file_queues_without_claiming_review(self):
  a=sync(self.root,{'questions':[]},{});self.assertEqual(a['recordings'][0]['review_status'],'pending')
 def test_changed_source_preserves_history_and_flags_answer(self):
  a=sync(self.root,self.faq,{});self.payload['segments'][0]['text']='Changed words';self.path.write_text(json.dumps(self.payload));b=sync(self.root,self.faq,a);r=b['recordings'][0];self.assertEqual(r['review_status'],'changed_needs_review');self.assertEqual(r['stale_question_ids'],['q1']);self.assertEqual(len(r['history']),1);self.assertEqual(self.faq['questions'][0]['answers'][0]['sources'][0]['transcript_sha256'],a['recordings'][0]['transcript_sha256'])
 def test_missing_source_not_silently_removed(self):
  a=sync(self.root,self.faq,{});self.path.unlink();b=sync(self.root,self.faq,a);self.assertEqual(b['recordings'][0]['review_status'],'source_missing');self.assertFalse(b['recordings'][0]['present'])
 def test_full_review_not_inferred_but_existing_explicit_status_preserved(self):
  a=sync(self.root,self.faq,{});a['recordings'][0]['review_status']='fully_reviewed';self.assertEqual(sync(self.root,self.faq,a)['recordings'][0]['review_status'],'fully_reviewed')
if __name__=='__main__':unittest.main()
