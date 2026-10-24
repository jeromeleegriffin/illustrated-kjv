from test_review import faq
import unittest,tempfile,json
from pathlib import Path
class Completion(unittest.TestCase):
 def test_completion_cursor_resume_and_hash_invalidation(self):
  with tempfile.TemporaryDirectory() as t:
   b=Path(t);folder=b/'search-library/transcripts';folder.mkdir(parents=True);p=folder/'aaaaaaaaaaa.json';d=dict(id='aaaaaaaaaaa',teacher='Arnold Murray',source_sha256='s',duration=2000,catalog={'references':[]},segments=[dict(start=1900,end=1990,text='Question and answer')]);p.write_text(json.dumps(d))
   evidence=dict(video_id=d['id'],teacher=d['teacher'],transcript_sha256=faq.digest(p),qa_start=1900,qa_end=1990,cursor_seconds=1950,reviewed_ranges=[dict(start=1900,end=1950)],qa_boundaries_confirmed=True,all_listener_questions_reviewed=False,unresolved_ranges=[])
   r=dict(questions=[],occurrences=[],recording_reviews=[evidence]);reg=b/'reg.json'
   def run():
    reg.write_text(json.dumps(r));report=faq.build(b,b/'out',reg);record=json.loads((b/'out/teaching-faq-review.json').read_text())['recordings'][0];return report,record
   report,record=run();self.assertEqual(record['cursor_seconds'],1950);self.assertEqual(report['review']['fully_reviewed'],0)
   evidence.update(cursor_seconds=1990,all_listener_questions_reviewed=True,reviewed_ranges=[dict(start=1900,end=1990)])
   for _ in range(2):self.assertEqual(run()[0]['review']['fully_reviewed'],1)
   evidence['unresolved_ranges']=[dict(start=1960,end=1970)];self.assertEqual(run()[0]['review']['fully_reviewed'],0);evidence['unresolved_ranges']=[]
   evidence['reviewed_ranges']=[dict(start=1900,end=1950),dict(start=1960,end=1990)];self.assertEqual(run()[0]['review']['fully_reviewed'],0)
   evidence['reviewed_ranges']=[dict(start=1900,end=1990)];d['segments'][0]['text']='Changed';p.write_text(json.dumps(d));report,record=run();self.assertEqual(report['review']['fully_reviewed'],0);self.assertEqual(record['review_status'],'source_changed_needs_review')
