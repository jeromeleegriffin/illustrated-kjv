import importlib.util, tempfile, pathlib, unittest
s=importlib.util.spec_from_file_location('collector',pathlib.Path(__file__).resolve().parents[1]/'scripts'/'collector.py')
c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class CollectorTests(unittest.TestCase):
 def test_video_ids(self):
  self.assertEqual(c.vid('https://youtu.be/Loj1QDHxH3E?t=2'),'Loj1QDHxH3E')
  self.assertEqual(c.vid('https://www.youtube.com/watch?v=Loj1QDHxH3E&list=XYZ'),'Loj1QDHxH3E')
  self.assertIsNone(c.vid('https://example.com/?v=Loj1QDHxH3E'))
 def test_scan_unique(self):
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'videos.json';p.write_text('https://youtu.be/Loj1QDHxH3E https://www.youtube.com/watch?v=Loj1QDHxH3E')
   self.assertEqual(len(c.scan(p)),1)
 def test_vtt(self):
  sample='WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nSelf-control\n\n00:00:02.000 --> 00:00:03.000\nSelf-control\n\n00:00:04.000 --> 00:00:05.000\nGod is good'
  seg=c.parse_vtt(sample)
  self.assertEqual(len(seg),2);self.assertEqual(seg[1]['text'],'God is good')
if __name__=='__main__':unittest.main()
