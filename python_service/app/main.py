"""
EyeZen FastAPI ML service.

Endpoints
---------
GET  /health   – liveness probe
POST /predict  – retinal fundus validation + disease prediction
"""

from __future__ import annotations

import io
import logging
import os

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from .inference import APTOSPredictor, ODIRPredictor, RetinalValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="EyeZen ML Service", version="1.0.0")

# ---------------------------------------------------------------------------
# Lazy-loaded singletons (instantiated on first request to allow the server
# to start even when model files are not yet present).
# ---------------------------------------------------------------------------
_validator: RetinalValidator | None = None
_odir: ODIRPredictor | None = None
_aptos: APTOSPredictor | None = None


def _get_validator() -> RetinalValidator:
    global _validator  # noqa: PLW0603
    if _validator is None:
        _validator = RetinalValidator()
    return _validator


def _get_odir() -> ODIRPredictor:
    global _odir  # noqa: PLW0603
    if _odir is None:
        _odir = ODIRPredictor()
    return _odir


def _get_aptos() -> APTOSPredictor | None:
    global _aptos  # noqa: PLW0603
    if _aptos is None and os.environ.get("MODEL_PATH_APTOS"):
        _aptos = APTOSPredictor()
    return _aptos


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
def health() -> dict:
    """Liveness probe."""
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> JSONResponse:
    """
    Validate the uploaded file as a retinal fundus image and run disease
    prediction.

    Returns
    -------
    200  Retinal image – prediction JSON.
    400  Not a retinal fundus image or not a valid image file.
    """
    # 1. Decode image safely
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except (UnidentifiedImageError, Exception):
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_image", "message": "Could not decode image file"},
        )

    # 2. Retinal validation gate
    validator = _get_validator()
    if not validator.is_retinal(image):
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_image", "message": "Not a retinal fundus image"},
        )

    # 3. ODIR multi-label prediction
    odir = _get_odir()
    odir_predictions = odir.predict(image)
    top_label = (
        max(odir_predictions, key=lambda p: p["score"])["label"]
        if odir_predictions
        else "Unknown"
    )

    result: dict = {
        "is_retinal": True,
        "odir_predictions": odir_predictions,
        "top_odir_label": top_label,
        "model_version": os.environ.get("MODEL_VERSION", "dev"),
        "notes": (
            "Research tool only. Predictions are not a medical diagnosis. "
            "Please consult a qualified eye care professional for evaluation."
        ),
    }

    # 4. Optional APTOS DR grading
    aptos = _get_aptos()
    if aptos is not None:
        result["aptos_dr_grade"] = aptos.predict(image)

    return JSONResponse(status_code=200, content=result)
