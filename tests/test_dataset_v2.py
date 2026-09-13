import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'v2_realistic'/'raw_posts.jsonl'
HARD=ROOT/'data'/'gold_eval'/'candidate_hard_cases.jsonl'

PII=[
    re.compile(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b'),
    re.compile(r'https?://|www\.',re.I),
    re.compile(r'(?<!\d)(?:\+?90\s*)?0?5\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}(?!\d)'),
    re.compile(r'(?<!\d)\d{11}(?!\d)'),
    re.compile(r'(?<!\w)@[A-Za-z0-9_]{2,}'),
]

def load_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

class DatasetV2Tests(unittest.TestCase):
    def test_raw_corpus(self):
        rows=load_jsonl(RAW)
        self.assertEqual(len(rows),320)
        self.assertEqual(len({r['id'] for r in rows}),320)
        self.assertEqual(len({r['text'] for r in rows}),320)
        topics={}
        for r in rows:
            topics[r['topic_family']]=topics.get(r['topic_family'],0)+1
            self.assertEqual(r['provenance'],'synthetic_original')
            self.assertEqual(r['source_basis'],'public_topic_ecology_not_user_posts')
            self.assertIsNone(r['human_label'])
            self.assertTrue(20<=len(r['text'])<=280)
            self.assertFalse(any(p.search(r['text']) for p in PII))
        self.assertEqual(set(topics.values()),{32})
        self.assertEqual(len(topics),10)

    def test_hard_gold_candidates(self):
        rows=load_jsonl(HARD)
        self.assertEqual(len(rows),40)
        self.assertEqual(len({r['id'] for r in rows}),40)
        self.assertEqual(len({r['text'] for r in rows}),40)
        for r in rows:
            self.assertTrue(r['challenge'])
            self.assertTrue(20<=len(r['text'])<=280)
            self.assertFalse(any(p.search(r['text']) for p in PII))

if __name__=='__main__':
    unittest.main()
