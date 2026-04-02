"""
Low-light image enhancement for night vision
"""
import cv2
import numpy as np
from app.config import LOW_LIGHT_THRESHOLD, CLAHE_CLIP_LIMIT, CLAHE_TILE_GRID_SIZE
import logging

logger = logging.getLogger(__name__)

class ImageEnhancer:
    def __init__(self):
        # Create CLAHE object
        self.clahe = cv2.createCLAHE(
            clipLimit=CLAHE_CLIP_LIMIT,
            tileGridSize=CLAHE_TILE_GRID_SIZE
        )
        logger.info("ImageEnhancer initialized with CLAHE")
    
    def is_low_light(self, frame: np.ndarray) -> bool:
        """
        Check if frame is low-light based on average brightness
        """
        # Convert to grayscale and calculate mean
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        return avg_brightness < LOW_LIGHT_THRESHOLD
    
    def enhance(self, frame: np.ndarray) -> np.ndarray:
        """
        Enhance low-light frame using CLAHE in LAB color space
        """
        try:
            # Convert BGR to LAB
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            
            # Split channels
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            l_enhanced = self.clahe.apply(l)
            
            # Merge channels
            lab_enhanced = cv2.merge([l_enhanced, a, b])
            
            # Convert back to BGR
            enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
            
            return enhanced
        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            return frame  # Return original on error
    
    def process(self, frame: np.ndarray) -> tuple[np.ndarray, bool]:
        """
        Process frame: enhance if low-light, return (frame, was_enhanced)
        """
        if self.is_low_light(frame):
            enhanced = self.enhance(frame)
            return enhanced, True
        return frame, False
