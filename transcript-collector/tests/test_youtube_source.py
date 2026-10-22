import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import Library
from youtube_source import collect as real_collect, wait_until

class Clock:
    def __init__(self): self.value=100000
    def time(self): return self.value
    def sleep(self, seconds): self.value+=seconds

def collect(*args, **kwargs):
    clock=Clock()
    kwargs.setdefault("clock",clock.time)
    kwargs.setdefault("sleep",clock.sleep)
    return real_collect(*args,**kwargs)

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
                return SimpleNamespace(returncode=1,stdout='',stderr='HTTP Error 403: Forbidden')
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
                (folder/(vid+'.info.json')).write_text(json.dumps({'id':vid,'requested_subtitles':{'en':{'ext':'vtt','url':'https://example.invalid/captions?lang=en'}}}))
                if vid == 'abcdefghijk':
                    (folder/(vid+'.en.vtt')).write_text('WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nSynthetic beginning fixture\n')
                return SimpleNamespace(returncode=0,stdout='',stderr='')
            report = collect(lib,'synthetic test only',runner=saved)
            self.assertEqual([r['status'] for r in report['results']],['saved_quality_review','no_english_caption_saved'])
            self.assertEqual(len(lib.find('beginning')),1)
            self.assertEqual(len(collect(lib,'synthetic test only',runner=lambda *a,**k: self.fail('unnecessary retry'))['results']),2)
            lib.close()

    def test_preflight_bounds_requests_then_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = self.library(Path(tmp)); calls = []
            def empty(command, **kwargs):
                calls.append(command[-1])
                return SimpleNamespace(returncode=0, stdout='', stderr='')
            first = collect(lib,'fixture',runner=empty,max_new=1)
            self.assertEqual(len(first['results']),1)
            second = collect(lib,'fixture',runner=empty)
            self.assertEqual(len(second['results']),2)
            self.assertEqual(len(set(calls)),2)
            lib.close()

    def test_english_variant_and_unrelated_numbers_are_not_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = self.library(Path(tmp))
            def saved(command, **kwargs):
                self.assertEqual(kwargs['encoding'],'utf-8')
                vid=command[-1].split('=')[-1]
                folder=lib.root/'youtube-captions'
                (folder/(vid+'.info.json')).write_text(json.dumps({'id':vid,'requested_subtitles':{'en-US':{'ext':'vtt','url':'https://example.invalid/captions?lang=en-US'}}}))
                (folder/(vid+'.en-US.vtt')).write_text('WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nSynthetic English variant\n')
                return SimpleNamespace(returncode=0,stdout='Lesson 403 duration 429',stderr='')
            report=collect(lib,'fixture',runner=saved,max_new=1)
            self.assertEqual(report['results'][0]['status'],'saved_quality_review')
            self.assertFalse(lib.setting('youtube_access_hold',False))
            from diagnostics import access_summary
            summary=access_summary(lib.root)
            self.assertIn('Saved for quality review: 1',summary)
            self.assertNotIn('Synthetic English variant',summary)
            lib.close()

    def test_explicit_resume_retries_transient_failure_at_most_three(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib=self.library(Path(tmp)); calls=[]
            def unavailable(command,**kwargs):
                calls.append(command[-1])
                return SimpleNamespace(returncode=1,stdout='',stderr='No module named yt_dlp')
            for _ in range(4):collect(lib,'fixture',runner=unavailable)
            self.assertEqual(sum(url.endswith('abcdefghijk') for url in calls),3)
            self.assertEqual(sum(url.endswith('lmnopqrstuv') for url in calls),1)
            lib.close()

    def test_rate_limit_persists_wait_then_retries_same_recording(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib=self.library(Path(tmp)); clock=Clock(); calls=[]
            def limited(command, **kwargs):
                calls.append(clock.time())
                self.assertIn('caption_worker.py', command[1])
                self.assertIn('youtube:skip=translated_subs,hls,dash', command)
                return SimpleNamespace(returncode=1,stdout='',stderr='HTTP Error 429: Too Many Requests')
            first=real_collect(lib,'fixture',runner=limited,clock=clock.time,sleep=clock.sleep)
            self.assertEqual(first['results'][-1]['status'],'rate_limited')
            self.assertFalse(lib.setting('youtube_access_hold',None))
            lib.close();lib=Library(Path(tmp)/'library')
            real_collect(lib,'fixture',runner=limited,clock=clock.time,sleep=clock.sleep)
            self.assertGreaterEqual(calls[1]-calls[0],3600)
            real_collect(lib,'fixture',runner=limited,clock=clock.time,sleep=clock.sleep)
            self.assertGreaterEqual(calls[2]-calls[1],7200)
            with self.assertRaises(ValueError):real_collect(lib,'fixture',runner=limited,clock=clock.time,sleep=clock.sleep)
            self.assertEqual(len(calls),3);lib.close()

    def test_legacy_429_migration_and_pause_send_no_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib=self.library(Path(tmp));vid='abcdefghijk';clock=Clock()
            lib.status(vid,'access_blocked','legacy')
            lib.set_setting('youtube_access_hold',{'id':vid})
            (lib.root/'youtube-source-report.json').write_text(json.dumps({'results':[{'id':vid,'status':'access_blocked','diagnostic':'HTTP Error 429: Too Many Requests'}]}))
            real_collect(lib,'fixture',stop=lambda:True,runner=lambda *a,**k:self.fail('request during pause'),clock=clock.time,sleep=clock.sleep)
            self.assertEqual(lib.setting('youtube_next_request_at'),103600)
            self.assertIsNone(lib.setting('youtube_access_hold'))
            self.assertEqual(lib.row(vid)['status'],'temporarily_failed')
            self.assertFalse(wait_until(104000,lambda:True,lambda x:None,clock.time,clock.sleep))
            lib.close()

    def test_pacing_is_persistent_between_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib=self.library(Path(tmp));clock=Clock();calls=[]
            def empty(command,**kwargs):
                calls.append(clock.time())
                return SimpleNamespace(returncode=0,stdout='',stderr='')
            real_collect(lib,'fixture',runner=empty,max_new=1,clock=clock.time,sleep=clock.sleep)
            lib.close();lib=Library(Path(tmp)/'library')
            real_collect(lib,'fixture',runner=empty,clock=clock.time,sleep=clock.sleep)
            self.assertGreaterEqual(calls[1]-calls[0],60);lib.close()

    def test_stale_caption_without_current_selection_is_not_imported(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib=self.library(Path(tmp))
            folder=lib.root/'youtube-captions';folder.mkdir()
            (folder/'abcdefghijk.en.vtt').write_text('WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nStale caption\n')
            def empty(command,**kwargs):
                (folder/'abcdefghijk.info.json').write_text(json.dumps({'id':'abcdefghijk','requested_subtitles':{}}))
                return SimpleNamespace(returncode=0,stdout='',stderr='')
            report=collect(lib,'fixture',runner=empty,max_new=1)
            self.assertEqual(report['results'][-1]['status'],'no_english_caption_saved')
            self.assertFalse(lib.row('abcdefghijk')['source']);lib.close()

    def test_migration_does_not_consume_a_network_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib=self.library(Path(tmp));vid='abcdefghijk';calls=[]
            (lib.root/'youtube-source-report.json').write_text(json.dumps({'results':[
                {'id':vid,'status':'rate_limited'},
                {'id':vid,'status':'rate_limited','migration':'no network request'},
                {'id':vid,'status':'rate_limited'}]}))
            def failed(command,**kwargs):
                calls.append(command[-1]);return SimpleNamespace(returncode=1,stdout='',stderr='temporary network failure')
            collect(lib,'fixture',runner=failed,max_new=1)
            self.assertTrue(calls[0].endswith(vid));lib.close()
