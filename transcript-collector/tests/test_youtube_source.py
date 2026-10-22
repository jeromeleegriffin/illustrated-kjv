import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import Library
from youtube_source import collect

class YouTubeSourceTests(unittest.TestCase):
    def library(self, root):
        catalog = root / 'catalog.json'
        catalog.write_text(json.dumps({'books':[{'name':'Genesis','lessons':[
            {'id':id,'teacher':'Arnold Murray','start':[1,1],'end':[1,2]}
            for id in ('abcdefghijk','lmnopqrstuv')]}]}))
        lib = Library(root/'library', catalog)
        lib.set_setting('online_enabled', True)
        return lib

    def test_block_persists_and_stops_whole_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = self.library(Path(tmp)); calls = []
            def blocked(*args, **kwargs):
                calls.append(args)
                return SimpleNamespace(returncode=1,stdout='',stderr='HTTP Error 429: Too Many Requests')
            report = collect(lib, 'synthetic test only', runner=blocked)
            self.assertEqual(len(calls), 1)
            self.assertEqual(report['results'][0]['status'],'access_blocked')
            self.assertEqual(lib.row('lmnopqrstuv')['status'], 'cataloged')
            lib.close(); lib = Library(Path(tmp)/'library')
            with self.assertRaises(ValueError):collect(lib,'synthetic test only',runner=blocked)
            self.assertEqual(len(calls), 1); lib.close()

    def test_success_requires_real_valid_caption_and_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = self.library(Path(tmp))
            def saved(command, **kwargs):
                vid = command[-1].split('=')[-1]
                folder = lib.root/'youtube-captions'
                (folder/(vid+'.info.json')).write_text(json.dumps({'id':vid}))
                if vid == 'abcdefghijk':
                    (folder/(vid+'.en.vtt')).write_text('WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nSynthetic beginning fixture\n')
                return SimpleNamespace(returncode=0,stdout='',stderr='')
            report = collect(lib,'synthetic test only',runner=saved)
            self.assertEqual([r['status'] for r in report['results']],['saved_quality_review','no_english_caption_saved'])
            self.assertEqual(len(lib.find('beginning')),1)
            self.assertEqual(len(collect(lib,'synthetic test only',runner=lambda *a,**k: self.fail('unnecessary retry'))['results']),2)
            lib.close()
