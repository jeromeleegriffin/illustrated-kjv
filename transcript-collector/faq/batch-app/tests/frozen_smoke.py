"""Windows CI: exercise the built EXE's real loopback HTTP server, not Python source."""
import json,subprocess,sys,tempfile,time,urllib.request,zipfile
from pathlib import Path

def main():
 exe=Path(sys.argv[1]).resolve()
 with tempfile.TemporaryDirectory() as temp:
  root=Path(temp);process=subprocess.Popen([str(exe),'--data',str(root),'--no-browser'])
  try:
   for _ in range(150):
    if process.poll() is not None:raise RuntimeError('Frozen app exited during startup')
    if (root/'session.json').exists():break
    time.sleep(.1)
   session=json.loads((root/'session.json').read_text());base,token=session['url'].split('/#');headers={'X-Griffin-Token':token}
   with urllib.request.urlopen(urllib.request.Request(base+'/api/status',headers=headers)) as r:assert json.load(r)['recordings']==0
   with urllib.request.urlopen(base+'/') as r:assert b'Griffin' in r.read()
   d={'id':'abcdefghijk','teacher':'Arnold Murray','duration':20,'segments':[{'start':0,'end':20,'text':'Synthetic local test only.'}]}
   zpath=root/'fixture.zip'
   with zipfile.ZipFile(zpath,'w') as z:z.writestr('search-library/transcripts/abcdefghijk.json',json.dumps(d))
   with urllib.request.urlopen(urllib.request.Request(base+'/api/import',data=zpath.read_bytes(),headers=headers)) as r:assert json.load(r)['ok']
   for _ in range(100):
    with urllib.request.urlopen(urllib.request.Request(base+'/api/status',headers=headers)) as r:s=json.load(r)
    if not s['busy']:break
    time.sleep(.1)
   assert s['recordings']==1 and s['windows']['pending']==1,s
   with urllib.request.urlopen(base+'/export?token='+token) as r:
    out=root/'export.zip';out.write_bytes(r.read())
   with zipfile.ZipFile(out) as z:assert z.testzip() is None and 'index.html' in z.namelist()
   print('Frozen Windows app: HTTP startup, private auth, streamed ZIP import, SQLite queue and export passed')
  finally:process.terminate();process.wait(timeout=15)

if __name__=='__main__':main()
