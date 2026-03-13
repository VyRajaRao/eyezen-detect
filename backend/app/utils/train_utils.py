"""
Model training utilities for PyTorch-based eye disease detection
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Callable, Optional, Tuple
import logging

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms, models
from PIL import Image
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from .preprocess import ImagePreprocessor

logger = logging.getLogger(__name__)

class EyeDiseaseDataset(Dataset):
    """Custom dataset for eye disease images"""
    
    def __init__(self, data_dir: str, transform=None, class_names: List[str] = None):
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.images = []
        self.labels = []
        
        # Auto-detect classes if not provided
        if class_names is None:
            self.class_names = sorted([d.name for d in self.data_dir.iterdir() if d.is_dir()])
        else:
            self.class_names = class_names
        
        self.class_to_idx = {cls_name: idx for idx, cls_name in enumerate(self.class_names)}
        
        # Load all images and labels
        self._load_data()
    
    def _load_data(self):
        """Load all image paths and labels"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        for class_name in self.class_names:
            class_dir = self.data_dir / class_name
            if not class_dir.exists():
                logger.warning(f"Class directory not found: {class_dir}")
                continue
            
            class_idx = self.class_to_idx[class_name]
            
            for img_path in class_dir.iterdir():
                if img_path.suffix.lower() in image_extensions:
                    self.images.append(str(img_path))
                    self.labels.append(class_idx)
        
        logger.info(f"Loaded {len(self.images)} images from {len(self.class_names)} classes")
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]
        label = self.labels[idx]
        
        # Load image
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

class ModelTrainer:
    """PyTorch model trainer for eye disease detection"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.preprocessor = ImagePreprocessor()
        logger.info(f"Using device: {self.device}")
    
    def create_model(self, num_classes: int, architecture: str = "resnet50", pretrained: bool = True) -> nn.Module:
        """Create a CNN model for eye disease classification"""
        
        if architecture == "resnet50":
            model = models.resnet50(pretrained=pretrained)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        
        elif architecture == "efficientnet_b0":
            model = models.efficientnet_b0(pretrained=pretrained)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        
        elif architecture == "vgg16":
            model = models.vgg16(pretrained=pretrained)
            model.classifier[6] = nn.Linear(model.classifier[6].in_features, num_classes)
        
        else:
            raise ValueError(f"Unsupported architecture: {architecture}")
        
        return model.to(self.device)
    
    async def train_model(
        self,
        dataset_name: str,
        epochs: int = 10,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        architecture: str = "resnet50",
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Train a model on the specified dataset"""
        
        try:
            # Load dataset
            dataset_path = f"data/processed/{dataset_name}"
            if not os.path.exists(dataset_path):
                raise FileNotFoundError(f"Dataset not found: {dataset_path}")
            
            # Create dataset
            full_dataset = EyeDiseaseDataset(
                dataset_path,
                transform=self.preprocessor.get_train_transform()
            )
            
            num_classes = len(full_dataset.class_names)
            logger.info(f"Training on {num_classes} classes: {full_dataset.class_names}")
            
            # Split dataset
            train_size = int(0.7 * len(full_dataset))
            val_size = int(0.2 * len(full_dataset))
            test_size = len(full_dataset) - train_size - val_size
            
            train_dataset, val_dataset, test_dataset = random_split(
                full_dataset, [train_size, val_size, test_size]
            )
            
            # Create data loaders
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
            
            # Create model
            model = self.create_model(num_classes, architecture, pretrained=True)
            
            # Loss function and optimizer
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(model.parameters(), lr=learning_rate)
            scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
            
            # Training loop
            best_val_acc = 0.0
            train_losses = []
            val_accuracies = []
            
            for epoch in range(epochs):
                # Training phase
                model.train()
                running_loss = 0.0
                correct_train = 0
                total_train = 0
                
                for batch_idx, (inputs, labels) in enumerate(train_loader):
                    inputs, labels = inputs.to(self.device), labels.to(self.device)
                    
                    optimizer.zero_grad()
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()
                    
                    running_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    total_train += labels.size(0)
                    correct_train += (predicted == labels).sum().item()
                
                # Validation phase
                model.eval()
                correct_val = 0
                total_val = 0
                
                with torch.no_grad():
                    for inputs, labels in val_loader:
                        inputs, labels = inputs.to(self.device), labels.to(self.device)
                        outputs = model(inputs)
                        _, predicted = torch.max(outputs, 1)
                        total_val += labels.size(0)
                        correct_val += (predicted == labels).sum().item()
                
                # Calculate metrics
                train_acc = 100 * correct_train / total_train
                val_acc = 100 * correct_val / total_val
                avg_loss = running_loss / len(train_loader)
                
                train_losses.append(avg_loss)
                val_accuracies.append(val_acc)
                
                logger.info(f'Epoch [{epoch+1}/{epochs}] - Loss: {avg_loss:.4f}, Train Acc: {train_acc:.2f}%, Val Acc: {val_acc:.2f}%')
                
                # Save best model
                if val_acc > best_val_acc:
                    best_val_acc = val_acc
                    best_model_path = f"models/best_model_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
                    os.makedirs("models", exist_ok=True)
                    torch.save(model, best_model_path)
                
                # Update progress callback
                if progress_callback:
                    progress_callback(epoch + 1, train_acc, val_acc, avg_loss)
                
                scheduler.step()
            
            # Save final model
            final_model_path = f"models/model_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
            torch.save(model, final_model_path)
            
            logger.info(f"Training completed. Best validation accuracy: {best_val_acc:.2f}%")
            
            return best_model_path if 'best_model_path' in locals() else final_model_path
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            raise