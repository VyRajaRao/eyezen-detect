"""
Kaggle dataset management utilities
"""

import os
import zipfile
import shutil
from typing import List, Dict, Optional
import logging
from pathlib import Path

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False
    logging.warning("Kaggle API not available. Install with: pip install kaggle")

logger = logging.getLogger(__name__)

class KaggleDatasetManager:
    def __init__(self):
        self.api = None
        self.data_dir = Path("data")
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        if KAGGLE_AVAILABLE:
            try:
                self.api = KaggleApi()
                self.api.authenticate()
                logger.info("Kaggle API authenticated successfully")
            except Exception as e:
                logger.error(f"Kaggle API authentication failed: {str(e)}")
                self.api = None
    
    def is_configured(self) -> bool:
        """Check if Kaggle API is properly configured"""
        return self.api is not None and KAGGLE_AVAILABLE
    
    async def search_datasets(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for datasets on Kaggle"""
        if not self.is_configured():
            raise Exception("Kaggle API not configured")
        
        try:
            datasets = self.api.dataset_list(search=query, max_size=max_results)
            
            results = []
            for dataset in datasets:
                results.append({
                    "name": f"{dataset.creatorName}/{dataset.slug}",
                    "title": dataset.title,
                    "size": dataset.totalBytes,
                    "download_count": dataset.downloadCount,
                    "last_updated": str(dataset.lastUpdated),
                    "description": dataset.subtitle
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Dataset search failed: {str(e)}")
            raise
    
    async def download_and_process_dataset(self, dataset_name: str, description: Optional[str] = None):
        """Download and process a Kaggle dataset"""
        if not self.is_configured():
            raise Exception("Kaggle API not configured")
        
        try:
            logger.info(f"Downloading dataset: {dataset_name}")
            
            # Create dataset-specific directory
            dataset_slug = dataset_name.split('/')[-1]
            dataset_raw_dir = self.raw_dir / dataset_slug
            dataset_processed_dir = self.processed_dir / dataset_slug
            
            dataset_raw_dir.mkdir(exist_ok=True)
            dataset_processed_dir.mkdir(exist_ok=True)
            
            # Download dataset
            self.api.dataset_download_files(
                dataset_name, 
                path=str(dataset_raw_dir),
                unzip=True
            )
            
            logger.info(f"Dataset downloaded to: {dataset_raw_dir}")
            
            # Process the dataset
            await self._process_dataset(dataset_raw_dir, dataset_processed_dir)
            
            logger.info(f"Dataset processed and saved to: {dataset_processed_dir}")
            
            return str(dataset_processed_dir)
            
        except Exception as e:
            logger.error(f"Dataset download/processing failed: {str(e)}")
            raise
    
    async def _process_dataset(self, raw_dir: Path, processed_dir: Path):
        """Process raw dataset into training format"""
        try:
            # This is a generic processor - you might need to customize based on dataset structure
            
            # Look for common dataset structures
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
            
            # Find all image files
            image_files = []
            for ext in image_extensions:
                image_files.extend(raw_dir.rglob(f'*{ext}'))
                image_files.extend(raw_dir.rglob(f'*{ext.upper()}'))
            
            if not image_files:
                logger.warning("No image files found in dataset")
                return
            
            # Try to organize by directory structure (common in Kaggle datasets)
            class_dirs = {}
            
            for img_file in image_files:
                # Get the parent directory as potential class name
                parent_dir = img_file.parent.name
                
                # Skip common non-class directories
                if parent_dir.lower() in ['train', 'test', 'val', 'validation', 'images']:
                    # Look one level up
                    if img_file.parent.parent != raw_dir:
                        parent_dir = img_file.parent.parent.name
                    else:
                        parent_dir = 'unknown'
                
                if parent_dir not in class_dirs:
                    class_dirs[parent_dir] = []
                class_dirs[parent_dir].append(img_file)
            
            # Copy files to processed directory with class structure
            for class_name, files in class_dirs.items():
                class_dir = processed_dir / class_name
                class_dir.mkdir(exist_ok=True)
                
                for i, src_file in enumerate(files):
                    # Create a clean filename
                    dst_file = class_dir / f"{class_name}_{i:06d}{src_file.suffix}"
                    shutil.copy2(src_file, dst_file)
                
                logger.info(f"Processed {len(files)} images for class: {class_name}")
            
        except Exception as e:
            logger.error(f"Dataset processing failed: {str(e)}")
            raise
    
    def get_available_datasets(self) -> List[str]:
        """Get list of locally available processed datasets"""
        if not self.processed_dir.exists():
            return []
        
        datasets = []
        for item in self.processed_dir.iterdir():
            if item.is_dir():
                datasets.append(item.name)
        
        return datasets
    
    def get_dataset_info(self, dataset_name: str) -> Dict:
        """Get information about a local dataset"""
        dataset_dir = self.processed_dir / dataset_name
        
        if not dataset_dir.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_name}")
        
        info = {
            "name": dataset_name,
            "path": str(dataset_dir),
            "classes": [],
            "total_images": 0
        }
        
        for class_dir in dataset_dir.iterdir():
            if class_dir.is_dir():
                image_count = len(list(class_dir.glob('*')))
                info["classes"].append({
                    "name": class_dir.name,
                    "count": image_count
                })
                info["total_images"] += image_count
        
        return info