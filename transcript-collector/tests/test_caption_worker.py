import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from caption_worker import select_native


def caption(query='lang=en', ext='vtt'):
    return {'ext':ext, 'url':'https://example.invalid/captions?' + query}


class NativeCaptionTests(unittest.TestCase):
    def test_original_preferred_over_translated_plain_en(self):
        result = select_native({}, {'en':[caption('lang=de&tlang=en')], 'en-orig':[caption()]})
        self.assertEqual(list(result), ['en-orig'])
        self.assertEqual(result['en-orig']['collector_generation'], 'automatic caption')

    def test_authored_english_preferred_and_only_one_download(self):
        result = select_native({'en-GB':[caption('lang=en-GB')]}, {'en-orig':[caption()]})
        self.assertEqual(list(result), ['en-GB'])
        self.assertEqual(result['en-GB']['collector_generation'], 'authored caption')

    def test_no_translation_even_if_label_says_original(self):
        for query in ('lang=de&tlang=en', 'lang=en&tlang=', 'lang=en&%74lang=en'):
            self.assertEqual(select_native({}, {'en-orig':[caption(query)]}), {})

    def test_native_alias_supported_without_original_label(self):
        self.assertEqual(list(select_native({}, {'en':[caption()]})), ['en'])

    def test_non_english_or_unsupported_formats_are_not_imported(self):
        self.assertEqual(select_native({'de':[caption('lang=de')]}, {'en':[caption(ext='json3')]}), {})

    def test_input_metadata_not_mutated(self):
        item = caption()
        select_native({'en':[item]}, {})
        self.assertNotIn('collector_generation', item)
