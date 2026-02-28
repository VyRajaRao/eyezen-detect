"""
train_aptos_dr_grading.py
-------------------------
Trains a 5-class diabetic retinopathy severity classifier on APTOS 2019.

DR grades: 0=No DR, 1=Mild, 2=Moderate, 3=Severe, 4=Proliferative

Usage
-----
    python train_aptos_dr_grading.py \\
        --data-dir /path/to/aptos2019-blindness-detection \\
        --epochs 30 \\
        --batch-size 32 \\
        --output-dir python_service/models

Expected dataset layout
-----------------------
  <data-dir>/
    train.csv            (id_code, diagnosis)
    train_images/
      <id_code>.png

Environment variables (optional, override CLI)
----------------------------------------------
  TRAIN_APTOS_DIR  path to APTOS 2019 dataset
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from torchvision import models

import sys
sys.path.insert(0, str(Path(__file__).parent))
from app.preprocessing import get_inference_transform, get_training_transform

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

NUM_CLASSES = 5
GRADE_NAMES = ["No DR", "Mild DR", "Moderate DR", "Severe DR", "Proliferative DR"]


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class APTOSDataset(Dataset):
    def __init__(self, df: pd.DataFrame, img_dir: Path, transform) -> None:
        self.df      = df.reset_index(drop=True)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        row     = self.df.iloc[idx]
        img_path = self.img_dir / f"{row['id_code']}.png"
        if not img_path.exists():
            # try .jpg fallback
            img_path = img_path.with_suffix(".jpg")
        img = Image.open(img_path).convert("RGB")
        return self.transform(img), int(row["diagnosis"])


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

def build_model(device: torch.device) -> nn.Module:
    weights = models.EfficientNet_B0_Weights.DEFAULT
    net = models.efficientnet_b0(weights=weights)
    in_features = net.classifier[1].in_features
    net.classifier = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(in_features, NUM_CLASSES),
    )
    return net.to(device)


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

def train(args: argparse.Namespace) -> None:
    data_dir   = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = data_dir / "train.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"train.csv not found in {data_dir}")
    img_dir = data_dir / "train_images"
    if not img_dir.is_dir():
        raise FileNotFoundError(f"train_images/ directory not found in {data_dir}")

    df = pd.read_csv(csv_path)
    logger.info("Loaded %d records from %s", len(df), csv_path)

    train_df, val_df = train_test_split(
        df, test_size=0.2, stratify=df["diagnosis"], random_state=42
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Device: %s  |  Train: %d  Val: %d", device, len(train_df), len(val_df))

    train_ds = APTOSDataset(train_df, img_dir, get_training_transform(224, augment=True))
    val_ds   = APTOSDataset(val_df,   img_dir, get_inference_transform(224))
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,  num_workers=args.workers)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size, shuffle=False, num_workers=args.workers)

    model     = build_model(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    best_acc = 0.0
    for epoch in range(1, args.epochs + 1):
        # --- Train ---
        model.train()
        epoch_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(images)
        epoch_loss /= len(train_ds)

        # --- Validate ---
        model.eval()
        all_preds, all_labels = [], []
        with torch.no_grad():
            for images, labels in val_loader:
                preds = model(images.to(device)).argmax(dim=1).cpu().numpy()
                all_preds.extend(preds.tolist())
                all_labels.extend(labels.numpy().tolist())

        acc = accuracy_score(all_labels, all_preds)
        scheduler.step()

        logger.info(
            "Epoch %d/%d  loss=%.4f  val_acc=%.4f",
            epoch, args.epochs, epoch_loss, acc,
        )

        if acc > best_acc:
            best_acc = acc
            save_path = output_dir / "aptos_dr_grading.pth"
            torch.save(model.state_dict(), save_path)
            logger.info("  ✓ Saved best model → %s", save_path)

    logger.info("=== Final validation metrics ===")
    logger.info("Accuracy: %.4f", best_acc)
    cm = confusion_matrix(all_labels, all_preds)
    logger.info("Confusion matrix (rows=actual, cols=predicted):\n%s", cm)
    logger.info("Grade names: %s", GRADE_NAMES)
    logger.info("Model saved at: %s", output_dir / "aptos_dr_grading.pth")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train APTOS 2019 DR grading classifier")
    p.add_argument(
        "--data-dir",
        default=os.environ.get("TRAIN_APTOS_DIR"),
        required=not os.environ.get("TRAIN_APTOS_DIR"),
        help="Root of the APTOS 2019 dataset (contains train.csv + train_images/)",
    )
    p.add_argument("--output-dir", default="python_service/models")
    p.add_argument("--epochs",     type=int,   default=30)
    p.add_argument("--batch-size", type=int,   default=32)
    p.add_argument("--lr",         type=float, default=1e-4)
    p.add_argument("--workers",    type=int,   default=4)
    return p.parse_args()


if __name__ == "__main__":
    train(parse_args())
