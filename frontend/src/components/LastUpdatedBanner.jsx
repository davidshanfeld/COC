import React from 'react';

const LastUpdatedBanner = ({ lastUpdatedIso, snapshotId, onViewLineage }) => {
  if (!lastUpdatedIso || !snapshotId) return null;
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '10px 14px',
      borderRadius: 8,
      background: 'rgba(255,255,255,0.06)',
      border: '1px solid rgba(255,255,255,0.1)',
      marginBottom: 12,
      fontSize: '0.9rem'
    }}>
      <div>
        <span style={{opacity: 0.8}}>Last updated:</span> <strong>{lastUpdatedIso}</strong>
        <span style={{marginLeft: 12, opacity: 0.8}}>Snapshot:</span> <strong>{snapshotId}</strong>
      </div>
      <button
        onClick={onViewLineage}
        style={{
          padding: '6px 10px',
          borderRadius: 6,
          background: 'rgba(0,128,128,0.3)',
          border: '1px solid var(--coastal-primary)',
          color: 'white',
          cursor: 'pointer'
        }}
      >
        View Lineage
      </button>
    </div>
  );
};

export default LastUpdatedBanner;