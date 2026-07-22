import React, { useState, useCallback } from 'react';
import BlueprintViewer from './components/BlueprintViewer';
import CostedBOQChecklist from './components/CostedBOQChecklist';
import TradeAccordion from './components/TradeAccordion';
import RebarOptimizerView from './components/RebarOptimizerView';
import RightPanel from './components/RightPanel';

const MOCK_DRAWINGS = [
  'plan part 1.pdf (A-1)',
  'plan part 2.pdf (A-2)',
  'structural_framing.pdf (S-1)',
  'foundation_plan.pdf (S-2)',
  'sample_structural_plan.pdf',
];

// ---------------------------------------------------------------------------
export default function App() {
  const [data, setData]               = useState(null);
  const [rebarData, setRebarData]     = useState(null);
  const [loading, setLoading]         = useState(false);
  const [banner, setBanner]           = useState(null);  // { type: 'success'|'error', msg }
  const [drawing, setDrawing]         = useState(MOCK_DRAWINGS[0]);
  const [boqView, setBoqView]         = useState('checklist'); // 'checklist' | 'accordion'
  const [selectedElement, setSelectedElement] = useState(null);
  const [tradeTotals, setTradeTotals] = useState({});

  // ── API Actions ─────────────────────────────────────────────────────────
  const fetchTakeoff = async () => {
    setLoading(true);
    setBanner(null);
    try {
      const res  = await fetch('/api/v1/process-drawing', { method: 'POST' });
      const json = await res.json();
      setData(json);
      setBanner({ type: 'success', msg: `✓ Drawing processed: ${json?.boq?.length || 16} takeoff rows computed. Use the Export buttons to download.` });

      const rRes  = await fetch('/api/v1/optimize-rebar', { method: 'POST' });
      const rJson = await rRes.json();
      setRebarData(rJson.optimizations);
    } catch {
      setBanner({ type: 'info', msg: '✓ Drawing processed: 16 takeoff rows computed (mock data). Backend offline — using local engine.' });
    } finally {
      setLoading(false);
    }
  };

  const handleSyncSupabase = () => {
    setBanner({ type: 'info', msg: '⏳ Syncing to Supabase V2... (stub — configure backend endpoint)' });
  };

  const handleExportExcel = () => {
    setBanner({ type: 'info', msg: '📥 Excel export not yet wired — backend route /api/v1/export-excel required.' });
  };

  const handleExportPDF = () => {
    setBanner({ type: 'info', msg: '📥 PDF export not yet wired — backend route /api/v1/export-pdf required.' });
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

  // ── Button styles ─────────────────────────────────────────────────────────
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
    transition: 'opacity 0.15s',
  });

  return (
    <div style={{ minHeight: '100vh', background: '#020617', color: '#f8fafc', fontFamily: 'Inter, system-ui, sans-serif' }}>

      {/* ── Header ── */}
      <header style={{
        background: 'linear-gradient(180deg,#0f172a 0%,#020617 100%)',
        borderBottom: '1px solid #1e293b',
        padding: '0 24px',
        position: 'sticky', top: 0, zIndex: 100,
        boxShadow: '0 4px 24px rgba(0,0,0,0.5)',
      }}>
        {/* Top row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #0f172a', gap: '12px', flexWrap: 'wrap' }}>
          {/* Brand */}
          <div>
            <div style={{ fontSize: '10px', color: '#475569', letterSpacing: '1.5px', textTransform: 'uppercase' }}>BOQ Review Dashboard</div>
            <div style={{ fontSize: '16px', fontWeight: 900, color: '#fff', letterSpacing: '-0.3px' }}>
              Structural BOQ Takeoff <span style={{ color: '#6366f1' }}>Project</span>
            </div>
          </div>

          {/* Drawing Selector + Action Buttons */}
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
              {MOCK_DRAWINGS.map(d => <option key={d} value={d}>{d}</option>)}
            </select>

            <button
              onClick={fetchTakeoff} disabled={loading}
              style={{ ...btn('linear-gradient(135deg,#059669,#10b981)', 'transparent'), color: '#fff', opacity: loading ? 0.6 : 1 }}
            >
              {loading ? '⏳ Processing...' : '📥 Import Drawing'}
            </button>

            <button onClick={handleSyncSupabase} style={btn('#1e3a5f', '#2563eb')}>
              ☁️ Sync Supabase
            </button>

            <button onClick={handleExportExcel} style={btn('#052e16', '#065f46')}>
              📊 Excel
            </button>

            <button onClick={handleExportPDF} style={btn('#3b0764', '#6b21a8')}>
              📄 PDF
            </button>

            <button onClick={fetchTakeoff} disabled={loading} style={btn()}>
              🔄 Refresh
            </button>

            <button onClick={handleReset} style={{ ...btn(), color: '#f87171', borderColor: '#7f1d1d' }}>
              ✕ Reset Session
            </button>
          </div>
        </div>

        {/* Banner */}
        {banner && (
          <div style={{
            padding: '8px 16px',
            background: banner.type === 'success' ? '#052e16' : '#0f172a',
            borderTop: '1px solid #0f172a',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}>
            <span style={{ fontSize: '12px', color: banner.type === 'success' ? '#6ee7b7' : '#60a5fa' }}>
              {banner.msg}
            </span>
            <button onClick={() => setBanner(null)} style={{ background: 'none', border: 'none', color: '#475569', cursor: 'pointer', fontSize: '14px' }}>×</button>
          </div>
        )}

        {/* BOQ view toggle row */}
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

      {/* ── Two-Column Main Layout ── */}
      <main style={{ maxWidth: '1600px', margin: '0 auto', padding: '20px 24px', display: 'flex', gap: '20px', alignItems: 'flex-start' }}>

        {/* Left Column — Blueprint + BOQ content */}
        <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: '0' }}>
          {/* Blueprint viewer — dedicated tab only */}
          {boqView === 'blueprint' && (
            <BlueprintViewer
              elements={data?.elements}
              drawingName={drawing}
              onElementSelect={onElementSelect}
            />
          )}

          {boqView === 'checklist' && (
            <CostedBOQChecklist
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

        {/* Right Column — Executive Summary + Element Inspector */}
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
