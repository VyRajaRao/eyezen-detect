"""
Tests for the EyeZen Python ML service.

Run with:  pytest python_service/tests/test_api.py -v
"""

from __future__ import annotations

import io
import os

import pytest
from fastapi.testclient import TestClient
from PIL import Image


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """Create a test client with no model env-vars set (heuristic mode)."""
    # Ensure no model paths are accidentally set
    for var in ("MODEL_PATH_VALIDATOR", "MODEL_PATH_ODIR", "MODEL_PATH_APTOS"):
        os.environ.pop(var, None)

    from python_service.app.main import app  # noqa: PLC0415

    return TestClient(app)


def _png_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def _make_solid_color_image(r: int, g: int, b: int, size: int = 64) -> bytes:
    """Create a small solid-colour PNG in memory."""
    img = Image.new("RGB", (size, size), color=(r, g, b))
    return _png_bytes(img)


def _make_fundus_like_image(size: int = 224) -> bytes:
    """
    Create a synthetic fundus-like image:
    - Orange circular region in the centre
    - Black border outside
    """
    import numpy as np

    arr = np.zeros((size, size, 3), dtype=np.uint8)
    cy, cx = size // 2, size // 2
    radius = int(size * 0.42)
    yy, xx = np.ogrid[:size, :size]
    inside = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2
    # Orange tone: R high, G medium, B low
    arr[inside, 0] = 200  # R
    arr[inside, 1] = 120  # G
    arr[inside, 2] = 40   # B
    img = Image.fromarray(arr, mode="RGB")
    return _png_bytes(img)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"


class TestPredictRejection:
    def test_no_file_returns_422(self, client):
        """Sending no file should return 422 (FastAPI validation error)."""
        response = client.post("/predict")
        assert response.status_code == 422

    def test_non_image_bytes_returns_400(self, client):
        """Sending random bytes that are not an image should return 400."""
        response = client.post(
            "/predict",
            files={"file": ("random.bin", b"\x00\x01\x02\x03", "application/octet-stream")},
        )
        assert response.status_code == 400
        body = response.json()
        assert body.get("error") == "invalid_image"

    def test_plain_text_returns_400(self, client):
        """Sending a text file should return 400 (not an image)."""
        response = client.post(
            "/predict",
            files={"file": ("note.txt", b"Hello world", "text/plain")},
        )
        assert response.status_code == 400

    def test_solid_blue_image_returns_400(self, client):
        """
        A solid blue image has B >> R, so the heuristic should reject it
        as non-retinal (fundus images are orange/reddish).
        We also give it no dark border so it fails both conditions.
        """
        # Solid blue: R=0, G=0, B=200
        image_bytes = _make_solid_color_image(0, 0, 200, size=224)
        response = client.post(
            "/predict",
            files={"file": ("blue.png", image_bytes, "image/png")},
        )
        # The heuristic should reject this as non-retinal
        assert response.status_code == 400
        body = response.json()
        assert body.get("error") == "invalid_image"
        assert "retinal" in body.get("message", "").lower()


class TestPredictAcceptance:
    def test_fundus_like_image_returns_200(self, client):
        """
        A synthetic fundus-like image (orange disc on black) should pass the
        heuristic validator and return a 200 with the expected JSON structure.
        """
        image_bytes = _make_fundus_like_image(224)
        response = client.post(
            "/predict",
            files={"file": ("fundus.png", image_bytes, "image/png")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("is_retinal") is True
        assert "odir_predictions" in body
        assert "top_odir_label" in body
        assert "model_version" in body
        assert "notes" in body
        # odir_predictions should have 8 entries
        assert len(body["odir_predictions"]) == 8
        # Each entry should have label + score
        for pred in body["odir_predictions"]:
            assert "label" in pred
            assert "score" in pred
            assert isinstance(pred["score"], float)

    def test_mildly_warm_image_accepted(self, client):
        """
        A mildly warm-toned image (R/B ratio ~1.3) that previously failed
        the old threshold of 1.5 should now pass with the relaxed 1.1 threshold.
        This simulates a processed / slightly desaturated fundus image.
        """
        # R=130, G=110, B=100 → ratio ≈ 1.30 (was rejected with old 1.5 threshold)
        image_bytes = _make_solid_color_image(130, 110, 100, size=224)
        response = client.post(
            "/predict",
            files={"file": ("mild_warm.png", image_bytes, "image/png")},
        )
        assert response.status_code == 200, (
            "Mildly warm-toned image (R/B≈1.3) should be accepted by the relaxed heuristic"
        )
