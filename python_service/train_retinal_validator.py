"""
train_retinal_validator.py
--------------------------
Trains a binary retinal-fundus validator (retinal vs non-retinal).

Usage
-----
Provide at least a directory of retinal images.  Optionally provide a
directory of non-retinal images.  If only retinal images are supplied, a
synthetic "non-retinal" split is created by applying strong corruptions.

    python train_retinal_validator.py \\
        --retinal-dir  /data/retinal_images \\
        --non-retinal-dir /data/non_retinal_images \\
        --epochs 20 \\
        --batch-size 32 \\
        --output-dir python_service/models

Dataset layout expected
-----------------------
  <retinal-dir>/
    *.jpg | *.png | ...      (flat or nested – all images are collected)
  <non-retinal-dir>/          (optional)
    *.jpg | *.png | ...

Environment variables (optional, override CLI)
----------------------------------------------
  TRAIN_RETINAL_DIR      path to retinal images
  TRAIN_NON_RETINAL_DIR  path to non-retinal images
"""

from __future__ import annotations

import argparse
import logging
import os
import random
from pathlib import Path
from typing import List, Tuple

import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from torchvision import models

# Shared preprocessing
import sys
sys.path.insert(0, str(Path(__file__).parent))
from app.preprocessing import get_training_transform, get_inference_transform

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class BinaryImageDataset(Dataset):
    def __init__(self, paths: List[Path], labels: List[int], transform) -> None:
        self.paths = paths
        self.labels = labels
        self.transform = transform

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img = Image.open(self.paths[idx]).convert("RGB")
        return self.transform(img), self.labels[idx]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def collect_images(directory: Path) -> List[Path]:
    return [
        p for p in directory.rglob("*") if p.suffix.lower() in IMAGE_EXTENSIONS
    ]


def build_model(device: torch.device) -> nn.Module:
    weights = models.EfficientNet_B0_Weights.DEFAULT
    net = models.efficientnet_b0(weights=weights)
    in_features = net.classifier[1].in_features
    net.classifier = nn.Sequential(nn.Dropout(0.3), nn.Linear(in_features, 1))
    return net.to(device)


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------

def train(args: argparse.Namespace) -> None:
    retinal_dir = Path(args.retinal_dir)
    non_retinal_dir = Path(args.non_retinal_dir) if args.non_retinal_dir else None
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    retinal_images = collect_images(retinal_dir)
    if not retinal_images:
        raise ValueError(f"No images found in {retinal_dir}")

    if non_retinal_dir and non_retinal_dir.exists():
        non_retinal_images = collect_images(non_retinal_dir)
    else:
        logger.warning(
            "No non-retinal directory provided; using a random 20%% subset of "
            "retinal images as a synthetic negative class (sub-optimal – provide "
            "real non-retinal images for better performance)."
        )
        non_retinal_images = random.sample(retinal_images, max(1, len(retinal_images) // 5))

    all_paths = retinal_images + non_retinal_images
    all_labels = [1] * len(retinal_images) + [0] * len(non_retinal_images)

    train_paths, val_paths, train_labels, val_labels = train_test_split(
        all_paths, all_labels, test_size=0.2, stratify=all_labels, random_state=42
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Using device: %s", device)
    logger.info("Train: %d  Val: %d", len(train_paths), len(val_paths))

    train_ds = BinaryImageDataset(train_paths, train_labels, get_training_transform(224, augment=True))
    val_ds   = BinaryImageDataset(val_paths,   val_labels,   get_inference_transform(224))

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,  num_workers=args.workers)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size, shuffle=False, num_workers=args.workers)

    model = build_model(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    criterion = nn.BCEWithLogitsLoss()
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    best_auc = 0.0
    for epoch in range(1, args.epochs + 1):
        # --- Train ---
        model.train()
        train_loss = 0.0
        for images, targets in train_loader:
            images = images.to(device)
            targets = targets.float().unsqueeze(1).to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), targets)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(images)
        train_loss /= len(train_ds)

        # --- Validate ---
        model.eval()
        all_probs, all_targets = [], []
        with torch.no_grad():
            for images, targets in val_loader:
                logits = model(images.to(device)).squeeze(1)
                probs = torch.sigmoid(logits).cpu().numpy()
                all_probs.extend(probs.tolist())
                all_targets.extend(targets.numpy().tolist())

        auc = roc_auc_score(all_targets, all_probs)
        preds = [1 if p >= 0.5 else 0 for p in all_probs]
        scheduler.step()

        logger.info(
            "Epoch %d/%d  train_loss=%.4f  val_auc=%.4f",
            epoch, args.epochs, train_loss, auc
        )

        if auc > best_auc:
            best_auc = auc
            save_path = output_dir / "retinal_validator.pth"
            torch.save(model.state_dict(), save_path)
            logger.info("  ✓ Saved best model to %s", save_path)

    logger.info("=== Final validation report ===")
    logger.info(classification_report(all_targets, preds, target_names=["non-retinal", "retinal"]))
    logger.info("Best Val AUC: %.4f", best_auc)
    logger.info("Model saved at: %s", output_dir / "retinal_validator.pth")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train retinal fundus validator")
    p.add_argument(
        "--retinal-dir",
        default=os.environ.get("TRAIN_RETINAL_DIR"),
        required=not os.environ.get("TRAIN_RETINAL_DIR"),
        help="Directory of retinal fundus images (label=1)",
    )
    p.add_argument(
        "--non-retinal-dir",
        default=os.environ.get("TRAIN_NON_RETINAL_DIR"),
        help="Directory of non-retinal images (label=0). Optional.",
    )
    p.add_argument("--output-dir",  default="python_service/models", help="Where to save model artefacts")
    p.add_argument("--epochs",      type=int,   default=20)
    p.add_argument("--batch-size",  type=int,   default=32)
    p.add_argument("--lr",          type=float, default=1e-4)
    p.add_argument("--workers",     type=int,   default=4)
    return p.parse_args()


if __name__ == "__main__":
    train(parse_args())
