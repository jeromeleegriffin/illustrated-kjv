import json, tempfile, unittest
from pathlib import Path
from scripts.prepare_catalog import prepare
class RunnerTest(unittest.TestCase):
 def test_catalog_and_teacher_filter(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'bible-teaching.json'; out=Path(td)/'catalog.json'
   p.write_text(json.dumps({'books':[{'name':'Genesis','lessons':[{'id':'2F0K2ip_82U','url':'https://www.youtube.com/watch?v=2F0K2ip_82U','teacher':'Arnold Murray'}]}]}))
   rows=prepare(p,out)
   self.assertEqual(len(rows),1)
   self.assertEqual(rows[0]['teacher'],'Arnold Murray')
