import io,json,sys,tempfile,threading,time,unittest,urllib.request,urllib.error,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import Store,read_document,windows,validate_result,sha,cues
from app import Controller,Server,keep_windows_awake
from unittest.mock import patch,Mock

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
 def test_split_window_recovery_preserves_coverage(self):
  self.store.import_zip(self.z);job=self.store.next_job();self.assertTrue(self.store.split_job(job,'Model output incomplete'))
  reopened=Store(self.root/'data');spans=[]
  while True:
   j=reopened.next_job()
   if not j:break
   spans.append((j['start'],j['end']));reopened.finish(j,[],{})
  covered=0
  for start,end in sorted(spans):self.assertLessEqual(start,covered);covered=max(covered,end)
  self.assertEqual(covered,600);self.assertEqual(reopened.status()['machine_pass_finished_recordings'],1)
  with reopened.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM processing_events').fetchone()[0],1)
 def test_split_retry_is_bounded(self):
  self.store.import_zip(self.z);attempts=0
  while True:
   j=self.store.next_job()
   if not j:break
   attempts+=1;self.assertLess(attempts,60)
   if not self.store.split_job(j,'Model output incomplete'):self.store.fail(j,'minimum window reached')
  with self.store.connect() as db:
   self.assertTrue(all(row[0]<=90 for row in db.execute("SELECT end-start FROM jobs WHERE state='failed'")))
 def test_no_jobs_not_finished(self):
  self.store.import_zip(self.z)
  with self.store.connect() as db:db.execute('DELETE FROM jobs')
  self.assertEqual(self.store.status()['machine_pass_finished_recordings'],0)
 def test_hold_counter_tracks_eligible_queue(self):
  self.store.import_zip(self.z)
  extra={'external-review-assignments.json':{'assignments':[{'status':'pending','recordings':[{'video_id':self.d['id']}]}]}}
  archive(self.z,self.d,extra);self.store.import_zip(self.z)
  self.assertEqual(self.store.status()['windows'].get('pending',0),0)
  self.assertEqual(self.store.status()['held_recordings'],1);self.assertIsNone(self.store.next_job())
  archive(self.z,self.d);self.store.import_zip(self.z)
  self.assertEqual(self.store.status()['windows']['pending'],3)
 def test_completed_reservation_formats_release(self):
  for terminal in ['completed','released','cancelled']:
   for field in ['video_ids','recording_ids','recordings']:
    value=[{'video_id':self.d['id']}] if field=='recordings' else [self.d['id']]
    archive(self.z,self.d,{'external-review-assignments.json':{'assignments':[{'status':terminal,field:value}]}})
    self.assertEqual(self.store.import_zip(self.z)['held'],0)
 def test_large_candidate_library_reads_only_requested_page(self):
  self.store.import_zip(self.z);job=self.store.next_job()
  self.store.finish(job,[{'question':str(i),'start':i} for i in range(2000)],{})
  original=json.loads
  with patch('core.json.loads',wraps=original) as loads:
   result=self.store.candidates(99)
   self.assertEqual(result['total'],2000);self.assertEqual(result['items'][0]['question'],'990');self.assertEqual(loads.call_count,10)
  clamped=self.store.candidates(9999);self.assertEqual(clamped['page'],199);self.assertEqual(len(clamped['items']),10)
 def test_malformed_segment_reported_not_crash(self):
  self.d['segments']=[None];archive(self.z,self.d)
  self.assertEqual(self.store.import_zip(self.z)['invalid'],1)
 def test_export_snapshot_during_worker_commit(self):
  from contextlib import contextmanager
  self.store.import_zip(self.z);job=self.store.next_job();original=self.store.connect;started=False;writer_thread=None
  def save():
   with original() as writer:writer.execute("UPDATE jobs SET state='saved',result='[]',metrics='{}' WHERE id=?",(job['id'],))
  @contextmanager
  def tracked():
   with original() as db:
    def trace(sql):
     nonlocal started,writer_thread
     if "FROM jobs WHERE state<>" in sql and not started:
      started=True;writer_thread=threading.Thread(target=save);writer_thread.start();time.sleep(.05)
    db.set_trace_callback(trace);yield db
  with patch.object(self.store,'connect',tracked):result=self.store.export(self.root/'during.zip')
  writer_thread.join(5)
  self.assertTrue(started);self.assertFalse(writer_thread.is_alive());self.assertEqual(result['unfinished_windows'],3)
  self.assertEqual(self.store.status()['windows']['saved'],1)
 def test_import_retains_verified_backup(self):
  self.store.import_zip(self.z);j=self.store.next_job();self.store.finish(j,[],{})
  self.store.import_zip(self.z)
  import sqlite3
  from contextlib import closing
  with closing(sqlite3.connect(self.store.root/'last-good.sqlite')) as db:
   self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
   self.assertEqual(db.execute("SELECT count(*) FROM jobs WHERE state='saved'").fetchone()[0],1)
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
 def test_cut_or_thin_answers_withheld(self):
  d=document();w=windows(d)[1]
  q=dict(question_first_cue=25,answer_first_cue=26,answer_last_cue=26,question='What is rest?',answer='The pastor explains an elaborate unsupported teaching with many more claims than the few source words can establish at all.',uncertainty=[])
  r=validate_result(d,w,{'questions':[q]})[0]
  self.assertEqual(r['answer'],'');self.assertEqual(r['review_status'],'held_machine_proposal');self.assertIn('proposed_answer_unverified',r)
 def test_model_truncation_flag_withholds_answer(self):
  d=document();w=windows(d)[1]
  for flag in ['truncated','answer_cut_off','incomplete_answer','missing answer']:
   q=dict(question_first_cue=25,answer_first_cue=26,answer_last_cue=26,question='What is rest?',answer='The pastor replies.',uncertainty=[flag])
   r=validate_result(d,w,{'questions':[q]})[0]
   self.assertEqual(r['answer'],'');self.assertEqual(r['review_status'],'held_machine_proposal')
 def test_listener_comment_not_presented_as_question(self):
  d=document();d['segments'][25]['text']='A friend died. I feel people need to pay attention.';w=windows(d)[1]
  q=dict(question_first_cue=25,answer_first_cue=26,answer_last_cue=26,question='Why are people dying?',answer='The pastor gives a reason.',uncertainty=[])
  r=validate_result(d,w,{'questions':[q]})[0]
  self.assertEqual(r['answer'],'');self.assertIn('no_explicit_question_in_selected_evidence',r['uncertainty'])
 def test_yes_no_question_has_evidence_signal(self):
  d=document();d['segments'][25]['text']='Is this teaching correct';w=windows(d)[1]
  q=dict(question_first_cue=25,answer_first_cue=26,answer_last_cue=26,question='Is this correct?',answer='The pastor replies.',uncertainty=[])
  r=validate_result(d,w,{'questions':[q]})[0]
  self.assertEqual(r['review_status'],'machine_candidate_unapproved')
 def test_malformed_timestamps(self):
  d=document();d['segments'][0]['start']=float('nan')
  with self.assertRaises(ValueError):read_document(json.dumps(d))
 def test_rolling_overlap(self):
  d=document();d['segments']=[{'start':0,'end':1,'text':'The living word'},{'start':1,'end':2,'text':'living word is true'}]
  self.assertEqual(cues(d)[1]['text'],'is true')

