"""Bounded real-worker probe. Never opens or modifies the teaching database."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from engine import atomic, digest, parse_captions

KNOWN = ['qqzXl4z-m1M', 'HcWbNez6GUY', 'NV99i2jcIJU']

def failure_code(text):
    text = text.lower()
    if '429' in text or 'too many requests' in text: return 'rate_limited'
    if any(x in text for x in ('403', 'not a bot', 'sign in', 'captcha', 'access denied')): return 'access_blocked'
    if 'no module named yt_dlp' in text: return 'dependency_missing'
    if any(x in text for x in ('proxyerror', 'connection refused', 'name resolution', 'network is unreachable')): return 'network_error'
    return 'request_failed'

def probe(vid, root, runner=subprocess.run):
    folder = root / vid
    folder.mkdir()
    state = folder / 'stages.json'
    result = {'video_id': vid, 'discovery': 'not_confirmed', 'selection': 'not_attempted',
              'retrieval': 'not_confirmed', 'parse': 'not_attempted', 'persistence': 'not_attempted',
              'status': 'not_processed', 'accuracy': 'not_verified'}
    env = dict(os.environ, GRIFFIN_CAPTION_DIAGNOSTIC=str(state.resolve()))
    command = [sys.executable, str(Path(__file__).with_name('caption_worker.py')),
               '--ignore-config', '--skip-download', '--write-subs', '--write-auto-subs',
               '--sub-format', 'vtt', '--extractor-args', 'youtube:skip=translated_subs,hls,dash',
               '--sleep-requests', '2', '--sleep-subtitles', '5', '--no-playlist',
               '--socket-timeout', '15', '--retries', '0', '--extractor-retries', '0',
               '-o', str(folder / '%(id)s.%(ext)s'), '--', 'https://www.youtube.com/watch?v='+vid]
    try:
        proc = runner(command, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        result['returncode'] = proc.returncode
        # Raw process output is used in memory only. Never write URLs, headers or tokens.
        if proc.returncode: result['status'] = failure_code((proc.stdout or '')+'\n'+(proc.stderr or ''))
        else: result['status'] = 'no_caption_saved'
    except subprocess.TimeoutExpired:
        result['status'] = 'timeout'
    except OSError:
        result['status'] = 'process_launch_failed'
    if state.exists():
        stage = json.loads(state.read_text(encoding='utf-8'))
        if stage.get('video_id') != vid:
            result['status'] = 'identity_mismatch'
            return result
        result.update({k:stage[k] for k in ('discovery','selection','tracks')})
    tracks = result.get('tracks', [])
    if len(tracks)==1:
        language = tracks[0]['language']
        if not re.fullmatch(r'en(?:-[A-Za-z]{2,3})?(?:-orig)?', language):
            result['status']='unsupported_language'; return result
        caption = folder / (vid+'.'+language+'.vtt')
        if caption.exists():
            result['retrieval']='file_received'
            try:
                cues=parse_captions(caption)
                result.update(parse='valid', segments=len(cues), first_start=cues[0]['start'],
                              last_end=cues[-1]['end'], sha256=digest(caption))
                atomic(folder/'segments.json', cues)
                assert json.loads((folder/'segments.json').read_text(encoding='utf-8'))==cues
                result['persistence']='saved_and_reopened'
                # A nonzero process remains a failure even if it left a partial file.
                if result['returncode']==0: result['status']='saved_quality_review'
            except (ValueError, KeyError, OSError, AssertionError):
                result['parse']='failed'; result['status']='validation_failed'
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count',type=int,choices=(1,2,3),default=1)
    parser.add_argument('--output',type=Path,default=Path('diagnostics'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    root=Path(tempfile.mkdtemp(prefix='caption-check-',dir=args.output)).resolve()
    try: version=importlib.metadata.version('yt-dlp')
    except importlib.metadata.PackageNotFoundError: version='not installed'
    report={'yt_dlp_version':version,'python':sys.version.split()[0],'platform':sys.platform,
            'scope':'diagnostic only; no library changes; no audio download', 'results':[]}
    for index,vid in enumerate(KNOWN[:args.count]):
        if index: time.sleep(60)
        print('Checking '+vid,flush=True)
        result=probe(vid,root);report['results'].append(result);atomic(root/'report.json',report)
        print(vid+': '+result['status'],flush=True)
        if result['status']!='saved_quality_review':
            print('Stopped after failure; no retries or additional video requests.',flush=True);break
    print('Report: '+str(root/'report.json'))
    return 0 if all(r['status']=='saved_quality_review' for r in report['results']) else 1

if __name__=='__main__': sys.exit(main())
