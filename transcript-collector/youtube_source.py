"""Optional caption-only adapter. No cookies, proxies, media download or block bypass."""
import json
import subprocess
import sys
from pathlib import Path
from engine import atomic, now, parse_captions, process

BLOCKS = ('429', '403', 'sign in', 'not a bot', 'captcha', 'too many requests', 'access denied')


def collect(lib, permission_basis, stop=lambda: False, progress=lambda message: None, runner=subprocess.run, max_new=None):
    if not permission_basis.strip():
        raise ValueError('A permission basis for automated caption access is required')
    if not lib.setting('online_enabled', False):
        raise ValueError('Online providers are disabled')
    if lib.setting('youtube_access_hold', None):
        raise ValueError('YouTube provider paused after an access block. Review youtube-source-report.json; do not repeatedly retry.')
    folder = lib.root / 'youtube-captions'
    folder.mkdir(exist_ok=True)
    report_path = lib.root / 'youtube-source-report.json'
    report = json.loads(report_path.read_text()) if report_path.exists() else {'results': []}
    previously_attempted = {r['id'] for r in report['results']}
    report['permission_basis'] = permission_basis
    attempted_now = 0
    for row in lib.db.execute('SELECT id,source,status FROM recordings ORDER BY rowid').fetchall():
        vid = row['id']
        if stop() or (max_new is not None and attempted_now >= max_new): break
        if row['source'] or vid in previously_attempted or row['status'] == 'access_blocked': continue
        attempted_now += 1
        progress('Checking YouTube captions: ' + vid)
        result = {'id': vid, 'checked': now()}
        command = [sys.executable, '-m', 'yt_dlp', '--ignore-config', '--skip-download',
                   '--write-subs', '--write-auto-subs', '--sub-langs', 'en', '--sub-format', 'vtt',
                   '--write-info-json', '--no-playlist', '--socket-timeout', '15',
                   '--retries', '0', '--extractor-retries', '0', '--no-overwrites',
                   '-o', str(folder / '%(id)s.%(ext)s'), '--', 'https://www.youtube.com/watch?v=' + vid]
        try:
            proc = runner(command, capture_output=True, text=True, timeout=65)
            diagnostic = (proc.stdout or '') + '\n' + (proc.stderr or '')
            # No user cookies are requested or read; retain bounded diagnostics privately.
            result.update(returncode=proc.returncode, diagnostic=diagnostic[-12000:])
            if any(term in diagnostic.lower() for term in BLOCKS):
                result['status'] = 'access_blocked'
                lib.status(vid, 'access_blocked', 'YouTube provider access blocked; see private diagnostic report')
                lib.set_setting('youtube_access_hold', {'id': vid, 'checked': now()})
            elif 'No module named yt_dlp' in diagnostic:
                result['status'] = 'dependency_missing'
            elif proc.returncode != 0:
                result['status'] = 'request_failed'
            else:
                caption = folder / (vid + '.en.vtt')
                metadata = folder / (vid + '.info.json')
                if not caption.is_file():
                    result['status'] = 'no_english_caption_saved'
                else:
                    info = json.loads(metadata.read_text(encoding='utf-8'))
                    if info.get('id') != vid: raise ValueError('Downloaded metadata ID mismatch')
                    cues = parse_captions(caption)
                    provenance = {'adapter': 'yt-dlp caption-only', 'permission_basis': permission_basis,
                                  'source_id': vid, 'url': info.get('webpage_url'),
                                  'channel': info.get('channel'), 'title': info.get('title'),
                                  'teacher_verification': 'catalog attribution; independent review required',
                                  'generation': 'may be automatic; inspect original caption metadata'}
                    lib.attach(vid, caption, json.dumps(provenance))
                    process(lib, vid)
                    result.update(status='saved_quality_review', segments=len(cues))
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
        except Exception as exc:
            result.update(status='failed', error=str(exc))
        report['results'].append(result)
        atomic(report_path, report)
        progress(vid + ': ' + result['status'])
        # Prevent thousands of repeated failures, including environmental failures.
        if result['status'] in ('access_blocked', 'dependency_missing', 'request_failed', 'timeout', 'failed'):
            break
    return report
