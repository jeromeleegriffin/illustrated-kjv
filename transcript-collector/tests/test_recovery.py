import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recover_captions import rebuild
from engine import Library

class RecoveryTests(unittest.TestCase):
    def test_independent_recovery_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root / 'catalog.json'
            catalog.write_text(json.dumps({'books':[{'name':'Genesis','lessons':[
                {'id':'abcdefghijk','teacher':'Arnold Murray','start':[1,1],'end':[1,2]}]}]}))
            source = root / 'sources'; source.mkdir()
            caption = source / 'abcdefghijk.txt'
            text = 'YouTube transcript\nVideo ID: abcdefghijk\n\n[0:01] beginning synthetic fixture\n'
            caption.write_text(text)
            target = root / 'recovered'
            result = rebuild(catalog, source, target)
            self.assertTrue(result['recovery']['usable'])
            self.assertEqual(caption.read_text(), text)
            # Recovered library remains usable when original exports move away.
            caption.unlink()
            lib = Library(target)
            self.assertEqual(len(lib.find('beginning')), 1)
            self.assertTrue(lib.verify()['library_usable'])
            lib.close()
            caption.write_text(text)
            with self.assertRaises(FileExistsError):
                rebuild(catalog, source, target)
            with self.assertRaises(FileExistsError):
                rebuild(catalog, source, source)
