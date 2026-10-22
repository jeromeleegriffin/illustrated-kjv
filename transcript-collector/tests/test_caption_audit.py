import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from caption_audit import reconcile
from engine import Library

class AuditEvidenceTests(unittest.TestCase):
    def test_success_requires_valid_saved_file_and_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root/'catalog.json'
            catalog.write_text(json.dumps({'books':[{'name':'Genesis','lessons':[
                {'id':'abcdefghijk','teacher':'Arnold Murray','start':[1,1],'end':[1,2]}]}]}))
            folder = root/'exports'; folder.mkdir()
            observation = [{'id':'abcdefghijk','status':'export_saved'}]
            report = reconcile(catalog, folder, root/'library', observation)
            self.assertEqual(report['counts'], {'tested_unresolved':1})
            file = folder/'abcdefghijk.txt'
            file.write_text('YouTube transcript\nVideo ID: wrongvideo1\n\n[0:01] synthetic text\n')
            report = reconcile(catalog, folder, root/'library', observation)
            self.assertEqual(report['counts'], {'tested_unresolved':1})
            file.write_text('YouTube transcript\nVideo ID: abcdefghijk\nCaptions: auto-generated\n\n[0:01] synthetic text\n')
            for _ in range(2):
                report = reconcile(catalog, folder, root/'library', observation)
                self.assertEqual(report['counts'], {'saved_quality_review':1})
                self.assertEqual(report['verification']['structurally_valid'],1)
                self.assertEqual(report['verified_complete'],0)
            with self.assertRaises(ValueError):
                reconcile(catalog, folder, root/'library', [{'id':'unknownid00','status':'export_saved'}])
            # Corrupt only a disposable test index, not its source transcript.
            lib = Library(root/'library')
            with lib.db:
                lib.db.execute("UPDATE search_data SET block=x'0000' WHERE id=(SELECT max(id) FROM search_data)")
            result = lib.verify()
            self.assertFalse(result['library_usable'])
            self.assertTrue(result['database_errors'])
            self.assertEqual(result['structurally_valid'],1)
            lib.close()

if __name__ == '__main__':
    unittest.main()
