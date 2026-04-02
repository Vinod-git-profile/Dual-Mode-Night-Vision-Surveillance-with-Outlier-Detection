import React from 'react';

function StatsBar({ state }) {
  return (
    <div className="stats-bar">
      <div className="stat">
        👤 People: <span className="stat-value">{state?.person_count || 0}</span>
      </div>
      <div className="stat">
        🐾 Animals: <span className="stat-value">{state?.animal_count || 0}</span>
      </div>
      <div className="stat">
        🚗 Vehicles: <span className="stat-value">{state?.vehicle_count || 0}</span>
      </div>
      {state?.last_event && (
        <div className="stat">
          🚨 Last Event: <span className="stat-value">{state.last_event}</span>
        </div>
      )}
    </div>
  );
}

export default StatsBar;
