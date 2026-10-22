import json, tempfile, unittest
from pathlib import Path
from scripts.collector import load_approved, parse_vtt, vid

class ApprovalTests(unittest.TestCase):
 def test_reject_empty(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'a.json'; f.write_text('{"approved_ids":[]}')
   with self.assertRaises(ValueError):load_approved(f)
 def test_only_valid_ids(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'a.json'; f.write_text('{"approved_ids":["Loj1QDHxH3E"]}')
   self.assertEqual(load_approved(f),{'Loj1QDHxH3E'})
 def test_vtt(self):
  txt='WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nSelf control\n\n00:00:02.000 --> 00:00:03.000\nSelf control\n'
  self.assertEqual(len(parse_vtt(txt)),1)
if __name__=='__main__':unittest.main()
