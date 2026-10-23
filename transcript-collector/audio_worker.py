"""Bounded original-English audio retrieval; no credentials or restriction bypass."""
import json
import math
import shutil
import sys
from pathlib import Path
from engine import atomic, digest


def select_original(formats):
    eligible = [f for f in formats if str(f.get('language', '')).lower().split('-')[0] == 'en'
                and 'original' in str(f.get('format_note', '')).lower()
                and f.get('vcodec') == 'none' and f.get('acodec') not in (None, 'none')
                and f.get('ext') in ('m4a', 'webm')]
    if not eligible:
        raise ValueError('No explicitly identified original English audio track; manual source review needed')
    return max(eligible, key=lambda f: float(f.get('abr') or f.get('tbr') or 0))


def validate_media(path, expected_duration):
    if not math.isfinite(expected_duration) or expected_duration <= 0:
        raise ValueError('Missing recording duration')
    with open(path, 'rb') as handle:
        prefix = handle.read(512).lstrip().lower()
    if not prefix or prefix.startswith((b'<', b'{', b'[')):
        raise ValueError('Downloaded response is empty or a webpage, not audio')
    import av
    duration = 0.0
    with av.open(str(path)) as media:
        if not media.streams.audio:
            raise ValueError('No audio stream')
        for frame in media.decode(audio=0):
            duration += frame.samples / frame.sample_rate
    if duration <= 0 or abs(duration - expected_duration) > max(3, expected_duration * .01):
        raise ValueError(f'Incomplete audio: decoded {duration:.1f}s; expected {expected_duration:.1f}s')
    return duration


def retrieve(video_id, folder, max_bytes, reserve_bytes):
    from yt_dlp import YoutubeDL
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    receipt = folder / (video_id + '.verified.json')
    if receipt.exists():
        data = json.loads(receipt.read_text(encoding='utf-8'))
        path = folder / data['filename']
        if path.parent != folder or data['id'] != video_id:
            raise ValueError('Invalid cached receipt identity')
        if path.is_file() and digest(path) == data['sha256']:
            return data
    def budget(progress):
        if progress.get('downloaded_bytes', 0) > max_bytes or shutil.disk_usage(folder).free < reserve_bytes:
            raise ValueError('Download stopped at configured disk limit')
    if shutil.disk_usage(folder).free < reserve_bytes + max_bytes:
        raise ValueError('Insufficient free space for configured download allowance')
    options = {'ignoreconfig': True, 'noplaylist': True, 'socket_timeout': 15,
               'retries': 0, 'extractor_retries': 0, 'fragment_retries': 0,
               'fixup': 'never', 'progress_hooks': [budget], 'max_filesize': max_bytes,
               'outtmpl': str(folder / (video_id + '.%(ext)s')), 'continuedl': True}
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info('https://www.youtube.com/watch?v=' + video_id, download=False)
        if info.get('id') != video_id or info.get('is_live'):
            raise ValueError('Recording identity mismatch or live recording')
        chosen = select_original(info.get('formats', []))
        ydl.params['format'] = chosen['format_id']
        ydl.process_ie_result(info, download=True)
    path = folder / (video_id + '.' + chosen['ext'])
    duration = validate_media(path, float(info.get('duration') or 0))
    data = {'id': video_id, 'filename': path.name, 'sha256': digest(path), 'duration': duration,
            'format_id': chosen['format_id'], 'language': chosen['language'],
            'title': info.get('title'), 'status': 'media_verified',
            'url': 'https://www.youtube.com/watch?v=' + video_id}
    atomic(receipt, data)
    return data

if __name__ == '__main__':
    retrieve(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
