"""Select one native English caption; never request server-side translation."""
import re
import sys
import os
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


def select_native(normal, automatic):
    """Prefer authored English, then original English ASR, then native aliases.

    Check URLs as well as labels: plain 'en' can be a translated track.
    Return only VTT and one language so a second download cannot fail the job.
    """
    for tracks, generation in ((normal, 'authored caption'), (automatic, 'automatic caption')):
        tracks = tracks or {}
        keys = sorted(tracks, key=lambda k: (not k.endswith('-orig'), k != 'en', k))
        for key in keys:
            if not re.fullmatch(r'en(?:-[A-Za-z]{2,3})?(?:-orig)?', key):
                continue
            for fmt in reversed(tracks[key]):
                url = fmt.get('url', '')
                parsed = urlsplit(url)
                if fmt.get('ext') != 'vtt' or parsed.scheme not in ('http', 'https'):
                    continue
                if 'tlang' in parse_qs(parsed.query, keep_blank_values=True):
                    continue
                return {key: dict(fmt, collector_generation=generation,
                                  collector_selection='native English; no translation parameter')}
    return {}


def main():
    import yt_dlp

    class NativeEnglishDL(yt_dlp.YoutubeDL):
        def process_subtitles(self, video_id, normal_subtitles, automatic_captions):
            selected = select_native(normal_subtitles, automatic_captions)
            # Optional diagnostic side channel: allowlisted fields only, never URLs.
            if os.environ.get('GRIFFIN_CAPTION_DIAGNOSTIC'):
                target = Path(os.environ['GRIFFIN_CAPTION_DIAGNOSTIC'])
                payload = {'video_id': video_id, 'discovery': 'completed',
                           'selection': 'selected' if selected else 'no_supported_native_english_track',
                           'tracks': [{'language': k, 'generation': v['collector_generation']}
                                      for k, v in selected.items()]}
                tmp = target.with_suffix('.tmp')
                tmp.write_text(json.dumps(payload), encoding='utf-8')
                tmp.replace(target)
            self.to_screen('[collector] Native English caption: ' + (', '.join(selected) or 'unavailable'))
            return selected

    opts = yt_dlp.parse_options(sys.argv[1:])
    with NativeEnglishDL(opts.ydl_opts) as downloader:
        return downloader.download(opts.urls)


if __name__ == '__main__':
    sys.exit(main())
