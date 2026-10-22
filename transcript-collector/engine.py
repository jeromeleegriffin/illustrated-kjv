"""Private local library. No cloud ASR, no implicit YouTube extraction."""
from __future__ import annotations
import hashlib, html, json, math, os, re, shutil, sqlite3, time, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone
from prepare_queue import prepare

TEACHERS=('Arnold Murray','Dennis Murray')
MODELS={'base.en':150,'small.en':500,'medium.en':1600}
MEDIA={'.mp3','.mp4','.m4a','.wav','.flac','.ogg','.mkv','.webm','.aac','.wma'}
CAPTIONS={'.srt','.vtt','.json','.txt'}
def now(): return datetime.now(timezone.utc).isoformat()
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def atomic(p,data):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with open(str(p)+'.tmp','w',encoding='utf-8') as f:
  json.dump(data,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
 os.replace(str(p)+'.tmp',p)
def seconds(s):
 parts=s.replace(',','.').split(':');return sum(float(v)*60**i for i,v in enumerate(reversed(parts)))
def parse_captions(path):
 p=Path(path);raw=p.read_text(encoding='utf-8-sig');rows=[]
 if p.suffix.lower()=='.txt':
  if not raw.startswith('YouTube transcript\n'):raise ValueError('Expected a timestamped YouTube transcript export')
  for line in raw.splitlines():
   m=re.fullmatch(r'\[(\d+:\d{2}(?::\d{2})?)\] (.+)',line)
   if m:
    t=seconds(m[1]);rows.append({'start':t,'end':t,'timing':'start_only','text':m[2]})
 elif p.suffix.lower()=='.json':
  doc=json.loads(raw);items=doc if isinstance(doc,list) else doc.get('segments',doc.get('content',[]))
  for x in items:
   start=float(x.get('start',float(x.get('offset',0))/1000))
   end=float(x['end']) if 'end' in x else start+float(x['duration'])/(1000 if 'offset' in x else 1)
   rows.append({'start':start,'end':end,'text':x['text']})
 else:
  for block in re.split(r'\n\s*\n',raw.replace('\r','')):
   lines=block.splitlines()
   for i,line in enumerate(lines):
    m=re.search(r'(\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})\s*-->\s*(\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})',line)
    if m:rows.append({'start':seconds(m[1]),'end':seconds(m[2]),'text':' '.join(lines[i+1:])});break
 result=[]
 for x in rows:
  x['text']=html.unescape(re.sub('<[^>]*>','',x['text'])).strip()
  if not x['text']:continue
  point=x.get('timing')=='start_only' and x['end']==x['start']
  if not all(math.isfinite(x[k]) for k in ('start','end')) or x['start']<0 or (x['end']<=x['start'] and not point):raise ValueError('Invalid caption time')
  if result and x['start']<result[-1]['start']:raise ValueError('Unordered caption cues')
  # Merge only overlapping identical cues; spoken repetitions at distinct times survive.
  if not point and result and x['start']<=result[-1]['end'] and x['text']==result[-1]['text']:
   result[-1]['end']=max(result[-1]['end'],x['end']);continue
  if result and x['start']<result[-1]['end']:
   a=result[-1]['text'].split();b=x['text'].split()
   for n in range(min(len(a),len(b)),0,-1):
    if a[-n:]==b[:n]:x['text']=' '.join(b[n:]);break
   if not x['text']:continue
  result.append(x)
 if not result:raise ValueError('No usable timestamped captions')
 return result

class Library:
 def __init__(self,root,catalog=None):
  self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True)
  self.db=sqlite3.connect(self.root/'library.sqlite',timeout=30);self.db.row_factory=sqlite3.Row
  self.db.executescript('''PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;
  CREATE TABLE IF NOT EXISTS recordings(id TEXT PRIMARY KEY,teacher TEXT NOT NULL,metadata TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'cataloged',source TEXT,provenance TEXT,media_hash TEXT,duration REAL,model TEXT,attempts INTEGER DEFAULT 0,error TEXT,updated TEXT,export_hash TEXT);
  CREATE TABLE IF NOT EXISTS chunks(id TEXT,idx INTEGER,start REAL,end REAL,segments TEXT,warnings TEXT,PRIMARY KEY(id,idx));
  CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(id UNINDEXED,teacher,reference,text,start UNINDEXED);
  CREATE TABLE IF NOT EXISTS events(time TEXT,id TEXT,stage TEXT,detail TEXT);
  CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
  ''')
  if catalog:
   rows=prepare(catalog)
   with self.db:
    for r in rows:
     old=self.db.execute('SELECT teacher,metadata FROM recordings WHERE id=?',(r['id'],)).fetchone()
     if old and (old['teacher']!=r['teacher'] or json.loads(old['metadata'])!=r):raise ValueError('Catalog changed; explicit migration required: '+r['id'])
     self.db.execute('INSERT OR IGNORE INTO recordings(id,teacher,metadata,updated) VALUES(?,?,?,?)',(r['id'],r['teacher'],json.dumps(r),now()))
 def close(self):self.db.close()
 def setting(self,key,default=None):
  r=self.db.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone();return json.loads(r[0]) if r else default
 def set_setting(self,key,value):
  with self.db:self.db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',(key,json.dumps(value)))
 def row(self,id):
  r=self.db.execute('SELECT * FROM recordings WHERE id=?',(id,)).fetchone()
  if not r:raise ValueError('Unknown catalog ID: '+id)
  return dict(r)
 def status(self,id,status,error=None):
  with self.db:
   self.db.execute('UPDATE recordings SET status=?,error=?,updated=? WHERE id=?',(status,error,now(),id))
   self.db.execute('INSERT INTO events VALUES(?,?,?,?)',(now(),id,status,error))
 def recover(self):
  for r in self.db.execute("SELECT id FROM recordings WHERE status='transcribing'").fetchall():self.status(r[0],'ready','Recovered after interruption; committed chunks preserved')
 def attach(self,id,path,provenance):
  r=self.row(id);p=Path(path).resolve()
  if not p.is_file():raise ValueError('File does not exist')
  if not provenance.strip():raise ValueError('Source permission/provenance required')
  if p.suffix.lower()=='.txt':
   raw=p.read_text(encoding='utf-8-sig')
   identity=re.search(r'^Video ID: (\S+)$',raw,re.M)
   if not identity or identity[1]!=id:raise ValueError('Transcript export video ID mismatch')
   parse_captions(p)
  sha=digest(p)
  if r['media_hash'] and r['media_hash']!=sha:raise ValueError('Different source already attached; preserve existing work and review identity')
  other=self.db.execute('SELECT id FROM recordings WHERE media_hash=? AND id!=?',(sha,id)).fetchone()
  if other:raise ValueError('Same file already attached to '+other[0]+'; review duplicate identity')
  with self.db:self.db.execute('UPDATE recordings SET source=?,provenance=?,media_hash=?,updated=? WHERE id=?',(str(p),provenance,sha,now(),id))
  if r['status'] not in ('quality_review','verified_complete'):self.status(id,'ready')
 def import_folder(self,folder,provenance):
  result={'matched':[],'unmatched':[],'errors':[]}
  ids={r[0] for r in self.db.execute('SELECT id FROM recordings')}
  for p in Path(folder).rglob('*'):
   if not p.is_file() or p.suffix.lower() not in MEDIA|CAPTIONS:continue
   matches=[id for id in ids if re.search(r'(?<![A-Za-z0-9_-])'+re.escape(id)+r'(?![A-Za-z0-9_-])',p.stem)]
   side=p.with_suffix(p.suffix+'.metadata.json')
   if side.exists():
    try:
     d=json.loads(side.read_text());id=d['video_id']
     if d.get('teacher')!=self.row(id)['teacher']:raise ValueError('Teacher metadata conflict')
     matches=[id]
    except Exception as e:result['errors'].append({'file':str(p),'error':str(e)});continue
   if len(matches)!=1:result['unmatched'].append(str(p));continue
   try:self.attach(matches[0],p,provenance);result['matched'].append(matches[0])
   except Exception as e:result['errors'].append({'file':str(p),'error':str(e)})
  atomic(self.root/'import-report.json',result);return result
 def save_chunk(self,id,idx,start,end,segments,warnings):
  with self.db:self.db.execute('INSERT OR REPLACE INTO chunks VALUES(?,?,?,?,?,?)',(id,idx,start,end,json.dumps(segments),json.dumps(warnings)))
 def export(self,id):
  r=self.row(id);chunks=self.db.execute('SELECT * FROM chunks WHERE id=? ORDER BY idx',(id,)).fetchall()
  if not chunks:raise ValueError('No chunks saved')
  segments=[s for c in chunks for s in json.loads(c['segments'])]
  if not segments:raise ValueError('Empty recognition output; not a transcript')
  for i,c in enumerate(chunks):
   if c['idx']!=i or (i and abs(c['start']-chunks[i-1]['end'])>0.02):raise ValueError('Missing chunk')
  if r['duration'] is None or abs(chunks[-1]['end']-r['duration'])>0.1:raise ValueError('Incomplete recording')
  payload={'schema':'griffin-transcript-v1','id':id,'teacher':r['teacher'],'catalog':json.loads(r['metadata']),'provenance':r['provenance'],'source_sha256':r['media_hash'],'duration':r['duration'],'engine':r['model'],'machine_generated':None if r['model']=='caption-import' else True,'verification':'quality_review','warnings':[w for c in chunks for w in json.loads(c['warnings'])],'segments':segments}
  p=self.root/'transcripts'/(id+'.json');atomic(p,payload)
  with self.db:
   self.db.execute('DELETE FROM search WHERE id=?',(id,))
   refs='; '.join(f"{x['book']} {x['start'][0]}:{x['start'][1]}–{x['end'][0]}:{x['end'][1]}" for x in payload['catalog']['references'])
   self.db.executemany('INSERT INTO search VALUES(?,?,?,?,?)',[(id,r['teacher'],refs,s['text'],s['start']) for s in segments])
   self.db.execute('UPDATE recordings SET export_hash=? WHERE id=?',(digest(p),id))
  self.status(id,'quality_review');return payload
 def verify(self):
  failures=[];good=0
  for r in self.db.execute('SELECT * FROM recordings WHERE export_hash IS NOT NULL').fetchall():
   p=self.root/'transcripts'/(r['id']+'.json')
   try:
    if digest(p)!=r['export_hash']:raise ValueError('Transcript checksum changed')
    d=json.loads(p.read_text(encoding='utf-8'))
    if d['id']!=r['id'] or d['teacher']!=r['teacher'] or not d['segments']:raise ValueError('Transcript identity/content invalid')
    for s in d['segments']:
     point=s.get('timing')=='start_only' and s['start']==s['end']
     if not (0<=s['start']<=s['end']<=d['duration']+0.1) or (s['start']==s['end'] and not point):raise ValueError('Invalid timestamp')
    good+=1
   except Exception as e:
    failures.append({'id':r['id'],'error':str(e)});self.status(r['id'],'temporarily_failed',str(e))
  result={'structurally_valid':good,'failures':failures,'note':'Structural validation is not audio accuracy verification.'};atomic(self.root/'verification.json',result);return result
 def find(self,query,teacher=''):
  tokens=re.findall(r'\w+',query)
  if not tokens:return []
  expression=' AND '.join('"'+x+'"' for x in tokens)
  return [dict(r) for r in self.db.execute('SELECT id,teacher,reference,text,start FROM search WHERE search MATCH ? AND (?="" OR teacher=?) LIMIT 200',(expression,teacher,teacher))]
 def summary(self):
  counts=dict(self.db.execute('SELECT status,count(*) FROM recordings GROUP BY status').fetchall())
  return {'total':self.db.execute('SELECT count(*) FROM recordings').fetchone()[0],'teachers':dict(self.db.execute('SELECT teacher,count(*) FROM recordings GROUP BY teacher')),'states':counts,'transcripts_saved':self.db.execute('SELECT count(*) FROM recordings WHERE export_hash IS NOT NULL').fetchone()[0]}

