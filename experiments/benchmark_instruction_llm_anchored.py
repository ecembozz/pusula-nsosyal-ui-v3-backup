#!/usr/bin/env python3
"""Screen instruction-tuned models for offline PUSULA batch labeling.

This is a DEVELOPMENT benchmark only. It selects a deterministic balanced
subset from the single-annotator 48-case development set and asks the model for
five independent integer scores on a 0-100 anchored scale. No examples from the
development set are included in the prompt.
"""

from __future__ import annotations

import json
import math
import os
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = os.environ.get("PUSULA_INSTRUCTION_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
PER_CLASS = int(os.environ.get("PUSULA_SCREEN_PER_CLASS", "6"))
DIMS = ("ogretici", "eglendirici", "haber", "sosyal")

SYSTEM = """Sen PUSULA için Türkçe sosyal medya gönderilerini analiz eden bir etiketleme bileşenisin.
Kullanıcının ne istediğini tahmin etmiyorsun. Yalnızca verilen gönderinin hangi ihtiyaca ne kadar hizmet ettiğini puanlıyorsun.

Boyutlar birbirinden bağımsızdır; toplamları 100 olmak zorunda değildir:
- ogretici: bilgi, açıklama, yöntem, öneri veya öğrenilebilir fayda
- eglendirici: mizah, ironi, oyun, hikâye veya keyif verme
- haber: kamusal/güncel olay, duyuru, sonuç veya yeni gelişme aktarma
- sosyal: kişisel deneyim, duygu, fikir, sohbet daveti veya topluluk etkileşimi
- clickbait: yanıltıcı abartı, kasıtlı merak boşluğu veya vaat edilen bilgiyi saklama

Her alan için 0-100 arası TAM SAYI ver:
0 = hiç sinyal yok
25 = zayıf/ikincil
50 = belirgin ama baskın değil
75 = güçlü
100 = temel işlevlerden biri
Ara tam sayılar kullanılabilir. 0 puanı yalnız gerçekten sinyal yoksa kullan.
Mizah, emoji veya ünlem tek başına clickbait değildir. Kişisel durum güncellemesi tek başına haber değildir.
Yalnız JSON döndür; açıklama, markdown veya ek metin yazma."""

USER_TEMPLATE = """Gönderi:
{text}

Yalnız şu anahtarlarla JSON döndür:
{{"ogretici":0,"eglendirici":0,"haber":0,"sosyal":0,"clickbait":0}}"""


def read_jsonl(path: str):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def load_cases():
    cases = {}
    for path in ["data/gold_eval/candidate_hard_cases.jsonl", "data/gold_eval/candidate_news_cases.jsonl"]:
        for row in read_jsonl(path):
            cases[row["id"]] = row["text"]
    return cases


def select_balanced(gold_rows):
    """First N IDs per dominant class after lexical ID sort.

    This is deterministic and prevents manual/cherry-picked screening examples.
    """
    buckets = {d: [] for d in DIMS}
    for row in sorted(gold_rows, key=lambda r: r["id"]):
        buckets[row["dominant_intent"]].append(row)
    selected = []
    for dim in DIMS:
        if len(buckets[dim]) < PER_CLASS:
            raise SystemExit(f"not enough {dim} rows for PER_CLASS={PER_CLASS}")
        selected.extend(buckets[dim][:PER_CLASS])
    return sorted(selected, key=lambda r: r["id"])


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def macro_f1(gold, pred):
    vals, details = [], {}
    for label in DIMS:
        tp = sum(g == label and p == label for g, p in zip(gold, pred))
        fp = sum(g != label and p == label for g, p in zip(gold, pred))
        fn = sum(g == label and p != label for g, p in zip(gold, pred))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        details[label] = {"precision": precision, "recall": recall, "f1": f1, "support": sum(g == label for g in gold)}
        vals.append(f1)
    return sum(vals) / len(vals), details


def extract_scores(text: str):
    match = re.search(r"\{.*?\}", text, flags=re.S)
    if not match:
        raise ValueError("no JSON object")
    obj = json.loads(match.group(0))
    parsed = {}
    for key in (*DIMS, "clickbait"):
        if key not in obj:
            raise ValueError(f"missing key {key}")
        value = float(obj[key])
        if not 0 <= value <= 100:
            raise ValueError(f"out-of-range {key}={value}")
        parsed[key] = value / 100.0
    return parsed


def main():
    cases = load_cases()
    all_gold = read_jsonl("data/gold_eval/draft_labels_annotator_a.jsonl")
    gold = select_balanced(all_gold)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype="auto",
        low_cpu_mem_usage=True,
    )
    model.eval()
    model_commit = getattr(model.config, "_commit_hash", None)

    valid = []
    failures = []
    start = time.monotonic()

    for item in gold:
        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TEMPLATE.format(text=cases[item["id"]])},
        ]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=768)
        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=72,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        generated = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        try:
            scores = extract_scores(generated)
            valid.append((item, scores, generated))
        except Exception as exc:
            failures.append({"id": item["id"], "error": str(exc), "raw": generated})

    elapsed = time.monotonic() - start
    per_dim_abs = defaultdict(list)
    cosines, gold_dom, pred_dom, rows = [], [], [], []

    for item, scores, raw in valid:
        gv = tuple(float(item["intent"][d]) for d in DIMS)
        pv = tuple(scores[d] for d in DIMS)
        for dim, g, p in zip(DIMS, gv, pv):
            per_dim_abs[dim].append(abs(g - p))
        cosines.append(cosine(gv, pv))
        gd = item["dominant_intent"]
        pd = DIMS[max(range(4), key=lambda i: pv[i])]
        gold_dom.append(gd)
        pred_dom.append(pd)
        rows.append({
            "id": item["id"],
            "gold_dominant": gd,
            "pred_dominant": pd,
            "gold_vector": list(gv),
            "pred_vector": list(pv),
            "clickbait": scores["clickbait"],
            "raw": raw,
        })

    if not valid:
        raise SystemExit(json.dumps({"model": MODEL_ID, "failures": failures}, ensure_ascii=False))

    per_dim_mae = {dim: sum(vals) / len(vals) for dim, vals in per_dim_abs.items()}
    acc = sum(g == p for g, p in zip(gold_dom, pred_dom)) / len(valid)
    mf1, per_class = macro_f1(gold_dom, pred_dom)
    zero_vector_count = sum(all(v == 0 for v in row["pred_vector"]) for row in rows)

    result = {
        "benchmark_status": "balanced_24_case_development_screen_not_final_gold",
        "selection_rule": f"first_{PER_CLASS}_lexical_ids_per_dominant_class",
        "model": MODEL_ID,
        "model_commit": model_commit,
        "n_expected": len(gold),
        "n_valid_json": len(valid),
        "json_valid_rate": len(valid) / len(gold),
        "elapsed_seconds": elapsed,
        "seconds_per_post": elapsed / len(gold),
        "failures": failures,
        "gold_distribution": dict(Counter(gold_dom)),
        "pred_distribution": dict(Counter(pred_dom)),
        "zero_intent_vector_count": zero_vector_count,
        "dominant_accuracy": acc,
        "macro_f1": mf1,
        "intent_mae": sum(per_dim_mae.values()) / len(DIMS),
        "intent_mae_by_dimension": per_dim_mae,
        "mean_cosine_similarity": sum(cosines) / len(cosines),
        "per_class": per_class,
        "rows": rows,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
