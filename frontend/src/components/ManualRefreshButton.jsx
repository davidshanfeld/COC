import React from 'react';

const ManualRefreshButton = ({ disabled, onRefresh, tooltip }) => {
  return (
    <div style={{ display: 'inline-block', position: 'relative' }}>
      <button
        onClick={onRefresh}
        disabled={disabled}
        style={{
          padding: '8px 14px',
          borderRadius: 8,
          background: disabled ? 'rgba(255,255,255,0.1)' : 'rgba(0,128,128,0.35)',
          border: '1px solid rgba(255,255,255,0.2)',
          color: 'white',
          cursor: disabled ? 'not-allowed' : 'pointer'
        }}
      >
        Refresh (Create Snapshot)
      </button>
      {disabled && tooltip && (
        <div style={{ position: 'absolute', top: '110%', left: 0, background: 'rgba(0,0,0,0.7)', color: '#fff', padding: '6px 8px', borderRadius: 6, fontSize: 12, width: 240 }}>
          {tooltip}
        </div>
      )}
    </div>
  );
};

export default ManualRefreshButton;