import React, { useState } from 'react';
import SnapshotSelector from './SnapshotSelector';

const DownloadCenter = ({ userType }) => {
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  const [gpBasicPass, setGpBasicPass] = useState('');
  const [selectedSnapshotId, setSelectedSnapshotId] = useState(null);
  const [busy, setBusy] = useState(false);
  const isGp = userType === 'gp';

  const authHeader = gpBasicPass ? { 'Authorization': 'Basic ' + btoa('gp:' + gpBasicPass) } : {};

  const downloadBlob = async (resp, fallbackName) => {
    const blob = await resp.blob();
    const cd = resp.headers.get('Content-Disposition') || '';
    const match = cd.match(/filename="?([^";]+)"?/);
    const filename = match ? match[1] : fallbackName;
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename; document.body.appendChild(a); a.click();
    document.body.removeChild(a); URL.revokeObjectURL(url);
  };

  const handleExportExcel = async () => {
    if (!isGp) return;
    if (!gpBasicPass) { alert('Enter GP admin password to unlock exports.'); return; }
    setBusy(true);
    try {
      const qs = selectedSnapshotId ? `?snapshot_id=${encodeURIComponent(selectedSnapshotId)}` : '';
      const resp = await fetch(`${backendUrl}/api/export/excel${qs}`, { method: 'GET', headers: { ...authHeader } });
      if (!resp.ok) throw new Error('Excel export failed');
      await downloadBlob(resp, 'Coastal_Excel_Analytics.xlsx');
    } catch (e) {
      console.error(e);
      alert('Excel export failed');
    } finally { setBusy(false); }
  };

  const handleExportExecSummary = async () => {
    if (!isGp) return;
    if (!gpBasicPass) { alert('Enter GP admin password to unlock exports.'); return; }
    setBusy(true);
    try {
      const resp = await fetch(`${backendUrl}/api/export/executive-summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeader },
        body: JSON.stringify({})
      });
      if (!resp.ok) throw new Error('Executive summary export failed');
      await downloadBlob(resp, 'Executive_Summary.pdf');
    } catch (e) {
      console.error(e);
      alert('Executive Summary export failed');
    } finally { setBusy(false); }
  };

  const handleExportPitch = async () => {
    if (!isGp) return;
    if (!gpBasicPass) { alert('Enter GP admin password to unlock exports.'); return; }
    setBusy(true);
    try {
      const resp = await fetch(`${backendUrl}/api/export/pitch-deck`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeader },
        body: JSON.stringify({ format: 'pptx' })
      });
      if (!resp.ok) throw new Error('Pitch deck export failed');
      await downloadBlob(resp, 'Coastal_Oak_Pitch.pptx');
    } catch (e) {
      console.error(e);
      alert('Pitch deck export failed');
    } finally { setBusy(false); }
  };

  if (!isGp) {
    return (
      <div className="excel-container" style={{ padding: '20px' }}>
        <div style={{ textAlign: 'center', color: 'white', padding: '60px' }}>
          <div style={{ fontSize: '1.2rem', marginBottom: 10 }}>Restricted</div>
          <div style={{ fontSize: '0.95rem', opacity: 0.8 }}>Downloads are restricted to General Partners only.</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ color: 'var(--ink, #ECF1EF)', marginBottom: 8 }}>Downloads</h2>
      <p style={{ color: 'var(--ink_muted, #A7B2AF)', marginBottom: 20 }}>Export institutional artifacts. Use the snapshot selector to bind exports to a specific version.</p>

      <div style={{ display: 'flex', gap: 16, alignItems: 'center', marginBottom: 16, flexWrap: 'wrap' }}>
        <SnapshotSelector
          backendUrl={backendUrl}
          gpBasicPass={gpBasicPass}
          setGpBasicPass={setGpBasicPass}
          selectedSnapshotId={selectedSnapshotId}
          onChange={(id) => setSelectedSnapshotId(id)}
          userType={userType}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
        <div style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 14, padding: 16 }}>
          <h4 style={{ marginBottom: 8 }}>Executive Summary (PDF)</h4>
          <p style={{ opacity: 0.8, fontSize: 14 }}>Branded one-pager with KPIs and sources.</p>
          <button disabled={busy} onClick={handleExportExecSummary} className="export-button" style={{ marginTop: 8 }}>Download PDF</button>
        </div>
        <div style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 14, padding: 16 }}>
          <h4 style={{ marginBottom: 8 }}>Pitch Deck (PPTX)</h4>
          <p style={{ opacity: 0.8, fontSize: 14 }}>Auto-generated PPTX with KPIs and Sources & Methods.</p>
          <button disabled={busy} onClick={handleExportPitch} className="export-button" style={{ marginTop: 8 }}>Download PPTX</button>
        </div>
        <div style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 14, padding: 16 }}>
          <h4 style={{ marginBottom: 8 }}>Excel Model</h4>
          <p style={{ opacity: 0.8, fontSize: 14 }}>Versioned Excel with Summary, Deals, KPIs, Lineage sheets.</p>
          <button disabled={busy} onClick={handleExportExcel} className="export-button" style={{ marginTop: 8 }}>Download XLSX</button>
        </div>
      </div>
    </div>
  );
};

export default DownloadCenter;