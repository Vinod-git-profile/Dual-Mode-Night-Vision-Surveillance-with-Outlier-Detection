"""
Single-source video processing engine
"""
import cv2
import numpy as np
import threading
import time
from datetime import datetime
from pathlib import Path
from app.detector import ObjectDetector
from app.enhancement import ImageEnhancer
from app.tracker import CentroidTracker
from app.anomaly import AnomalyDetector
from app.database import db
from app.config import (
    UI_FPS, AI_FPS, SNAPSHOTS_DIR, STREAM_QUALITY, STREAM_MAX_WIDTH
)
import logging

logger = logging.getLogger(__name__)

class VideoEngine:
    def __init__(self):
        # Components
        self.detector = ObjectDetector()
        self.enhancer = ImageEnhancer()
        self.tracker = CentroidTracker()
        self.anomaly_detector = AnomalyDetector()
        
        # Source
        self.cap = None
        self.source_type = None
        self.source_value = None
        
        # State
        self.is_running = False
        self.analytics_enabled = False
        self.current_mode = "human"
        
        # Processing
        self.current_frame = None
        self.annotated_frame = None
        self.lock = threading.Lock()
        
        # Stats
        self.person_count = 0
        self.animal_count = 0
        self.vehicle_count = 0
        self.detections = []
        self.last_event = None
        self.last_event_time = None
        
        # Thread
        self.thread = None
        self.stop_signal = False
        
        # Camera ID
        self.camera_id = "CAM-1"
        
        logger.info("VideoEngine initialized")
    
    def start_source(self, source_type: str, source_value):
        """Start video source"""
        self.stop()
        
        try:
            if source_type == "camera":
                self.cap = cv2.VideoCapture(source_value, cv2.CAP_DSHOW)
            else:
                self.cap = cv2.VideoCapture(source_value)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open source: {source_type} {source_value}")
                return False
            
            self.source_type = source_type
            self.source_value = source_value
            self.is_running = True
            self.stop_signal = False
            
            # Start processing thread
            self.thread = threading.Thread(target=self._process_loop, daemon=True)
            self.thread.start()
            
            logger.info(f"Source started: {source_type} {source_value}")
            db.insert_log(self.camera_id, "info", f"Source started: {source_type} {source_value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start source: {e}")
            return False
    
    def stop(self):
        """Stop video source"""
        self.stop_signal = True
        self.is_running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        with self.lock:
            self.current_frame = None
            self.annotated_frame = None
            self.detections = []
            self.person_count = 0
            self.animal_count = 0
            self.vehicle_count = 0
        
        logger.info("Source stopped")
    
    def set_analytics(self, enabled: bool):
        """Enable or disable analytics"""
        with self.lock:
            self.analytics_enabled = enabled
            
            if not enabled:
                # Flush UI - clear detections and counts
                self.detections = []
                self.annotated_frame = None
                self.person_count = 0
                self.animal_count = 0
                self.vehicle_count = 0
                self.tracker.reset()
                self.anomaly_detector.reset()
        
        logger.info(f"Analytics {'enabled' if enabled else 'disabled'}")
        db.insert_log(self.camera_id, "info", f"Analytics {'enabled' if enabled else 'disabled'}")
    
    def set_mode(self, mode: str):
        """Set monitoring mode"""
        with self.lock:
            self.current_mode = mode
            self.anomaly_detector.set_mode(mode)
        
        logger.info(f"Mode set to: {mode}")
        db.insert_log(self.camera_id, "info", f"Mode set to: {mode}")
    
    def get_frame(self):
        """Get current frame for streaming"""
        with self.lock:
            if self.analytics_enabled and self.annotated_frame is not None:
                frame = self.annotated_frame.copy()
            elif self.current_frame is not None:
                frame = self.current_frame.copy()
            else:
                frame = None
        
        return frame
    
    def get_state(self):
        """Get current engine state"""
        with self.lock:
            state = {
                'source_type': self.source_type,
                'source_value': str(self.source_value) if self.source_value is not None else None,
                'mode': self.current_mode,
                'analytics_enabled': self.analytics_enabled,
                'cuda_available': self.detector.cuda_available,
                'is_running': self.is_running,
                'person_count': self.person_count,
                'animal_count': self.animal_count,
                'vehicle_count': self.vehicle_count,
                'last_event': self.last_event,
                'last_event_time': self.last_event_time
            }
        return state
    
    def _process_loop(self):
        """Main processing loop"""
        ui_interval = 1.0 / UI_FPS
        ai_interval = 1.0 / AI_FPS
        last_ai_time = 0
        consecutive_failures = 0
        max_failures = 30  # Stop after 30 consecutive failures (~3 seconds)
        
        while not self.stop_signal and self.is_running:
            loop_start = time.time()
            
            # Read frame
            ret, frame = self.cap.read()
            if not ret:
                consecutive_failures += 1
                logger.warning(f"Failed to read frame (attempt {consecutive_failures}/{max_failures})")
                
                # If video file ended or camera disconnected
                if consecutive_failures >= max_failures:
                    logger.info("Video source ended or disconnected, stopping...")
                    self.stop()
                    break
                
                time.sleep(0.1)
                continue
            
            # Reset failure counter on successful read
            consecutive_failures = 0
            
            # Resize if too large
            if frame.shape[1] > STREAM_MAX_WIDTH:
                scale = STREAM_MAX_WIDTH / frame.shape[1]
                frame = cv2.resize(frame, None, fx=scale, fy=scale)
            
            # Store current frame
            with self.lock:
                self.current_frame = frame.copy()
            
            # AI processing at lower FPS
            current_time = time.time()
            if current_time - last_ai_time >= ai_interval:
                last_ai_time = current_time
                
                if self.analytics_enabled:
                    self._process_analytics(frame)
            
            # Sleep to maintain UI FPS
            elapsed = time.time() - loop_start
            sleep_time = max(0, ui_interval - elapsed)
            time.sleep(sleep_time)
    
    def _process_analytics(self, frame: np.ndarray):
        """Process frame for analytics"""
        try:
            # Enhancement
            enhanced, was_enhanced = self.enhancer.process(frame)
            
            # Detection
            detections = self.detector.detect(enhanced)
            
            # Tracking
            detections = self.tracker.update(detections)
            
            # Count by category
            person_count = sum(1 for d in detections if d['category'] == 'person')
            animal_count = sum(1 for d in detections if d['category'] == 'animal')
            vehicle_count = sum(1 for d in detections if d['category'] == 'vehicle')
            
            # Anomaly detection
            mode = None
            with self.lock:
                mode = self.current_mode
            
            anomalies = self.anomaly_detector.detect(detections, mode)
            
            # Handle anomalies
            if anomalies:
                self._handle_anomalies(anomalies, enhanced, detections)
            
            # Draw detections
            annotated = self.detector.draw_detections(enhanced, detections)
            
            # Update state
            with self.lock:
                self.detections = detections
                self.person_count = person_count
                self.animal_count = animal_count
                self.vehicle_count = vehicle_count
                self.annotated_frame = annotated
                
        except Exception as e:
            logger.error(f"Analytics processing failed: {e}")
    
    def _handle_anomalies(self, anomalies: list, frame: np.ndarray, detections: list):
        """Handle detected anomalies"""
        for anomaly in anomalies:
            try:
                # Save snapshot
                snapshot_path = self._save_snapshot(frame, detections, anomaly['type'])
                
                # Insert event to MongoDB
                with self.lock:
                    mode = self.current_mode
                
                event_id = db.insert_event(
                    camera_id=self.camera_id,
                    mode=mode,
                    event_type=anomaly['type'],
                    severity=anomaly['severity'],
                    description=anomaly['description'],
                    snapshot_path=snapshot_path,
                    metadata=anomaly['metadata']
                )
                
                # Insert log
                db.insert_log(
                    camera_id=self.camera_id,
                    level='alert',
                    message=f"Anomaly detected: {anomaly['type']} - {anomaly['description']}",
                    metadata=anomaly['metadata']
                )
                
                # Update last event
                with self.lock:
                    self.last_event = anomaly['type']
                    self.last_event_time = datetime.utcnow().isoformat()
                
                logger.info(f"Anomaly handled: {anomaly['type']}")
                
            except Exception as e:
                logger.error(f"Failed to handle anomaly: {e}")
    
    def _save_snapshot(self, frame: np.ndarray, detections: list, event_type: str) -> str:
        """Save snapshot with detections"""
        try:
            # Create date-based folder
            date_str = datetime.now().strftime("%Y%m%d")
            snapshot_dir = SNAPSHOTS_DIR / date_str
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.camera_id}_{event_type}_{timestamp}.jpg"
            filepath = snapshot_dir / filename
            
            # Draw detections on frame
            annotated = self.detector.draw_detections(frame, detections)
            
            # Save
            cv2.imwrite(str(filepath), annotated)
            
            logger.info(f"Snapshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            return None

# Global engine instance
engine = VideoEngine()
