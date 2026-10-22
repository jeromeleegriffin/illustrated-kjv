"""Windows desktop interface; all data stays in a user-selected private folder."""
import json, os, queue, threading, tkinter as tk, webbrowser
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from engine import Library,process,MODELS,download

BASE=Path(__file__).resolve().parent
CATALOG=BASE/'catalog.json' if (BASE/'catalog.json').exists() else BASE.parent/'dist/bible-teaching.json'
CONFIG=Path(os.environ.get('LOCALAPPDATA',Path.home()/'.local/share'))/'GriffinShepherdCollector'/'location.json'
class App:
 def __init__(self,root):
  self.root=root;root.title("Griffin Shepherd's Chapel Transcript Collector — 009");root.geometry('1180x780')
  self.events=queue.Queue();self.stop=threading.Event();self.worker=None
  try:self.output=Path(json.loads(CONFIG.read_text())['output'])
  except (OSError,ValueError,KeyError):self.output=Path.home()/'GriffinShepherdLibrary'
  from instance_lock import InstanceLock
  self.lock=InstanceLock(CONFIG.parent/'collector.lock')
  self.lib=Library(self.output,CATALOG);self.lib.recover()
  from diagnostics import hardware
  from engine import atomic
  atomic(self.output/'hardware.json',hardware())
  self.model=tk.StringVar(value=self.lib.setting('model','small.en'));self.hardware=tk.StringVar(value=self.lib.setting('hardware','cpu'))
  self.query=tk.StringVar();self.teacher=tk.StringVar();self.message=tk.StringVar(value='Ready. No complete archive has been established.');self.stats=tk.StringVar()
  ttk.Label(root,text="Griffin Shepherd's Chapel Transcript Collector",font=('Segoe UI',20,'bold')).pack(anchor='w',padx=15,pady=10)
  ttk.Label(root,textvariable=self.stats,wraplength=1100).pack(anchor='w',padx=15)
  controls=ttk.Frame(root);controls.pack(fill='x',padx=12,pady=12)
  for title,fn in [('Start / Resume',self.start),('Pause',self.pause),('Stop',self.pause),('Retry Failed',self.retry),('Verify Library',self.verify),('Import Folder',self.import_folder),('Attach File',self.attach),('Online Source',self.online),('Settings',self.settings)]:ttk.Button(controls,text=title,command=fn).pack(side='left',padx=2)
  more=ttk.Frame(root);more.pack(fill='x',padx=15,pady=4)
  ttk.Button(more,text='Scan official download listings',command=self.discover).pack(side='left')
  ttk.Button(more,text='Import approved source manifest',command=self.manifest).pack(side='left',padx=6)
  ttk.Button(more,text='Test automatic caption access',command=self.youtube).pack(side='left',padx=6)
  bar=ttk.Frame(root);bar.pack(fill='x',padx=15)
  ttk.Entry(bar,textvariable=self.query,width=55).pack(side='left');ttk.Combobox(bar,textvariable=self.teacher,values=['','Arnold Murray','Dennis Murray'],state='readonly',width=22).pack(side='left',padx=6)
  ttk.Button(bar,text='Search transcripts',command=self.search).pack(side='left');ttk.Button(bar,text='All recordings',command=self.refresh).pack(side='left')
  pane=ttk.Panedwindow(root,orient='vertical');pane.pack(fill='both',expand=True,padx=15,pady=10)
  frame=ttk.Frame(pane);pane.add(frame,weight=3)
  self.tree=ttk.Treeview(frame,columns=('teacher','lesson','status'),show='headings',selectmode='browse')
  for col,width in [('teacher',150),('lesson',550),('status',180)]:self.tree.heading(col,text=col.title());self.tree.column(col,width=width)
  scroll=ttk.Scrollbar(frame,orient='vertical',command=self.tree.yview);self.tree.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');self.tree.pack(fill='both',expand=True);self.tree.bind('<<TreeviewSelect>>',self.view)
  textframe=ttk.Frame(pane);pane.add(textframe,weight=2)
  self.viewer=tk.Text(textframe,wrap='word',font=('Segoe UI',11));ts=ttk.Scrollbar(textframe,command=self.viewer.yview);self.viewer.configure(yscrollcommand=ts.set);ts.pack(side='right',fill='y');self.viewer.pack(fill='both',expand=True)
  ttk.Button(root,text='Open selected original recording',command=self.original).pack(anchor='w',padx=15)
  ttk.Label(root,textvariable=self.message,wraplength=1100).pack(fill='x',padx=15,pady=10)
  root.protocol('WM_DELETE_WINDOW',self.close);self.refresh();root.after(300,self.poll)
 def selected(self):
  sel=self.tree.selection();return sel[0].split('|')[0] if sel else None
 def idle(self):
  if self.worker and self.worker.is_alive():messagebox.showinfo('Working','Pause and wait for the current chunk to finish first.');return False
  return True
 def refresh(self):
  self.tree.delete(*self.tree.get_children())
  for r in self.lib.db.execute('SELECT * FROM recordings ORDER BY rowid'):
   d=json.loads(r['metadata']);refs='; '.join(x['title'] or x['book'] for x in d['references'])
   self.tree.insert('', 'end',iid=r['id'],values=(r['teacher'],refs,r['status']))
  s=self.lib.summary();self.stats.set(f"{s['total']} recordings | Arnold: {s['teachers'].get('Arnold Murray',0)} | Dennis: {s['teachers'].get('Dennis Murray',0)} | Saved transcripts: {s['transcripts_saved']} | Verified complete: {s['states'].get('verified_complete',0)}\nStates: {s['states']}")
 def view(self,event=None):
  id=self.selected()
  if not id:return
  r=self.lib.row(id);d=json.loads(r['metadata']);p=self.output/'transcripts'/(id+'.json')
  body=f"{r['teacher']} | {id}\n{d['url']}\nStatus: {r['status']}\nSource: {r['source'] or 'Not located'}\nProvenance: {r['provenance'] or 'Unverified'}\nError: {r['error'] or 'None'}\nPassages: {json.dumps(d['references'],ensure_ascii=False)}\n\n"
  if p.exists():
   try:
    transcript=json.loads(p.read_text(encoding='utf-8'));body+='MACHINE TRANSCRIPT / CAPTION IMPORT — accuracy and completeness need review.\n\n'
    body+='\n\n'.join(f"[{s['start']:.1f}–{s['end']:.1f}s] {s['text']}" for s in transcript['segments'])
   except Exception as e:body+='Cannot read transcript: '+str(e)
  self.viewer.delete('1.0','end');self.viewer.insert('1.0',body)
 def original(self):
  if self.selected():webbrowser.open(json.loads(self.lib.row(self.selected())['metadata'])['url'])
 def search(self):
  rows=self.lib.find(self.query.get(),self.teacher.get());self.tree.delete(*self.tree.get_children())
  for i,r in enumerate(rows):self.tree.insert('','end',iid=r['id']+'|'+str(i),values=(r['teacher'],f"[{r['start']}s] {r['reference']} — {r['text']}",'search result'))
  self.message.set(f'{len(rows)} matching segments (maximum 200). Subject search currently uses transcript keywords.')
 def attach(self):
  if not self.idle():return
  id=self.selected()
  if not id:messagebox.showinfo('Choose recording','Select the matching catalog recording first.');return
  p=filedialog.askopenfilename(title='Authorized audio, video, SRT, VTT or timestamped JSON')
  if not p:return
  provenance=simpledialog.askstring('Provenance','Describe the authorized source and recording identity:')
  if not provenance:return
  try:self.lib.attach(id,p,provenance);self.refresh()
  except Exception as e:messagebox.showerror('Import failed',str(e))
 def import_folder(self):
  if not self.idle():return
  p=filedialog.askdirectory()
  if not p:return
  provenance=simpledialog.askstring('Provenance','Source/permission for these files (IDs in filenames or metadata sidecars):')
  if not provenance:return
  try:r=self.lib.import_folder(p,provenance);self.message.set(f"Matched {len(r['matched'])}; unmatched {len(r['unmatched'])}; errors {len(r['errors'])}. See import-report.json.");self.refresh()
  except Exception as e:messagebox.showerror('Import failed',str(e))
 def online(self):
  if not self.idle():return
  id=self.selected()
  if not id:return
  if not self.lib.setting('online_enabled',False):messagebox.showinfo('Source settings','Enable authorized online downloads in Settings first.');return
  url=simpledialog.askstring('Direct media','Authorized direct audio/video URL (not a YouTube watch page):')
  if not url:return
  provenance=simpledialog.askstring('Source evidence','Permission and evidence this is the selected recording and teacher:')
  if not provenance:return
  from urllib.parse import urlparse
  host=urlparse(url).hostname or ''
  if host.endswith('youtube.com') or host.endswith('youtu.be'):messagebox.showerror('Unsupported source','A watch page is not a media download. Obtain an authorized media file or captions.');return
  def run():
   lib=Library(self.output)
   try:
    p=download(url,self.output/'media'/(id+'.media'),max_bytes=int(lib.setting('max_file_gb',2)*1024**3),reserve_gb=lib.setting('reserve_gb',2));lib.attach(id,p,provenance+' URL: '+url);self.events.put('Source downloaded and ready')
   except Exception as e:
    status='access_blocked' if getattr(e,'code',None) in (401,403,429) else 'temporarily_failed';lib.status(id,status,str(e));self.events.put(str(e))
   finally:lib.close();self.events.put('REFRESH')
  self.worker=threading.Thread(target=run,daemon=True);self.worker.start()
 def background(self,fn):
  if not self.idle():return
  self.stop.clear()
  def run():
   lib=Library(self.output)
   try:fn(lib)
   except Exception as e:self.events.put(str(e))
   finally:lib.close();self.events.put('REFRESH')
  self.worker=threading.Thread(target=run,daemon=True);self.worker.start()
 def youtube(self):
  if not self.idle():return
  if not self.lib.setting('online_enabled',False):messagebox.showinfo('Source settings','Enable authorized online downloads in Settings first.');return
  if self.lib.setting('youtube_access_hold',None):messagebox.showinfo('Provider paused','YouTube access was blocked. Read youtube-source-report.json in your output directory. Automatic retries are stopped.');return
  basis=self.lib.setting('youtube_permission_basis','')
  if not basis:
   basis=simpledialog.askstring('YouTube caption permission','Describe your permission for automated caption access. This adapter cannot bypass platform restrictions:')
   if not basis:return
   self.lib.set_setting('youtube_permission_basis',basis)
  from youtube_source import collect
  self.background(lambda lib:collect(lib,basis,self.stop.is_set,self.events.put,max_new=5))
 def discover(self):
  from audit import official_sources
  from engine import atomic
  def run(lib):
   d=official_sources(CATALOG);atomic(self.output/'source-availability.json',d)
   n=sum(bool(r['source_candidates']) for r in d['videos']);self.events.put(f'Official listings scanned: {n} candidate matches. Identity remains unverified. See source-availability.json.')
  self.background(run)
 def manifest(self):
  if not self.idle():return
  p=filedialog.askopenfilename(title='Approved source manifest',filetypes=[('JSON','*.json')])
  if not p:return
  from sources import ingest_manifest
  self.background(lambda lib:self.events.put(f'Processed {len(ingest_manifest(lib,p,self.stop.is_set,self.events.put))} source entries. See source-import-report.json.'))
 def start(self):
  if not self.idle():return
  self.stop.clear();model=self.model.get();hardware=self.hardware.get()
  def run():
   lib=Library(self.output)
   try:
    basis=lib.setting('youtube_permission_basis','')
    if lib.setting('online_enabled',False) and basis:
     from youtube_source import collect
     try:collect(lib,basis,self.stop.is_set,self.events.put)
     except Exception as e:self.events.put('Caption provider: '+str(e))
    elif not basis:self.events.put('Automatic caption access is not configured. Use Test automatic caption access once to configure it.')
    rows=lib.db.execute("SELECT id FROM recordings WHERE status='ready' ORDER BY rowid").fetchall()
    for r in rows:
     if self.stop.is_set():break
     try:process(lib,r[0],model,hardware,self.stop.is_set,self.events.put)
     except Exception as e:self.events.put(f'{r[0]} failed: {e}')
     self.events.put('REFRESH')
    self.events.put('Queue stopped.' if self.stop.is_set() else 'Ready-source queue finished. Missing sources remain unprocessed.')
   finally:lib.close()
  self.worker=threading.Thread(target=run,daemon=True);self.worker.start()
 def pause(self):self.stop.set();self.message.set('Stopping after the current chunk/download; saved progress is preserved.')
 def retry(self):
  if not self.idle():return
  with self.lib.db:self.lib.db.execute("UPDATE recordings SET status='ready' WHERE status='temporarily_failed' AND source IS NOT NULL AND attempts<3 AND export_hash IS NULL")
  self.refresh();self.start()
 def verify(self):
  if not self.idle():return
  r=self.lib.verify();self.message.set(json.dumps(r));self.refresh()
 def settings(self):
  if not self.idle():return
  win=tk.Toplevel(self.root);win.title('Settings');win.geometry('580x410')
  ttk.Label(win,text=f'Private library: {self.output}',wraplength=550).pack(pady=8)
  def location():
   p=filedialog.askdirectory()
   if not p:return
   self.lib.close();self.output=Path(p);self.lib=Library(p,CATALOG);self.lib.recover();CONFIG.parent.mkdir(parents=True,exist_ok=True);CONFIG.write_text(json.dumps({'output':p}));win.destroy();self.refresh()
  ttk.Button(win,text='Choose / open library folder (existing data stays in place)',command=location).pack()
  ttk.Label(win,text='Model download: base.en ~150 MB; small.en ~500 MB; medium.en ~1.6 GB').pack(pady=8)
  ttk.Combobox(win,textvariable=self.model,values=list(MODELS),state='readonly').pack()
  ttk.Label(win,text='Hardware: CPU works without an NVIDIA GPU. CUDA requires compatible libraries.').pack(pady=8)
  ttk.Combobox(win,textvariable=self.hardware,values=['cpu','cuda'],state='readonly').pack()
  online=tk.BooleanVar(value=self.lib.setting('online_enabled',False));ttk.Checkbutton(win,text='Enable authorized online downloads',variable=online).pack(pady=8)
  reserve=tk.StringVar(value=str(self.lib.setting('reserve_gb',2)));limit=tk.StringVar(value=str(self.lib.setting('max_file_gb',2)))
  ttk.Label(win,text='Minimum free disk GB / maximum single download GB').pack();ttk.Entry(win,textvariable=reserve,width=10).pack();ttk.Entry(win,textvariable=limit,width=10).pack()
  def save():
   try:
    a=float(reserve.get());b=float(limit.get())
    if not 0.1<=a<=10000 or not 0.01<=b<=100:raise ValueError('Invalid disk limits')
    for k,v in [('model',self.model.get()),('hardware',self.hardware.get()),('online_enabled',online.get()),('reserve_gb',a),('max_file_gb',b)]:self.lib.set_setting(k,v)
    win.destroy()
   except ValueError as e:messagebox.showerror('Settings',str(e))
  ttk.Button(win,text='Save',command=save).pack(pady=8)
 def poll(self):
  try:
   while True:
    msg=self.events.get_nowait()
    if msg=='REFRESH':self.refresh()
    else:self.message.set(msg)
  except queue.Empty:pass
  self.root.after(300,self.poll)
 def close(self):
  if self.worker and self.worker.is_alive():self.pause();self.message.set('Waiting for safe checkpoint before closing.');self.root.after(500,self.close);return
  self.lib.close();self.lock.close();self.root.destroy()

if __name__=='__main__':
 root=tk.Tk();ttk.Style().theme_use('clam');App(root);root.mainloop()
