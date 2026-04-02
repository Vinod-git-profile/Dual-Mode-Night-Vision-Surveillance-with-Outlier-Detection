import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import VideoPanel from './components/VideoPanel';
import ControlsPanel from './components/ControlsPanel';
import StatsBar from './components/StatsBar';
import AlertsPanel from './components/AlertsPanel';
import LogsPanel from './components/LogsPanel';
import { getVideoState } from './api';

function App() {
  const [state, setState] = useState(null);
  
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await getVideoState();
        setState(res.data);
      } catch (err) {
        console.error('Failed to fetch state:', err);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="app">
      <Sidebar />
      <div className="main-content">
        <VideoPanel />
        <StatsBar state={state} />
        <ControlsPanel state={state} />
      </div>
      <div className="right-panel">
        <AlertsPanel />
        <LogsPanel />
      </div>
    </div>
  );
}

export default App;
