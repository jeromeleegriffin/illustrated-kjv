from test_review import faq
import unittest,tempfile,json,copy
from pathlib import Path

class TopicalConfirmation(unittest.TestCase):
 def test_only_hash_bound_caption_confirmation_allows_topical_answer(self):
  with tempfile.TemporaryDirectory() as t:
   b=Path(t);p=b/'topical-library/search-library/transcripts/aaaaaaaaaaa.json';p.parent.mkdir(parents=True)
   d=dict(id='aaaaaaaaaaa',teacher='Unconfirmed',catalog_teacher='Arnold Murray',source_sha256='raw-caption',duration=2000,catalog={'title':'A topical lesson'},segments=[dict(start=1,end=4,text='Family Bible study hour with Pastor Arnold Murray'),dict(start=1900,end=1910,text='Question and directly answered reply')]);p.write_text(json.dumps(d))
   evidence=dict(teacher='Arnold Murray',transcript_sha256=faq.digest(p),source_sha256='raw-caption',basis='captioned_program_introduction',caption_passage_read=True,start_index=0,end_index=1)
   r=dict(questions=[dict(id='q',question='Question?',topic='Topical')],occurrences=[dict(question_id='q',video_id=d['id'],teacher='Arnold Murray',variant='v',start=1900,end=1910,summary='Reviewed reply.',scripture_mentions=[],transcript_sha256=faq.digest(p),recording_group=d['id'],review_status='caption_passage_checked_audio_pending')])
   reg=b/'reg.json'
   def run():
    reg.write_text(json.dumps(r));report=faq.build(b,b/'out',reg);q=json.loads((b/'out/teaching-faq.json').read_text())['questions'][0];return report,q
   self.assertEqual(run()[1]['asked_count'],0)
   r['teacher_confirmations']={d['id']:evidence};self.assertEqual(run()[1]['asked_count'],1);self.assertEqual(run()[0]['review']['teacher_pending'],0)
   for field,bad in [('transcript_sha256','stale'),('source_sha256','other-raw'),('basis','approved_metadata_only'),('caption_passage_read',False),('start_index',-1),('end_index',9),('teacher','Dennis Murray')]:
    r['teacher_confirmations'][d['id']]=dict(evidence,**{field:bad});self.assertEqual(run()[1]['asked_count'],0,field)
   r['teacher_confirmations'][d['id']]=evidence;d['segments'][0]['text']='Changed caption';p.write_text(json.dumps(d));self.assertEqual(run()[1]['asked_count'],0)

if __name__=='__main__':unittest.main()
