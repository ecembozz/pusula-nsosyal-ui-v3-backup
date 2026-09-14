from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, f1_score
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

from benchmark_intent_balanced_corpus import load_balanced
from benchmark_style_generalization import load_hard_eval
from benchmark_supervised_embeddings import INTENTS, cosine_rows, dominant_from_scores

ROOT = Path(__file__).resolve().parents[1]


def seed_everything(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


class TextDataset(Dataset):
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        r = self.rows[idx]
        return {
            "text": r["text"],
            "y_vec": torch.tensor(r["y"][:4], dtype=torch.float32),
            "y_dom": torch.tensor(INTENTS.index(r["dominant"]), dtype=torch.long),
            "y_click": torch.tensor(float(r["y"][4]), dtype=torch.float32),
            "id": r["id"],
        }


def mean_pool(last_hidden, attention_mask):
    mask = attention_mask.unsqueeze(-1).float()
    summed = (last_hidden * mask).sum(dim=1)
    denom = mask.sum(dim=1).clamp(min=1e-9)
    return summed / denom


def find_encoder_layers(model):
    candidates = [
        getattr(getattr(model, "encoder", None), "layer", None),
        getattr(getattr(getattr(model, "transformer", None), "encoder", None), "layer", None),
        getattr(getattr(model, "transformer", None), "layer", None),
    ]
    for layers in candidates:
        if layers is not None:
            try:
                if len(layers) > 0:
                    return layers
            except TypeError:
                pass
    raise RuntimeError("Could not locate transformer encoder layers for selective unfreezing")


class MultiTaskIntentModel(nn.Module):
    def __init__(self, model_name: str, unfreeze_last_n: int = 2, dropout: float = 0.15):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden = int(self.encoder.config.hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.intent_head = nn.Linear(hidden, 4)
        self.dom_head = nn.Linear(hidden, 4)
        self.click_head = nn.Linear(hidden, 1)

        for p in self.encoder.parameters():
            p.requires_grad = False

        layers = find_encoder_layers(self.encoder)
        unfreeze_last_n = max(0, min(unfreeze_last_n, len(layers)))
        if unfreeze_last_n:
            for layer in layers[-unfreeze_last_n:]:
                for p in layer.parameters():
                    p.requires_grad = True

        # Final normalization layers usually stabilize a light adaptation.
        for name, p in self.encoder.named_parameters():
            lname = name.lower()
            if "layernorm" in lname or "layer_norm" in lname:
                p.requires_grad = True

    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled = mean_pool(out.last_hidden_state, attention_mask)
        pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
        z = self.dropout(pooled)
        intent = torch.sigmoid(self.intent_head(z))
        dom_logits = self.dom_head(z)
        click = torch.sigmoid(self.click_head(z)).squeeze(-1)
        return pooled, intent, dom_logits, click


def make_collate(tokenizer, max_length):
    def collate(batch):
        texts = ["query: " + r["text"] for r in batch]
        toks = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        return {
            **toks,
            "y_vec": torch.stack([r["y_vec"] for r in batch]),
            "y_dom": torch.stack([r["y_dom"] for r in batch]),
            "y_click": torch.stack([r["y_click"] for r in batch]),
            "ids": [r["id"] for r in batch],
        }
    return collate


def evaluate(model, loader, device):
    model.eval()
    ys, preds, dom_true, dom_pred, clicks_true, clicks_pred, embeds = [], [], [], [], [], [], []
    ids = []
    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            pooled, intent, dom_logits, click = model(input_ids, attention_mask)
            ys.append(batch["y_vec"].numpy())
            preds.append(intent.cpu().numpy())
            dom_true.extend(batch["y_dom"].tolist())
            dom_pred.extend(torch.argmax(dom_logits, dim=1).cpu().tolist())
            clicks_true.extend(batch["y_click"].tolist())
            clicks_pred.extend(click.cpu().tolist())
            embeds.append(pooled.cpu().numpy())
            ids.extend(batch["ids"])

    y = np.vstack(ys)
    pred = np.vstack(preds)
    dom_true_names = [INTENTS[i] for i in dom_true]
    dom_pred_names = [INTENTS[i] for i in dom_pred]
    click_true = np.asarray(clicks_true, dtype=float)
    click_pred = np.asarray(clicks_pred, dtype=float)
    emb = np.vstack(embeds)
    return {
        "metrics": {
            "dominant_accuracy": float(accuracy_score(dom_true_names, dom_pred_names)),
            "macro_f1": float(f1_score(dom_true_names, dom_pred_names, labels=INTENTS, average="macro", zero_division=0)),
            "intent_mae": float(np.mean(np.abs(y - pred))),
            "mean_cosine_similarity": float(np.mean(cosine_rows(y, pred))),
            "clickbait_mae": float(np.mean(np.abs(click_true - click_pred))),
            "pred_distribution": dict(Counter(dom_pred_names)),
            "per_class_accuracy": {
                cls: float(np.mean([dom_pred_names[i] == cls for i in np.where(np.asarray(dom_true_names) == cls)[0]]))
                for cls in INTENTS
            },
        },
        "ids": ids,
        "y": y,
        "pred": pred,
        "dom_true": dom_true_names,
        "dom_pred": dom_pred_names,
        "click_true": click_true,
        "click_pred": click_pred,
        "embeddings": emb,
    }


def train_one(model, train_loader, eval_loader, device, epochs, encoder_lr, head_lr, weight_decay):
    encoder_params = [p for p in model.encoder.parameters() if p.requires_grad]
    head_params = [
        *model.intent_head.parameters(),
        *model.dom_head.parameters(),
        *model.click_head.parameters(),
    ]
    optimizer = torch.optim.AdamW(
        [
            {"params": encoder_params, "lr": encoder_lr},
            {"params": head_params, "lr": head_lr},
        ],
        weight_decay=weight_decay,
    )
    total_steps = max(1, epochs * len(train_loader))
    warmup_steps = max(1, int(total_steps * 0.1))

    def lr_factor(step):
        if step < warmup_steps:
            return (step + 1) / warmup_steps
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return max(0.1, 1.0 - 0.9 * progress)

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_factor)
    mse = nn.MSELoss()
    ce = nn.CrossEntropyLoss()
    bce = nn.BCELoss()

    history = []
    global_step = 0
    for epoch in range(1, epochs + 1):
        model.train()
        running = 0.0
        for batch in train_loader:
            optimizer.zero_grad(set_to_none=True)
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            y_vec = batch["y_vec"].to(device)
            y_dom = batch["y_dom"].to(device)
            y_click = batch["y_click"].to(device)

            _, intent, dom_logits, click = model(input_ids, attention_mask)
            loss_vec = mse(intent, y_vec)
            loss_dom = ce(dom_logits, y_dom)
            loss_click = bce(click, y_click)
            loss = 1.0 * loss_vec + 0.65 * loss_dom + 0.30 * loss_click
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            running += float(loss.item())
            global_step += 1

        snapshot = evaluate(model, eval_loader, device)["metrics"]
        history.append({
            "epoch": epoch,
            "train_loss": running / max(1, len(train_loader)),
            "eval_dominant_accuracy": snapshot["dominant_accuracy"],
            "eval_macro_f1": snapshot["macro_f1"],
            "eval_intent_mae": snapshot["intent_mae"],
            "eval_mean_cosine_similarity": snapshot["mean_cosine_similarity"],
        })
    return history


def embedding_ood(train_emb, test_emb):
    train_sim = train_emb @ train_emb.T
    np.fill_diagonal(train_sim, -1.0)
    train_nearest = np.max(train_sim, axis=1)
    threshold = float(np.quantile(train_nearest, 0.10))
    nearest = np.max(test_emb @ train_emb.T, axis=1)
    return threshold, nearest, nearest < threshold


def confidence_report(eval_result, nearest, ood_flags):
    pred_vec = np.clip(eval_result["pred"], 0, 1)
    sorted_scores = np.sort(pred_vec, axis=1)
    margin = sorted_scores[:, -1] - sorted_scores[:, -2]
    proximity = np.clip((nearest - 0.45) / 0.55, 0, 1)
    confidence = 0.60 * proximity + 0.40 * margin
    correct = np.asarray([a == b for a, b in zip(eval_result["dom_true"], eval_result["dom_pred"])], dtype=bool)
    out = {
        "ood_rate": float(np.mean(ood_flags)),
        "mean_nearest_train_cosine": float(np.mean(nearest)),
        "id_accuracy": float(np.mean(correct[~ood_flags])) if np.any(~ood_flags) else None,
        "ood_accuracy": float(np.mean(correct[ood_flags])) if np.any(ood_flags) else None,
    }
    for coverage in (0.50, 0.75):
        n = max(1, int(round(len(confidence) * coverage)))
        idx = np.argsort(-confidence)[:n]
        out[f"accuracy_at_{int(coverage*100)}pct_coverage"] = float(np.mean(correct[idx]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/multilingual-e5-small")
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--max-length", type=int, default=160)
    ap.add_argument("--unfreeze-last-n", type=int, default=2)
    ap.add_argument("--encoder-lr", type=float, default=2e-5)
    ap.add_argument("--head-lr", type=float, default=8e-4)
    ap.add_argument("--weight-decay", type=float, default=0.01)
    ap.add_argument("--output", default="experiments/results/multitask_finetune.json")
    ap.add_argument("--summary", default="experiments/results/multitask_finetune.md")
    args = ap.parse_args()

    seed_everything(42)
    train_rows = load_balanced()
    hard_rows = load_hard_eval()
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    collate = make_collate(tokenizer, args.max_length)
    train_loader = DataLoader(TextDataset(train_rows), batch_size=args.batch_size, shuffle=True, collate_fn=collate)
    train_eval_loader = DataLoader(TextDataset(train_rows), batch_size=args.batch_size, shuffle=False, collate_fn=collate)
    hard_loader = DataLoader(TextDataset(hard_rows), batch_size=args.batch_size, shuffle=False, collate_fn=collate)

    device = torch.device("cpu")
    model = MultiTaskIntentModel(args.model, unfreeze_last_n=args.unfreeze_last_n)
    revision = getattr(model.encoder.config, "_commit_hash", None)
    model.to(device)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())

    baseline_hard = evaluate(model, hard_loader, device)
    history = train_one(
        model,
        train_loader,
        hard_loader,
        device,
        args.epochs,
        args.encoder_lr,
        args.head_lr,
        args.weight_decay,
    )
    train_final = evaluate(model, train_eval_loader, device)
    hard_final = evaluate(model, hard_loader, device)

    threshold, nearest, ood_flags = embedding_ood(train_final["embeddings"], hard_final["embeddings"])
    hard_final["metrics"]["ood_threshold"] = threshold
    hard_final["metrics"]["confidence_ood"] = confidence_report(hard_final, nearest, ood_flags)

    result = {
        "status": "development_only_not_final_gold",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "training": {
            "train_n": len(train_rows),
            "hard_eval_n": len(hard_rows),
            "train_distribution": dict(Counter(r["dominant"] for r in train_rows)),
            "hard_eval_distribution": dict(Counter(r["dominant"] for r in hard_rows)),
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "max_length": args.max_length,
            "unfreeze_last_n": args.unfreeze_last_n,
            "encoder_lr": args.encoder_lr,
            "head_lr": args.head_lr,
            "weight_decay": args.weight_decay,
            "trainable_parameters": int(trainable),
            "total_parameters": int(total),
            "trainable_fraction": float(trainable / total),
        },
        "baseline_untrained_heads_on_hard": baseline_hard["metrics"],
        "history": history,
        "train_final": train_final["metrics"],
        "hard_final": hard_final["metrics"],
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    h = hard_final["metrics"]
    c = h["confidence_ood"]
    lines = [
        "# Multitask encoder fine-tuning pilot",
        "",
        "> Development-only. Trained only on the 136 intent-balanced assistant-authored development examples. The 48 hard-style examples remain completely held out from gradient updates. Not final competition metrics.",
        "",
        f"Base encoder: `{args.model}` @ `{revision}`",
        f"Unfrozen transformer layers: **last {args.unfreeze_last_n}**",
        f"Trainable parameters: **{trainable:,} / {total:,} ({trainable/total:.2%})**",
        f"Training examples: **{len(train_rows)}**; hard-style held-out evaluation: **{len(hard_rows)}**.",
        "",
        "## Held-out hard-style result",
        "",
        f"- Dominant accuracy: **{h['dominant_accuracy']:.3f}**",
        f"- Macro-F1: **{h['macro_f1']:.3f}**",
        f"- 4D intent MAE: **{h['intent_mae']:.3f}**",
        f"- Mean intent cosine: **{h['mean_cosine_similarity']:.3f}**",
        f"- Clickbait MAE: **{h['clickbait_mae']:.3f}**",
        f"- OOD rate: **{c['ood_rate']:.3f}**",
        f"- Accuracy at 50% confidence coverage: **{c['accuracy_at_50pct_coverage']:.3f}**",
        f"- Per-class accuracy: `{h['per_class_accuracy']}`",
        "",
        "## Training curve",
        "",
        "| Epoch | Train loss | Hard acc. | Hard macro-F1 | 4D MAE | Cosine |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for r in history:
        lines.append(
            f"| {r['epoch']} | {r['train_loss']:.4f} | {r['eval_dominant_accuracy']:.3f} | {r['eval_macro_f1']:.3f} | {r['eval_intent_mae']:.3f} | {r['eval_mean_cosine_similarity']:.3f} |"
        )
    lines += [
        "",
        "This is a model-selection experiment only. Because the same 48 hard examples are inspected across development rounds, they are not a final untouched test set.",
        "",
    ]
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "embedding_model": result["embedding_model"],
        "embedding_revision": result["embedding_revision"],
        "training": result["training"],
        "hard_final": result["hard_final"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
