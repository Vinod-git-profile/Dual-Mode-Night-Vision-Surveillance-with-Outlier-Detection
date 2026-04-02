"""
YOLO object detector with CUDA optimization
"""
import torch
import cv2
import numpy as np
from ultralytics import YOLO
from app.config import (
    YOLO_MODEL, YOLO_CONF_THRESHOLD, YOLO_IOU_THRESHOLD,
    PERSON_CLASS_ID, ANIMAL_CLASS_IDS, VEHICLE_CLASS_IDS
)
import logging

logger = logging.getLogger(__name__)

class ObjectDetector:
    def __init__(self):
        self.model = None
        self.device = None
        self.cuda_available = False
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize YOLO model with CUDA if available"""
        try:
            # Check CUDA availability
            self.cuda_available = torch.cuda.is_available()
            self.device = 'cuda:0' if self.cuda_available else 'cpu'
            
            logger.info(f"Initializing YOLO model on {self.device}")
            
            # Load model
            self.model = YOLO(YOLO_MODEL)
            self.model.to(self.device)
            
            if self.cuda_available:
                logger.info(f"CUDA enabled - GPU: {torch.cuda.get_device_name(0)}")
            else:
                logger.warning("CUDA not available - using CPU")
                
        except Exception as e:
            logger.error(f"Failed to initialize YOLO: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> list:
        """
        Detect objects in frame
        Returns list of detections: {bbox, confidence, class_id, class_name, category}
        """
        if self.model is None:
            return []
        
        try:
            # Run inference
            results = self.model(
                frame,
                conf=YOLO_CONF_THRESHOLD,
                iou=YOLO_IOU_THRESHOLD,
                device=self.device,
                verbose=False
            )
            
            detections = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get box coordinates
                    xyxy = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = self.model.names[cls_id]
                    
                    # Categorize detection
                    category = self._categorize_class(cls_id)
                    
                    if category:  # Only include relevant categories
                        detections.append({
                            'bbox': xyxy.tolist(),  # [x1, y1, x2, y2]
                            'confidence': conf,
                            'class_id': cls_id,
                            'class_name': cls_name,
                            'category': category,
                            'track_id': None  # Will be assigned by tracker
                        })
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []
    
    def _categorize_class(self, class_id: int) -> str:
        """Categorize COCO class into person/animal/vehicle"""
        if class_id == PERSON_CLASS_ID:
            return 'person'
        elif class_id in ANIMAL_CLASS_IDS:
            return 'animal'
        elif class_id in VEHICLE_CLASS_IDS:
            return 'vehicle'
        return None
    
    def draw_detections(self, frame: np.ndarray, detections: list) -> np.ndarray:
        """Draw bounding boxes and labels on frame"""
        annotated = frame.copy()
        
        for det in detections:
            bbox = det['bbox']
            x1, y1, x2, y2 = map(int, bbox)
            
            # Color by category
            if det['category'] == 'person':
                color = (0, 255, 255)  # Yellow
            elif det['category'] == 'animal':
                color = (0, 165, 255)  # Orange
            else:
                color = (255, 0, 0)  # Blue for vehicles
            
            # Draw box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det['class_name']}"
            if det.get('track_id') is not None:
                label += f" #{det['track_id']}"
            label += f" {det['confidence']:.2f}"
            
            # Label background
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)
            
            # Label text
            cv2.putText(annotated, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return annotated
