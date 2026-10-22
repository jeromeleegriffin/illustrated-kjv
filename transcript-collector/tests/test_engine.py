import sys,tempfile,json,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import Library,parse_captions,process,atomic
from prepare_queue import prepare
class EngineTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  self.catalog=self.root/'catalog.json';atomic(self.catalog,{'books':[{'name':'Genesis','lessons':[{'id':'abcdefghijk','teacher':'Arnold Murray','title':'Genesis 1:1','start':[1,1],'end':[1,1]}]}]})
  self.lib=Library(self.root/'data',self.catalog)
 def tearDown(self):self.lib.close();self.temp.cleanup()
 def caption(self,text='In the beginning'):
  p=self.root/'abcdefghijk.vtt';p.write_text('WEBVTT\n\n00:00.000 --> 00:02.000\n'+text+'\n',encoding='utf-8');return p
 def test_caption_search_restart(self):
  self.lib.attach('abcdefghijk',self.caption(),'Synthetic test, not ministry speech');process(self.lib,'abcdefghijk')
  self.assertEqual(self.lib.row('abcdefghijk')['status'],'quality_review');self.assertEqual(len(self.lib.find('beginning')),1)
  self.lib.close();self.lib=Library(self.root/'data',self.catalog);self.assertEqual(self.lib.verify()['structurally_valid'],1)
 def test_corruption_detected(self):
  self.lib.attach('abcdefghijk',self.caption(),'Fixture');process(self.lib,'abcdefghijk');(self.root/'data/transcripts/abcdefghijk.json').write_text('{}')
  self.assertEqual(len(self.lib.verify()['failures']),1)
 def test_resume_does_not_lose_chunks(self):
  self.lib.status('abcdefghijk','transcribing');self.lib.save_chunk('abcdefghijk',0,0,3,[{'start':0,'end':3,'text':'fixture'}],[]);self.lib.recover()
  self.assertEqual(self.lib.row('abcdefghijk')['status'],'ready');self.assertEqual(self.lib.db.execute('SELECT count(*) FROM chunks').fetchone()[0],1)
 def test_missing_chunk_not_complete(self):
  self.lib.save_chunk('abcdefghijk',1,300,600,[{'start':300,'end':301,'text':'fixture'}],[])
  with self.assertRaises(ValueError):self.lib.export('abcdefghijk')
 def test_invalid_teacher_fails(self):
  d=json.loads(self.catalog.read_text());d['books'][0]['lessons'][0]['teacher']='Someone else';atomic(self.catalog,d)
  with self.assertRaises(ValueError):prepare(self.catalog)
 def test_wrong_source_rejected(self):
  p=self.caption();self.lib.attach('abcdefghijk',p,'Fixture');p.write_text('changed')
  with self.assertRaises(ValueError):process(self.lib,'abcdefghijk')
 def test_duplicate_caption_overlap(self):
  p=self.caption('hello world');p.write_text(p.read_text()+'\n00:01.000 --> 00:03.000\nhello world\n');s=parse_captions(p)
  self.assertEqual(len(s),1);self.assertEqual(s[0]['end'],3)
 def test_spoken_repetition_preserved(self):
  p=self.caption('hello');p.write_text(p.read_text()+'\n00:03.000 --> 00:04.000\nhello\n');self.assertEqual(len(parse_captions(p)),2)
 def test_srt_and_json(self):
  p=self.root/'a.srt';p.write_text('1\n00:00:01,000 --> 00:00:02,000\nText\n');self.assertEqual(parse_captions(p)[0]['start'],1)
  p=self.root/'a.json';atomic(p,{'content':[{'offset':1000,'duration':2000,'text':'Text'}]});self.assertEqual(parse_captions(p)[0]['end'],3)
 def test_empty_invalid_times(self):
  p=self.root/'a.json';atomic(p,[{'start':2,'end':1,'text':'Bad'}])
  with self.assertRaises(ValueError):parse_captions(p)
 def test_folder_import(self):
  self.caption();result=self.lib.import_folder(self.root,'Test fixture');self.assertIn('abcdefghijk',result['matched'])
 def test_search_injection_safe(self):self.assertEqual(self.lib.find('" OR * --'),[])
if __name__=='__main__':unittest.main()

class ProcessingTests(unittest.TestCase):
 setUp=EngineTests.setUp
 tearDown=EngineTests.tearDown
 caption=EngineTests.caption
 def test_chunk_resume_without_retranscription(self):
  from unittest.mock import patch
  from types import SimpleNamespace
  p=self.root/'audio.wav';p.write_bytes(b'fixture');self.lib.attach('abcdefghijk',p,'Synthetic audio adapter test')
  calls=[]
  class Model:
   def __init__(self,*a,**k):pass
   def transcribe(self,a,**kw):
    calls.append(a);return iter([SimpleNamespace(start=0,end=1,text='fixture speech',avg_logprob=0,no_speech_prob=0,compression_ratio=1)]),None
  chunks=[(0,0,2,'first'),(1,2,4,'second')]
  with patch('engine.audio_chunks',return_value=iter(chunks)):
   process(self.lib,'abcdefghijk','base.en',model_factory=Model,stop=lambda:len(calls)==1)
  self.assertEqual(self.lib.row('abcdefghijk')['status'],'ready')
  with patch('engine.audio_chunks',return_value=iter(chunks)):process(self.lib,'abcdefghijk','base.en',model_factory=Model)
  self.assertEqual(calls,['first','second']);self.assertEqual(self.lib.verify()['structurally_valid'],1)
 def test_source_manifest_teacher_guard(self):
  from sources import ingest_manifest
  p=self.root/'sources.json';atomic(p,{'sources':[{'id':'abcdefghijk','teacher':'Dennis Murray','identity_verified':True,'permission_basis':'fixture','identity_evidence':'fixture','path':str(self.caption())}]})
  result=ingest_manifest(self.lib,p);self.assertEqual(result[0]['status'],'source_review_needed');self.assertIsNone(self.lib.row('abcdefghijk')['source'])

class BrowserExportTests(unittest.TestCase):
 setUp=EngineTests.setUp
 tearDown=EngineTests.tearDown
 def test_start_only_export_restart_and_identity(self):
  p=self.root/'abcdefghijk.txt'
  p.write_text('YouTube transcript\nVideo ID: abcdefghijk\nLanguage: en\nCaptions: authored or unspecified\n\n[0:02] A synthetic opening\n[1:05] A synthetic closing\n')
  self.lib.attach('abcdefghijk',p,'Synthetic browser export fixture')
  process(self.lib,'abcdefghijk')
  self.assertEqual(self.lib.verify()['structurally_valid'],1)
  d=json.loads((self.lib.root/'transcripts/abcdefghijk.json').read_text())
  self.assertEqual(d['segments'][-1]['end'],65)
  self.assertEqual(d['segments'][-1]['timing'],'start_only')
  self.assertEqual(len(self.lib.find('synthetic closing')),1)
  p.write_text(p.read_text().replace('abcdefghijk','wrongvideo1'))
  with self.assertRaises(ValueError):self.lib.attach('abcdefghijk',p,'Fixture')
