import React, { useState, useEffect } from 'react';
import { getLogs } from '../api';

function LogsPanel() {
  const [logs, setLogs] = useState([]);
  
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await getLogs(30);
        setLogs(res.data.logs || []);
      } catch (err) {
        console.error('Failed to fetch logs:', err);
      }
    };
    
    fetchLogs();
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="panel-section">
      <h3>📋 System Logs</h3>
      {logs.length === 0 ? (
        <p style={{color: '#777', fontSize: '13px'}}>No logs yet</p>
      ) : (
        logs.map(log => (
          <div key={log.log_id} className={`log-item ${log.level}`}>
            <span style={{fontWeight: 'bold'}}>[{log.level.toUpperCase()}]</span> {log.message}
            <div className="timestamp">
              {new Date(log.timestamp).toLocaleString()}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default LogsPanel;
