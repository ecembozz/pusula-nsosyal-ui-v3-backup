import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'v2_realistic'/'raw_posts.jsonl'
HARD=ROOT/'data'/'gold_eval'/'candidate_hard_cases.jsonl'
NEWS=ROOT/'data'/'gold_eval'/'candidate_news_cases.jsonl'
DRAFT=ROOT/'data'/'gold_eval'/'draft_labels_annotator_a.jsonl'

DIMS=('ogretici','eglendirici','haber','sosyal')
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

    def test_hard_development_cases(self):
        hard=load_jsonl(HARD)
        news=load_jsonl(NEWS)
        rows=hard+news
        self.assertEqual(len(hard),40)
        self.assertEqual(len(news),8)
        self.assertEqual(len(rows),48)
        self.assertEqual(len({r['id'] for r in rows}),48)
        self.assertEqual(len({r['text'] for r in rows}),48)
        for r in rows:
            self.assertTrue(r['challenge'])
            self.assertTrue(20<=len(r['text'])<=280)
            self.assertFalse(any(p.search(r['text']) for p in PII))

    def test_single_annotator_draft_schema(self):
        cases={r['id'] for r in load_jsonl(HARD)+load_jsonl(NEWS)}
        labels=load_jsonl(DRAFT)
        self.assertEqual(len(labels),48)
        self.assertEqual({r['id'] for r in labels},cases)
        distribution=Counter()
        for r in labels:
            self.assertEqual(r['annotation_status'],'draft_single_annotator')
            self.assertEqual(r['annotator_role'],'assistant_draft_a')
            self.assertIn(r['dominant_intent'],DIMS)
            self.assertTrue(0.0<=float(r['clickbait'])<=1.0)
            self.assertTrue(0.0<=float(r['annotation_confidence'])<=1.0)
            self.assertEqual(set(r['intent']),set(DIMS))
            for dim in DIMS:
                self.assertTrue(0.0<=float(r['intent'][dim])<=1.0)
            # Dominant must match the maximum draft dimension. Ties are allowed
            # only when the recorded dominant is one of the maxima.
            mx=max(float(r['intent'][d]) for d in DIMS)
            self.assertAlmostEqual(float(r['intent'][r['dominant_intent']]),mx)
            distribution[r['dominant_intent']]+=1
        self.assertEqual(distribution,Counter({'sosyal':15,'eglendirici':13,'ogretici':12,'haber':8}))

if __name__=='__main__':
    unittest.main()
