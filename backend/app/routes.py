"""
API routes for Night Vision Surveillance
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from pathlib import Path
import cv2
import shutil
from app.engine import engine
from app.models import (
    SourceRequest, AnalyticsRequest, ModeRequest,
    VideoState, CameraDevice, EventsResponse, LogsResponse, Event, Log
)
from app.database import db
from app.config import UPLOADS_DIR
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Video streaming
@router.get("/video/stream")
async def video_stream():
    """MJPEG video stream"""
    import numpy as np
    import time
    
    def generate():
        while True:
            frame = engine.get_frame()
            if frame is not None:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    time.sleep(0.1)
            else:
                # Send placeholder black frame with text
                black = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(black, 'No Video Source', (180, 230), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(black, 'Click Camera or Upload Video', (120, 270), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
                ret, buffer = cv2.imencode('.jpg', black, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                time.sleep(0.1)
    
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.get("/video/state", response_model=VideoState)
async def get_video_state():
    """Get current video state"""
    state = engine.get_state()
    return VideoState(**state)

# Device management
@router.get("/devices/cameras")
async def list_cameras():
    """List available cameras"""
    cameras = []
    for i in range(10):  # Check first 10 indices
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            cameras.append({
                'index': i,
                'name': f'Camera {i}',
                'available': True
            })
            cap.release()
    
    return {'cameras': cameras}

# Control endpoints
@router.post("/control/source")
async def set_source(request: SourceRequest):
    """Set video source"""
    success = engine.start_source(request.type, request.value)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to start source")
    return {'status': 'success', 'source': request.dict()}

@router.post("/control/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload video file"""
    try:
        # Save uploaded file
        UPLOADS_DIR.mkdir(exist_ok=True)
        filepath = UPLOADS_DIR / file.filename
        
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        # Set as source
        success = engine.start_source("file", str(filepath))
        if not success:
            raise HTTPException(status_code=400, detail="Failed to start video")
        
        return {'status': 'success', 'filename': file.filename, 'path': str(filepath)}
    
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/control/analytics")
async def set_analytics(request: AnalyticsRequest):
    """Enable/disable analytics"""
    engine.set_analytics(request.enabled)
    return {'status': 'success', 'analytics_enabled': request.enabled}

@router.post("/control/mode")
async def set_mode(request: ModeRequest):
    """Set monitoring mode"""
    engine.set_mode(request.mode)
    return {'status': 'success', 'mode': request.mode}

# Data endpoints
@router.get("/data/events", response_model=EventsResponse)
async def get_events(limit: int = Query(50, ge=1, le=500)):
    """Get recent events"""
    events_data = db.get_events(limit=limit)
    events = [Event(**event) for event in events_data]
    return EventsResponse(events=events, total=len(events))

@router.get("/data/logs", response_model=LogsResponse)
async def get_logs(limit: int = Query(100, ge=1, le=1000)):
    """Get recent logs"""
    logs_data = db.get_logs(limit=limit)
    logs = [Log(**log) for log in logs_data]
    return LogsResponse(logs=logs, total=len(logs))
