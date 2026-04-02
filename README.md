# Night Vision Surveillance System using Machine Learning and Computer Vision

## Abstract

This project presents a real-time intelligent surveillance system designed to operate efficiently in low-light environments. The system enhances video frames using night vision techniques and applies deep learning-based object detection for monitoring human, animal, and vehicle activities. It integrates anomaly detection mechanisms to identify unusual events such as loitering, crowd formation, and unexpected object presence. The system provides a user-friendly dashboard for real-time monitoring, alerts, and logs, making it suitable for security and surveillance applications.

---

## 1. Introduction

With the increasing need for automated security systems, traditional surveillance methods are insufficient in handling real-time monitoring and anomaly detection, especially in low-light conditions. This project addresses these challenges by combining computer vision and machine learning techniques to build a smart surveillance system capable of detecting and analyzing activities in real time.

---

## 2. Objectives

* To develop a real-time video surveillance system.
* To enhance video quality in low-light environments.
* To detect and track objects such as humans, animals, and vehicles.
* To identify anomalies such as loitering, crowd formation, and unusual activity.
* To provide a dashboard interface for monitoring alerts and logs.

---

## 3. System Overview

### 3.1 Input Sources

* Laptop camera
* External webcam
* Recorded video files

### 3.2 Processing Pipeline

1. Frame Capture using OpenCV
2. Low-light Enhancement (Night Vision Processing)
3. Object Detection using YOLOv8
4. Object Tracking
5. Mode-based Anomaly Detection
6. Snapshot Storage
7. Event and Log Storage in MongoDB

---

## 4. Modes of Operation

### 4.1 Human Mode

* Loitering Detection
* Crowd Threshold Detection
* Animal Presence Detection

### 4.2 Animal Mode

* Human Presence Detection
* Vehicle Presence Detection
* Animal Spike Detection

---

## 5. Technologies Used

### Backend

* Python
* FastAPI
* OpenCV
* PyTorch
* YOLOv8 (Ultralytics)
* PyMongo

### Frontend

* React (Vite)
* Axios

### Database

* MongoDB

---

## 6. Features

* Real-time video processing
* Night vision enhancement
* Deep learning-based object detection
* Anomaly detection system
* Snapshot capture for critical events
* MongoDB-based event and log storage
* Interactive dashboard with live feed
* Analytics toggle and mode switching

---

## 7. System Architecture

The system follows a single-source processing architecture where one video feed is processed at a time. This ensures stability and avoids concurrency-related issues. The backend handles video processing and data storage, while the frontend dashboard displays live results.

---

## 8. Installation and Setup

### 8.1 Prerequisites

* Python 3.9 or higher
* Node.js (v18 or higher)
* MongoDB installed and running

### 8.2 Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 8.3 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 8.4 Access Application

Open browser and go to:

```
http://localhost:5173
```

---

## 9. Usage Instructions

1. Click **Refresh Cameras** to detect available devices
2. Select a camera OR upload a video file
3. Enable **Analytics**
4. Choose mode (Human / Animal)
5. Monitor live feed, alerts, and logs

---

## 10. Output

* Live annotated video feed
* Object counts (people, animals, vehicles)
* Alerts for anomalies
* Logs for system activity
* Snapshots saved locally

---

## 11. Advantages

* Works in low-light conditions
* Supports multiple input sources
* Real-time anomaly detection
* Simple and stable architecture
* Scalable for future improvements

---

## 12. Limitations

* Single camera processing only
* CPU-based systems may have lower performance
* Rule-based anomaly detection may have limited accuracy

---

## 13. Future Scope

* Multi-camera support
* Advanced tracking algorithms (DeepSORT)
* Model fine-tuning for higher accuracy
* Cloud deployment and remote monitoring

---

## 15. Conclusion

The project successfully demonstrates the integration of machine learning and computer vision techniques for building an intelligent surveillance system. It provides real-time monitoring, anomaly detection, and efficient visualization through a dashboard, making it a practical solution for modern security systems.
The project successfully demonstrates the integration of machine learning and computer vision techniques for building an intelligent surveillance system. It provides real-time monitoring, anomaly detection, and efficient visualization through a dashboard, making it a practical solution for modern security systems.
