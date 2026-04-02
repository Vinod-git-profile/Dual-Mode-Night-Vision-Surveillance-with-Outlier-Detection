import React from 'react';
import { setAnalytics, setMode } from '../api';

function ControlsPanel({ state }) {
  const handleAnalytics = async (e) => {
    try {
      await setAnalytics(e.target.checked);
    } catch (err) {
      console.error('Failed to toggle analytics:', err);
    }
  };
  
  const handleMode = async (e) => {
    try {
      await setMode(e.target.value);
    } catch (err) {
      console.error('Failed to set mode:', err);
    }
  };
  
  return (
    <div className="controls-panel">
      <div className="control-group">
        <label>Mode:</label>
        <select className="select" value={state?.mode || 'human'} onChange={handleMode}>
          <option value="human">Human Security</option>
          <option value="animal">Animal Monitoring</option>
        </select>
      </div>
      <div className="control-group">
        <label>Analytics:</label>
        <label className="toggle">
          <input type="checkbox" checked={state?.analytics_enabled || false} onChange={handleAnalytics} />
          <span className="slider"></span>
        </label>
      </div>
      <div className="control-group">
        <span className={`cuda-indicator ${state?.cuda_available ? '' : 'unavailable'}`}>
          {state?.cuda_available ? '⚡ CUDA' : '❌ CPU'}
        </span>
      </div>
    </div>
  );
}

export default ControlsPanel;
