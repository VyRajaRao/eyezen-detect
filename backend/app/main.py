"""
FastAPI Eye Disease Detection Backend
Integrates with Kaggle datasets and PyTorch models for eye disease classification
"""

import os
import io
import base64
import time
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from PIL import Image
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms, models
import cv2

# Import custom modules
from utils.kaggle_utils import KaggleDatasetManager
from utils.preprocess import ImagePreprocessor
from utils.train_utils import ModelTrainer
from utils.metrics import MetricsTracker
from database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EyeZen Detect API",
    description="AI-powered eye disease detection using Kaggle datasets and PyTorch",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and components
current_model = None
image_preprocessor = ImagePreprocessor()
metrics_tracker = MetricsTracker()
database = Database()

# Pydantic models for API requests/responses
class DatasetDownloadRequest(BaseModel):
    dataset: str
    description: Optional[str] = None

class TrainModelRequest(BaseModel):
    dataset_name: str
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 0.001

class PredictionResponse(BaseModel):
    image_id: str
    predicted_disease: str
    confidence: float
    all_predictions: List[Dict[str, float]]
    processing_time: float
    image_quality: str
    heatmap: Optional[str] = None
    timestamp: str
    model_info: Dict[str, Any]

class TrainingStatus(BaseModel):
    is_training: bool
    current_epoch: Optional[int] = None
    total_epochs: Optional[int] = None
    train_accuracy: Optional[float] = None
    val_accuracy: Optional[float] = None
    loss: Optional[float] = None
    estimated_time_remaining: Optional[str] = None

# Global training status
training_status = {
    "is_training": False,
    "current_epoch": None,
    "total_epochs": None,
    "train_accuracy": None,
    "val_accuracy": None,
    "loss": None,
    "estimated_time_remaining": None
}

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    try:
        # Initialize database
        await database.init_db()
        
        # Load the latest model if available
        await load_latest_model()
        
        # Initialize Kaggle API
        kaggle_manager = KaggleDatasetManager()
        if kaggle_manager.is_configured():
            logger.info("Kaggle API configured successfully")
        else:
            logger.warning("Kaggle API not configured. Set KAGGLE_USERNAME and KAGGLE_KEY in .env")
        
        logger.info("FastAPI backend initialized successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")

async def load_latest_model():
    """Load the latest trained model"""
    global current_model
    
    models_dir = "models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        logger.info("Created models directory")
        return
    
    # Look for the latest model file
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.pt')]
    if not model_files:
        logger.info("No trained models found")
        return
    
    # Load the most recent model
    latest_model = max(model_files, key=lambda x: os.path.getctime(os.path.join(models_dir, x)))
    model_path = os.path.join(models_dir, latest_model)
    
    try:
        # Load PyTorch model
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        current_model = torch.load(model_path, map_location=device)
        current_model.eval()
        
        logger.info(f"Loaded model: {latest_model}")
        
    except Exception as e:
        logger.error(f"Failed to load model {latest_model}: {str(e)}")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": current_model is not None,
        "pytorch_available": torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

