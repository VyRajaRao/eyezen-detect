"""
Shared image preprocessing utilities.
Used by both inference (app/inference.py) and training scripts.
"""

from __future__ import annotations

from typing import Tuple

import torch
from PIL import Image
from torchvision import transforms

# ImageNet statistics – used for all transfer-learning models
IMAGENET_MEAN: Tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: Tuple[float, float, float] = (0.229, 0.224, 0.225)


def get_inference_transform(image_size: int = 224) -> transforms.Compose:
    """Return a deterministic transform for inference."""
    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )


def get_training_transform(image_size: int = 224, augment: bool = True) -> transforms.Compose:
    """Return a training transform with optional data augmentation."""
    if augment:
        return transforms.Compose(
            [
                transforms.Resize((image_size + 32, image_size + 32)),
                transforms.RandomCrop(image_size),
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
                transforms.ColorJitter(
                    brightness=0.2, contrast=0.2, saturation=0.1, hue=0.05
                ),
                transforms.ToTensor(),
                transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
            ]
        )
    else:
        return transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
            ]
        )


def preprocess_image(image: Image.Image, image_size: int = 224) -> torch.Tensor:
    """Convert a PIL image to a normalised float tensor with a batch dimension."""
    transform = get_inference_transform(image_size)
    return transform(image).unsqueeze(0)  # (1, C, H, W)
