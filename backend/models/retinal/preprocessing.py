"""Retinal image preprocessing utilities."""
import numpy as np
from PIL import Image
import io
from pathlib import Path
from typing import Union, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


def validate_image_quality(image_data: Union[bytes, str, Path]) -> Dict[str, Any]:
    """
    Validate retinal image quality before analysis.

    Args:
        image_data: Image as bytes, file path, or Path object

    Returns:
        Validation result dict with is_valid, message, and quality_score
    """
    try:
        # Load image
        if isinstance(image_data, (str, Path)):
            img = Image.open(image_data)
        elif isinstance(image_data, bytes):
            img = Image.open(io.BytesIO(image_data))
        else:
            return {'is_valid': False, 'message': 'Invalid image format', 'quality_score': 0.0}

        # Convert to RGB
        img = img.convert('RGB')

        # Check dimensions
        width, height = img.size
        if width < 224 or height < 224:
            return {
                'is_valid': False,
                'message': f'Image too small ({width}x{height}), minimum 224x224 required',
                'quality_score': 0.0
            }

        # Check if image is too dark or too bright
        img_array = np.array(img)
        mean_brightness = np.mean(img_array)

        if mean_brightness < 30:
            return {
                'is_valid': False,
                'message': 'Image too dark for analysis',
                'quality_score': 0.3
            }

        if mean_brightness > 225:
            return {
                'is_valid': False,
                'message': 'Image overexposed',
                'quality_score': 0.3
            }

        # Calculate quality score
        quality_score = min(1.0, (width * height) / (1024 * 1024))  # Based on resolution
        quality_score *= (1.0 - abs(mean_brightness - 128) / 128)  # Brightness penalty

        return {
            'is_valid': True,
            'message': 'Image quality acceptable',
            'quality_score': float(quality_score),
            'dimensions': (width, height),
            'mean_brightness': float(mean_brightness)
        }

    except Exception as e:
        logger.error(f"Image validation failed: {str(e)}")
        return {
            'is_valid': False,
            'message': f'Validation error: {str(e)}',
            'quality_score': 0.0
        }


def preprocess_retinal_image(image_data: Union[bytes, str, Path, np.ndarray],
                             target_size: tuple = (224, 224)) -> np.ndarray:
    """
    Preprocess retinal image for model input.

    Args:
        image_data: Image as bytes, file path, Path, or numpy array
        target_size: Target image size (height, width)

    Returns:
        Preprocessed image array (1, height, width, 3)
    """
    try:
        # Load image
        if isinstance(image_data, (str, Path)):
            img = Image.open(image_data).convert('RGB')
        elif isinstance(image_data, bytes):
            img = Image.open(io.BytesIO(image_data)).convert('RGB')
        elif isinstance(image_data, np.ndarray):
            if len(image_data.shape) == 2:  # Grayscale
                img = Image.fromarray(image_data).convert('RGB')
            else:
                img = Image.fromarray(image_data.astype('uint8'))
        else:
            img = image_data

        # Resize to target size
        img = img.resize(target_size, Image.Resampling.LANCZOS)

        # Convert to numpy array
        img_array = np.array(img)

        # Normalize to [0, 1]
        img_array = img_array.astype('float32') / 255.0

        # Add batch dimension
        if len(img_array.shape) == 3:
            img_array = np.expand_dims(img_array, axis=0)

        logger.debug(f"Image preprocessed: shape={img_array.shape}, dtype={img_array.dtype}")

        return img_array

    except Exception as e:
        logger.error(f"Image preprocessing failed: {str(e)}")
        raise
