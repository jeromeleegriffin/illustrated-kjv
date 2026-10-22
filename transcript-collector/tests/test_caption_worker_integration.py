"""Real yt-dlp pipeline against localhost only; metadata is synthetic."""
import importlib.util
import json
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import caption_worker


@unittest.skipUnless(importlib.util.find_spec('yt_dlp'), 'Requires installed pinned yt-dlp')
class WorkerIntegrationTests(unittest.TestCase):
    def test_real_downloader_saves_selected_native_track_and_metadata(self):
        import yt_dlp
        hits = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                hits.append(self.path)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nSynthetic native caption fixture\n')

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                base = 'http://127.0.0.1:' + str(server.server_port)

                def extract(downloader, url, *args, **kwargs):
                    return downloader.process_ie_result({
                        'id':'abcdefghijk', 'title':'Synthetic fixture', 'extractor':'fixture',
                        'webpage_url':'https://example.invalid/watch',
                        'url':base+'/NEVER-download-video', 'ext':'mp4',
                        'automatic_captions':{
                            'en':[{'ext':'vtt','url':base+'/translated?tlang=en'}],
                            'en-orig':[{'ext':'vtt','url':base+'/native?lang=en'}]}}, download=True)

                argv = ['caption_worker.py', '--ignore-config', '--skip-download',
                        '--write-subs', '--write-auto-subs', '--sub-format', 'vtt',
                        '--write-info-json', '--no-clean-info-json', '--force-overwrites',
                        '-o', tmp+'/%(id)s.%(ext)s', 'https://example.invalid/watch']
                with patch.object(sys, 'argv', argv), patch.object(yt_dlp.YoutubeDL, 'extract_info', extract):
                    self.assertEqual(caption_worker.main(), 0)
                info = json.loads((Path(tmp)/'abcdefghijk.info.json').read_text(encoding='utf-8'))
                self.assertEqual(hits, ['/native?lang=en'])
                self.assertEqual(list(info['requested_subtitles']), ['en-orig'])
                self.assertEqual(info['requested_subtitles']['en-orig']['collector_generation'], 'automatic caption')
                self.assertTrue((Path(tmp)/'abcdefghijk.en-orig.vtt').is_file())
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
