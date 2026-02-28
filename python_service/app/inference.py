"""
Inference helpers for the EyeZen ML service.

Three components are defined here:
  - RetinalValidator  – binary gate; decides whether the upload is a retinal
                        fundus image.
  - ODIRPredictor     – multi-label classifier trained on ODIR-5K.
  - APTOSPredictor    – DR grading (0–4) trained on APTOS 2019.

Each class attempts to load a trained PyTorch model from an env-var path.
If the model file is absent or the env-var is unset, a safe fallback is used
instead of raising at startup:
  - RetinalValidator  → heuristic-based fundus check (documented below).
  - ODIRPredictor     → returns placeholder predictions with score 0.0.
  - APTOSPredictor    → returns None (APTOS grading is optional).
"""

from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models

from .preprocessing import preprocess_image

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ODIR class labels (ODIR-5K standard ordering)
# ---------------------------------------------------------------------------
ODIR_LABELS: List[str] = [
    "Normal",
    "Diabetic Retinopathy",
    "Glaucoma",
    "Cataract",
    "Age-related Macular Degeneration",
    "Hypertension",
    "Myopia",
    "Other",
]

APTOS_GRADES: Dict[int, str] = {
    0: "No DR",
    1: "Mild DR",
    2: "Moderate DR",
    3: "Severe DR",
    4: "Proliferative DR",
}


# ---------------------------------------------------------------------------
# Helper: build EfficientNet backbone
# ---------------------------------------------------------------------------
def _build_efficientnet(num_outputs: int, pretrained: bool = False) -> nn.Module:
    """Return an EfficientNet-B0 with a custom head."""
    weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
    backbone = models.efficientnet_b0(weights=weights)
    in_features = backbone.classifier[1].in_features
    backbone.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_outputs),
    )
    return backbone


def _load_model(model: nn.Module, path: str, device: torch.device) -> bool:
    """Load weights from *path* into *model* in-place.  Returns True on success."""
    if not path or not os.path.isfile(path):
        return False
    try:
        state = torch.load(path, map_location=device)
        # Accept raw state-dicts or checkpoint dicts
        if isinstance(state, dict) and "model_state_dict" in state:
            state = state["model_state_dict"]
        model.load_state_dict(state)
        model.eval()
        logger.info("Loaded model weights from %s", path)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not load model from %s: %s", path, exc)
        return False


# ---------------------------------------------------------------------------
# Retinal validator
# ---------------------------------------------------------------------------
class RetinalValidator:
    """
    Validates whether an image is a retinal fundus photograph.

    Behaviour
    ---------
    *Model mode*   – If ``MODEL_PATH_VALIDATOR`` points to a valid ``.pt`` /
                     ``.pth`` file the trained binary classifier is used.
    *Heuristic mode* – Fallback when no model is available.  Checks two
                       image-level features that are characteristic of
                       fundus photographs:

                       1. **Circular bright region with dark surround** –
                          fundus cameras produce images with a bright
                          circular field and a black border.  We compare the
                          mean luminance inside a centred circle of radius
                          42 % of the shorter image dimension against the
                          mean luminance outside it.  A ratio ≥
                          ``THRESHOLD_RETINAL`` (default 1.5) suggests a
                          fundus image.

                       2. **Orange / reddish dominant colour** – the red
                          channel mean should exceed the blue channel mean
                          by at least 1.5× (the retina is orange/red).

                       An image passes the gate if *either* condition is met.
                       This heuristic produces false-positives on some
                       orange-toned photographs but errs on the side of
                       inclusiveness so that genuine fundus images are not
                       rejected.  For production use, train and load a
                       dedicated validator model.
    """

    def __init__(self) -> None:
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._threshold = float(os.environ.get("THRESHOLD_RETINAL", "0.5"))
        self._model_loaded = False

        path = os.environ.get("MODEL_PATH_VALIDATOR", "")
        if path:
            self._net = _build_efficientnet(num_outputs=1)
            self._net.to(self._device)
            self._model_loaded = _load_model(self._net, path, self._device)

        if not self._model_loaded:
            logger.info(
                "RetinalValidator: no model loaded – using heuristic fallback. "
                "Set MODEL_PATH_VALIDATOR to enable model-based validation."
            )

    def is_retinal(self, image: Image.Image) -> bool:
        if self._model_loaded:
            return self._model_predict(image)
        return self._heuristic(image)

    # ------------------------------------------------------------------
    # Model-based prediction
    # ------------------------------------------------------------------
    def _model_predict(self, image: Image.Image) -> bool:
        tensor = preprocess_image(image).to(self._device)
        with torch.no_grad():
            logit = self._net(tensor).squeeze()
            prob = torch.sigmoid(logit).item()
        return prob >= self._threshold

    # ------------------------------------------------------------------
    # Heuristic fallback
    # ------------------------------------------------------------------
    def _heuristic(self, image: Image.Image) -> bool:
        heuristic_threshold = float(os.environ.get("THRESHOLD_RETINAL", "1.5"))
        img_rgb = np.array(image.convert("RGB"), dtype=np.float32)
        h, w = img_rgb.shape[:2]

        # --- Feature 1: circular bright region with dark border ----------
        cy, cx = h // 2, w // 2
        radius = min(h, w) * 0.42
        yy, xx = np.ogrid[:h, :w]
        inside = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2
        gray = img_rgb.mean(axis=2)
        inside_mean = float(gray[inside].mean()) if inside.any() else 0.0
        outside_mean = float(gray[~inside].mean()) if (~inside).any() else 255.0
        outside_mean = max(outside_mean, 1.0)
        circle_ratio = inside_mean / outside_mean
        has_dark_border = outside_mean < 60.0

        # --- Feature 2: orange / reddish dominant colour -----------------
        r_mean = float(img_rgb[:, :, 0].mean())
        b_mean = float(img_rgb[:, :, 2].mean())
        color_ratio = r_mean / max(b_mean, 1.0)

        return (has_dark_border and circle_ratio >= heuristic_threshold) or (
            color_ratio >= 1.5 and r_mean >= 30.0
        )


