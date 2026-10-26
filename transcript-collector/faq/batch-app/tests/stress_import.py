import sys,tempfile,json,zipfile,hashlib,time,sqlite3
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import Store
start=time.time()
with tempfile.TemporaryDirectory(prefix='griffin-import-stress-') as td:
 p=Path(td);z=p/'synthetic-1360.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
  for i in range(1360):
   id=hashlib.sha256(str(i).encode()).hexdigest()[:11]
   d=dict(id=id,teacher='Arnold Murray' if i%2 else 'Dennis Murray',duration=3500,segments=[dict(start=t,end=t+2,text='Synthetic import integrity test only. No actual teaching or source claims.') for t in range(0,3498,3)])
   out.writestr('search-library/transcripts/'+id+'.json',json.dumps(d))
 s=Store(p/'data');report=[]
 for n in range(3):
  counts=s.import_zip(z)
  with s.connect() as db:
   integrity=[tuple(row) for row in db.execute('PRAGMA integrity_check')];records=db.execute('SELECT count(*) FROM recordings').fetchone()[0];jobs=db.execute('SELECT count(*) FROM jobs').fetchone()[0]
  assert records==1360,(n,records)
  assert integrity==[('ok',)],(n,integrity[:5])
  report.append(dict(pass_number=n+1,counts=counts,records=records,jobs=jobs,integrity='ok'));print(json.dumps(report[-1]),flush=True)
 assert report[0]['jobs']==report[-1]['jobs']
 print(json.dumps(dict(test='1360-recording repeated import integrity stress',passed=True,sqlite_version=sqlite3.sqlite_version,elapsed_seconds=round(time.time()-start,1),rounds=report)),flush=True)
