"""
Centroid-based object tracker for persistent IDs
"""
import numpy as np
from scipy.spatial import distance
from collections import OrderedDict
from app.config import MAX_TRACK_AGE, MAX_TRACK_DISTANCE
import logging

logger = logging.getLogger(__name__)

class CentroidTracker:
    def __init__(self):
        self.next_object_id = 0
        self.objects = OrderedDict()  # {id: centroid}
        self.disappeared = OrderedDict()  # {id: frame_count}
        
    def register(self, centroid):
        """Register a new object with next available ID"""
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1
    
    def deregister(self, object_id):
        """Remove object from tracking"""
        del self.objects[object_id]
        del self.disappeared[object_id]
    
    def update(self, detections: list) -> list:
        """
        Update tracker with new detections
        Returns detections with track_id assigned
        """
        # If no detections, mark all as disappeared
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                
                # Deregister if disappeared too long
                if self.disappeared[object_id] > MAX_TRACK_AGE:
                    self.deregister(object_id)
            
            return []
        
        # Calculate centroids for current detections
        input_centroids = np.zeros((len(detections), 2), dtype="int")
        for i, det in enumerate(detections):
            bbox = det['bbox']
            cx = int((bbox[0] + bbox[2]) / 2)
            cy = int((bbox[1] + bbox[3]) / 2)
            input_centroids[i] = (cx, cy)
        
        # If no tracked objects yet, register all
        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self.register(input_centroids[i])
                detections[i]['track_id'] = self.next_object_id - 1
        else:
            # Get existing object IDs and centroids
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            
            # Compute distance between existing and new centroids
            D = distance.cdist(np.array(object_centroids), input_centroids)
            
            # Find minimum distance matches
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            # Update matched objects
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                
                # Check if distance is reasonable
                if D[row, col] > MAX_TRACK_DISTANCE:
                    continue
                
                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0
                
                detections[col]['track_id'] = object_id
                
                used_rows.add(row)
                used_cols.add(col)
            
            # Mark disappeared objects
            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                
                if self.disappeared[object_id] > MAX_TRACK_AGE:
                    self.deregister(object_id)
            
            # Register new objects
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)
            for col in unused_cols:
                self.register(input_centroids[col])
                detections[col]['track_id'] = self.next_object_id - 1
        
        return detections
    
    def reset(self):
        """Reset tracker state"""
        self.objects.clear()
        self.disappeared.clear()
        self.next_object_id = 0
        logger.info("Tracker reset")
