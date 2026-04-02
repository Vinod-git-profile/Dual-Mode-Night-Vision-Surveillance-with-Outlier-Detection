"""
MongoDB database operations (synchronous)
"""
from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
from app.config import MONGO_URI, MONGO_DB_NAME
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.server_info()
            self.db = self.client[MONGO_DB_NAME]
            
            # Create indexes
            self.db.events.create_index([("timestamp", DESCENDING)])
            self.db.events.create_index([("camera_id", 1)])
            self.db.logs.create_index([("timestamp", DESCENDING)])
            self.db.logs.create_index([("camera_id", 1)])
            
            logger.info(f"Connected to MongoDB: {MONGO_DB_NAME}")
            return True
        except PyMongoError as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def insert_event(self, camera_id: str, mode: str, event_type: str, 
                     severity: str, description: str, snapshot_path: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Insert an event document"""
        try:
            event_doc = {
                "event_id": str(uuid.uuid4()),
                "camera_id": camera_id,
                "mode": mode,
                "event_type": event_type,
                "severity": severity,
                "description": description,
                "snapshot_path": snapshot_path,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow()
            }
            self.db.events.insert_one(event_doc)
            logger.info(f"Event inserted: {event_type}")
            return event_doc["event_id"]
        except PyMongoError as e:
            logger.error(f"Failed to insert event: {e}")
            return None
    
    def insert_log(self, camera_id: str, level: str, message: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Insert a log document"""
        try:
            log_doc = {
                "log_id": str(uuid.uuid4()),
                "camera_id": camera_id,
                "level": level,
                "message": message,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow()
            }
            self.db.logs.insert_one(log_doc)
            return log_doc["log_id"]
        except PyMongoError as e:
            logger.error(f"Failed to insert log: {e}")
            return None
    
    def get_events(self, camera_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get recent events"""
        try:
            query = {}
            if camera_id:
                query["camera_id"] = camera_id
            
            events = list(self.db.events.find(query).sort("timestamp", DESCENDING).limit(limit))
            # Convert ObjectId to string for JSON serialization
            for event in events:
                event["_id"] = str(event["_id"])
            return events
        except PyMongoError as e:
            logger.error(f"Failed to get events: {e}")
            return []
    
    def get_logs(self, camera_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get recent logs"""
        try:
            query = {}
            if camera_id:
                query["camera_id"] = camera_id
            
            logs = list(self.db.logs.find(query).sort("timestamp", DESCENDING).limit(limit))
            # Convert ObjectId to string
            for log in logs:
                log["_id"] = str(log["_id"])
            return logs
        except PyMongoError as e:
            logger.error(f"Failed to get logs: {e}")
            return []

# Global database instance
db = Database()
