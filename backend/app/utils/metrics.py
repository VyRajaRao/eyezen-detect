"""
Metrics tracking and monitoring utilities
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MetricsTracker:
    """Track and store model performance metrics"""
    
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for metrics storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    predicted_class TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    processing_time REAL NOT NULL,
                    image_quality TEXT,
                    model_version TEXT
                )
            ''')
            
            # Create training_runs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    dataset_name TEXT NOT NULL,
                    model_architecture TEXT NOT NULL,
                    epochs INTEGER NOT NULL,
                    batch_size INTEGER NOT NULL,
                    learning_rate REAL NOT NULL,
                    final_train_accuracy REAL,
                    final_val_accuracy REAL,
                    best_val_accuracy REAL,
                    model_path TEXT,
                    training_time REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Metrics database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    async def log_prediction(
        self,
        predicted_class: str,
        confidence: float,
        processing_time: float,
        image_quality: str = "Unknown",
        model_version: str = "2.0.0"
    ):
        """Log a prediction result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predictions 
                (timestamp, predicted_class, confidence, processing_time, image_quality, model_version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                predicted_class,
                confidence,
                processing_time,
                image_quality,
                model_version
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to log prediction: {str(e)}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metrics = {}
            
            # Prediction statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_predictions,
                    AVG(confidence) as avg_confidence,
                    AVG(processing_time) as avg_processing_time,
                    predicted_class,
                    COUNT(*) as class_count
                FROM predictions 
                GROUP BY predicted_class
                ORDER BY class_count DESC
            ''')
            
            prediction_stats = cursor.fetchall()
            
            metrics["prediction_summary"] = {
                "total_predictions": sum(row[4] for row in prediction_stats) if prediction_stats else 0,
                "average_confidence": prediction_stats[0][1] if prediction_stats else 0,
                "average_processing_time": prediction_stats[0][2] if prediction_stats else 0,
                "class_distribution": [
                    {"class": row[3], "count": row[4]} for row in prediction_stats
                ]
            }
            
            conn.close()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            return {}