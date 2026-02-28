'use strict';

require('dotenv').config();

const express = require('express');
const multer = require('multer');
const FormData = require('form-data');
const fetch = require('node-fetch');
const path = require('path');
const { rateLimit } = require('express-rate-limit');

const app = express();
const PORT = parseInt(process.env.PORT || '3001', 10);
const PYTHON_ML_URL = (process.env.PYTHON_ML_URL || 'http://localhost:8000').replace(/\/$/, '');

// Serve built frontend in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '..', 'dist')));
}

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10 MB
});

// Rate limiter: max 60 predict requests per IP per minute
const predictLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 60,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'rate_limited', message: 'Too many requests, please try again later.' },
});

// Rate limiter for all /api routes: 120 requests per IP per minute
const apiLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 120,
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api', apiLimiter);

/** GET /api/health – returns Node + Python service status */
app.get('/api/health', async (_req, res) => {
  try {
    const response = await fetch(`${PYTHON_ML_URL}/health`, { timeout: 5000 });
    const data = await response.json();
    res.json({ node: 'ok', python: data });
  } catch (_err) {
    res.status(503).json({ node: 'ok', python: 'unavailable' });
  }
});

/** POST /api/predict – accepts multipart `file`, forwards to Python service */
app.post('/api/predict', predictLimiter, upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'no_file', message: 'No file uploaded' });
  }

  const form = new FormData();
  form.append('file', req.file.buffer, {
    filename: req.file.originalname || 'upload.jpg',
    contentType: req.file.mimetype || 'image/jpeg',
  });

  let pyResponse;
  try {
    pyResponse = await fetch(`${PYTHON_ML_URL}/predict`, {
      method: 'POST',
      body: form,
      headers: form.getHeaders(),
      timeout: 60000,
    });
  } catch (err) {
    console.error('[predict] Python service unreachable:', err.message);
    return res.status(502).json({ error: 'gateway_error', message: 'ML service is unavailable' });
  }

  let data;
  try {
    data = await pyResponse.json();
  } catch (_err) {
    return res.status(502).json({ error: 'gateway_error', message: 'Invalid response from ML service' });
  }

  // Propagate non-200 responses (e.g. 400 invalid_image) verbatim
  if (!pyResponse.ok) {
    return res.status(pyResponse.status).json(data);
  }

  // Map Python response to the PredictionResult shape the frontend expects,
  // while also passing through the extended fields.
  const topLabel = data.top_odir_label || 'Unknown';
  const odir = Array.isArray(data.odir_predictions) ? data.odir_predictions : [];
  const topScore = odir.find((p) => p.label === topLabel)?.score ?? 0;

  return res.json({
    // Core fields consumed by existing ResultsSection UI
    disease: topLabel,
    confidence: topScore,
    // Extended fields (future use / richer UI)
    is_retinal: data.is_retinal,
    odir_predictions: odir,
    aptos_dr_grade: data.aptos_dr_grade ?? null,
    model_version: data.model_version ?? null,
    notes: data.notes ?? null,
  });
});

// Rate limiter for SPA fallback: 200 requests per IP per minute
const spaLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 200,
  standardHeaders: true,
  legacyHeaders: false,
});

// SPA fallback in production
if (process.env.NODE_ENV === 'production') {
  app.get('*', spaLimiter, (_req, res) => {
    res.sendFile(path.join(__dirname, '..', 'dist', 'index.html'));
  });
}

app.listen(PORT, () => {
  console.log(`[server] Node backend listening on port ${PORT}`);
  console.log(`[server] Forwarding ML requests to ${PYTHON_ML_URL}`);
});
