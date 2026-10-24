import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from diagnostic_captions import probe
class DiagnosticTests(unittest.TestCase):
 def run_case(self,code=0,body=None,blocked=False):
  with tempfile.TemporaryDirectory() as tmp:
   def runner(command,**kwargs):
    state=Path(kwargs['env']['GRIFFIN_CAPTION_DIAGNOSTIC'])
    if not blocked:
     state.write_text(json.dumps({'video_id':'abcdefghijk','discovery':'completed','selection':'selected','tracks':[{'language':'en','generation':'authored caption'}]}))
     if body is not None:(state.parent/'abcdefghijk.en.vtt').write_text(body)
    return subprocess.CompletedProcess(command,code,'','HTTP Error 429 https://example.invalid?token=PRIVATE' if blocked else '')
   r=probe('abcdefghijk',Path(tmp),runner)
   self.assertNotIn('PRIVATE',json.dumps(r));return r
 def test_valid_saved(self):
  r=self.run_case(body='WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nExample caption\n')
  self.assertEqual(r['status'],'saved_quality_review');self.assertEqual(r['persistence'],'saved_and_reopened')
 def test_html_not_success(self):self.assertEqual(self.run_case(body='<html>Site unavailable</html>')['status'],'validation_failed')
 def test_selection_without_download(self):
  r=self.run_case();self.assertEqual(r['selection'],'selected');self.assertEqual(r['status'],'no_caption_saved')
 def test_block_redaction(self):
  r=self.run_case(code=1,blocked=True);self.assertEqual(r['status'],'rate_limited');self.assertEqual(r['discovery'],'not_confirmed')
 def test_partial_nonzero_not_success(self):
  r=self.run_case(code=1,body='WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nPartial text\n');self.assertEqual(r['status'],'request_failed')
