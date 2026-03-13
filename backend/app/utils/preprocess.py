"""
Image preprocessing utilities for eye disease detection
"""

import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
        
        # Define transforms for training
        self.train_transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomCrop(target_size),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=20),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Define transforms for inference
        self.inference_transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(target_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def preprocess_for_prediction(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for model prediction"""
        try:
            # Convert numpy array to PIL Image
            if isinstance(image, np.ndarray):
                if image.dtype != np.uint8:
                    image = (image * 255).astype(np.uint8)
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            
            # Ensure RGB format
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Apply preprocessing
            processed = self.enhance_retinal_image(np.array(pil_image))
            
            # Resize to target size
            processed = cv2.resize(processed, self.target_size)
            
            # Normalize to [0, 1]
            processed = processed.astype(np.float32) / 255.0
            
            return processed
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            raise
    
    def enhance_retinal_image(self, image: np.ndarray) -> np.ndarray:
        """Apply retinal-specific image enhancements"""
        try:
            # Convert to LAB color space for better processing
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_channel = clahe.apply(l_channel)
            
            # Merge channels back
            enhanced_lab = cv2.merge([l_channel, a_channel, b_channel])
            enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
            
            # Apply Gaussian blur to reduce noise
            enhanced_rgb = cv2.GaussianBlur(enhanced_rgb, (3, 3), 0)
            
            # Detect and crop circular region (retinal boundary)
            cropped = self.detect_and_crop_retina(enhanced_rgb)
            
            return cropped if cropped is not None else enhanced_rgb
            
        except Exception as e:
            logger.warning(f"Image enhancement failed, using original: {str(e)}")
            return image
    
    def detect_and_crop_retina(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Detect retinal boundary and crop to circular region"""
        try:
            # Convert to grayscale for circle detection
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            
            # Use HoughCircles to detect circular boundary
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=gray.shape[0] // 2,
                param1=50,
                param2=30,
                minRadius=gray.shape[0] // 4,
                maxRadius=gray.shape[0] // 2
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                
                # Take the largest circle
                if len(circles) > 0:
                    x, y, r = circles[0]
                    
                    # Create circular mask
                    mask = np.zeros(gray.shape, dtype=np.uint8)
                    cv2.circle(mask, (x, y), r, 255, -1)
                    
                    # Apply mask to original image
                    result = cv2.bitwise_and(image, image, mask=mask)
                    
                    # Crop to bounding box of circle
                    x1, y1 = max(0, x - r), max(0, y - r)
                    x2, y2 = min(image.shape[1], x + r), min(image.shape[0], y + r)
                    
                    cropped = result[y1:y2, x1:x2]
                    
                    return cropped
            
            return None
            
        except Exception as e:
            logger.warning(f"Retinal boundary detection failed: {str(e)}")
            return None
    
    def get_train_transform(self):
        """Get training data transforms"""
        return self.train_transform
    
    def get_inference_transform(self):
        """Get inference data transforms"""
        return self.inference_transform