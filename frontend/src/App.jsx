import React, { useState, useEffect, useRef, useCallback } from 'react';
import BlueprintViewer from './components/BlueprintViewer';
import CostedBOQChecklist from './components/CostedBOQChecklist';
import TradeAccordion from './components/TradeAccordion';
import RebarOptimizerView from './components/RebarOptimizerView';
import RightPanel from './components/RightPanel';

export default function App() {
  const [data, setData]               = useState(null);
  const [rebarData, setRebarData]     = useState(null);
  const [loading, setLoading]         = useState(false);
  const [banner, setBanner]           = useState(null);
  const [drawingsList, setDrawingsList] = useState(['sample_structural_plan.pdf']);
  const [drawing, setDrawing]         = useState('sample_structural_plan.pdf');
  const [boqView, setBoqView]         = useState('checklist');
  const [selectedElement, setSelectedElement] = useState(null);
  const [tradeTotals, setTradeTotals] = useState({});

  const fileInputRef = useRef(null);

  // Load saved sessions to populate drawing dropdown
  const loadSavedSessions = async () => {
    try {
      const res = await fetch('/api/v1/sessions');
      const json = await res.json();
      if (json.status === 'success' && Array.isArray(json.sessions) && json.sessions.length > 0) {
        const names = json.sessions.map(s => s.drawing_name).filter(Boolean);
        const unique = Array.from(new Set(names));
        if (unique.length > 0) {
          setDrawingsList(unique);
          setDrawing(unique[0]);
        }
      }
    } catch {
      // Ignore network fallback
    }
  };

  useEffect(() => {
    loadSavedSessions();
  }, []);

  // ── Core Takeoff Fetch ──────────────────────────────────────────────────
  const fetchTakeoff = async (uploadedFile = null) => {
    setLoading(true);
    setBanner(null);

    try {
      let reqOptions = { method: 'POST' };

      if (uploadedFile) {
        const formData = new FormData();
        formData.append('file', uploadedFile);
        reqOptions.body = formData;
      }

      const res  = await fetch('/api/v1/process-drawing', reqOptions);
      const json = await res.json();

      if (json.status === 'success') {
        setData(json);
        const fileName = uploadedFile ? uploadedFile.name : json.drawing?.filename || drawing;
        setDrawing(fileName);

        // Add file name to drawings list if not already present
        setDrawingsList(prev => prev.includes(fileName) ? prev : [fileName, ...prev]);

        const sourceLabel = json.input_source === 'pdf_parsed' ? 'PDF Text Parsed' : 'Engine Standard Inputs';
        setBanner({
          type: 'success',
          msg: `✓ Drawing processed [${sourceLabel}]: ${json.boq?.length || 30} takeoff items computed. Grand Total: ₱${(json.summary?.grand_total_direct_cost || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
        });
      } else {
        throw new Error(json.reason || 'Failed to process drawing');
      }

      // Fetch Rebar Optimization
      const rRes  = await fetch('/api/v1/optimize-rebar', { method: 'POST' });
      const rJson = await rRes.json();
      if (rJson.status === 'success') {
        setRebarData(rJson.optimizations);
      }
    } catch (err) {
      setBanner({
        type: 'info',
        msg: `⚠ Note: Backend connecting/offline. ${err.message || ''}`
      });
    } finally {
      setLoading(false);
    }
  };

  // ── Import Action (Triggers File Picker) ───────────────────────────────
  const handleImportClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files && e.target.files[0];
    if (file) {
      fetchTakeoff(file);
    }
  };

  // ── Supabase Sync Action ───────────────────────────────────────────────
  const handleSyncSupabase = async () => {
    if (!data || !data.boq) {
      setBanner({ type: 'info', msg: '⚠ Run takeoff first before syncing to database.' });
      return;
    }

    setBanner({ type: 'info', msg: '⏳ Syncing takeoff session to database...' });

    try {
      const res = await fetch('/api/v1/sync-supabase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: data.session_id,
          drawing_name: drawing,
          boq: data.boq,
          grand_total: data.summary?.grand_total_direct_cost || 0,
        }),
      });
      const json = await res.json();

      if (json.status === 'saved') {
        const dest = json.storage === 'local_sqlite' ? 'Local SQLite (boq_v2.db)' : 'Supabase Cloud V2';
        setBanner({
          type: 'success',
          msg: `✓ Session ${json.session_id.slice(0,8)}... saved to ${dest} (${json.item_count} items synced).`
        });
      } else {
        setBanner({
          type: 'info',
          msg: `ℹ Database sync status: ${json.reason || json.status || 'saved locally'}.`
        });
      }
    } catch (err) {
      setBanner({ type: 'error', msg: `✕ Sync error: ${err.message}` });
    }
  };

  // ── Export Actions ─────────────────────────────────────────────────────
  const handleExportCSV = () => {
    window.open('/api/v1/export-csv', '_blank');
    setBanner({ type: 'success', msg: '📥 Downloading Plan2Takeoff_V2_BOQ.csv...' });
  };

  const handleExportJSON = () => {
    window.open('/api/v1/export-json', '_blank');
    setBanner({ type: 'success', msg: '📥 Downloading Plan2Takeoff_V2_Takeoff.json...' });
  };

  const handleReset = () => {
    setData(null);
    setRebarData(null);
    setBanner(null);
    setSelectedElement(null);
    setTradeTotals({});
  };

  const onElementSelect = useCallback((el) => setSelectedElement(el), []);
  const onTotalsChange  = useCallback((totals) => setTradeTotals(totals), []);

  // ── Styles ─────────────────────────────────────────────────────────────
  const btn = (color = '#1e293b', borderColor = '#334155') => ({
    background: color,
    border: `1px solid ${borderColor}`,
    borderRadius: '7px',
    color: '#e2e8f0',
    fontFamily: 'Inter, sans-serif',
    fontSize: '12px',
    fontWeight: 600,
    padding: '7px 14px',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    transition: 'all 0.15s',
  });

  return (
    <div style={{ minHeight: '100vh', background: '#020617', color: '#f8fafc', fontFamily: 'Inter, system-ui, sans-serif' }}>
      
      {/* Hidden file input for file selection */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf,.dxf,.dwg"
        style={{ display: 'none' }}
      />

      {/* ── Header ── */}
      <header style={{
        background: 'linear-gradient(180deg,#0f172a 0%,#020617 100%)',
        borderBottom: '1px solid #1e293b',
        padding: '0 24px',
        position: 'sticky', top: 0, zIndex: 100,
        boxShadow: '0 4px 24px rgba(0,0,0,0.5)',
      }}>
        {/* Top bar */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #0f172a', gap: '12px', flexWrap: 'wrap' }}>
          {/* Brand */}
          <div>
            <div style={{ fontSize: '10px', color: '#475569', letterSpacing: '1.5px', textTransform: 'uppercase' }}>Plan2Takeoff V2 — Review Dashboard</div>
            <div style={{ fontSize: '16px', fontWeight: 900, color: '#fff', letterSpacing: '-0.3px' }}>
              Structural BOQ Takeoff <span style={{ color: '#6366f1' }}>Engine</span>
            </div>
          </div>

          {/* Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <select
              value={drawing}
              onChange={e => setDrawing(e.target.value)}
              style={{
                background: '#0f172a', border: '1px solid #334155',
                borderRadius: '7px', color: '#cbd5e1',
                fontSize: '12px', padding: '7px 12px', cursor: 'pointer',
                fontFamily: 'Inter, sans-serif', outline: 'none', minWidth: '220px',
              }}
            >
              {drawingsList.map(d => <option key={d} value={d}>{d}</option>)}
            </select>

            <button
              onClick={handleImportClick} disabled={loading}
              style={{ ...btn('linear-gradient(135deg,#059669,#10b981)', 'transparent'), color: '#fff', opacity: loading ? 0.6 : 1 }}
            >
              {loading ? '⏳ Parsing...' : '📥 Import PDF/DXF'}
            </button>

            <button onClick={handleSyncSupabase} style={btn('#1e3a5f', '#2563eb')}>
              ☁️ Sync Session DB
            </button>

            <button onClick={handleExportCSV} style={btn('#052e16', '#065f46')}>
              📊 Export CSV
            </button>

            <button onClick={handleExportJSON} style={btn('#3b0764', '#6b21a8')}>
              📄 Export JSON
            </button>

            <button onClick={() => fetchTakeoff()} disabled={loading} style={btn()}>
              🔄 Refresh
            </button>

            <button onClick={handleReset} style={{ ...btn(), color: '#f87171', borderColor: '#7f1d1d' }}>
              ✕ Reset
            </button>
          </div>
        </div>

        {/* Banner */}
        {banner && (
          <div style={{
            padding: '8px 16px',
            background: banner.type === 'success' ? '#052e16' : banner.type === 'error' ? '#7f1d1d' : '#0f172a',
            borderTop: '1px solid #0f172a',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}>
            <span style={{ fontSize: '12px', color: banner.type === 'success' ? '#6ee7b7' : banner.type === 'error' ? '#fca5a5' : '#60a5fa' }}>
              {banner.msg}
            </span>
            <button onClick={() => setBanner(null)} style={{ background: 'none', border: 'none', color: '#475569', cursor: 'pointer', fontSize: '14px' }}>×</button>
          </div>
        )}

        {/* View mode toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 0', flexWrap: 'wrap' }}>
          {[
            { id: 'checklist',  label: '📋 BOQ Checklist' },
            { id: 'accordion',  label: '📊 Trade Accordion' },
            { id: 'blueprint',  label: '🗺️ Blueprint Viewer' },
            { id: 'rebar',      label: '⚙️ Rebar Optimizer' },
          ].map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setBoqView(id)}
              style={{
                background: boqView === id ? 'rgba(99,102,241,0.2)' : 'transparent',
                border: boqView === id ? '1px solid rgba(99,102,241,0.5)' : '1px solid transparent',
                borderRadius: '7px',
                color: boqView === id ? '#a5b4fc' : '#64748b',
                fontFamily: 'Inter, sans-serif', fontSize: '12px', fontWeight: 600,
                padding: '5px 14px', cursor: 'pointer', transition: 'all 0.15s',
              }}
            >
              {label}
            </button>
          ))}
        </div>
      </header>

      {/* ── Main Layout ── */}
      <main style={{ maxWidth: '1600px', margin: '0 auto', padding: '20px 24px', display: 'flex', gap: '20px', alignItems: 'flex-start' }}>

        {/* Left Column */}
        <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: '0' }}>
          {boqView === 'blueprint' && (
            <BlueprintViewer
              elements={data?.elements}
              drawingName={drawing}
              onElementSelect={onElementSelect}
            />
          )}

          {boqView === 'checklist' && (
            <CostedBOQChecklist
              boqData={data?.boq}
              onRowSelect={setSelectedElement}
              onTotalsChange={onTotalsChange}
            />
          )}

          {boqView === 'accordion' && (
            <TradeAccordion boqItems={data?.boq || []} />
          )}

          {boqView === 'rebar' && (
            <RebarOptimizerView optimizations={rebarData || []} />
          )}
        </div>

        {/* Right Column */}
        {(boqView === 'checklist' || boqView === 'blueprint') && (
          <div style={{ width: '300px', flexShrink: 0, position: 'sticky', top: '130px' }}>
            <RightPanel
              tradeTotals={tradeTotals}
              selectedElement={selectedElement}
            />
          </div>
        )}
      </main>
    </div>
  );
}
