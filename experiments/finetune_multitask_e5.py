from __future__ import annotations

import argparse
import copy
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
TRAIN_FILE = ROOT / "data/dev_labels/intent_balanced_training_v1.jsonl"
HARD_LABELS = ROOT / "data/gold_eval/draft_labels_annotator_a.jsonl"
HARD_TEXT_FILES = [
    ROOT / "data/gold_eval/candidate_hard_cases.jsonl",
    ROOT / "data/gold_eval/candidate_news_cases.jsonl",
]
INTENTS = ["ogretici", "eglendirici", "haber", "sosyal"]
INTENT_TO_ID = {k: i for i, k in enumerate(INTENTS)}


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def seed_all(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(False)


def load_train_rows():
    rows = []
    for r in read_jsonl(TRAIN_FILE):
        rows.append(
            {
                "id": r["id"],
                "text": r["text"],
                "dominant": r["dominant_intent"],
                "dominant_id": INTENT_TO_ID[r["dominant_intent"]],
                "intent": [float(r["intent"][k]) for k in INTENTS],
                "clickbait": float(r["clickbait"]),
                "style_bucket": r.get("style_bucket", "unknown"),
            }
        )
    return rows


def load_hard_rows():
    meta = {}
    for path in HARD_TEXT_FILES:
        for r in read_jsonl(path):
            meta[r["id"]] = r
    rows = []
    for r in read_jsonl(HARD_LABELS):
        src = meta[r["id"]]
        rows.append(
            {
                "id": r["id"],
                "text": src["text"],
                "dominant": r["dominant_intent"],
                "dominant_id": INTENT_TO_ID[r["dominant_intent"]],
                "intent": [float(r["intent"][k]) for k in INTENTS],
                "clickbait": float(r["clickbait"]),
                "challenge": list(src.get("challenge", [])),
            }
        )
    return rows


class TextDataset(Dataset):
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        return self.rows[idx]


def collate_factory(tokenizer, max_length):
    def collate(rows):
        texts = ["query: " + r["text"] for r in rows]
        toks = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        return {
            "tokens": toks,
            "intent": torch.tensor([r["intent"] for r in rows], dtype=torch.float32),
            "dominant": torch.tensor([r["dominant_id"] for r in rows], dtype=torch.long),
            "clickbait": torch.tensor([r["clickbait"] for r in rows], dtype=torch.float32),
            "ids": [r["id"] for r in rows],
        }

    return collate


def mean_pool(last_hidden, attention_mask):
    mask = attention_mask.unsqueeze(-1).float()
    summed = (last_hidden * mask).sum(dim=1)
    denom = mask.sum(dim=1).clamp(min=1e-9)
    return summed / denom


class MultiTaskE5(nn.Module):
    def __init__(self, model_name: str, dropout: float = 0.12):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden = int(self.encoder.config.hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.intent_head = nn.Sequential(
            nn.Linear(hidden, hidden // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden // 2, 4),
        )
        self.dominant_head = nn.Linear(hidden, 4)
        self.clickbait_head = nn.Linear(hidden, 1)

    def forward(self, tokens):
        out = self.encoder(**tokens)
        emb = mean_pool(out.last_hidden_state, tokens["attention_mask"])
        emb = F.normalize(emb, p=2, dim=1)
        z = self.dropout(emb)
        intent = torch.sigmoid(self.intent_head(z))
        dominant = self.dominant_head(z)
        clickbait = torch.sigmoid(self.clickbait_head(z)).squeeze(-1)
        return {
            "embedding": emb,
            "intent": intent,
            "dominant": dominant,
            "clickbait": clickbait,
        }


def find_encoder_layers(encoder):
    candidates = [
        getattr(encoder, "encoder", None),
        getattr(getattr(encoder, "base_model", None), "encoder", None),
        getattr(getattr(encoder, "transformer", None), "encoder", None),
    ]
    for obj in candidates:
        if obj is not None and hasattr(obj, "layer"):
            return list(obj.layer)
    # Fallback for architectures whose base model nests the encoder one level deeper.
    for child in encoder.children():
        if hasattr(child, "encoder") and hasattr(child.encoder, "layer"):
            return list(child.encoder.layer)
    raise RuntimeError("Could not locate transformer encoder layers for partial unfreezing")


def configure_trainable(model: MultiTaskE5, unfreeze_last_n: int):
    for p in model.encoder.parameters():
        p.requires_grad = False
    layers = find_encoder_layers(model.encoder)
    if unfreeze_last_n > 0:
        for layer in layers[-unfreeze_last_n:]:
            for p in layer.parameters():
                p.requires_grad = True
        # Allow final encoder LayerNorm when exposed separately.
        for name, p in model.encoder.named_parameters():
            low = name.lower()
            if "layernorm" in low and ("pooler" not in low):
                # Only norms that already belong to unfrozen tail or the final output norm.
                if any(f"layer.{i}." in name for i in range(max(0, len(layers)-unfreeze_last_n), len(layers))) or "encoder.layer_norm" in low:
                    p.requires_grad = True
    return len(layers)


def loss_fn(outputs, batch):
    pred_vec = outputs["intent"]
    gold_vec = batch["intent"]
    mse = F.mse_loss(pred_vec, gold_vec)
    cos = F.cosine_similarity(pred_vec, gold_vec, dim=1).mean()
    vector_loss = 0.65 * mse + 0.35 * (1.0 - cos)
    dominant_loss = F.cross_entropy(outputs["dominant"], batch["dominant"])
    click_loss = F.mse_loss(outputs["clickbait"], batch["clickbait"])
    total = vector_loss + 0.40 * dominant_loss + 0.15 * click_loss
    return total, {
        "total": float(total.detach()),
        "vector": float(vector_loss.detach()),
        "dominant": float(dominant_loss.detach()),
        "clickbait": float(click_loss.detach()),
    }


def batch_to_device(batch, device):
    toks = {k: v.to(device) for k, v in batch["tokens"].items()}
    return {
        **batch,
        "tokens": toks,
        "intent": batch["intent"].to(device),
        "dominant": batch["dominant"].to(device),
        "clickbait": batch["clickbait"].to(device),
    }


def collect_predictions(model, loader, device):
    model.eval()
    vectors, dom_logits, clickbait, embeddings = [], [], [], []
    gold_vec, gold_dom, gold_click, ids = [], [], [], []
    with torch.no_grad():
        for raw in loader:
            batch = batch_to_device(raw, device)
            out = model(batch["tokens"])
            vectors.append(out["intent"].cpu().numpy())
            dom_logits.append(out["dominant"].cpu().numpy())
            clickbait.append(out["clickbait"].cpu().numpy())
            embeddings.append(out["embedding"].cpu().numpy())
            gold_vec.append(batch["intent"].cpu().numpy())
            gold_dom.append(batch["dominant"].cpu().numpy())
            gold_click.append(batch["clickbait"].cpu().numpy())
            ids.extend(raw["ids"])
    return {
        "intent": np.vstack(vectors),
        "dom_logits": np.vstack(dom_logits),
        "clickbait": np.concatenate(clickbait),
        "embedding": np.vstack(embeddings),
        "gold_intent": np.vstack(gold_vec),
        "gold_dom": np.concatenate(gold_dom),
        "gold_clickbait": np.concatenate(gold_click),
        "ids": ids,
    }


def softmax_np(x):
    z = x - np.max(x, axis=1, keepdims=True)
    e = np.exp(z)
    return e / np.sum(e, axis=1, keepdims=True)


def metric_block(pred):
    vec = np.clip(pred["intent"], 0.0, 1.0)
    gold = pred["gold_intent"]
    dom_pred = np.argmax(pred["dom_logits"], axis=1)
    dom_gold = pred["gold_dom"]
    probs = softmax_np(pred["dom_logits"])
    sorted_probs = np.sort(probs, axis=1)
    margin = sorted_probs[:, -1] - sorted_probs[:, -2]
    correct = dom_pred == dom_gold
    result = {
        "dominant_accuracy": float(accuracy_score(dom_gold, dom_pred)),
        "macro_f1": float(f1_score(dom_gold, dom_pred, labels=list(range(4)), average="macro", zero_division=0)),
        "intent_mae": float(np.mean(np.abs(gold - vec))),
        "mean_cosine_similarity": float(np.mean(np.sum(gold * vec, axis=1) / np.maximum(np.linalg.norm(gold, axis=1) * np.linalg.norm(vec, axis=1), 1e-12))),
        "clickbait_mae": float(np.mean(np.abs(pred["gold_clickbait"] - np.clip(pred["clickbait"], 0, 1)))),
        "pred_distribution": dict(Counter(INTENTS[i] for i in dom_pred)),
        "per_class_accuracy": {},
    }
    for i, cls in enumerate(INTENTS):
        idx = np.where(dom_gold == i)[0]
        result["per_class_accuracy"][cls] = float(np.mean(dom_pred[idx] == i)) if len(idx) else None
    for coverage in (0.50, 0.75):
        n = max(1, int(round(len(correct) * coverage)))
        idx = np.argsort(-margin)[:n]
        result[f"accuracy_at_{int(coverage*100)}pct_coverage"] = float(np.mean(correct[idx]))
    return result


def challenge_breakdown(rows, pred):
    dom_pred = np.argmax(pred["dom_logits"], axis=1)
    dom_gold = pred["gold_dom"]
    vec = np.clip(pred["intent"], 0, 1)
    gold = pred["gold_intent"]
    id_to_i = {x: i for i, x in enumerate(pred["ids"])}
    buckets = defaultdict(list)
    for row in rows:
        i = id_to_i[row["id"]]
        for tag in row.get("challenge", []):
            buckets[tag].append(i)
    out = {}
    for tag, idxs in sorted(buckets.items()):
        if len(idxs) < 3:
            continue
        idx = np.asarray(idxs, dtype=int)
        out[tag] = {
            "n": int(len(idx)),
            "dominant_accuracy": float(np.mean(dom_pred[idx] == dom_gold[idx])),
            "intent_mae": float(np.mean(np.abs(vec[idx] - gold[idx]))),
        }
    return out


def ood_report(train_pred, hard_pred):
    train_emb = train_pred["embedding"]
    hard_emb = hard_pred["embedding"]
    train_sim = train_emb @ train_emb.T
    np.fill_diagonal(train_sim, -1.0)
    train_nearest = np.max(train_sim, axis=1)
    threshold = float(np.quantile(train_nearest, 0.10))
    hard_nearest = np.max(hard_emb @ train_emb.T, axis=1)
    ood = hard_nearest < threshold
    dom_pred = np.argmax(hard_pred["dom_logits"], axis=1)
    correct = dom_pred == hard_pred["gold_dom"]
    return {
        "threshold_p10_train_nearest_cosine": threshold,
        "mean_hard_nearest_train_cosine": float(np.mean(hard_nearest)),
        "ood_rate": float(np.mean(ood)),
        "id_accuracy": float(np.mean(correct[~ood])) if np.any(~ood) else None,
        "ood_accuracy": float(np.mean(correct[ood])) if np.any(ood) else None,
    }


def make_optimizer(model, encoder_lr, head_lr):
    enc_params, head_params = [], []
    for name, p in model.named_parameters():
        if not p.requires_grad:
            continue
        if name.startswith("encoder."):
            enc_params.append(p)
        else:
            head_params.append(p)
    groups = []
    if enc_params:
        groups.append({"params": enc_params, "lr": encoder_lr, "weight_decay": 0.01})
    if head_params:
        groups.append({"params": head_params, "lr": head_lr, "weight_decay": 0.01})
    return torch.optim.AdamW(groups)


def train_variant(
    variant_name,
    model_name,
    tokenizer,
    train_rows,
    val_rows,
    hard_rows,
    device,
    batch_size,
    max_length,
    epochs,
    patience,
    seed,
    unfreeze_last_n,
    encoder_lr,
    head_lr,
):
    seed_all(seed)
    model = MultiTaskE5(model_name)
    n_layers = configure_trainable(model, unfreeze_last_n)
    model.to(device)

    collate = collate_factory(tokenizer, max_length)
    gen = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(TextDataset(train_rows), batch_size=batch_size, shuffle=True, generator=gen, collate_fn=collate)
    val_loader = DataLoader(TextDataset(val_rows), batch_size=batch_size, shuffle=False, collate_fn=collate)
    hard_loader = DataLoader(TextDataset(hard_rows), batch_size=batch_size, shuffle=False, collate_fn=collate)
    full_train_loader = DataLoader(TextDataset(train_rows + val_rows), batch_size=batch_size, shuffle=False, collate_fn=collate)

    optimizer = make_optimizer(model, encoder_lr, head_lr)
    steps_total = max(1, len(train_loader) * epochs)
    warmup = max(1, int(0.10 * steps_total))

    def lr_lambda(step):
        if step < warmup:
            return max(0.05, (step + 1) / warmup)
        remain = max(0, steps_total - step)
        return max(0.05, remain / max(1, steps_total - warmup))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    best_state = None
    best_epoch = 0
    best_score = -1e9
    stale = 0
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        losses = []
        for raw in train_loader:
            batch = batch_to_device(raw, device)
            optimizer.zero_grad(set_to_none=True)
            out = model(batch["tokens"])
            loss, parts = loss_fn(out, batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
            optimizer.step()
            scheduler.step()
            losses.append(parts)

        val_pred = collect_predictions(model, val_loader, device)
        val_metrics = metric_block(val_pred)
        selection = (
            0.45 * val_metrics["mean_cosine_similarity"]
            + 0.35 * (1.0 - val_metrics["intent_mae"])
            + 0.20 * val_metrics["macro_f1"]
        )
        history.append(
            {
                "epoch": epoch,
                "train_loss": float(np.mean([x["total"] for x in losses])),
                "val_selection_score": float(selection),
                "val": val_metrics,
            }
        )
        if selection > best_score + 1e-5:
            best_score = selection
            best_epoch = epoch
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
            if stale >= patience:
                break

    if best_state is None:
        raise RuntimeError("No best state captured")
    model.load_state_dict(best_state)
    model.to(device)

    val_pred = collect_predictions(model, val_loader, device)
    hard_pred = collect_predictions(model, hard_loader, device)
    train_pred = collect_predictions(model, full_train_loader, device)
    hard_metrics = metric_block(hard_pred)
    hard_metrics["by_challenge"] = challenge_breakdown(hard_rows, hard_pred)
    hard_metrics["ood"] = ood_report(train_pred, hard_pred)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return {
        "variant": variant_name,
        "transformer_layers": n_layers,
        "unfreeze_last_n": unfreeze_last_n,
        "trainable_params": int(trainable),
        "total_params": int(total),
        "trainable_fraction": float(trainable / total),
        "best_epoch": int(best_epoch),
        "best_internal_selection_score": float(best_score),
        "internal_validation": metric_block(val_pred),
        "hard_style_development": hard_metrics,
        "history": history,
    }


def markdown(result):
    lines = [
        "# Partial multilingual E5 multitask fine-tuning pilot",
        "",
        "> Development-only model-selection experiment. The 48 hard-style labels remain single-annotator draft labels and are not final competition gold.",
        "",
        f"Encoder: `{result['model_name']}` @ `{result.get('model_revision')}`",
        f"Training corpus: **{result['train_total_n']}** intent-balanced/style-diverse examples; hard-style development set: **{result['hard_n']}** examples.",
        f"Internal split: **{result['train_split_n']} train / {result['internal_val_n']} validation**, stratified by dominant intent.",
        "",
        "The hard-style set is not used for gradient updates, epoch selection, or early stopping.",
        "",
        "| Variant | Unfrozen encoder layers | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | Clickbait MAE | Top-50% acc. | OOD rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, r in result["variants"].items():
        h = r["hard_style_development"]
        lines.append(
            f"| {name} | {r['unfreeze_last_n']} | {h['dominant_accuracy']:.3f} | {h['macro_f1']:.3f} | "
            f"{h['intent_mae']:.3f} | {h['mean_cosine_similarity']:.3f} | {h['clickbait_mae']:.3f} | "
            f"{h['accuracy_at_50pct_coverage']:.3f} | {h['ood']['ood_rate']:.3f} |"
        )
    lines += ["", "## Per-class hard-style accuracy", ""]
    for name, r in result["variants"].items():
        lines.append(f"- **{name}:** `{r['hard_style_development']['per_class_accuracy']}`")
    lines += [
        "",
        "## Interpretation guardrails",
        "",
        "- Compare the partially fine-tuned encoder against the frozen-encoder multitask control; improvement must be visible on the untouched hard-style development set, not only on the internal validation split.",
        "- The 48-case hard set has already been used for architecture decisions in this development cycle, so it cannot later be relabeled as an untouched final test set.",
        "- A final competition claim requires a new independently double-annotated holdout collected after model selection is frozen.",
        "",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/multilingual-e5-small")
    ap.add_argument("--output", default="experiments/results/finetune_multitask_e5.json")
    ap.add_argument("--summary", default="experiments/results/finetune_multitask_e5.md")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--epochs", type=int, default=14)
    ap.add_argument("--patience", type=int, default=4)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--max-length", type=int, default=96)
    args = ap.parse_args()

    seed_all(args.seed)
    torch.set_num_threads(max(1, min(4, torch.get_num_threads())))
    device = torch.device("cpu")

    train_rows = load_train_rows()
    hard_rows = load_hard_rows()
    labels = [r["dominant"] for r in train_rows]
    idx = np.arange(len(train_rows))
    tr_idx, va_idx = train_test_split(
        idx,
        test_size=0.1764705882,  # 24/136
        random_state=args.seed,
        shuffle=True,
        stratify=labels,
    )
    tr_rows = [train_rows[i] for i in tr_idx]
    va_rows = [train_rows[i] for i in va_idx]

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    probe = AutoModel.from_pretrained(args.model)
    revision = getattr(probe.config, "_commit_hash", None)
    del probe

    common = dict(
        model_name=args.model,
        tokenizer=tokenizer,
        train_rows=tr_rows,
        val_rows=va_rows,
        hard_rows=hard_rows,
        device=device,
        batch_size=args.batch_size,
        max_length=args.max_length,
        epochs=args.epochs,
        patience=args.patience,
        seed=args.seed,
    )

    frozen = train_variant(
        variant_name="frozen_encoder_multitask",
        unfreeze_last_n=0,
        encoder_lr=0.0,
        head_lr=7e-4,
        **common,
    )
    partial = train_variant(
        variant_name="unfreeze_last_1_multitask",
        unfreeze_last_n=1,
        encoder_lr=1.2e-5,
        head_lr=5e-4,
        **common,
    )

    result = {
        "status": "development_only_not_final_gold",
        "model_name": args.model,
        "model_revision": revision,
        "seed": args.seed,
        "train_total_n": len(train_rows),
        "train_distribution": dict(Counter(labels)),
        "style_distribution": dict(Counter(r["style_bucket"] for r in train_rows)),
        "train_split_n": len(tr_rows),
        "internal_val_n": len(va_rows),
        "hard_n": len(hard_rows),
        "hard_distribution": dict(Counter(r["dominant"] for r in hard_rows)),
        "hard_set_role": "architecture-development-only; never used for gradients or early stopping",
        "variants": {
            "frozen_encoder_multitask": frozen,
            "unfreeze_last_1_multitask": partial,
        },
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / args.summary).write_text(markdown(result), encoding="utf-8")

    compact = {
        "model": args.model,
        "revision": revision,
        "split": {"train": len(tr_rows), "internal_val": len(va_rows), "hard": len(hard_rows)},
        "variants": {
            k: {
                "best_epoch": v["best_epoch"],
                "trainable_fraction": v["trainable_fraction"],
                "internal_validation": v["internal_validation"],
                "hard_style_development": {
                    key: val
                    for key, val in v["hard_style_development"].items()
                    if key not in {"by_challenge"}
                },
            }
            for k, v in result["variants"].items()
        },
    }
    print(json.dumps(compact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
