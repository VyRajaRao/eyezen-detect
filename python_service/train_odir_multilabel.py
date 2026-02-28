"""
train_odir_multilabel.py
------------------------
Trains a multi-label EfficientNet-B0 on the ODIR-5K dataset.

Usage
-----
    python train_odir_multilabel.py \\
        --data-dir /path/to/ODIR-5K \\
        --epochs 30 \\
        --batch-size 32 \\
        --output-dir python_service/models

Expected dataset layout
-----------------------
  <data-dir>/
    ODIR-5K_Training_Dataset/   or   Training_Images/
      <patient_id>_left.jpg
      <patient_id>_right.jpg
      ...
    data.xlsx   (or ODIR-5K_Training_Annotations.xlsx)
      Columns: ID, Left-Diagnostic Keywords, Right-Diagnostic Keywords,
               Patient Age, Patient Sex, Left-Fundus, Right-Fundus,
               N, D, G, C, A, H, M, O   (0/1 labels)

Alternatively supply a CSV derived from the original XLSX:
  <data-dir>/
    annotations.csv   (ID, image_filename, N, D, G, C, A, H, M, O)
    images/
      *.jpg

Environment variables (optional, override CLI)
----------------------------------------------
  TRAIN_ODIR_DIR  path to ODIR-5K dataset directory
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from torchvision import models

import sys
sys.path.insert(0, str(Path(__file__).parent))
from app.preprocessing import get_inference_transform, get_training_transform

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ODIR_LABELS: List[str] = ["N", "D", "G", "C", "A", "H", "M", "O"]
ODIR_LABEL_NAMES: List[str] = [
    "Normal", "Diabetic Retinopathy", "Glaucoma", "Cataract",
    "Age-related Macular Degeneration", "Hypertension", "Myopia", "Other",
]


# ---------------------------------------------------------------------------
# Dataset helpers
# ---------------------------------------------------------------------------

def _find_annotations(data_dir: Path) -> Tuple[pd.DataFrame, Path]:
    """Locate and load the annotation file; return (df, images_dir)."""
    # Try CSV first
    for csv_name in ("annotations.csv", "data.csv"):
        p = data_dir / csv_name
        if p.exists():
            df = pd.read_csv(p)
            img_dir = data_dir / "images"
            return df, img_dir

    # Try XLSX
    for xlsx_name in (
        "ODIR-5K_Training_Annotations.xlsx",
        "data.xlsx",
        "ODIR_Training_Annotations.xlsx",
    ):
        p = data_dir / xlsx_name
        if p.exists():
            df = pd.read_excel(p)
            img_dir = _find_images_dir(data_dir)
            return df, img_dir

    raise FileNotFoundError(
        f"Could not find annotation file in {data_dir}. "
        "Expected annotations.csv or ODIR-5K_Training_Annotations.xlsx."
    )


def _find_images_dir(data_dir: Path) -> Path:
    for candidate in (
        "ODIR-5K_Training_Dataset",
        "Training_Images",
        "images",
        "train_images",
    ):
        p = data_dir / candidate
        if p.is_dir():
            return p
    return data_dir


def _build_records(df: pd.DataFrame, img_dir: Path) -> pd.DataFrame:
    """
    Normalise the DataFrame into columns: image_path, N, D, G, C, A, H, M, O.
    Handles both the original ODIR XLSX format and a pre-processed CSV.
    """
    # Already in expected format?
    if "image_path" in df.columns and all(c in df.columns for c in ODIR_LABELS):
        df["image_path"] = df["image_path"].apply(lambda p: img_dir / p if not Path(p).is_absolute() else Path(p))
        return df[["image_path"] + ODIR_LABELS].dropna()

    # Original XLSX format: separate left/right images per patient
    records = []
    for _, row in df.iterrows():
        labels = [int(row.get(c, 0)) for c in ODIR_LABELS]
        for eye in ("Left-Fundus", "Right-Fundus"):
            fname = row.get(eye)
            if pd.isna(fname):
                continue
            path = img_dir / str(fname)
            if path.exists():
                records.append({"image_path": path, **dict(zip(ODIR_LABELS, labels))})

    return pd.DataFrame(records).dropna()


class ODIRDataset(Dataset):
    def __init__(self, records: pd.DataFrame, transform) -> None:
        self.records = records.reset_index(drop=True)
        self.transform = transform

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        row = self.records.iloc[idx]
        img = Image.open(row["image_path"]).convert("RGB")
        labels = torch.tensor([float(row[c]) for c in ODIR_LABELS], dtype=torch.float32)
        return self.transform(img), labels


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

def build_model(device: torch.device) -> nn.Module:
    weights = models.EfficientNet_B0_Weights.DEFAULT
    net = models.efficientnet_b0(weights=weights)
    in_features = net.classifier[1].in_features
    net.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, len(ODIR_LABELS)),
    )
    return net.to(device)


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

def train(args: argparse.Namespace) -> None:
    data_dir   = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df_raw, img_dir = _find_annotations(data_dir)
    df = _build_records(df_raw, img_dir)

    if len(df) == 0:
        raise ValueError(f"No valid image records found under {data_dir}.")
    logger.info("Found %d labelled images", len(df))

    # Stratify on the most common label column (N/normal)
    stratify_col = df["N"].astype(int)
    train_df, val_df = train_test_split(
        df, test_size=0.2, stratify=stratify_col, random_state=42
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Device: %s  |  Train: %d  Val: %d", device, len(train_df), len(val_df))

    train_ds = ODIRDataset(train_df, get_training_transform(224, augment=True))
    val_ds   = ODIRDataset(val_df,   get_inference_transform(224))
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,  num_workers=args.workers)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size, shuffle=False, num_workers=args.workers)

    model     = build_model(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    criterion = nn.BCEWithLogitsLoss()
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    best_mean_auc = 0.0
    for epoch in range(1, args.epochs + 1):
        # --- Train ---
        model.train()
        epoch_loss = 0.0
        for images, targets in train_loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), targets)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(images)
        epoch_loss /= len(train_ds)

        # --- Validate ---
        model.eval()
        all_probs = []
        all_targets = []
        with torch.no_grad():
            for images, targets in val_loader:
                logits = model(images.to(device))
                probs  = torch.sigmoid(logits).cpu().numpy()
                all_probs.append(probs)
                all_targets.append(targets.numpy())

        probs_arr   = np.concatenate(all_probs,   axis=0)
        targets_arr = np.concatenate(all_targets, axis=0)

        # Per-label AUC (skip labels with only one class in val set)
        aucs = []
        for i, lbl in enumerate(ODIR_LABELS):
            if targets_arr[:, i].sum() > 0 and targets_arr[:, i].sum() < len(targets_arr):
                aucs.append(roc_auc_score(targets_arr[:, i], probs_arr[:, i]))
            else:
                aucs.append(float("nan"))
        mean_auc = float(np.nanmean(aucs))
        scheduler.step()

        logger.info(
            "Epoch %d/%d  loss=%.4f  mean_AUC=%.4f",
            epoch, args.epochs, epoch_loss, mean_auc,
        )

        if mean_auc > best_mean_auc:
            best_mean_auc = mean_auc
            save_path = output_dir / "odir_multilabel.pth"
            torch.save(model.state_dict(), save_path)
            logger.info("  ✓ Saved best model → %s", save_path)

    # --- Final evaluation ---
    logger.info("=== Per-label AUC ===")
    for lbl, auc in zip(ODIR_LABELS, aucs):
        logger.info("  %-4s  AUC: %s", lbl, f"{auc:.4f}" if not np.isnan(auc) else "N/A")

    preds_arr = (probs_arr >= 0.4).astype(int)
    logger.info("Macro F1: %.4f", f1_score(targets_arr, preds_arr, average="macro", zero_division=0))
    logger.info("Best mean AUC: %.4f", best_mean_auc)
    logger.info("Model saved at: %s", output_dir / "odir_multilabel.pth")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train ODIR-5K multi-label classifier")
    p.add_argument(
        "--data-dir",
        default=os.environ.get("TRAIN_ODIR_DIR"),
        required=not os.environ.get("TRAIN_ODIR_DIR"),
        help="Root of the ODIR-5K dataset",
    )
    p.add_argument("--output-dir", default="python_service/models")
    p.add_argument("--epochs",     type=int,   default=30)
    p.add_argument("--batch-size", type=int,   default=32)
    p.add_argument("--lr",         type=float, default=1e-4)
    p.add_argument("--workers",    type=int,   default=4)
    return p.parse_args()


if __name__ == "__main__":
    train(parse_args())
