"""Windows-portable local browser application. Standard library only."""
import argparse, json, os, secrets, shutil, socket, subprocess, sys, threading, time, traceback, urllib.request, webbrowser, zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from core import Store, Ollama, MODEL, VERSION, read_document, windows, validate_result, sha, cues

RUNTIME_URL='https://github.com/ollama/ollama/releases/download/v0.40.11/ollama-windows-amd64.zip'
RUNTIME_SHA='bda4a493ba8a7c24d57263cd843cd68cee84f44aed4299eeed532acad7eda12a'
RUNTIME_BYTES=1586356606
ASSETS=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))

def data_root(): return Path(os.environ.get('LOCALAPPDATA',str(Path.home())))/'GriffinFAQProcessor'

def keep_windows_awake(active):
    """Prevent automatic sleep only while the worker is processing; display may sleep."""
    if os.name!='nt':return
    import ctypes
    flags=0x80000000 | (0x00000001 if active else 0)
    if not ctypes.windll.kernel32.SetThreadExecutionState(flags):
        raise OSError('Windows could not set the processing sleep preference')

class Controller:
    def __init__(self,root):
        self.store=Store(root);self.lock=threading.Lock();self.mode='paused';self.message='Import your private teaching library ZIP, then set up the free AI.';self.busy=False;self.active=False;self.child=None;self.exit=False
        self.model=self.store.setting('model') or MODEL
        self.hardware=self.store.setting('hardware') or 'auto'
        self.worker=threading.Thread(target=self.run,daemon=True);self.worker.start()
    def close(self):
        self.exit=True;self.mode='paused'
        if self.child and self.child.poll() is None:
            if os.name=='nt':
                subprocess.run(['taskkill','/PID',str(self.child.pid),'/T','/F'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
            else:self.child.terminate()
            try:self.child.wait(timeout=15)
            except subprocess.TimeoutExpired:self.child.kill()
        self.worker.join(timeout=5)
    def status(self):
        return {**self.store.status(),'mode':self.mode,'message':self.message,'busy':self.busy,'active':self.active,'model':self.model,'hardware':self.hardware,'data_directory':str(self.store.root.resolve()),'free_disk_gb':round(shutil.disk_usage(self.store.root).free/1024**3,1),'cpu_threads':os.cpu_count()}
    def background(self,func):
        with self.lock:
            if self.busy or self.active or self.mode=='running': raise ValueError('Pause processing before this operation')
            self.busy=True
        def work():
            try: func()
            except Exception as e: self.message=str(e); self.log(e)
            finally:self.busy=False
        threading.Thread(target=work,daemon=True).start()
    def log(self,e):
        with (self.store.root/'diagnostics.log').open('a',encoding='utf-8') as f:f.write(time.ctime()+' '+str(e)+'\n'+traceback.format_exc()+'\n')
    def ensure_runtime(self):
        try: Ollama(self.model).models();return
        except Exception: pass
        executable=shutil.which('ollama')
        if not executable and os.name=='nt':
            normal=Path(os.environ.get('LOCALAPPDATA',''))/'Programs'/'Ollama'/'ollama.exe'
            if normal.exists():executable=str(normal)
        portable=self.store.root/'runtime'/'ollama.exe'
        if not executable and portable.exists():executable=str(portable)
        if not executable:
            if os.name!='nt': raise RuntimeError('Install/start Ollama on this operating system. Windows setup is built in.')
            self.message='Downloading official free AI runtime (1.59 GB). This may take several minutes.'
            if shutil.disk_usage(self.store.root).free<14*1024**3: raise ValueError('At least 14 GB free disk space is required for runtime, model and working files')
            temp=self.store.root/'runtime-download.zip.partial'
            import hashlib
            h=hashlib.sha256();size=0
            with urllib.request.urlopen(RUNTIME_URL,timeout=90) as response,temp.open('wb') as out:
                while True:
                    block=response.read(1024*1024)
                    if not block:break
                    size+=len(block)
                    if size>RUNTIME_BYTES:raise ValueError('Runtime exceeded its expected size')
                    h.update(block);out.write(block)
                    self.message=f'Downloading official runtime: {size//1048576} / {RUNTIME_BYTES//1048576} MB'
            if size!=RUNTIME_BYTES or h.hexdigest()!=RUNTIME_SHA: raise ValueError('Official runtime checksum failed. Nothing was executed.')
            self.message='Verifying and unpacking the official AI runtime…'
            dest=self.store.root/'runtime';dest.mkdir(exist_ok=True)
            with zipfile.ZipFile(temp) as z:
                if z.testzip():raise ValueError('Runtime ZIP failed integrity check')
                for info in z.infolist():
                    path=dest/info.filename
                    if not path.resolve().is_relative_to(dest.resolve()):raise ValueError('Unsafe runtime path')
                z.extractall(dest)
            temp.unlink();executable=str(portable)
            if not portable.exists():raise ValueError('Official runtime archive layout changed; expected ollama.exe')
        env={**os.environ,'OLLAMA_HOST':'127.0.0.1:11434','OLLAMA_NO_CLOUD':'1','OLLAMA_NUM_PARALLEL':'1','OLLAMA_MODELS':str((self.store.root/'models').resolve())}
        log=(self.store.root/'engine.log').open('ab')
        flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
        self.child=subprocess.Popen([executable,'serve'],env=env,stdout=log,stderr=log,creationflags=flags);log.close()
        for _ in range(100):
            try:Ollama(self.model).models();return
            except Exception:time.sleep(.2)
        raise RuntimeError('AI engine did not start. See engine.log in the data folder.')
    def setup(self):
        self.ensure_runtime();engine=Ollama(self.model)
        if not any(m.get('name')==self.model for m in engine.models()):
            self.message='Downloading the free English-capable local model (about 5.2 GB).'
            def progress(x):
                self.message=x.get('status','Downloading model')
                if x.get('total'):self.message+=f" {x.get('completed',0)//1048576} / {x['total']//1048576} MB"
            engine.pull(progress)
        self.message='Free AI is ready. Import your private ZIP if needed, then click Start.'
    def import_file(self,path):
        self.message='Checking and importing the private archive…'
        result=self.store.import_zip(path,lambda c:setattr(self,'message',f"Imported {c['imported']} recordings; {c['held']} held; {c['unchanged']} already present"))
        self.message='Import finished: '+json.dumps(result)
        Path(path).unlink(missing_ok=True)
    def run(self):
        awake=False
        while not self.exit:
            if self.mode!='running':
                if awake:
                    try:keep_windows_awake(False)
                    except OSError as e:self.log(e)
                    awake=False
                time.sleep(.25);continue
            if not awake:
                try:keep_windows_awake(True);awake=True
                except OSError as e:self.log(e)
            try:
                job=self.store.next_job()
                if not job:self.mode='paused';self.message='No pending eligible windows. Export results; inspect failures and holds.';continue
                self.active=True
                self.message=f"{job['teacher']} · {job['video_id']} · {job['start']:.0f}–{job['end']:.0f} seconds"
                raw=Path(job['source_path']).read_bytes()
                if sha(raw)!=job['source_hash']:raise ValueError('Transcript changed on disk. Reimport the archive; old results will not be reused.')
                d=read_document(raw)
                if not 0<=job['start']<job['end']<=d['duration']+.1:raise ValueError('Invalid saved window range')
                window={'start':job['start'],'end':job['end'],'cues':[c for c in cues(d) if c['end']>=job['start'] and c['start']<job['end']]}
                engine=Ollama(self.model);engine.hardware=self.hardware
                response,metrics=engine.extract(window,job['teacher']);result=validate_result(d,window,response)
                self.store.finish(job,result,metrics)
            except Exception as e:
                quality_error=isinstance(e,json.JSONDecodeError) or isinstance(e,ValueError) and str(e).startswith(('Model output incomplete','Model invented a cue index','Invalid question/answer cue order','Invalid model JSON','Empty/oversized paraphrase'))
                if 'job' in locals() and job and quality_error and self.store.split_job(job,e):
                    self.message='Retrying a quality-failed window in smaller overlapping pieces.'
                    continue
                if 'job' in locals() and job:self.store.fail(job,e)
                self.log(e);self.message=str(e)
                # Stop a systemic engine error instead of failing the entire library.
                if not isinstance(e,ValueError):self.mode='paused'
            finally: self.active=False
        if awake:
            try:keep_windows_awake(False)
            except OSError as e:self.log(e)
    def command(self,cmd,body):
        if cmd=='setup':self.background(self.setup)
        elif cmd=='start':
            if self.busy:raise ValueError('Wait for import/setup to finish')
            self.ensure_runtime()
            if not any(m.get('name')==self.model for m in Ollama(self.model).models()):raise ValueError('Click Set up free AI first')
            self.mode='running';self.message='Processing started. Keep this app and Windows awake.'
        elif cmd in ('pause','stop'):self.mode='paused';self.message='Pausing after the current window is safely saved. You can resume later.'
        elif cmd=='retry':
            if self.mode=='running' or self.active:raise ValueError('Pause and wait for the current window before retrying')
            self.store.retry();self.message='Failed windows queued for retry. Click Start.'
        elif cmd=='settings':
            if self.mode=='running' or self.busy or self.active:raise ValueError('Pause and wait before changing settings')
            if body.get('hardware') not in ('auto','cpu'):raise ValueError('Invalid hardware mode')
            self.hardware=body['hardware'];self.store.setting('hardware',self.hardware)
        else:raise ValueError('Unknown command')

HTML=r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Griffin FAQ Batch Processor</title>
<style>body{font:18px system-ui;max-width:1000px;margin:30px auto;padding:0 20px;color:#172735;background:#f5f7fa}h1{font-size:28px}button,select,input{font:inherit;margin:5px;padding:10px}button{cursor:pointer;background:white;border:1px solid #678;border-radius:6px}button:disabled{opacity:.5}section{background:white;padding:18px;margin:18px 0;border-radius:10px;border:1px solid #ddd}#message{font-weight:600;white-space:pre-wrap}small{display:block;line-height:1.6}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:8px;border-bottom:1px solid #ddd}#error{color:#9b1515}a{color:#065aa0}</style>
<h1>Griffin Shepherd’s Chapel FAQ Batch Processor</h1><p>Process saved transcripts automatically on this computer. Your existing approved FAQs stay intact.</p>
<section><h2>1. Import your saved library</h2><input type="file" id="file" accept=".zip"><button id="import">Import ZIP</button><p>Choose Griffin_Private_Teaching_Library_Batch_001.zip. Importing it again skips unchanged recordings.</p><small>Private files stay on this computer. Topical recordings with unconfirmed teachers, completed reviews and external assignments are held. This app does not download YouTube videos.</small></section>
<section><h2>2. Set up free local AI</h2><button id="setup">Set up free AI</button><select id="hardware"><option value="auto">Automatic hardware</option><option value="cpu">CPU only</option></select><button id="settings">Save setting</button><p>One-time internet download: up to 1.59 GB runtime + about 5.2 GB model. Allow 14 GB free disk space. No subscription or transcription API fee.</p><small>Uses the official Ollama runtime and Qwen3 8B model. Model license: <a href="https://ollama.com/library/qwen3:8b" target="_blank" rel="noreferrer">Qwen model terms</a>. Once downloaded, caption processing works offline. Recommended: 16 GB RAM. Keep Windows on. During processing the app prevents automatic sleep; you may turn off the display. Closing the laptop lid or choosing Sleep can still interrupt it.</small></section>
<section><h2>3. Run automatic batches</h2><button id="start">Start / Resume</button><button id="pause">Pause</button><button id="stop">Stop</button><button id="retry">Retry failed</button><a href="/export" id="export">Download private results ZIP</a><p id="message">Loading…</p><p id="error" role="alert"></p><div id="counts"></div><h3>Recent activity / errors</h3><pre id="current" style="white-space:pre-wrap"></pre><small id="folder"></small></section>
<section><h2>Private candidate viewer</h2><button id="prev">Previous</button><button id="next">Next</button><span id="page"></span><div id="candidates"></div></section>
<section><h2>What the results mean</h2><p>These are AI-generated FAQ candidates with timestamped caption evidence. They require semantic and teacher review before being added to the public Bible app. “Machine pass finished” does not mean every question was found or verified. No automatic publishing occurs.</p><p>Pause saves the current window, then stops. After a power loss, reopen this app and click Resume. Overlapping windows can produce duplicates; variants and uncertainty flags are retained for review.</p></section>
<script>const token=location.hash.slice(1)||sessionStorage.getItem('griffin-session')||'';if(token)sessionStorage.setItem('griffin-session',token);history.replaceState(null,'',location.pathname);let busy=false;async function command(cmd,body={}){try{document.getElementById('error').textContent='';let r=await fetch('/api/'+cmd,{method:'POST',headers:{'Content-Type':'application/json','X-Griffin-Token':token},body:JSON.stringify(body)});let d=await r.json();if(!r.ok)throw Error(d.error);await refresh()}catch(e){document.getElementById('error').textContent=e.message}}
for(let cmd of ['setup','start','pause','stop','retry'])document.getElementById(cmd).onclick=()=>command(cmd);
document.getElementById('settings').onclick=()=>command('settings',{hardware:document.getElementById('hardware').value});
document.getElementById('import').onclick=async()=>{let file=document.getElementById('file').files[0];if(!file)return;try{document.getElementById('message').textContent='Uploading private ZIP to this computer…';let r=await fetch('/api/import',{method:'POST',headers:{'X-Griffin-Token':token},body:file});let d=await r.json();if(!r.ok)throw Error(d.error)}catch(e){document.getElementById('error').textContent=e.message}};
async function refresh(){try{let r=await fetch('/api/status',{headers:{'X-Griffin-Token':token}});if(!r.ok)throw Error('Session expired. Reopen the app to open its private page.');let s=await r.json();document.getElementById('message').textContent=s.message;document.getElementById('counts').textContent=`Recordings imported: ${s.recordings} | Machine pass finished: ${s.machine_pass_finished_recordings} | Windows saved: ${s.windows.saved||0} | Remaining: ${s.windows.pending||0} | Failed: ${s.windows.failed||0}`;document.getElementById('current').textContent=s.current.map(x=>`${x.video_id} ${Math.round(x.start)}–${Math.round(x.end)}s ${x.state}: ${x.error||''}`).join('\n');document.getElementById('folder').textContent=`CPU threads: ${s.cpu_threads} | Free storage: ${s.free_disk_gb} GB | Private data folder: ${s.data_directory}`;document.getElementById('export').href='/export?token='+encodeURIComponent(token);for(let id of ['import','setup','start','retry','settings'])document.getElementById(id).disabled=s.busy||s.active||(s.mode==='running'&&id!=='start');}catch(e){document.getElementById('error').textContent=e.message}}refresh();setInterval(refresh,2500);
let candidatePage=0;async function showCandidates(){try{let r=await fetch('/api/candidates?page='+candidatePage,{headers:{'X-Griffin-Token':token}});let data=await r.json();if(!r.ok)throw Error(data.error);let box=document.getElementById('candidates');box.replaceChildren();document.getElementById('page').textContent=`Page ${candidatePage+1} · ${data.total} raw candidates`;document.getElementById('prev').disabled=candidatePage===0;document.getElementById('next').disabled=(candidatePage+1)*10>=data.total;for(let q of data.items){let article=document.createElement('article'),h=document.createElement('h3'),a=document.createElement('a'),p=document.createElement('p'),flags=document.createElement('small'),detail=document.createElement('details'),summary=document.createElement('summary'),evidence=document.createElement('pre');h.textContent=q.question;a.textContent=q.teacher+' · '+q.video_id+' · '+Math.floor(q.start)+'s';a.href='https://www.youtube.com/watch?v='+q.video_id+'&t='+Math.floor(q.start)+'s';a.target='_blank';a.rel='noreferrer';p.textContent=q.answer||'Answer withheld: incomplete or insufficient caption evidence. It remains in the private repair queue.';flags.textContent='UNAPPROVED · '+q.uncertainty.join('; ');summary.textContent='Original caption evidence and model notes';evidence.style.whiteSpace='pre-wrap';evidence.textContent=JSON.stringify({evidence:q.evidence,notes:q.window_notes||[],withheld_proposal:q.proposed_answer_unverified||null},null,2);detail.append(summary,evidence);article.append(h,a,p,flags,detail);box.append(article)}}catch(e){document.getElementById('error').textContent=e.message}}document.getElementById('prev').onclick=()=>{candidatePage--;showCandidates()};document.getElementById('next').onclick=()=>{candidatePage++;showCandidates()};showCandidates();setInterval(showCandidates,15000);</script></html>'''

class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,controller):
        self.controller=controller;self.token=secrets.token_urlsafe(32);super().__init__(('127.0.0.1',0),Handler)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def reply(self,code,data,kind='application/json'):
        raw=json.dumps(data).encode() if kind=='application/json' else data.encode()
        self.send_response(code);self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.send_header('X-Frame-Options','DENY');self.end_headers();self.wfile.write(raw)
    def authorized(self,query_token=False):
        from urllib.parse import urlparse,parse_qs
        token=self.headers.get('X-Griffin-Token','')
        if query_token:token=parse_qs(urlparse(self.path).query).get('token',[''])[0]
        host=f'127.0.0.1:{self.server.server_port}'
        if self.headers.get('Host')!=host:return False
        if self.headers.get('Origin') not in (None,'http://'+host):return False
        return secrets.compare_digest(token,self.server.token)
    def do_GET(self):
        try:
            if self.path=='/':self.reply(200,HTML,'text/html');return
            if not self.authorized(self.path.startswith('/export?')):self.reply(403,{'error':'Private app session required'});return
            if self.path=='/api/status':self.reply(200,self.server.controller.status());return
            if self.path.startswith('/api/candidates?'):
                from urllib.parse import urlparse,parse_qs
                page=int(parse_qs(urlparse(self.path).query).get('page',['0'])[0])
                if not 0<=page<=100000:raise ValueError('Invalid page')
                self.reply(200,self.server.controller.store.candidates(page));return
            if self.path.startswith('/export?'):
                path=self.server.controller.store.root/'Griffin_Private_FAQ_Results.zip'
                self.server.controller.store.export(path)
                self.send_response(200);self.send_header('Content-Type','application/zip');self.send_header('Content-Disposition','attachment; filename="Griffin_Private_FAQ_Results.zip"');self.send_header('Content-Length',str(path.stat().st_size));self.end_headers()
                with path.open('rb') as f:shutil.copyfileobj(f,self.wfile)
                return
            self.reply(404,{'error':'Not found'})
        except Exception as e:self.reply(500,{'error':str(e)})
    def do_POST(self):
        if not self.authorized():self.reply(403,{'error':'Private app session required'});return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if self.path=='/api/import':
                c=self.server.controller
                with c.lock:
                    if c.busy or c.active or c.mode=='running':raise ValueError('Pause and wait for current operation before importing')
                    c.busy=True
                try:
                    if not 0<size<=2*1024**3:raise ValueError('Choose a ZIP smaller than 2 GB')
                    if shutil.disk_usage(c.store.root).free<size+1024**3:raise ValueError('Insufficient free disk space')
                    self.connection.settimeout(90);path=c.store.root/'incoming.zip.partial'
                    with path.open('wb') as f:
                        remaining=size
                        while remaining:
                            block=self.rfile.read(min(1024*1024,remaining))
                            if not block:raise ValueError('Incomplete upload')
                            f.write(block);remaining-=len(block)
                    def ingest():
                        try:c.import_file(path)
                        except Exception as e:c.message=str(e);c.log(e)
                        finally:c.busy=False
                    threading.Thread(target=ingest,daemon=True).start()
                except Exception:c.busy=False;raise
            else:
                if not 0<size<=4096:raise ValueError('Invalid request size')
                self.server.controller.command(self.path.removeprefix('/api/'),json.loads(self.rfile.read(size)))
            self.reply(200,{'ok':True})
        except Exception as e:self.reply(400,{'error':str(e)})

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=data_root());p.add_argument('--self-test',action='store_true');p.add_argument('--no-browser',action='store_true');args=p.parse_args()
    if args.self_test:
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            s=Store(temp);assert s.status()['recordings']==0;s.export(Path(temp)/'test.zip')
        print('Griffin FAQ Processor executable self-test passed');return
    args.data.mkdir(parents=True,exist_ok=True)
    # Hold a process-wide socket lock. An accidental second launch opens the existing session.
    lock=socket.socket();lockfile=args.data/'session.json'
    try:lock.bind(('127.0.0.1',48377))
    except OSError:
        if lockfile.exists():
            old=json.loads(lockfile.read_text());webbrowser.open(old['url'])
        return
    controller=Controller(args.data);server=Server(controller);url=f'http://127.0.0.1:{server.server_port}/#{server.token}'
    lockfile.write_text(json.dumps({'url':url}));print('Griffin FAQ Batch Processor '+VERSION+'\nKeep this window open.\n'+url)
    if not args.no_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:
        controller.exit=True;server.server_close();lock.close();lockfile.unlink(missing_ok=True)
        controller.close()

if __name__=='__main__':main()
