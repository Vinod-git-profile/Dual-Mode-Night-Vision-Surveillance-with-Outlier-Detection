import React, { useState, useEffect } from 'react';
import { getEvents } from '../api';

function AlertsPanel() {
  const [events, setEvents] = useState([]);
  
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await getEvents(20);
        setEvents(res.data.events || []);
      } catch (err) {
        console.error('Failed to fetch events:', err);
      }
    };
    
    fetchEvents();
    const interval = setInterval(fetchEvents, 2000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="panel-section">
      <h3>🚨 Alerts</h3>
      {events.length === 0 ? (
        <p style={{color: '#777', fontSize: '13px'}}>No alerts yet</p>
      ) : (
        events.map(event => (
          <div key={event.event_id} className={`alert-item ${event.severity}`}>
            <div style={{fontWeight: 'bold', marginBottom: '5px'}}>
              {event.event_type.toUpperCase().replace('_', ' ')}
            </div>
            <div>{event.description}</div>
            <div className="timestamp">
              {new Date(event.timestamp).toLocaleString()}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default AlertsPanel;
