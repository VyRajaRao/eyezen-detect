# EyeZen Detect

A research-grade retinal fundus image analysis tool built with React, Node.js, and PyTorch.

> **Disclaimer**: This is a research tool only. Results are **not** a medical diagnosis and have
> not been validated as a clinical device. Always consult a qualified eye care professional.

---

## Architecture

```
Browser (React/Vite, port 8080 in dev)
        │ /api/*
        ▼
Node.js backend (Express, port 3001)  ←── PYTHON_ML_URL env var
        │ POST /predict (multipart)
        ▼
Python ML service (FastAPI, port 8000)
```

- **Frontend**: Vite + React + TypeScript (existing UI preserved).
- **Node backend** (`server/`): receives image uploads from the frontend, forwards to the Python service, and returns the prediction JSON.
- **Python ML service** (`python_service/`): validates whether the upload is a retinal fundus image, then runs ODIR multi-label prediction and optional APTOS DR grading.

---

## Quick-start (development)

### Prerequisites

- Node.js >= 18
- Python >= 3.10
- (GPU optional but recommended for training)

### 1 – Install dependencies

```bash
# Frontend
npm install

# Node backend
cd server && npm install && cd ..

# Python service
pip install -r python_service/requirements.txt
```

### 2 – Configure environment

```bash
# Node backend
cp server/.env.example server/.env
# Edit server/.env – set PORT and PYTHON_ML_URL

# Python service
cp python_service/.env.example python_service/.env
# Edit python_service/.env – set MODEL_PATH_* variables (see Training section)
```

### 3 – Run all three services

Open **three terminals**:

```bash
# Terminal 1 – Python ML service
cd python_service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 – Node backend
cd server
node index.js          # or: npm run dev  (hot-reload)

# Terminal 3 – Frontend (Vite dev server with /api proxy)
npm run dev
```

Visit `http://localhost:8080`.

---

## API contract

### `GET /api/health`
```json
{ "node": "ok", "python": { "status": "ok" } }
```

### `POST /api/predict`
Accepts `multipart/form-data` with field `file` (image).

**Success (200)**:
```json
{
  "disease": "Normal",
  "confidence": 0.0,
  "is_retinal": true,
  "odir_predictions": [{"label": "Normal", "score": 0.0}, ...],
  "top_odir_label": "Normal",
  "aptos_dr_grade": null,
  "model_version": "dev",
  "notes": "Research tool only. ..."
}
```

**Non-retinal image (400)**:
```json
{ "error": "invalid_image", "message": "Not a retinal fundus image" }
```

---

## Training

Training scripts live in `python_service/`. Each script accepts `--data-dir` and saves a `.pth` artefact under `python_service/models/`.

### Retinal validator

```bash
python python_service/train_retinal_validator.py \
    --retinal-dir     /data/retinal_images \
    --non-retinal-dir /data/non_retinal_images \
    --output-dir      python_service/models \
    --epochs 20
# Set MODEL_PATH_VALIDATOR=python_service/models/retinal_validator.pth
```

### ODIR-5K multi-label classifier

Dataset: [ODIR-5K](https://odir2019.grand-challenge.org/) – root dir with `ODIR-5K_Training_Annotations.xlsx` and image folder.

```bash
python python_service/train_odir_multilabel.py \
    --data-dir   /data/ODIR-5K \
    --output-dir python_service/models \
    --epochs 30
# Set MODEL_PATH_ODIR=python_service/models/odir_multilabel.pth
```

### APTOS 2019 DR grading (optional)

Dataset: [APTOS 2019](https://www.kaggle.com/competitions/aptos2019-blindness-detection) – root dir with `train.csv` and `train_images/`.

```bash
python python_service/train_aptos_dr_grading.py \
    --data-dir   /data/aptos2019 \
    --output-dir python_service/models \
    --epochs 30
# Set MODEL_PATH_APTOS=python_service/models/aptos_dr_grading.pth
```

---

## Retinal validator fallback (no model)

If `MODEL_PATH_VALIDATOR` is unset, a heuristic is used:
1. **Circular bright region with dark border** – luminance ratio inside vs outside a centred circle >= `THRESHOLD_RETINAL` (default 1.5).
2. **Orange/reddish dominant colour** – R-channel mean >= 1.5x B-channel mean.

Train a dedicated model for production use.

---

## Tests

```bash
pytest python_service/tests/ -v
```

---

## Environment variables

### Node backend (`server/.env`)

| Variable        | Default                 | Description                       |
|-----------------|-------------------------|-----------------------------------|
| `PORT`          | `3001`                  | Node server port                  |
| `PYTHON_ML_URL` | `http://localhost:8000` | URL of the Python ML service      |

### Python ML service (`python_service/.env`)

| Variable               | Default | Description                                          |
|------------------------|---------|------------------------------------------------------|
| `MODEL_PATH_VALIDATOR` | (none)  | Path to retinal validator `.pth`; heuristic if unset |
| `MODEL_PATH_ODIR`      | (none)  | Path to ODIR `.pth`; placeholder predictions if unset |
| `MODEL_PATH_APTOS`     | (none)  | Path to APTOS `.pth`; DR grading skipped if unset   |
| `THRESHOLD_RETINAL`    | `0.5` (model) / `1.5` (heuristic) | Retinal gate threshold |
| `THRESHOLD_ODIR`       | `0.4`   | Per-label threshold for ODIR                        |
| `MODEL_VERSION`        | `dev`   | Version string in prediction response               |

### Frontend

| Variable       | Default                 | Description                   |
|----------------|-------------------------|-------------------------------|
| `VITE_API_URL` | `http://localhost:3001` | Vite dev proxy target         |
