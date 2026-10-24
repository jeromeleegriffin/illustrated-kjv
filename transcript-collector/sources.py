"""Approved source manifests provide unattended ingestion without guessing identities."""
import json
from pathlib import Path
from urllib.parse import urlparse
from engine import download,atomic,now

def ingest_manifest(lib,manifest,stop=lambda:False,progress=lambda x:None):
 doc=json.loads(Path(manifest).read_text(encoding='utf-8'));rows=doc.get('sources',[])
 if not isinstance(rows,list):raise ValueError('sources must be a list')
 results=[]
 for entry in rows:
  if stop():break
  id=entry.get('id','')
  try:
   r=lib.row(id)
   if entry.get('teacher')!=r['teacher']:raise ValueError('Teacher does not match catalog')
   if entry.get('identity_verified') is not True or not entry.get('permission_basis') or not entry.get('identity_evidence'):raise ValueError('Explicit source identity verification, evidence and permission basis required')
   if r['source'] or r['status']=='access_blocked':results.append({'id':id,'status':'existing_or_blocked_preserved'});continue
   progress('Importing '+id)
   if entry.get('path'):
    path=Path(entry['path']);path=path if path.is_absolute() else Path(manifest).resolve().parent/path
   else:
    if not lib.setting('online_enabled',False):raise ValueError('Online providers disabled in Settings')
    url=entry['url'];host=urlparse(url).hostname or ''
    if host.endswith('youtube.com') or host.endswith('youtu.be'):raise ValueError('Watch pages unsupported; supply authorized direct media or caption file')
    suffix=Path(urlparse(url).path).suffix.lower()
    if suffix not in ('.mp3','.mp4','.m4a','.wav','.flac','.ogg','.webm','.mkv','.vtt','.srt','.json'):suffix='.media'
    path=download(url,lib.root/'media'/(id+suffix),int(lib.setting('max_file_gb',2)*1024**3),lib.setting('reserve_gb',2))
   lib.attach(id,path,json.dumps(entry,ensure_ascii=False));results.append({'id':id,'status':'ready'})
  except Exception as e:
   status='access_blocked' if getattr(e,'code',None) in (401,403,429) else 'source_review_needed'
   results.append({'id':id,'status':status,'error':str(e)})
   if status=='access_blocked':lib.status(id,status,str(e))
 atomic(lib.root/'source-import-report.json',{'checked':now(),'results':results});return results
