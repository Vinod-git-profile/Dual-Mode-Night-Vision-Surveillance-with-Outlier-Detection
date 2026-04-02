"""
Mode-based anomaly detection
"""
import time
from collections import defaultdict, deque
from app.config import (
    LOITER_SECONDS, CROWD_THRESHOLD,
    ANIMAL_SPIKE_THRESHOLD, SPIKE_WINDOW_SECONDS, ANIMAL_BASELINE_SMOOTHING,
    SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH
)
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        # Human mode tracking
        self.track_first_seen = {}  # {track_id: timestamp}
        self.track_positions = defaultdict(list)  # {track_id: [(x, y, time)]}
        
        # Animal mode tracking
        self.animal_counts_window = deque(maxlen=int(SPIKE_WINDOW_SECONDS))
        self.animal_baseline = 0
        
        self.current_mode = "human"
        
    def set_mode(self, mode: str):
        """Set detection mode and reset state"""
        self.current_mode = mode
        self.reset()
        logger.info(f"Anomaly detector mode set to: {mode}")
    
    def detect(self, detections: list, mode: str) -> list:
        """
        Detect anomalies based on mode
        Returns list of anomaly events
        """
        if mode != self.current_mode:
            self.set_mode(mode)
        
        if mode == "human":
            return self._detect_human_anomalies(detections)
        else:
            return self._detect_animal_anomalies(detections)
    
    def _detect_human_anomalies(self, detections: list) -> list:
        """Detect anomalies in HUMAN mode"""
        anomalies = []
        current_time = time.time()
        
        # Count by category
        person_count = sum(1 for d in detections if d['category'] == 'person')
        animal_count = sum(1 for d in detections if d['category'] == 'animal')
        
        # 1. Loitering detection
        for det in detections:
            if det['category'] == 'person' and det.get('track_id') is not None:
                track_id = det['track_id']
                
                # Record first seen time
                if track_id not in self.track_first_seen:
                    self.track_first_seen[track_id] = current_time
                
                # Calculate dwell time
                dwell_time = current_time - self.track_first_seen[track_id]
                
                # Check for loitering
                if dwell_time > LOITER_SECONDS:
                    bbox = det['bbox']
                    cx = (bbox[0] + bbox[2]) / 2
                    cy = (bbox[1] + bbox[3]) / 2
                    
                    anomalies.append({
                        'type': 'loitering',
                        'severity': SEVERITY_MEDIUM,
                        'description': f'Person (ID {track_id}) loitering for {int(dwell_time)}s',
                        'metadata': {
                            'track_id': track_id,
                            'dwell_time': dwell_time,
                            'position': [cx, cy]
                        }
                    })
                    # Reset to avoid continuous alerts
                    self.track_first_seen[track_id] = current_time
        
        # 2. Crowd detection
        if person_count >= CROWD_THRESHOLD:
            anomalies.append({
                'type': 'crowd',
                'severity': SEVERITY_MEDIUM,
                'description': f'Crowd detected: {person_count} people (threshold: {CROWD_THRESHOLD})',
                'metadata': {
                    'person_count': person_count,
                    'threshold': CROWD_THRESHOLD
                }
            })
        
        # 3. Animal presence
        if animal_count > 0:
            anomalies.append({
                'type': 'animal_presence',
                'severity': SEVERITY_LOW,
                'description': f'{animal_count} animal(s) detected in human monitoring area',
                'metadata': {
                    'animal_count': animal_count
                }
            })
        
        # Clean up old tracks
        active_track_ids = {d.get('track_id') for d in detections if d.get('track_id') is not None}
        for track_id in list(self.track_first_seen.keys()):
            if track_id not in active_track_ids:
                del self.track_first_seen[track_id]
        
        return anomalies
    
    def _detect_animal_anomalies(self, detections: list) -> list:
        """Detect anomalies in ANIMAL mode"""
        anomalies = []
        current_time = time.time()
        
        # Count by category
        person_count = sum(1 for d in detections if d['category'] == 'person')
        animal_count = sum(1 for d in detections if d['category'] == 'animal')
        vehicle_count = sum(1 for d in detections if d['category'] == 'vehicle')
        
        # 1. Human presence
        if person_count > 0:
            anomalies.append({
                'type': 'human_presence',
                'severity': SEVERITY_MEDIUM,
                'description': f'{person_count} person(s) detected in animal monitoring area',
                'metadata': {
                    'person_count': person_count
                }
            })
        
        # 2. Vehicle presence
        if vehicle_count > 0:
            anomalies.append({
                'type': 'vehicle_presence',
                'severity': SEVERITY_MEDIUM,
                'description': f'{vehicle_count} vehicle(s) detected in animal monitoring area',
                'metadata': {
                    'vehicle_count': vehicle_count
                }
            })
        
        # 3. Animal count spike
        self.animal_counts_window.append((current_time, animal_count))
        
        # Update baseline (exponential moving average)
        if self.animal_baseline == 0:
            self.animal_baseline = animal_count
        else:
            self.animal_baseline = (ANIMAL_BASELINE_SMOOTHING * self.animal_baseline + 
                                   (1 - ANIMAL_BASELINE_SMOOTHING) * animal_count)
        
        # Check for spike
        if animal_count > self.animal_baseline + ANIMAL_SPIKE_THRESHOLD:
            anomalies.append({
                'type': 'animal_spike',
                'severity': SEVERITY_HIGH,
                'description': f'Animal count spike: {animal_count} (baseline: {int(self.animal_baseline)})',
                'metadata': {
                    'current_count': animal_count,
                    'baseline': self.animal_baseline,
                    'spike_threshold': ANIMAL_SPIKE_THRESHOLD
                }
            })
        
        return anomalies
    
    def reset(self):
        """Reset anomaly detection state"""
        self.track_first_seen.clear()
        self.track_positions.clear()
        self.animal_counts_window.clear()
        self.animal_baseline = 0
        logger.info("Anomaly detector reset")
