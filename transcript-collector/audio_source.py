"""Missing-caption fallback; shares all YouTube pacing and access holds."""
import json
import subprocess
import sys
import time
from pathlib import Path
from engine import atomic, digest, now, process
from youtube_source import BLOCKS, COOLDOWN_SECONDS, MAX_RATE_LIMITS, PACE_SECONDS, is_rate_limit, wait_until


def collect_audio(lib, basis, stop=lambda: False, progress=lambda message: None,
                  model='small.en', hardware='cpu', max_new=10, runner=subprocess.run):
    if not basis.strip() or not lib.setting('online_enabled', False) or not lib.setting('youtube_audio_enabled', False):
        return 0
    if lib.setting('youtube_access_hold', None) or lib.setting('youtube_rate_limits', 0) >= MAX_RATE_LIMITS:
        progress('Audio provider held: existing YouTube access restriction remains in effect.')
        return 0
    captions = lib.root / 'youtube-source-report.json'
    if not captions.exists(): return 0
    latest = {r['id']:r for r in json.loads(captions.read_text(encoding='utf-8'))['results']}
    report_path = lib.root / 'youtube-audio-report.json'
    report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {'results': []}
    attempted = {r['id'] for r in report['results']}
    folder = lib.root / 'youtube-audio'; folder.mkdir(exist_ok=True)
    count = 0
    for vid, caption in latest.items():
        if stop() or count >= max_new: break
        if caption['status'] != 'no_english_caption_saved' or vid in attempted or lib.row(vid)['source']: continue
        if not wait_until(lib.setting('youtube_next_request_at', 0), stop, progress): break
        count += 1; progress('Downloading original English audio: ' + vid)
        result = {'id': vid, 'checked': now()}
        try:
            proc = runner([sys.executable, str(Path(__file__).with_name('audio_worker.py')), vid, str(folder),
                           str(int(lib.setting('max_file_gb', 2)*1024**3)), str(int(lib.setting('reserve_gb', 2)*1024**3))],
                          capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)
            diagnostic = (proc.stdout or '') + '\n' + (proc.stderr or '')
            result['diagnostic'] = diagnostic[-12000:]
            if is_rate_limit(diagnostic):
                n = lib.setting('youtube_rate_limits', 0) + 1
                lib.set_setting('youtube_rate_limits', n)
                lib.set_setting('youtube_next_request_at', time.time()+COOLDOWN_SECONDS*2**(n-1))
                result['status'] = 'rate_limited'
            elif any(x in diagnostic.lower() for x in BLOCKS):
                lib.set_setting('youtube_access_hold', {'id': vid, 'checked': now()})
                result['status'] = 'access_blocked'
            elif proc.returncode:
                result['status'] = 'audio_unavailable'
            else:
                data = json.loads((folder/(vid+'.verified.json')).read_text(encoding='utf-8'))
                path = folder / data['filename']
                if path.parent != folder or data['id'] != vid or digest(path) != data['sha256']:
                    raise ValueError('Audio receipt identity/checksum mismatch')
                lib.attach(vid, path, json.dumps(dict(data, permission_basis=basis,
                           teacher_verification='catalog attribution; independent review required')))
                result['status'] = 'media_verified'
                # Commit retrieval before ASR so interruption never redownloads attached media.
                report['results'].append(result.copy()); atomic(report_path, report)
                process(lib, vid, model, hardware, stop, progress)
                result['status'] = lib.row(vid)['status']
        except Exception as exc:
            result.update(status='failed', error=str(exc))
        if result['status'] != 'rate_limited':
            lib.set_setting('youtube_next_request_at', time.time()+PACE_SECONDS)
        report['results'].append(result); atomic(report_path, report); progress('REFRESH')
        if result['status'] not in ('quality_review', 'verified_complete', 'ready'): break
    return count
