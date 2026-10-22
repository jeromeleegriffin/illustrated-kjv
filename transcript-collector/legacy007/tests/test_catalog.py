import sys,unittest,json,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_catalog import prepare
class CatalogTests(unittest.TestCase):
 def test_dedup(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/'bible-teaching.json';out=Path(d)/'out.json'
   src.write_text(json.dumps({'books':[{'name':'Genesis','lessons':[{'id':'Loj1QDHxH3E','teacher':'Arnold Murray','url':'https://www.youtube.com/watch?v=Loj1QDHxH3E'},{'id':'Loj1QDHxH3E','teacher':'Arnold Murray','url':'https://www.youtube.com/watch?v=Loj1QDHxH3E'}]}]}))
   rows=prepare(src,out);self.assertEqual(len(rows),1);self.assertEqual(json.loads(out.read_text())['total_distinct'],1)
if __name__=='__main__':unittest.main()
