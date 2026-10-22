"""Optional caption-only adapter. No cookies, proxies, media download or block bypass."""
import json
import subprocess
import sys
import time
from pathlib import Path
from engine import atomic, now, parse_captions, process

BLOCKS = ('http error 403', 'sign in', 'not a bot', 'captcha', 'access denied')


PACE_SECONDS = 60
COOLDOWN_SECONDS = 3600
MAX_RATE_LIMITS = 3


def is_rate_limit(diagnostic):
    text = diagnostic.lower()
    return ('http error 429' in text or 'too many requests' in text) and not any(term in text for term in BLOCKS)


def wait_until(deadline, stop, progress, clock=time.time, sleep=time.sleep):
    """Interruptible wait; never send requests during a persisted cooldown."""
    last = None
    while clock() < deadline:
        if stop(): return False
        remaining = max(1, int(deadline - clock()))
        bucket = remaining // 30
        if bucket != last:
            progress(f'Waiting before next caption request: {remaining} seconds. Pause is available.')
            last = bucket
        sleep(min(1, max(0, deadline - clock())))
    return not stop()


def collect(lib, permission_basis, stop=lambda: False, progress=lambda message: None, runner=subprocess.run, max_new=None, clock=time.time, sleep=time.sleep):
    if not permission_basis.strip():
        raise ValueError('A permission basis for automated caption access is required')
    if not lib.setting('online_enabled', False):
        raise ValueError('Online providers are disabled')
    folder = lib.root / 'youtube-captions'
    folder.mkdir(exist_ok=True)
    report_path = lib.root / 'youtube-source-report.json'
    report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {'results': []}
    # Migrate only a positively identified legacy HTTP 429, never a login/403/bot block.
    hold = lib.setting('youtube_access_hold', None)
    if hold:
        entry = next((r for r in reversed(report['results']) if r['id'] == hold.get('id')), {})
        if is_rate_limit(entry.get('diagnostic', '')):
            lib.set_setting('youtube_next_request_at', clock() + COOLDOWN_SECONDS)
            lib.set_setting('youtube_rate_limits', 1)
            lib.set_setting('youtube_access_hold', None)
            lib.status(hold['id'], 'temporarily_failed', 'Legacy HTTP 429: waiting one hour before retry')
            report['results'].append(dict(entry, status='rate_limited', checked=now(), migration='Build 011 cooldown; no network request'))
            atomic(report_path, report)
        else:
            raise ValueError('YouTube provider paused after an access block. Review youtube-source-report.json; do not repeatedly retry.')
    if lib.setting('youtube_rate_limits', 0) >= MAX_RATE_LIMITS:
        raise ValueError('Repeated rate limits: automatic requests stopped after three events. Review the access report.')
    from collections import Counter
    attempts = Counter(r['id'] for r in report['results'] if not r.get('migration'))
    latest = {r['id']:r for r in report['results']}
    retryable = {'dependency_missing','timeout','request_failed','failed','rate_limited'}
    previously_attempted = {vid for vid,r in latest.items() if r['status'] not in retryable or attempts[vid] >= 3}
    report['permission_basis'] = permission_basis
    attempted_now = 0
    for row in lib.db.execute('SELECT id,source,status FROM recordings ORDER BY rowid').fetchall():
        vid = row['id']
        if stop() or (max_new is not None and attempted_now >= max_new): break
        if row['source'] or vid in previously_attempted or row['status'] == 'access_blocked': continue
        if not wait_until(lib.setting('youtube_next_request_at', 0), stop, progress, clock, sleep): break
        attempted_now += 1
        progress('Checking YouTube captions: ' + vid)
        result = {'id': vid, 'checked': now()}
        command = [sys.executable, str(Path(__file__).with_name('caption_worker.py')), '--ignore-config', '--skip-download',
                   '--write-subs', '--write-auto-subs', '--sub-format', 'vtt',
                   '--extractor-args', 'youtube:skip=translated_subs,hls,dash',
                   '--sleep-requests', '2', '--sleep-subtitles', '5',
                   '--write-info-json', '--no-clean-info-json', '--no-playlist', '--socket-timeout', '15',
                   '--retries', '0', '--extractor-retries', '0', '--force-overwrites',
                   '-o', str(folder / '%(id)s.%(ext)s'), '--', 'https://www.youtube.com/watch?v=' + vid]
        try:
            proc = runner(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
            diagnostic = (proc.stdout or '') + '\n' + (proc.stderr or '')
            # No user cookies are requested or read; retain bounded diagnostics privately.
            result.update(returncode=proc.returncode, diagnostic=diagnostic[-12000:])
            if is_rate_limit(diagnostic):
                result['status'] = 'rate_limited'
                count = lib.setting('youtube_rate_limits', 0) + 1
                lib.set_setting('youtube_rate_limits', count)
                delay = COOLDOWN_SECONDS * (2 ** (count - 1))
                lib.set_setting('youtube_next_request_at', clock() + delay)
                result['retry_not_before_epoch'] = clock() + delay
                lib.status(vid, 'temporarily_failed', 'HTTP 429: caption requests cooling down')
            elif any(term in diagnostic.lower() for term in BLOCKS):
                result['status'] = 'access_blocked'
                lib.status(vid, 'access_blocked', 'YouTube provider access blocked; see private diagnostic report')
                lib.set_setting('youtube_access_hold', {'id': vid, 'checked': now()})
            elif 'No module named yt_dlp' in diagnostic:
                result['status'] = 'dependency_missing'
            elif proc.returncode != 0:
                result['status'] = 'request_failed'
            else:
                metadata = folder / (vid + '.info.json')
                info = json.loads(metadata.read_text(encoding='utf-8')) if metadata.is_file() else {}
                if info and info.get('id') != vid: raise ValueError('Downloaded metadata ID mismatch')
                selected = info.get('requested_subtitles') or {}
                # Never import a stale file just because its filename resembles English.
                from caption_worker import select_native
                if len(selected) > 1: raise ValueError('Expected one selected caption track')
                valid = select_native({k:[v] for k,v in selected.items()}, {})
                if selected and not valid: raise ValueError('Selected caption is translated or unsupported')
                language = next(iter(valid), None)
                caption = folder / (vid + '.' + language + '.vtt') if language else None
                if caption is None or not caption.is_file():
                    result['status'] = 'no_english_caption_saved'
                else:
                    cues = parse_captions(caption)
                    provenance = {'adapter': 'yt-dlp caption-only', 'permission_basis': permission_basis,
                                  'source_id': vid, 'url': info.get('webpage_url'),
                                  'channel': info.get('channel'), 'title': info.get('title'),
                                  'teacher_verification': 'catalog attribution; independent review required',
                                  'language': language,
                                  'generation': selected[language].get('collector_generation', 'unknown; review required')}
                    lib.attach(vid, caption, json.dumps(provenance))
                    process(lib, vid)
                    result.update(status='saved_quality_review', segments=len(cues), language=language,
                                  generation=provenance['generation'])
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
        except Exception as exc:
            result.update(status='failed', error=str(exc))
        if result['status'] != 'rate_limited':
            lib.set_setting('youtube_next_request_at', clock() + PACE_SECONDS)
        report['results'].append(result)
        atomic(report_path, report)
        progress(vid + ': ' + result['status'])
        progress('REFRESH')
        if result['status'] == 'rate_limited':
            progress('Rate limited: saved cooldown. No more requests in this pass.')
            break
        # Prevent thousands of repeated failures, including environmental failures.
        if result['status'] in ('access_blocked', 'dependency_missing', 'request_failed', 'timeout', 'failed'):
            break
    report['attempted_this_run'] = attempted_now
    atomic(report_path, report)
    return report