class WorkerRecovery(unittest.TestCase):
 def test_malformed_model_output_auto_splits(self):
  import app
  class FakeEngine:
   def __init__(self,*a):pass
   def extract(self,w,teacher):
    if w['end']-w['start']>150:raise json.JSONDecodeError('truncated JSON','{',1)
    return {'questions':[],'notes':[]},{}
  with tempfile.TemporaryDirectory() as td,patch.object(app,'Ollama',FakeEngine):
   root=Path(td);z=root/'input.zip';archive(z,document());c=Controller(root/'data');c.store.import_zip(z);c.mode='running'
   deadline=time.time()+10
   while time.time()<deadline:
    status=c.store.status()
    if not status['windows'].get('pending') and not c.active and c.mode=='paused':break
    time.sleep(.05)
   c.close();self.assertEqual(c.store.status()['machine_pass_finished_recordings'],1)
   with c.store.connect() as db:self.assertGreater(db.execute('SELECT count(*) FROM processing_events').fetchone()[0],0)
 def test_pause_restart_resume_preserves_finished_windows(self):
  import app
  entered=threading.Event();release=threading.Event()
  class FakeEngine:
   def __init__(self,*a):pass
   def extract(self,w,t):entered.set();release.wait(5);return {'questions':[],'notes':[]},{}
  with tempfile.TemporaryDirectory() as td,patch.object(app,'Ollama',FakeEngine):
   z=Path(td)/'input.zip';archive(z,document());c=Controller(Path(td)/'data')
   try:
    c.store.import_zip(z);c.mode='running';self.assertTrue(entered.wait(3));c.command('pause',{});release.set()
    deadline=time.time()+5
    while c.active and time.time()<deadline:time.sleep(.02)
    self.assertEqual(c.mode,'paused');self.assertEqual(c.store.status()['windows']['saved'],1)
   finally:release.set();c.close()
   c=Controller(Path(td)/'data')
   try:
    c.mode='running';deadline=time.time()+5
    while (c.mode!='paused' or c.active) and time.time()<deadline:time.sleep(.02)
    self.assertEqual(c.store.status()['windows']['saved'],3)
   finally:c.close()
 def test_windows_awake_flags_and_release(self):
  kernel=Mock();kernel.SetThreadExecutionState.return_value=1
  with patch('ctypes.windll',Mock(kernel32=kernel),create=True),patch('app.os.name','nt'):
   keep_windows_awake(True);keep_windows_awake(False)
  self.assertEqual([c.args[0] for c in kernel.SetThreadExecutionState.call_args_list],[0x80000001,0x80000000])

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
 def test_concurrent_downloads_have_isolated_exports(self):
  from concurrent.futures import ThreadPoolExecutor
  paths=[];barrier=threading.Barrier(2);original=self.c.store.export
  def coordinated(path):paths.append(path);barrier.wait(3);return original(path)
  def download(_):
   with urllib.request.urlopen(self.base+'/export?token='+self.server.token,timeout=5) as r:
    with zipfile.ZipFile(io.BytesIO(r.read())) as z:self.assertIsNone(z.testzip())
  with patch.object(self.c.store,'export',coordinated),ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(download,range(2)))
  self.assertEqual(len(set(paths)),2);self.assertTrue(all(not p.exists() for p in paths))
 def test_pause_and_export_http(self):
  req=urllib.request.Request(self.base+'/api/pause',data=b'{}',headers={'X-Griffin-Token':self.server.token})
  with urllib.request.urlopen(req) as r:self.assertTrue(json.load(r)['ok'])
  with urllib.request.urlopen(self.base+'/export?token='+self.server.token) as r:
   with zipfile.ZipFile(io.BytesIO(r.read())) as z:self.assertIsNone(z.testzip());self.assertIn('index.html',z.namelist())

if __name__=='__main__':unittest.main()

