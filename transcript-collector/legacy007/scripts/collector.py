#!/usr/bin/env python3
"""Resumable, caption-only collector for authorized Shepherd's Chapel recordings.
Uses yt-dlp (installed separately), not YouTube API credentials.
"""
import argparse, csv, hashlib, html, json, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SUPPORTED={'.json','.jsonl','.csv','.txt','.md','.html','.js','.ts','.jsx','.tsx'}
URLS=re.compile(r'https?://(?:www\.|m\.)?(?:youtube\.com|youtu\.be)/[^\s"\'<>\\]+',re.I)
TAG=re.compile(r'<[^>]*>')
TIMELINE=re.compile(r'(?P<start>\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->')

def utc(): return datetime.now(timezone.utc).isoformat()
def vid(url):
    try:
        p=urlparse(url.strip().rstrip('),.;]}'))
        domain=p.netloc.lower().removeprefix('www.').removeprefix('m.')
        if domain=='youtu.be': token=p.path.strip('/').split('/')[0]
        elif domain=='youtube.com':
            parts=p.path.strip('/').split('/')
            token=(parse_qs(p.query).get('v') or [''])[0] if parts[0]=='watch' else (parts[1] if len(parts)>1 and parts[0] in ('embed','shorts','live') else '')
        else: return None
        return token if re.fullmatch(r'[\w-]{11}',token) else None
    except (IndexError,ValueError): return None

def extract_urls(raw):
    return [(m.group(),vid(m.group())) for m in URLS.finditer(raw)]

def scan(path):
    files=[path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED and not any(c in p.parts for c in ('.git','node_modules','transcripts','.next','dist-cache')))
    found={}
    for f in files:
        if f.stat().st_size>24_000_000: continue
        try: raw=f.read_text(encoding='utf-8',errors='replace')
        except OSError: continue
        for url,v in extract_urls(raw):
            if v and v not in found: found[v]={'id':v,'url':f'https://www.youtube.com/watch?v={v}','source':str(f)}
    return list(found.values())

def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    tmp.replace(path)

