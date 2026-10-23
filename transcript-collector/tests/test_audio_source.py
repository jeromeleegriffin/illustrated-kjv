import json
import tempfile
import unittest
import wave
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audio_worker import select_original, validate_media
from audio_source import collect_audio
from engine import Library

class AudioTests(unittest.TestCase):
 def test_original_selection_excludes_dubs(self):
  formats=[dict(language='es',format_note='original',vcodec='none',acodec='aac',ext='m4a',abr=200),dict(language='en-US',format_note='dubbed',vcodec='none',acodec='aac',ext='m4a',abr=200),dict(language='en-US',format_note='original (default)',vcodec='none',acodec='aac',ext='m4a',abr=128)]
  self.assertIs(select_original(formats),formats[2])
  with self.assertRaises(ValueError):select_original(formats[:2])
 def test_error_page_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'fake.m4a';p.write_text('<html><h1>Site Unavailable</h1></html>')
   with self.assertRaisesRegex(ValueError,'webpage'):validate_media(p,3510)
 def test_decode_and_truncation(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'fixture.wav'
   with wave.open(str(p),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(b'\x01\x00'*16000*5)
   self.assertAlmostEqual(validate_media(p,5),5)
   with self.assertRaisesRegex(ValueError,'Incomplete'):validate_media(p,3510)
 def test_provider_hold_prevents_request(self):
  with tempfile.TemporaryDirectory() as d:
   lib=Library(d)
   lib.set_setting('online_enabled',True);lib.set_setting('youtube_audio_enabled',True)
   lib.set_setting('youtube_access_hold',{'id':'test'})
   def forbidden(*a,**kw):raise AssertionError('Network request during hold')
   self.assertEqual(collect_audio(lib,'test',runner=forbidden),0);lib.close()
