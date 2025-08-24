import React from 'react';

const ALLOWLIST = new Set([
  'home.treasury.gov', 'treasury.gov', 'bls.gov', 'download.bls.gov',
  'fred.stlouisfed.org', 'stlouisfed.org', 'bea.gov', 'eia.gov', 'sec.gov',
  'energy.ca.gov', 'cpuc.ca.gov'
]);

const LineageModal = ({ open, onClose, lineage }) => {
  if (!open) return null;

  const items = Array.isArray(lineage) ? lineage : [];

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
      <div style={{ width: 680, maxWidth: '95%', maxHeight: '86%', overflowY: 'auto', background: 'rgba(18,26,24,0.98)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, padding: 18 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 style={{ margin: 0 }}>Data Lineage & Citations</h3>
          <button onClick={onClose} style={{ background: 'transparent', color: '#fff', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 6, padding: '6px 10px', cursor: 'pointer' }}>Close</button>
        </div>
        {items.length === 0 && (
          <div style={{ opacity: 0.8 }}>No lineage available.</div>
        )}
        {items.map((it, idx) => {
          const url = it.url || '';
          let domain = '';
          try { domain = new URL(url).hostname; } catch (e) {}
          const allowed = domain && ALLOWLIST.has(domain);
          return (
            <div key={idx} style={{ padding: '10px 0', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
              <div style={{ fontWeight: 600 }}>{it.title || 'Untitled Source'}</div>
              <div style={{ fontSize: 13, opacity: 0.85 }}>
                <span>{it.publisher || 'Unknown Publisher'}</span>
                {it.series_id ? <span> • Series: {it.series_id}</span> : null}
                {it.accessed_at ? <span> • Accessed: {it.accessed_at}</span> : null}
              </div>
              {allowed && url ? (
                <a href={url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--coastal-primary)' }}>
                  {url}
                </a>
              ) : (
                <div style={{ fontSize: 12, opacity: 0.75 }}>
                  {url ? `Link blocked (domain not allowlisted): ${url}` : 'No URL provided'}
                </div>
              )}
              {Array.isArray(it.transform_chain) && it.transform_chain.length > 0 && (
                <div style={{ marginTop: 6, fontSize: 12, opacity: 0.85 }}>
                  Transformations:
                  <ul style={{ marginTop: 4 }}>
                    {it.transform_chain.map((t, i2) => (
                      <li key={i2}>{t.id}: {t.desc}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LineageModal;