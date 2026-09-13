import unittest

from core.ranking import INTENTS, cosine, pusula_parts
from core.reranking import author_factor, filter_seen, rerank_feed


class RankingV2Tests(unittest.TestCase):
    def test_cosine_identity(self):
        self.assertAlmostEqual(cosine([1, 2, 3], [1, 2, 3]), 1.0, places=9)

    def test_quality_is_multiplicative_gate(self):
        post = {
            "tahmin_niyet": list(INTENTS["ogrenmek"]),
            "tazelik": 1.0,
            "etkilesim_puani": 1.0,
            "clickbait": 1.0,
        }
        parts = pusula_parts(post, "ogrenmek")
        self.assertGreater(parts["base"], 0.9)
        self.assertEqual(parts["quality"], 0.0)
        self.assertEqual(parts["score"], 0.0)

    def test_seen_filter(self):
        posts = [{"id": 1}, {"id": 2}, {"id": 3}]
        self.assertEqual([p["id"] for p in filter_seen(posts, {2})], [1, 3])

    def test_author_decay(self):
        self.assertEqual(author_factor(0), 1.0)
        self.assertEqual(author_factor(1), 0.5)
        self.assertEqual(author_factor(2), 0.25)
        self.assertEqual(author_factor(5), 0.25)

    def test_repeated_author_is_deprioritized(self):
        posts = [
            {
                "id": 1,
                "author_id": "same",
                "tahmin_niyet": [1.0, 0.1, 0.1, 0.1],
                "tazelik": 0.9,
                "etkilesim_puani": 0.9,
                "clickbait": 0.0,
            },
            {
                "id": 2,
                "author_id": "same",
                "tahmin_niyet": [0.98, 0.1, 0.1, 0.1],
                "tazelik": 0.9,
                "etkilesim_puani": 0.88,
                "clickbait": 0.0,
            },
            {
                "id": 3,
                "author_id": "other",
                "tahmin_niyet": [0.94, 0.12, 0.1, 0.1],
                "tazelik": 0.85,
                "etkilesim_puani": 0.82,
                "clickbait": 0.0,
            },
        ]
        out = rerank_feed(posts, "ogrenmek", limit=3, mmr_alpha=1.0)
        self.assertEqual(out[0]["id"], 1)
        self.assertEqual(out[1]["id"], 3)
        self.assertEqual(out[2]["id"], 2)

    def test_mmr_prefers_semantic_variety(self):
        posts = [
            {
                "id": 1,
                "author_id": "a",
                "tahmin_niyet": [1.0, 0.1, 0.1, 0.1],
                "embedding": [1.0, 0.0],
                "tazelik": 0.9,
                "etkilesim_puani": 0.9,
                "clickbait": 0.0,
            },
            {
                "id": 2,
                "author_id": "b",
                "tahmin_niyet": [0.99, 0.1, 0.1, 0.1],
                "embedding": [0.999, 0.01],
                "tazelik": 0.9,
                "etkilesim_puani": 0.89,
                "clickbait": 0.0,
            },
            {
                "id": 3,
                "author_id": "c",
                "tahmin_niyet": [0.92, 0.15, 0.1, 0.1],
                "embedding": [0.0, 1.0],
                "tazelik": 0.82,
                "etkilesim_puani": 0.78,
                "clickbait": 0.0,
            },
        ]
        out = rerank_feed(posts, "ogrenmek", limit=3, mmr_alpha=0.7)
        self.assertEqual(out[0]["id"], 1)
        self.assertEqual(out[1]["id"], 3)


if __name__ == "__main__":
    unittest.main()
