import React, { useEffect, useState } from 'react';

const SnapshotSelector = ({ backendUrl, gpBasicPass, setGpBasicPass, selectedSnapshotId, onChange, userType }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const authHeader = gpBasicPass ? { 'Authorization': 'Basic ' + btoa('gp:' + gpBasicPass) } : {};

  const fetchSnapshots = async () => {
    if (userType !== 'gp') return;
    if (!gpBasicPass) return; // require password to fetch
    try {
      setLoading(true);
      setError('');
      const resp = await fetch(`${backendUrl}/api/snapshots?limit=5`, { headers: { ...authHeader } });
      if (resp.status === 401) {
        setError('Unauthorized. Check GP admin password.');
        setItems([]);
        return;
      }
      if (!resp.ok) throw new Error('Failed to list snapshots');
      const data = await resp.json();
      setItems(Array.isArray(data.items) ? data.items : []);
    } catch (e) {
      setError('Failed to fetch snapshots');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchSnapshots(); }, [gpBasicPass]);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
      <div>
        <label style={{ fontSize: 12, opacity: 0.8, display: 'block' }}>Snapshot</label>
        <select
          value={selectedSnapshotId || 'latest'}
          onChange={(e) => onChange(e.target.value === 'latest' ? null : e.target.value)}
          disabled={loading || (userType === 'gp' && !gpBasicPass)}
          style={{ padding: '8px 10px', borderRadius: 8, background: 'rgba(255,255,255,0.06)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)' }}
        >
          <option value="latest">Latest live</option>
          {items.map((it) => (
            <option key={it.id} value={it.id}>{`${it.as_of_date} • ${it.seq}`}</option>
          ))}
        </select>
      </div>

      {userType === 'gp' && (
        <div>
          {!gpBasicPass && (
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input
                type="password"
                placeholder="Enter GP admin password"
                onChange={(e) => setGpBasicPass(e.target.value)}
                style={{ padding: '8px 10px', borderRadius: 8, background: 'rgba(255,255,255,0.06)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)' }}
              />
              <button onClick={fetchSnapshots} style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.2)', background: 'rgba(0,128,128,0.35)', color: '#fff', cursor: 'pointer' }}>Unlock</button>
            </div>
          )}
          {error && <div style={{ color: '#ff8080', fontSize: 12, marginTop: 4 }}>{error}</div>}
        </div>
      )}
    </div>
  );
};

export default SnapshotSelector;