def read_json(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except (ValueError,OSError): return {}

def parse_vtt(raw):
    # Collect complete cues, discarding karaoke-style rolling partial captions.
    cues=[]; lines=raw.replace('\ufeff','').splitlines(); current_time=None; pieces=[]
    def flush():
        nonlocal pieces,current_time
        if current_time is not None:
            val=' '.join(html.unescape(TAG.sub('',x)).strip() for x in pieces if x.strip())
            val=re.sub(r'\s+',' ',val).strip()
            if val: cues.append({'time':current_time,'text':val})
        pieces=[]
    for line in lines+['']:
        stripped=line.strip()
        m=TIMELINE.search(stripped)
        if m:
            flush(); current_time=m.group('start').replace(',','.'); continue
        if not stripped:
            flush();current_time=None;continue
        if current_time is not None: pieces.append(stripped)
    # Remove exact repeats; preserve adjacent overlapping but nonidentical cues.
    result=[]
    for c in cues:
        if result and result[-1]['text']==c['text']:continue
        result.append(c)
    return result

def captions(video,out,langs,auto):
    out.mkdir(parents=True,exist_ok=True)
    tpl=str(out/'%(id)s.%(language)s.%(ext)s')
    cmd=[sys.executable,'-m','yt_dlp','--skip-download','--no-playlist','--write-subs','--sub-langs',langs,'--sub-format','vtt','--no-overwrites','--output',tpl]
    if auto:cmd.append('--write-auto-subs')
    cmd.append(video['url'])
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
    except (OSError,subprocess.TimeoutExpired) as e: return None,str(e)
    candidates=sorted(out.glob(video['id']+'.*.vtt'),key=lambda x:(0 if '.en.' in x.name else 1,x.name))
    if not candidates:return None,(p.stdout+'\n'+p.stderr)[-1000:] or 'No VTT captions'
    chosen=candidates[0]; seg=parse_vtt(chosen.read_text(encoding='utf-8',errors='replace'))
    if not seg:return None,'Empty VTT'
    return {'id':video['id'],'url':video['url'],'source_catalog':video['source'],'caption_file':chosen.name,'segments':seg,'retrieved_utc':utc()},None

def load_approved(path):
    """Read an owner-reviewed manifest of IDs; never approve newly scanned links silently."""
    doc=read_json(path)
    rows=doc.get('approved_ids', []) if isinstance(doc,dict) else []
    if not isinstance(rows,list) or not rows:
        raise ValueError('Approval file requires a nonempty approved_ids list')
    clean=set()
    for value in rows:
        if not isinstance(value,str) or not re.fullmatch(r'[\w-]{11}',value):
            raise ValueError('Invalid approved YouTube ID: '+repr(value))
        clean.add(value)
    return clean

def write_approval_template(path, videos):
    if path.exists():
        print('Existing approval template preserved:',path)
        return
    atomic(path,{'instructions':'Review manifest.json and add only confirmed Arnold/Dennis Murray video IDs to approved_ids. Never use unreviewed IDs.', 'approved_ids':[], 'candidate_ids':[v['id'] for v in videos]})

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--catalog',required=True)
    p.add_argument('--out',default='transcript_output')
    p.add_argument('--languages',default='en.*,en')
    p.add_argument('--auto-captions',action='store_true')
    p.add_argument('--limit',type=int,default=10,help='Per-run attempt cap; 0 for all')
    p.add_argument('--retry-failed',action='store_true')
    p.add_argument('--scan-only',action='store_true')
    p.add_argument('--collect',action='store_true',help='Explicitly enable network collection; default writes manifest only')
    p.add_argument('--approved',help='Path to manually reviewed JSON approval containing approved_ids')
    a=p.parse_args(); catalog=Path(a.catalog);out=Path(a.out)
    if not catalog.exists(): p.error('Catalog not found: '+str(catalog))
    # Prefer the precise, teacher-verified manifest generated from the Bible catalog.
    doc=read_json(catalog)
    if isinstance(doc,dict) and doc.get('schema')=='shepherd-approved-candidates-v1':
        videos=[{'id':v['id'],'url':v['url'],'source':v['source'],'teacher':v['teacher']} for v in doc.get('videos',[]) if v.get('teacher') in ('Arnold Murray','Dennis Murray')]
    else:
        videos=scan(catalog)
    print('Discovered',len(videos),'unique YouTube IDs')
    if a.scan_only:return 0
    out.mkdir(parents=True,exist_ok=True)
    atomic(out/'manifest.json',{'generated_utc':utc(),'catalog':str(catalog),'candidates':videos,'warning':'Review candidate sources and confirm authorization before collecting transcripts.'})
    write_approval_template(out/'approval-template.json',videos)
    if not a.collect:
        print('Manifest written:',out/'manifest.json','(no network requests)');return 0
    if not a.approved:p.error('For collection, provide --approved path/to/approved.json with reviewed IDs')
    try: approved=load_approved(Path(a.approved))
    except ValueError as e:p.error(str(e))
    videos=[v for v in videos if v['id'] in approved]
    if not videos:p.error('None of the approved IDs appear in this catalog')
    try:import yt_dlp # noqa: F401
    except ImportError:p.error('yt-dlp not installed. Run: py -m pip install -U yt-dlp')
    state_file=out/'state.json';state=read_json(state_file)
    if not isinstance(state,dict):state={}
    # Prefer new lessons before retrying previously failed ones.
    # This prevents a handful of inaccessible captions from starving the catalog.
    videos.sort(key=lambda v: (state.get(v['id'], {}).get('status') == 'failed', v['id']))
    attempted=success=0
    for v in videos:
        prior=state.get(v['id'],{}).get('status')
        if prior=='ok' or (prior=='failed' and (not a.retry_failed or int(state.get(v['id'],{}).get('attempts',0))>=3)):continue
        if a.limit and attempted>=a.limit:break
        attempted+=1
        result,error=captions(v,out/'captions',a.languages,a.auto_captions)
        tries=int(state.get(v['id'],{}).get('attempts',0))+1
        if result:
            atomic(out/'transcripts'/(v['id']+'.json'),result)
            state[v['id']]={'status':'ok','source':v['source'],'segments':len(result['segments']),'attempts':tries};success+=1
        else:state[v['id']]={'status':'failed','source':v['source'],'error':(error or '')[-700:],'attempts':tries}
        atomic(state_file,state)
        print(f'{attempted} {v["id"]}: {state[v["id"]]["status"]}',flush=True)
        time.sleep(1)
    report={'approved_videos':len(videos),'completed':sum(s.get('status')=='ok' for s in state.values()),'failed':sum(s.get('status')=='failed' for s in state.values()),'attempted_this_run':attempted,'successful_this_run':success,'failed_this_run':attempted-success,'generated_utc':utc()}
    atomic(out/'report.json',report);print(json.dumps(report,indent=2));return 0
if __name__=='__main__':sys.exit(main())