def download(url,destination,max_bytes=2_000_000_000,reserve_gb=2):
 """Explicit direct media only. No endpoint guessing, credentials, or retry loop."""
 from urllib.parse import urlparse
 if urlparse(url).scheme not in ('https','http'):raise ValueError('HTTP(S) URL required')
 p=Path(destination);p.parent.mkdir(parents=True,exist_ok=True);tmp=Path(str(p)+'.part');size=0
 try:
  with urllib.request.urlopen(url,timeout=30) as r,open(tmp,'wb') as f:
   expected=int(r.headers.get('Content-Length','0'))
   if expected>max_bytes:raise ValueError('Media exceeds configured file size limit')
   while data:=r.read(1024*1024):
    size+=len(data)
    if size>max_bytes or shutil.disk_usage(p.parent).free<reserve_gb*1024**3:raise ValueError('Disk/file limit reached')
    f.write(data)
   f.flush();os.fsync(f.fileno())
  if not size or (expected and size!=expected):raise ValueError('Truncated download')
  os.replace(tmp,p);return p
 except Exception:
  tmp.unlink(missing_ok=True);raise

def audio_chunks(path,chunk_seconds=300):
 """Stream decode with bounded RAM; preserve original sample offsets."""
 import av,numpy as np
 rate=16000;resampler=av.AudioResampler(format='s16',layout='mono',rate=rate)
 buffer=np.empty(0,dtype=np.int16);offset=0;idx=0;length=rate*chunk_seconds
 with av.open(str(path)) as container:
  def frames():
   for frame in container.decode(audio=0):
    yield from resampler.resample(frame)
   yield from resampler.resample(None)
  for frame in frames():
   buffer=np.concatenate((buffer,frame.to_ndarray().reshape(-1)))
   while len(buffer)>=length:
    yield idx,offset/rate,(offset+length)/rate,buffer[:length].astype(np.float32)/32768
    buffer=buffer[length:];offset+=length;idx+=1
  if len(buffer):yield idx,offset/rate,(offset+len(buffer))/rate,buffer.astype(np.float32)/32768

