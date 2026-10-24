import unittest,tempfile,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_catalog import prepare
class ActualSchema(unittest.TestCase):
 def test_real_shape_and_verified_teacher(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'bible-teaching.json';out=Path(d)/'review.json'
   p.write_text(json.dumps({'books':[{'name':'Genesis','lessons':[{'id':'2F0K2ip_82U','teacher':'Arnold Murray','title':'Genesis 1:1 - 1:2','start':[1,1],'end':[1,2],'url':'https://www.youtube.com/watch?v=2F0K2ip_82U','official':True},{'id':'2F0K2ip_82U','teacher':'Arnold Murray','url':'https://www.youtube.com/watch?v=2F0K2ip_82U'},{'id':'aaaaaaaaaaa','teacher':'Other','url':'https://www.youtube.com/watch?v=aaaaaaaaaaa'}]}]}))
   rows=prepare(p,out); self.assertEqual(len(rows),1);doc=json.loads(out.read_text());self.assertEqual(doc['mapping_count'],3);self.assertEqual(len(doc['invalid']),1);self.assertEqual(doc['teacher_counts']['Arnold Murray'],1)
if __name__=='__main__':unittest.main()