# Dataset management endpoints
@app.post("/api/download-dataset")
async def download_dataset(request: DatasetDownloadRequest, background_tasks: BackgroundTasks):
    """Download and process a Kaggle dataset"""
    try:
        kaggle_manager = KaggleDatasetManager()
        
        if not kaggle_manager.is_configured():
            raise HTTPException(
                status_code=400, 
                detail="Kaggle API not configured. Please set KAGGLE_USERNAME and KAGGLE_KEY"
            )
        
        # Start download in background
        background_tasks.add_task(
            kaggle_manager.download_and_process_dataset,
            request.dataset,
            request.description
        )
        
        return {
            "message": f"Dataset download started: {request.dataset}",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Dataset download error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets")
async def list_datasets():
    """List available datasets"""
    try:
        datasets = await database.get_datasets()
        return {"datasets": datasets}
        
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets/popular")
async def get_popular_datasets():
    """Get popular eye disease datasets"""
    popular_datasets = [
        {
            "name": "aravind_eye_hospital/aptos-2019-blindness-detection",
            "title": "APTOS 2019 Blindness Detection",
            "description": "Detect diabetic retinopathy to stop blindness before it's too late",
            "size": "3.6 GB",
            "classes": ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"]
        },
        {
            "name": "andrewmvd/ocular-disease-recognition-odir5k", 
            "title": "Ocular Disease Recognition (ODIR-5K)",
            "description": "Multi-class retinal disease classification",
            "size": "1.8 GB",
            "classes": ["Normal", "Diabetes", "Glaucoma", "Cataract", "AMD", "Hypertension", "Myopia", "Others"]
        },
        {
            "name": "paultimothymooney/kermany2018",
            "title": "Retinal OCT Images (optical coherence tomography)",
            "description": "OCT images for retinal disease classification",
            "size": "5.2 GB", 
            "classes": ["CNV", "DME", "DRUSEN", "NORMAL"]
        }
    ]
    
    return {"datasets": popular_datasets}

# Model training endpoints
@app.post("/api/train-model")
async def train_model(request: TrainModelRequest, background_tasks: BackgroundTasks):
    """Start model training"""
    global training_status
    
    if training_status["is_training"]:
        raise HTTPException(status_code=400, detail="Training already in progress")
    
    try:
        # Check if dataset exists
        dataset_path = f"data/processed/{request.dataset_name}"
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail=f"Dataset not found: {request.dataset_name}")
        
        # Start training in background
        background_tasks.add_task(
            start_training,
            request.dataset_name,
            request.epochs,
            request.batch_size,
            request.learning_rate
        )
        
        return {
            "message": "Model training started",
            "dataset": request.dataset_name,
            "epochs": request.epochs,
            "batch_size": request.batch_size
        }
        
    except Exception as e:
        logger.error(f"Training start error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def start_training(dataset_name: str, epochs: int, batch_size: int, learning_rate: float):
    """Background task for model training"""
    global training_status, current_model
    
    training_status["is_training"] = True
    training_status["total_epochs"] = epochs
    
    try:
        trainer = ModelTrainer()
        
        # Train the model with progress callback
        def progress_callback(epoch, train_acc, val_acc, loss):
            training_status.update({
                "current_epoch": epoch,
                "train_accuracy": train_acc,
                "val_accuracy": val_acc,
                "loss": loss
            })
        
        model_path = await trainer.train_model(
            dataset_name=dataset_name,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            progress_callback=progress_callback
        )
        
        # Load the newly trained model
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        current_model = torch.load(model_path, map_location=device)
        current_model.eval()
        
        logger.info(f"Training completed. Model saved to: {model_path}")
        
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
    finally:
        training_status["is_training"] = False

@app.get("/api/train-status")
async def get_training_status():
    """Get current training status"""
    return TrainingStatus(**training_status)

# Prediction endpoint
@app.post("/api/predict")
async def predict_eye_disease(
    image: UploadFile = File(...),
    generate_heatmap: bool = Form(False)
):
    """Predict eye disease from uploaded image"""
    
    if current_model is None:
        raise HTTPException(status_code=503, detail="No trained model available")
    
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        
        # Read and preprocess image
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Preprocess for model
        start_time = time.time()
        processed_image = image_preprocessor.preprocess_for_prediction(np.array(pil_image))
        
        # Make prediction
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        with torch.no_grad():
            # Convert to tensor and add batch dimension
            image_tensor = torch.from_numpy(processed_image).permute(2, 0, 1).unsqueeze(0).float().to(device)
            
            # Get prediction
            outputs = current_model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
            # Get class names (you'll need to define these based on your dataset)
            class_names = [
                "Normal",
                "Diabetic Retinopathy", 
                "Glaucoma",
                "Cataract",
                "Age-related Macular Degeneration",
                "Hypertensive Retinopathy"
            ]
            
            # Get top prediction
            confidence, predicted_idx = torch.max(probabilities, 1)
            predicted_class = class_names[predicted_idx.item()]
            confidence_score = confidence.item()
            
            # Get all predictions
            all_predictions = []
            for i, class_name in enumerate(class_names):
                all_predictions.append({
                    "class": class_name,
                    "confidence": probabilities[0][i].item()
                })
            
            # Sort by confidence
            all_predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        processing_time = time.time() - start_time
        
        # Generate heatmap if requested
        heatmap_b64 = None
        if generate_heatmap:
            try:
                heatmap_b64 = generate_gradcam_heatmap(current_model, image_tensor, np.array(pil_image))
            except Exception as e:
                logger.warning(f"Failed to generate heatmap: {str(e)}")
        
        # Assess image quality
        image_quality = assess_image_quality(np.array(pil_image))
        
        response = PredictionResponse(
            image_id=f"img_{int(time.time())}",
            predicted_disease=predicted_class,
            confidence=confidence_score,
            all_predictions=all_predictions,
            processing_time=processing_time,
            image_quality=image_quality,
            heatmap=heatmap_b64,
            timestamp=datetime.now().isoformat(),
            model_info={
                "name": "ResNet50-EyeDisease",
                "version": "2.0.0",
                "framework": "PyTorch"
            }
        )
        
        # Log prediction for metrics
        await metrics_tracker.log_prediction(
            predicted_class, confidence_score, processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

def generate_gradcam_heatmap(model, image_tensor, original_image):
    """Generate Grad-CAM heatmap for model explanation"""
    try:
        # This is a simplified Grad-CAM implementation
        # You might want to use a more sophisticated library like pytorch-grad-cam
        
        # For now, return a placeholder
        # In a real implementation, you would:
        # 1. Hook into the last convolutional layer
        # 2. Compute gradients
        # 3. Generate heatmap
        # 4. Overlay on original image
        
        return None  # Placeholder
        
    except Exception as e:
        logger.error(f"Heatmap generation error: {str(e)}")
        return None

def assess_image_quality(image):
    """Assess image quality"""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        height, width = gray.shape
        
        if width < 224 or height < 224:
            return "Poor - Low Resolution"
        
        # Calculate variance of Laplacian (blur detection)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var > 100:
            return "Excellent"
        elif laplacian_var > 50:
            return "Good"
        elif laplacian_var > 20:
            return "Fair"
        else:
            return "Poor - Blurry Image"
    
    except Exception as e:
        logger.warning(f"Image quality assessment failed: {str(e)}")
        return "Unknown"

# Model management endpoints
@app.get("/api/get-models")
async def get_models():
    """List all available trained models"""
    try:
        models_dir = "models"
        if not os.path.exists(models_dir):
            return {"models": []}
        
        model_files = []
        for filename in os.listdir(models_dir):
            if filename.endswith('.pt'):
                filepath = os.path.join(models_dir, filename)
                stat = os.stat(filepath)
                model_files.append({
                    "name": filename,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return {"models": model_files}
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_metrics():
    """Get model performance metrics"""
    try:
        metrics = await metrics_tracker.get_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=5000,
        reload=True,
        log_level="info"
    )