import io,json,sys,tempfile,threading,time,unittest,urllib.request,urllib.error,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import Store,read_document,windows,validate_result,sha,cues
from app import Controller,Server

def document(id='abcdefghijk',teacher='Arnold Murray'):
 return {'id':id,'teacher':teacher,'duration':600,'segments':[{'start':i*10,'end':i*10+9,'text':('Question time. Mary asks: What is rest?' if i==25 else 'The pastor answers this listener.' if i==26 else 'Ordinary teaching.')} for i in range(60)]}
def archive(path,d,extra=None):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('search-library/transcripts/'+d['id']+'.json',json.dumps(d))
  for name,value in (extra or {}).items():z.writestr(name,json.dumps(value))

class Persistence(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.store=Store(self.root/'data');self.z=self.root/'input.zip';self.d=document();archive(self.z,self.d)
 def tearDown(self):self.temp.cleanup()
 def test_resume_duplicate_import_export(self):
  self.assertEqual(self.store.import_zip(self.z)['imported'],1)
  job=self.store.next_job();self.assertEqual(job['start'],0)
  reopened=Store(self.root/'data');again=reopened.next_job();self.assertEqual(again['id'],job['id'])
  reopened.finish(again,[],{});self.assertEqual(reopened.import_zip(self.z)['unchanged'],1)
  self.assertNotEqual(reopened.next_job()['id'],again['id'])
  output=self.root/'results.zip';manifest=reopened.export(output)
  self.assertFalse(manifest['public_approved']);self.assertEqual(manifest['unfinished_windows'],2)
  with zipfile.ZipFile(output) as z:self.assertIn('index.html',z.namelist());self.assertIsNone(z.testzip())
 def test_changed_hash_stales_old_jobs(self):
  self.store.import_zip(self.z);job=self.store.next_job();self.store.finish(job,[],{})
  self.d['segments'][0]['text']='changed';archive(self.z,self.d);self.store.import_zip(self.z)
  with self.store.connect() as db:self.assertEqual(db.execute("SELECT count(*) FROM jobs WHERE state='stale'").fetchone()[0],3)
 def test_reserved_and_teacher_holds(self):
  archive(self.z,self.d,{'faq-review/external-review-assignments.json':{'assignments':[{'status':'pending','recordings':[{'video_id':self.d['id']}]}]}})
  self.assertEqual(self.store.import_zip(self.z)['held'],1);self.assertIsNone(self.store.next_job())
  self.d['teacher']='Someone Else';self.d['segments'][0]['text']='changed';archive(self.z,self.d)
  self.assertEqual(self.store.import_zip(self.z)['held'],1)
 def test_completed_hash_bound(self):
  raw=json.dumps(self.d).encode();r={'recording_reviews':[{'video_id':self.d['id'],'transcript_sha256':sha(raw),'all_listener_questions_reviewed':True,'qa_boundaries_confirmed':True,'unresolved_ranges':[]}]}
  archive(self.z,self.d,{'faq-review/reviewed-occurrences.json':r});self.assertEqual(self.store.import_zip(self.z)['held'],1)
 def test_zip_path_and_duplicate_rejected(self):
  with zipfile.ZipFile(self.z,'w') as z:z.writestr('../escape.json','{}')
  with self.assertRaises(ValueError):self.store.import_zip(self.z)
 def test_reservation_changes_on_unchanged_source(self):
  self.store.import_zip(self.z)
  archive(self.z,self.d,{'faq-review/external-review-assignments.json':{'assignments':[{'status':'pending','recordings':[{'video_id':self.d['id']}]}]}})
  self.store.import_zip(self.z);self.assertIsNone(self.store.next_job())
 def test_start_only_captions_preserved(self):
  self.d['segments'][0]['end']=0;self.d['segments'][0]['timing']='start_only';archive(self.z,self.d)
  self.assertEqual(self.store.import_zip(self.z)['invalid'],0)
 def test_fail_retry(self):
  self.store.import_zip(self.z);j=self.store.next_job();self.store.fail(j,'engine offline');self.store.retry()
  self.assertEqual(self.store.next_job()['id'],j['id'])

class Extraction(unittest.TestCase):
 def test_whole_recording_contiguous_windows(self):
  d=document();w=windows(d);self.assertEqual(w[0]['start'],0);self.assertEqual(w[-1]['end'],600)
  for a,b in zip(w,w[1:]):self.assertLess(b['start'],a['end'])
  self.assertEqual(set(c['i'] for x in w for c in x['cues']),set(range(60)))
 def test_invented_anchor_rejected(self):
  d=document();w=windows(d)[0]
  q=dict(question_first_cue=999,question_last_cue=999,answer_first_cue=999,answer_last_cue=999,question='Q',answer='A',uncertainty=[])
  with self.assertRaises(ValueError):validate_result(d,w,{'questions':[q]})
 def test_evidence_and_status(self):
  d=document();w=windows(d)[1]
  q=dict(question_first_cue=25,question_last_cue=25,answer_first_cue=26,answer_last_cue=26,question='What is rest?',answer='The pastor replies.',uncertainty=[])
  r=validate_result(d,w,{'questions':[q]})[0]
  self.assertEqual(r['start'],250);self.assertEqual(r['end'],269);self.assertFalse(r['audio_verified']);self.assertEqual(r['evidence']['question'][0],d['segments'][25])
 def test_malformed_timestamps(self):
  d=document();d['segments'][0]['start']=float('nan')
  with self.assertRaises(ValueError):read_document(json.dumps(d))
 def test_rolling_overlap(self):
  d=document();d['segments']=[{'start':0,'end':1,'text':'The living word'},{'start':1,'end':2,'text':'living word is true'}]
  self.assertEqual(cues(d)[1]['text'],'is true')

class HTTP(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.c=Controller(self.temp.name);self.server=Server(self.c);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.base='http://127.0.0.1:'+str(self.server.server_port)
 def tearDown(self):self.c.exit=True;self.server.shutdown();self.server.server_close();self.c.worker.join(2);self.temp.cleanup()
 def test_private_api_and_origin(self):
  with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(self.base+'/api/status')
  self.assertEqual(e.exception.code,403)
  req=urllib.request.Request(self.base+'/api/status',headers={'X-Griffin-Token':self.server.token})
  with urllib.request.urlopen(req) as r:self.assertEqual(json.load(r)['recordings'],0)
  req=urllib.request.Request(self.base+'/api/pause',data=b'{}',headers={'X-Griffin-Token':self.server.token,'Origin':'https://evil.example'})
  with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(req)
 def test_pause_and_export_http(self):
  req=urllib.request.Request(self.base+'/api/pause',data=b'{}',headers={'X-Griffin-Token':self.server.token})
  with urllib.request.urlopen(req) as r:self.assertTrue(json.load(r)['ok'])
  with urllib.request.urlopen(self.base+'/export?token='+self.server.token) as r:
   with zipfile.ZipFile(io.BytesIO(r.read())) as z:self.assertIsNone(z.testzip());self.assertIn('index.html',z.namelist())

if __name__=='__main__':unittest.main()
