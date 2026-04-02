import React, { useState, useEffect } from 'react';
import { getCameras, setSource, uploadVideo } from '../api';

function Sidebar() {
  const [cameras, setCameras] = useState([]);
  
  const refreshCameras = async () => {
    try {
      const res = await getCameras();
      setCameras(res.data.cameras || []);
    } catch (err) {
      console.error('Failed to get cameras:', err);
    }
  };
  
  useEffect(() => {
    refreshCameras();
  }, []);
  
  const handleCamera = async (index) => {
    try {
      await setSource('camera', index);
      alert(`Camera ${index} started`);
    } catch (err) {
      alert('Failed to start camera');
    }
  };
  
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      await uploadVideo(file);
      alert('Video uploaded and started');
    } catch (err) {
      alert('Failed to upload video');
    }
  };
  
  return (
    <div className="sidebar">
      <h2>🎥 Sources</h2>
      <label className="btn">
        + Add Video File
        <input type="file" accept="video/*" onChange={handleFileUpload} className="file-input" />
      </label>
      <button className="btn btn-secondary" onClick={refreshCameras}>
        🔄 Refresh Cameras
      </button>
      <div className="camera-list">
        <h3 style={{fontSize: '14px', marginBottom: '10px', color: '#aaa'}}>Available Cameras</h3>
        {cameras.map(cam => (
          <div key={cam.index} className="camera-item" onClick={() => handleCamera(cam.index)}>
            {cam.name}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Sidebar;
