import csv
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cleaner import clean_text, char_ngrams, whitespace_tokens, PREPROCESS_VERSION
from importlib import import_module
m5 = import_module('05_prepare_m2_documents')

class TestM5(unittest.TestCase):
    def test_whitespace(self):
        self.assertEqual(clean_text(' A  \n B '),'A B')
    def test_nfc(self):
        self.assertEqual(clean_text('가'),'가')
    def test_id_preservation(self):
        s=clean_text(' WCAG 2.4.4  aria-label  COMP-LINK-001 ')
        for x in ('WCAG 2.4.4','aria-label','COMP-LINK-001'):
            self.assertIn(x,s)
    def test_negative_preservation(self):
        self.assertIn('않습니다',clean_text('적합하지   않습니다'))
    def test_oov(self):
        known={'규칙'}
        self.assertNotIn('메타정합검증',known)
    def test_ngrams(self):
        self.assertEqual(char_ngrams('규칙',2),['규칙'])
    def test_default_applied(self):
        docs=m5.prepare()
        self.assertEqual(len(docs),7)
        self.assertTrue(all(d['metadata']['status']=='applied' for d in docs))
    def test_include_proposed(self):
        self.assertEqual(len(m5.prepare(include_proposed=True)),8)
    def test_metadata(self):
        doc=next(d for d in m5.prepare() if d['document_id']=='COMP-LINK-001')
        self.assertEqual(doc['metadata']['preprocess_version'],PREPROCESS_VERSION)
        self.assertTrue(doc['metadata']['tree_path'])
        self.assertEqual(doc['metadata']['source_file'],'rules.csv')
        self.assertIn('reason:',doc['raw_text'])
    def test_preserve_text(self):
        docs=m5.prepare()
        self.assertTrue(all('raw_text' in d and 'clean_text' in d for d in docs))
    def test_file_count_and_schema(self):
        rows=m5.read_csv('rules.csv')
        self.assertEqual(len(rows),8)
        self.assertIn('reference_url',rows[0])
    def test_invalid_csv_path(self):
        with self.assertRaises(ValueError):m5.read_csv('../secret.csv')
    def test_tree(self):
        m=m5.tree_map()
        self.assertIn('ROOT',m)
        self.assertIn('웹 정합성 검사',m5.make_tree_path('ROOT',m))
    def test_no_blank_ids(self):
        self.assertTrue(all(d['document_id'] for d in m5.prepare()))

if __name__=='__main__':
    unittest.main()