def process(lib,id,model_name='small.en',hardware='cpu',stop=lambda:False,progress=lambda x:None,model_factory=None):
 r=lib.row(id)
 if not r['source']:raise ValueError('No source attached')
 if digest(r['source'])!=r['media_hash']:raise ValueError('Source checksum changed')
 if r['status'] in ('verified_complete','quality_review'):return
 p=Path(r['source']);is_caption=p.suffix.lower() in CAPTIONS
 chosen='caption-import' if is_caption else model_name
 if r['model'] and r['model']!=chosen:raise ValueError('Model differs from committed chunks; retain original setting to resume')
 with lib.db:lib.db.execute('UPDATE recordings SET model=?,attempts=attempts+1 WHERE id=?',(chosen,id))
 lib.status(id,'transcribing')
 try:
  if is_caption:
   rows=parse_captions(p);end=max(s['end'] for s in rows)
   with lib.db:lib.db.execute('UPDATE recordings SET duration=? WHERE id=?',(end,id))
   warnings=['Caption duration inferred from final cue; recording completeness unverified.']
   if p.suffix.lower()=='.txt':warnings.append('Start-only timestamps: end equals start as a point marker, not a measured end. Duration is only the final known timestamp. Caption authorship is unspecified; accuracy unverified.')
   lib.save_chunk(id,0,0,end,rows,warnings)
  else:
   if model_factory is None:
    from faster_whisper import WhisperModel
    model_factory=WhisperModel
   if model_name not in MODELS and not Path(model_name).is_dir():raise ValueError('Unknown model')
   progress('Loading model (first use downloads model files)')
   model=model_factory(model_name,device=hardware,compute_type='int8' if hardware=='cpu' else 'float16',cpu_threads=max(1,min(4,os.cpu_count() or 1)))
   done={x[0] for x in lib.db.execute('SELECT idx FROM chunks WHERE id=?',(id,))};end=0
   for idx,start,end,audio in audio_chunks(p):
    if stop():lib.status(id,'ready','Paused at committed chunk');return
    if idx in done:continue
    if shutil.disk_usage(lib.root).free<lib.setting('reserve_gb',2)*1024**3:raise ValueError('Free disk reserve reached')
    progress(f'{id}: {start/60:.1f}–{end/60:.1f} minutes')
    segs,info=model.transcribe(audio,language='en',beam_size=5,vad_filter=True,condition_on_previous_text=False,initial_prompt='Biblical names: Yahveh, Elohim, Melchizedek, Nebuchadnezzar, Thessalonians, Corinthians.',word_timestamps=True)
    result=[];warnings=[]
    for s in segs:
     text=s.text.strip()
     if not text:continue
     a=max(start,start+s.start);b=min(end,start+s.end)
     if b<=a:continue
     uncertain=s.avg_logprob < -1 or s.no_speech_prob>0.6 or s.compression_ratio>2.4
     if uncertain:warnings.append(f'Uncertain recognition at {a:.2f}s')
     if result and result[-1]['text']==text:warnings.append(f'Repeated line at {a:.2f}s retained for review')
     result.append({'start':a,'end':b,'text':text,'uncertain':uncertain})
    if not result:warnings.append(f'No speech recognized in chunk {idx}; silence or failure needs review')
    if idx:warnings.append(f'Check chunk boundary at {start:.2f}s')
    lib.save_chunk(id,idx,start,end,result,warnings)
   if not end:raise ValueError('No decoded audio')
   with lib.db:lib.db.execute('UPDATE recordings SET duration=? WHERE id=?',(end,id))
  lib.export(id)
 except Exception as e:
  lib.status(id,'temporarily_failed',str(e));raise
