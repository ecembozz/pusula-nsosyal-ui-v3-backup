from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neighbors import KNeighborsRegressor
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

from benchmark_intent_balanced_corpus import load_balanced
from benchmark_style_generalization import load_hard_eval
from benchmark_supervised_embeddings import INTENTS, cosine_rows, dominant_from_scores
from fine_tune_multitask_encoder import find_encoder_layers, mean_pool

ROOT = Path(__file__).resolve().parents[1]


def seed_all(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


class DS(Dataset):
    def __init__(self, rows):
        self.rows = rows
    def __len__(self):
        return len(self.rows)
    def __getitem__(self, i):
        r = self.rows[i]
        return {
            "id": r["id"],
            "text": r["text"],
            "dom": INTENTS.index(r["dominant"]),
            "vec": np.asarray(r["y"][:4], dtype=np.float32),
            "click": float(r["y"][4]),
        }


def collate_factory(tok, max_length):
    def collate(batch):
        enc = tok(
            ["query: " + x["text"] for x in batch],
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        return {
            **enc,
            "ids": [x["id"] for x in batch],
            "dom": torch.tensor([x["dom"] for x in batch], dtype=torch.long),
            "vec": torch.tensor(np.stack([x["vec"] for x in batch]), dtype=torch.float32),
            "click": torch.tensor([x["click"] for x in batch], dtype=torch.float32),
        }
    return collate


class Adapter(nn.Module):
    def __init__(self, model_name, unfreeze_last_n=2):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden = int(self.encoder.config.hidden_size)
        self.dom = nn.Linear(hidden, 4)
        self.click = nn.Linear(hidden, 1)
        for p in self.encoder.parameters():
            p.requires_grad = False
        layers = find_encoder_layers(self.encoder)
        for layer in layers[-min(unfreeze_last_n, len(layers)):]:
            for p in layer.parameters():
                p.requires_grad = True
        for name, p in self.encoder.named_parameters():
            lname = name.lower()
            if "layernorm" in lname or "layer_norm" in lname:
                p.requires_grad = True

    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        emb = mean_pool(out.last_hidden_state, attention_mask)
        emb = torch.nn.functional.normalize(emb, p=2, dim=1)
        return emb, self.dom(emb), torch.sigmoid(self.click(emb)).squeeze(-1)


def encode_all(model, loader, device):
    model.eval()
    embs, vecs, doms, clicks, logits_all = [], [], [], [], []
    ids = []
    with torch.no_grad():
        for b in loader:
            emb, logits, click = model(b["input_ids"].to(device), b["attention_mask"].to(device))
            embs.append(emb.cpu().numpy())
            logits_all.append(logits.cpu().numpy())
            vecs.append(b["vec"].numpy())
            doms.extend(b["dom"].tolist())
            clicks.extend(b["click"].tolist())
            ids.extend(b["ids"])
    return {
        "ids": ids,
        "emb": np.vstack(embs),
        "vec": np.vstack(vecs),
        "dom": np.asarray(doms, dtype=int),
        "click": np.asarray(clicks, dtype=float),
        "logits": np.vstack(logits_all),
    }


def softmax_np(x):
    x = x - np.max(x, axis=1, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=1, keepdims=True)


def evaluate_repr(train_pack, test_pack, k=7, blend=0.15):
    knn = KNeighborsRegressor(n_neighbors=k, weights="distance", metric="cosine")
    knn.fit(train_pack["emb"], train_pack["vec"])
    vec_knn = np.clip(knn.predict(test_pack["emb"]), 0, 1)
    probs = softmax_np(test_pack["logits"])
    vec_hybrid = np.clip((1.0 - blend) * vec_knn + blend * probs, 0, 1)

    dom_true = [INTENTS[i] for i in test_pack["dom"]]
    cls_pred = [INTENTS[i] for i in np.argmax(test_pack["logits"], axis=1)]

    def vec_metrics(pred):
        dom_pred = dominant_from_scores(pred)
        return {
            "dominant_accuracy": float(accuracy_score(dom_true, dom_pred)),
            "macro_f1": float(f1_score(dom_true, dom_pred, labels=INTENTS, average="macro", zero_division=0)),
            "intent_mae": float(np.mean(np.abs(test_pack["vec"] - pred))),
            "mean_cosine_similarity": float(np.mean(cosine_rows(test_pack["vec"], pred))),
            "pred_distribution": dict(Counter(dom_pred)),
            "per_class_accuracy": {
                cls: float(np.mean([dom_pred[i] == cls for i in np.where(np.asarray(dom_true) == cls)[0]]))
                for cls in INTENTS
            },
        }

    cls_correct = np.asarray([a == b for a, b in zip(dom_true, cls_pred)], dtype=bool)
    sorted_p = np.sort(probs, axis=1)
    margin = sorted_p[:, -1] - sorted_p[:, -2]
    idx50 = np.argsort(-margin)[:max(1, len(margin)//2)]

    train_sim = train_pack["emb"] @ train_pack["emb"].T
    np.fill_diagonal(train_sim, -1.0)
    threshold = float(np.quantile(np.max(train_sim, axis=1), 0.10))
    nearest = np.max(test_pack["emb"] @ train_pack["emb"].T, axis=1)
    ood = nearest < threshold

    return {
        "knn_vector": vec_metrics(vec_knn),
        "hybrid_vector": vec_metrics(vec_hybrid),
        "classifier": {
            "dominant_accuracy": float(accuracy_score(dom_true, cls_pred)),
            "macro_f1": float(f1_score(dom_true, cls_pred, labels=INTENTS, average="macro", zero_division=0)),
            "accuracy_at_50pct_confidence": float(np.mean(cls_correct[idx50])),
            "pred_distribution": dict(Counter(cls_pred)),
        },
        "ood": {
            "threshold": threshold,
            "ood_rate": float(np.mean(ood)),
            "mean_nearest_train_cosine": float(np.mean(nearest)),
        },
    }


def train_epoch(model, loader, optimizer, device, click_weight=0.15):
    model.train()
    ce = nn.CrossEntropyLoss()
    bce = nn.BCELoss()
    total = 0.0
    for b in loader:
        optimizer.zero_grad(set_to_none=True)
        emb, logits, click = model(b["input_ids"].to(device), b["attention_mask"].to(device))
        loss_dom = ce(logits, b["dom"].to(device))
        loss_click = bce(click, b["click"].to(device))
        loss = loss_dom + click_weight * loss_click
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total += float(loss.item())
    return total / max(1, len(loader))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/multilingual-e5-small")
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--max-length", type=int, default=160)
    ap.add_argument("--unfreeze-last-n", type=int, default=2)
    ap.add_argument("--encoder-lr", type=float, default=2e-5)
    ap.add_argument("--head-lr", type=float, default=8e-4)
    ap.add_argument("--knn-k", type=int, default=7)
    ap.add_argument("--blend", type=float, default=0.15)
    ap.add_argument("--output", default="experiments/results/task_adapted_knn.json")
    ap.add_argument("--summary", default="experiments/results/task_adapted_knn.md")
    args = ap.parse_args()

    seed_all(42)
    train_rows = load_balanced()
    hard_rows = load_hard_eval()
    tok = AutoTokenizer.from_pretrained(args.model)
    collate = collate_factory(tok, args.max_length)
    train_loader = DataLoader(DS(train_rows), batch_size=args.batch_size, shuffle=True, collate_fn=collate)
    train_eval_loader = DataLoader(DS(train_rows), batch_size=args.batch_size, shuffle=False, collate_fn=collate)
    hard_loader = DataLoader(DS(hard_rows), batch_size=args.batch_size, shuffle=False, collate_fn=collate)

    device = torch.device("cpu")
    model = Adapter(args.model, args.unfreeze_last_n).to(device)
    revision = getattr(model.encoder.config, "_commit_hash", None)
    encoder_params = [p for p in model.encoder.parameters() if p.requires_grad]
    head_params = [*model.dom.parameters(), *model.click.parameters()]
    optimizer = torch.optim.AdamW(
        [
            {"params": encoder_params, "lr": args.encoder_lr},
            {"params": head_params, "lr": args.head_lr},
        ],
        weight_decay=0.01,
    )

    baseline_train = encode_all(model, train_eval_loader, device)
    baseline_hard = encode_all(model, hard_loader, device)
    baseline = evaluate_repr(baseline_train, baseline_hard, args.knn_k, args.blend)

    history = []
    best = None
    best_score = -1.0
    for epoch in range(1, args.epochs + 1):
        loss = train_epoch(model, train_loader, optimizer, device)
        train_pack = encode_all(model, train_eval_loader, device)
        hard_pack = encode_all(model, hard_loader, device)
        ev = evaluate_repr(train_pack, hard_pack, args.knn_k, args.blend)
        score = ev["hybrid_vector"]["macro_f1"]
        if score > best_score:
            best_score = score
            best = {"epoch": epoch, "train_loss": loss, "evaluation": ev}
        history.append({"epoch": epoch, "train_loss": loss, "evaluation": ev})

    result = {
        "status": "development_only_not_final_gold",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "training": {
            "train_n": len(train_rows),
            "hard_eval_n": len(hard_rows),
            "epochs": args.epochs,
            "unfreeze_last_n": args.unfreeze_last_n,
            "encoder_lr": args.encoder_lr,
            "head_lr": args.head_lr,
            "knn_k": args.knn_k,
            "hybrid_classifier_blend": args.blend,
            "train_distribution": dict(Counter(r["dominant"] for r in train_rows)),
        },
        "baseline_frozen_encoder": baseline,
        "history": history,
        "best_by_hybrid_macro_f1": best,
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Task-adapted encoder + semantic k-NN pilot",
        "",
        "> Development-only. The encoder sees only the 136 balanced development training examples. The 48 hard-style examples never receive gradient updates. They are still a repeatedly inspected development set, not a final untouched test set.",
        "",
        f"Encoder: `{args.model}` @ `{revision}`",
        f"Training examples: **{len(train_rows)}**; hard-style development examples: **{len(hard_rows)}**.",
        f"k-NN: **k={args.knn_k}**; hybrid classifier blend: **{args.blend:.2f}**.",
        "",
        "| Epoch | Loss | kNN acc. | kNN F1 | kNN MAE | kNN cosine | Hybrid acc. | Hybrid F1 | Hybrid MAE |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    b = baseline
    lines.append(f"| 0 (frozen) | - | {b['knn_vector']['dominant_accuracy']:.3f} | {b['knn_vector']['macro_f1']:.3f} | {b['knn_vector']['intent_mae']:.3f} | {b['knn_vector']['mean_cosine_similarity']:.3f} | {b['hybrid_vector']['dominant_accuracy']:.3f} | {b['hybrid_vector']['macro_f1']:.3f} | {b['hybrid_vector']['intent_mae']:.3f} |")
    for row in history:
        ev = row["evaluation"]
        k = ev["knn_vector"]
        h = ev["hybrid_vector"]
        lines.append(f"| {row['epoch']} | {row['train_loss']:.4f} | {k['dominant_accuracy']:.3f} | {k['macro_f1']:.3f} | {k['intent_mae']:.3f} | {k['mean_cosine_similarity']:.3f} | {h['dominant_accuracy']:.3f} | {h['macro_f1']:.3f} | {h['intent_mae']:.3f} |")
    if best:
        h = best["evaluation"]["hybrid_vector"]
        lines += [
            "",
            "## Best development checkpoint",
            "",
            f"Epoch **{best['epoch']}**: hybrid accuracy **{h['dominant_accuracy']:.3f}**, macro-F1 **{h['macro_f1']:.3f}**, 4D MAE **{h['intent_mae']:.3f}**, cosine **{h['mean_cosine_similarity']:.3f}**.",
            "",
        ]
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"baseline": baseline, "best": best}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