# ---------------------------------------------------------------------------
# ODIR multi-label predictor
# ---------------------------------------------------------------------------
class ODIRPredictor:
    """
    Multi-label classifier for the eight ODIR-5K disease categories.

    If ``MODEL_PATH_ODIR`` is not set or the file is missing, placeholder
    predictions (score 0.0) are returned with a warning in the notes field.
    """

    def __init__(self) -> None:
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._threshold = float(os.environ.get("THRESHOLD_ODIR", "0.4"))
        self._model_loaded = False

        path = os.environ.get("MODEL_PATH_ODIR", "")
        if path:
            self._net = _build_efficientnet(num_outputs=len(ODIR_LABELS))
            self._net.to(self._device)
            self._model_loaded = _load_model(self._net, path, self._device)

        if not self._model_loaded:
            logger.warning(
                "ODIRPredictor: no model loaded – placeholder predictions will be returned. "
                "Set MODEL_PATH_ODIR and train with train_odir_multilabel.py."
            )

    def predict(self, image: Image.Image) -> List[Dict[str, object]]:
        if self._model_loaded:
            return self._model_predict(image)
        # Placeholder – all scores 0.0
        return [{"label": lbl, "score": 0.0} for lbl in ODIR_LABELS]

    def _model_predict(self, image: Image.Image) -> List[Dict[str, object]]:
        tensor = preprocess_image(image).to(self._device)
        with torch.no_grad():
            logits = self._net(tensor).squeeze(0)
            probs = torch.sigmoid(logits).cpu().numpy()
        return [
            {"label": lbl, "score": round(float(p), 4)}
            for lbl, p in zip(ODIR_LABELS, probs)
        ]


# ---------------------------------------------------------------------------
# APTOS DR grading predictor (optional)
# ---------------------------------------------------------------------------
class APTOSPredictor:
    """
    5-class DR severity classifier (grades 0–4) trained on APTOS 2019.

    Only instantiated when ``MODEL_PATH_APTOS`` is set.
    """

    def __init__(self) -> None:
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model_loaded = False

        path = os.environ.get("MODEL_PATH_APTOS", "")
        if path:
            self._net = _build_efficientnet(num_outputs=5)
            self._net.to(self._device)
            self._model_loaded = _load_model(self._net, path, self._device)

        if not self._model_loaded:
            logger.info(
                "APTOSPredictor: no model loaded – DR grading will be skipped. "
                "Set MODEL_PATH_APTOS and train with train_aptos_dr_grading.py."
            )

    def predict(self, image: Image.Image) -> Optional[str]:
        if not self._model_loaded:
            return None
        tensor = preprocess_image(image).to(self._device)
        with torch.no_grad():
            logits = self._net(tensor).squeeze(0)
            grade = int(logits.argmax().item())
        return APTOS_GRADES.get(grade, f"Grade {grade}")
