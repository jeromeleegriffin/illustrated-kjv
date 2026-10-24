import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('faq',(Path(__file__).parents[1]/'scripts/update_faq.py' if (Path(__file__).parents[1]/'scripts/update_faq.py').exists() else Path(__file__).parents[1]/'update_faq.py'));faq=importlib.util.module_from_spec(spec);spec.loader.exec_module(faq)
class Tracking(unittest.TestCase):
 def test_duplicate_uploads_count_once(self):
  self.assertEqual(faq.frequency([{'video_id':'one','recording_group':'same'},{'video_id':'two','recording_group':'same'},{'video_id':'three'}]),2)
 def test_resume_new_source_and_changed_approval(self):
  with tempfile.TemporaryDirectory() as t:
   b=Path(t);folder=b/'search-library/transcripts';folder.mkdir(parents=True);p=folder/'aaaaaaaaaaa.json'
   d=dict(id='aaaaaaaaaaa',teacher='Arnold Murray',source_sha256='source',duration=2000,catalog={'references':[]},segments=[{'start':1900,'end':1910,'text':'Question: will we know our family?'}]);p.write_text(json.dumps(d))
   reg=b/'registry.json';reg.write_text(json.dumps({'questions':[{'id':'family','question':'Family?','topic':'Family'}],'occurrences':[dict(question_id='family',video_id=d['id'],start=1900,end=1910,teacher=d['teacher'],variant='v',summary='A reviewed paraphrase.',scripture_mentions=[],transcript_sha256=faq.digest(p),recording_group=d['id'],review_status='caption_passage_checked_audio_pending')]}))
   a=faq.build(b,b/'out',reg);self.assertEqual(a['new_scans'],1);self.assertEqual(a['ranked_questions'][0]['count'],1)
   a=faq.build(b,b/'out',reg);self.assertEqual(a['unchanged_scans'],1);self.assertEqual(a['new_scans'],0)
   d['segments'][0]['text']='Changed words';p.write_text(json.dumps(d));a=faq.build(b,b/'out',reg);self.assertEqual(a['changed_scans'],1);self.assertEqual(a['ranked_questions'][0]['count'],0);self.assertEqual(len(a['invalid_approvals']),1)
   d['id']='bbbbbbbbbbb';(folder/'bbbbbbbbbbb.json').write_text(json.dumps(d));a=faq.build(b,b/'out',reg);self.assertEqual(a['new_scans'],1)
if __name__=='__main__':unittest.main()
