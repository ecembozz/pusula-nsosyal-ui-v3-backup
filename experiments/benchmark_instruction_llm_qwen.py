#!/usr/bin/env python3
"""Offline PUSULA intent-labeling pilot with a small instruction LLM.

This model is NEVER loaded by the web app. It is evaluated only as a batch
label producer whose validated JSON output could later be cached in the repo.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
DIMS = ("ogretici", "eglendirici", "haber", "sosyal")

SYSTEM = """Sen PUSULA için Türkçe sosyal medya gönderilerini etiketleyen bir analiz bileşenisin.
Kullanıcının niyetini tahmin etmiyorsun; yalnız verilen gönderinin hangi ihtiyaca ne kadar hizmet ettiğini ölçüyorsun.
Dört boyut birbirinden bağımsızdır ve toplamları 1 olmak zorunda değildir.
- ogretici: bilgi, açıklama, yöntem, öneri veya öğrenilebilir fayda
- eglendirici: mizah, ironi, oyun, hikâye veya keyif verme
- haber: kamusal/güncel olay, duyuru, sonuç veya yeni gelişme aktarma
- sosyal: kişisel deneyim, duygu, fikir, sohbet daveti veya topluluk etkileşimi
- clickbait: yanıltıcı abartı, kasıtlı merak boşluğu veya vaat edilen bilgiyi saklama
Mizah, emoji veya ünlem tek başına clickbait değildir. Kişisel durum güncellemesi tek başına haber değildir.
Yalnız geçerli JSON döndür. Açıklama yazma."""

USER_TEMPLATE = """Gönderi:
{text}

Şu şemada yalnız JSON döndür:
{{"ogretici":0.00,"eglendirici":0.00,"haber":0.00,"sosyal":0.00,"clickbait":0.00}}
Bütün değerler 0 ile 1 arasında sayı olmalı."""


def read_jsonl(path: str):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    return dot / (na*nb) if na and nb else 0.0


def macro_f1(gold, pred):
    vals, per_class = [], {}
    for label in DIMS:
        tp = sum(g == label and p == label for g, p in zip(gold, pred))
        fp = sum(g != label and p == label for g, p in zip(gold, pred))
        fn = sum(g == label and p != label for g, p in zip(gold, pred))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2*precision*recall/(precision+recall) if precision+recall else 0.0
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "support": sum(g == label for g in gold)}
        vals.append(f1)
    return sum(vals)/len(vals), per_class


def extract_json(text: str):
    m = re.search(r"\{.*?\}", text, flags=re.S)
    if not m:
        raise ValueError("no JSON object")
    obj = json.loads(m.group(0))
    values = {}
    for key in (*DIMS, "clickbait"):
        if key not in obj:
            raise ValueError(f"missing {key}")
        value = float(obj[key])
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"out of range {key}: {value}")
        values[key] = value
    return values


def main():
    cases = {}
    for path in ["data/gold_eval/candidate_hard_cases.jsonl", "data/gold_eval/candidate_news_cases.jsonl"]:
        for row in read_jsonl(path):
            cases[row["id"]] = row["text"]
    gold = read_jsonl("data/gold_eval/draft_labels_annotator_a.jsonl")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.float32)
    model.eval()
    model_commit = getattr(model.config, "_commit_hash", None)

    parsed = []
    failures = []
    for item in gold:
        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TEMPLATE.format(text=cases[item["id"]])},
        ]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=768)
        with torch.inference_mode():
            out = model.generate(
                **inputs,
                max_new_tokens=96,
                do_sample=False,
                repetition_penalty=1.02,
                pad_token_id=tokenizer.eos_token_id,
            )
        generated = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        try:
            scores = extract_json(generated)
            parsed.append((item, scores, generated))
        except Exception as exc:
            failures.append({"id": item["id"], "error": str(exc), "raw": generated})

    if not parsed:
        raise SystemExit(f"No valid model outputs. failures={failures}")

    per_dim_abs = defaultdict(list)
    click_abs, cosines, gold_dom, pred_dom, rows = [], [], [], [], []
    for item, scores, raw in parsed:
        gv = tuple(float(item["intent"][d]) for d in DIMS)
        pv = tuple(scores[d] for d in DIMS)
        for d, g, p in zip(DIMS, gv, pv):
            per_dim_abs[d].append(abs(g-p))
        click_abs.append(abs(float(item["clickbait"]) - scores["clickbait"]))
        cosines.append(cosine(gv, pv))
        gd = item["dominant_intent"]
        pd = DIMS[max(range(4), key=lambda i: pv[i])]
        gold_dom.append(gd)
        pred_dom.append(pd)
        rows.append({"id": item["id"], "gold_dominant": gd, "pred_dominant": pd, "gold_vector": list(gv), "pred_vector": list(pv), "clickbait": scores["clickbait"]})

    per_dim_mae = {d: sum(v)/len(v) for d, v in per_dim_abs.items()}
    acc = sum(g == p for g, p in zip(gold_dom, pred_dom)) / len(parsed)
    mf1, per_class = macro_f1(gold_dom, pred_dom)
    result = {
        "benchmark_status": "development_set_single_annotator_not_final_gold",
        "model": MODEL_ID,
        "model_commit": model_commit,
        "n_expected": len(gold),
        "n_valid_json": len(parsed),
        "json_valid_rate": len(parsed)/len(gold),
        "failures": failures,
        "gold_distribution_valid_subset": dict(Counter(gold_dom)),
        "pred_distribution": dict(Counter(pred_dom)),
        "dominant_accuracy": acc,
        "macro_f1": mf1,
        "intent_mae": sum(per_dim_mae.values())/len(DIMS),
        "intent_mae_by_dimension": per_dim_mae,
        "mean_cosine_similarity": sum(cosines)/len(cosines),
        "clickbait_mae": sum(click_abs)/len(click_abs),
        "per_class": per_class,
        "rows": rows,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    Path("/tmp/qwen_0_5b_instruction_draft48.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
