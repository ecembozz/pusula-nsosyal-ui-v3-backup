import json
import tempfile
import unittest
from pathlib import Path

from core.cached_semantic import CachedSemanticLabeler
from core.heuristic_labeler import HeuristicLabeler
from core.hybrid_labeler import HybridLabeler
from core.labeling import LabelResult, text_fingerprint


class LabelingV2Tests(unittest.TestCase):
    def test_label_result_validates_range(self):
        with self.assertRaises(ValueError):
            LabelResult(1.2, 0.0, 0.0, 0.0, 0.0, method="test")

    def test_fingerprint_normalizes_whitespace(self):
        self.assertEqual(text_fingerprint("a  b\n c"), text_fingerprint("a b c"))

    def test_heuristic_adapter_uses_pinned_snapshot(self):
        result = HeuristicLabeler().label("Fourier dönüşümü nasıl çalışır? Adım adım anlatıyorum.")
        self.assertEqual(result.method, "heuristic")
        self.assertEqual(len(result.intent_vector), 4)
        self.assertGreater(result.ogretici, result.haber)
        self.assertIsNone(result.confidence)

    def test_cached_semantic_labeler(self):
        text = "Bu örnek sadece cache doğrulaması için."
        row = {
            "text_sha256": text_fingerprint(text),
            "intent": {"ogretici": 0.8, "eglendirici": 0.1, "haber": 0.2, "sosyal": 0.3},
            "clickbait": 0.05,
            "confidence": 0.91,
            "method": "semantic",
            "model": "test-model",
            "prompt_version": "test-v1",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cache.jsonl"
            path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
            labeler = CachedSemanticLabeler(path)
            result = labeler.label(text)
            self.assertAlmostEqual(result.ogretici, 0.8)
            self.assertAlmostEqual(result.confidence or 0.0, 0.91)

    def test_hybrid_falls_back_on_low_confidence(self):
        class LowConfidence:
            name = "low"

            def label(self, text):
                return LabelResult(0.9, 0.1, 0.1, 0.1, 0.0, method="semantic", confidence=0.3)

        class Fallback:
            name = "fallback"

            def label(self, text):
                return LabelResult(0.2, 0.8, 0.1, 0.1, 0.0, method="heuristic")

        result = HybridLabeler(LowConfidence(), Fallback(), min_confidence=0.65).label("x")
        self.assertEqual(result.method, "heuristic")
        self.assertAlmostEqual(result.eglendirici, 0.8)

    def test_hybrid_keeps_high_confidence_semantic(self):
        class HighConfidence:
            name = "high"

            def label(self, text):
                return LabelResult(0.9, 0.1, 0.1, 0.1, 0.0, method="semantic", confidence=0.92)

        class Fallback:
            name = "fallback"

            def label(self, text):
                raise AssertionError("fallback should not run")

        result = HybridLabeler(HighConfidence(), Fallback(), min_confidence=0.65).label("x")
        self.assertEqual(result.method, "hybrid-semantic")
        self.assertAlmostEqual(result.confidence or 0.0, 0.92)


if __name__ == "__main__":
    unittest.main()
