"""
Database management for FastAPI backend
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    """Database manager for the FastAPI backend"""
    
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize the database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create datasets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    kaggle_name TEXT,
                    title TEXT,
                    description TEXT,
                    download_date TEXT,
                    processed_date TEXT,
                    status TEXT DEFAULT 'downloaded',
                    num_classes INTEGER,
                    total_images INTEGER,
                    class_distribution TEXT
                )
            ''')
            
            # Create models table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT UNIQUE NOT NULL,
                    architecture TEXT NOT NULL,
                    dataset_name TEXT,
                    created_date TEXT,
                    accuracy REAL,
                    loss REAL,
                    epochs INTEGER,
                    status TEXT DEFAULT 'trained'
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    async def get_datasets(self) -> List[Dict[str, Any]]:
        """Get all datasets from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, kaggle_name, title, description, download_date,
                       processed_date, status, num_classes, total_images, class_distribution
                FROM datasets
                ORDER BY download_date DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            datasets = []
            for row in results:
                dataset = {
                    "name": row[0],
                    "kaggle_name": row[1],
                    "title": row[2],
                    "description": row[3],
                    "download_date": row[4],
                    "processed_date": row[5],
                    "status": row[6],
                    "num_classes": row[7],
                    "total_images": row[8],
                    "class_distribution": json.loads(row[9]) if row[9] else None
                }
                datasets.append(dataset)
            
            return datasets
            
        except Exception as e:
            logger.error(f"Failed to get datasets: {str(e)}")
            return []