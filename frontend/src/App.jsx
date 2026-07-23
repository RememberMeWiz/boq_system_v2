import React, { useState, useEffect, useCallback } from 'react';
import BlueprintViewer from './components/BlueprintViewer';
import CostedBOQChecklist from './components/CostedBOQChecklist';
import TradeAccordion from './components/TradeAccordion';
import RebarOptimizerView from './components/RebarOptimizerView';
import RightPanel from './components/RightPanel';
import UploadModal from './components/UploadModal';
import ParserDashboard from './components/ParserDashboard';

// ── Custom Drawing Dropdown with Delete Button ────────────────────────────────
function DrawingDropdownMenu({ drawing, drawingsList, onSelect, onDelete }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={{ position: 'relative', minWidth: '270px' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          background: '#0f172a', border: '1px solid #334155',
          borderRadius: '7px', color: drawing ? '#e2e8f0' : '#94a3b8',
          fontSize: '12px', padding: '7px 12px', cursor: 'pointer',
          fontFamily: 'Inter, sans-serif', textAlign: 'left',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}
      >
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '210px' }}>
          {drawing || '-- Select or Import Drawing --'}
        </span>
        <span style={{ fontSize: '10px', color: '#64748b', marginLeft: '6px' }}>{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute', top: '100%', left: 0, right: 0, marginTop: '4px',
          background: '#0f172a', border: '1px solid #334155', borderRadius: '8px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.8)', zIndex: 250, maxHeight: '260px', overflowY: 'auto',
        }}>
          {drawingsList.length === 0 ? (
            <div style={{ padding: '10px 12px', fontSize: '11px', color: '#64748b' }}>No saved drawings in database</div>
          ) : (
            drawingsList.map(d => (
              <div
                key={d}
                onClick={() => {
                  onSelect(d);
                  setIsOpen(false);
                }}
                style={{
                  padding: '8px 12px', fontSize: '12px', color: d === drawing ? '#38bdf8' : '#cbd5e1',
                  background: d === drawing ? 'rgba(56,189,248,0.1)' : 'transparent',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  cursor: 'pointer', borderBottom: '1px solid #1e293b',
                  transition: 'background 0.15s',
                }}
              >
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '200px' }}>
                  📄 {d}
                </span>
                <button
                  onClick={(e) => onDelete(d, e)}
                  title="Delete drawing from database"
                  style={{
                    background: 'rgba(239,68,68,0.15)', border: '1px solid #ef4444',
                    color: '#ef4444', fontSize: '10px', fontWeight: 700,
                    cursor: 'pointer', padding: '2px 6px', borderRadius: '4px',
                  }}
                >
                  ✕ Delete
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [data, setData]               = useState(null);
  const [rebarData, setRebarData]     = useState(null);
  const [parserData, setParserData]   = useState(null); // /api/v1/parser/ingest result
  const [loading, setLoading]         = useState(false);
  const [banner, setBanner]           = useState(null);
  const [drawingsList, setDrawingsList] = useState([]);
  const [drawing, setDrawing]         = useState('');
  const [boqView, setBoqView]         = useState('checklist');
  const [selectedElement, setSelectedElement] = useState(null);
  const [tradeTotals, setTradeTotals] = useState({});
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

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
        }
      }
    } catch {
      // Ignore network fallback
    }
  };

  useEffect(() => {
    loadSavedSessions();
    fetchTakeoff(null, 'plan part 1.pdf');
  }, []);

  // ── Core Takeoff Fetch ──────────────────────────────────────────────────
  const fetchTakeoff = async (uploadedFile = null, selectedDrawingName = null, activeSessionId = null) => {
    setLoading(true);
    setBanner(null);

    const targetName = uploadedFile ? uploadedFile.name : (selectedDrawingName || drawing || 'plan part 1.pdf');
    setDrawing(targetName);
    setDrawingsList(prev => prev.includes(targetName) ? prev : [targetName, ...prev]);

    try {
      let currentSessionId = activeSessionId;

      // Step 1: Run Parser Ingest FIRST (for PDFs) to get single unified session_id & verification_gate
      if (!currentSessionId && targetName.toLowerCase().endsWith('.pdf')) {
        try {
          let pReqOptions = { method: 'POST' };
          if (uploadedFile) {
            const pFormData = new FormData();
            pFormData.append('file', uploadedFile);
            pReqOptions.body = pFormData;
          } else {
            pReqOptions.headers = { 'Content-Type': 'application/json' };
            pReqOptions.body = JSON.stringify({ drawing_name: targetName });
          }
          const pRes  = await fetch('/api/v1/parser/ingest', pReqOptions);
          const pJson = await pRes.json();
          if (pRes.ok) {
            setParserData(pJson);
            currentSessionId = pJson.session_id;
          }
        } catch { /* non-blocking fallback */ }
      }

      // Step 2: Run process-drawing WITH session_id to reuse session and enforce verification gate
      let reqOptions = { method: 'POST', headers: { 'Content-Type': 'application/json' } };
      let bodyData = { drawing_name: targetName };
      if (currentSessionId) bodyData.session_id = currentSessionId;
      reqOptions.body = JSON.stringify(bodyData);

      const res  = await fetch('/api/v1/process-drawing', reqOptions);
      const json = await res.json();

      if (res.status === 409) {
        // Verification Gate Blocked!
        setData(null);
        setBanner({
          type: 'error',
          msg: `🔒 Takeoff Calculation BLOCKED by Verification Gate: ${json.message || 'Resolve blocking issues or submit signoff in Parser & Signoff tab.'}`
        });
      } else if (json.status === 'success') {
        setData(json);
        const sourceLabel = json.input_source === 'pdf_vision_enriched'
          ? 'AI Vision Enriched'
          : (json.input_source === 'pdf_vector_parsed' ? 'Vector Parsed' : 'Fajardo Takeoff Engine');
        setBanner({
          type: 'success',
          msg: `✓ Drawing processed [${sourceLabel}]: ${json.boq?.length || 30} takeoff items computed. Grand Total: ₱${(json.summary?.grand_total_direct_cost || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
        });
      } else {
        throw new Error(json.reason || json.message || 'Failed to process drawing');
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
        msg: `⚠ Note: ${err.message || 'Error processing drawing.'}`
      });
    } finally {
      setLoading(false);
    }
  };

  // ── Delete Drawing Action ─────────────────────────────────────────────
  const handleDeleteDrawing = async (drawingToDelete, e) => {
    e.stopPropagation();
    if (!window.confirm(`Are you sure you want to delete "${drawingToDelete}" from the database?`)) return;

    try {
      await fetch(`/api/v1/sessions/${encodeURIComponent(drawingToDelete)}`, { method: 'DELETE' });
      setDrawingsList(prev => prev.filter(d => d !== drawingToDelete));

      if (drawing === drawingToDelete) {
        handleReset();
      }

      setBanner({
        type: 'success',
        msg: `✓ Deleted "${drawingToDelete}" from database and local storage.`
      });
    } catch (err) {
      setBanner({ type: 'error', msg: `✕ Failed to delete session: ${err.message}` });
    }
  };

  // ── Import Action (Opens Upload Modal) ──────────────────────────────────
  const handleImportClick = () => {
    setIsUploadModalOpen(true);
  };

  const handleModalUpload = (file) => {
    fetchTakeoff(file);
  };

  // ── Refresh Action ──────────────────────────────────────────────────────
  const handleRefresh = () => {
    if (drawing || data) {
      fetchTakeoff(null, drawing);
    } else {
      setBanner({ type: 'info', msg: 'ℹ Select a drawing or click "Import PDF/DXF" to compute takeoff data.' });
    }
  };

  // ── Reset Action ────────────────────────────────────────────────────────
  const handleReset = () => {
    setData(null);
    setRebarData(null);
    setParserData(null);
    setSelectedElement(null);
    setTradeTotals({});
    setDrawing('');
    setBanner({ type: 'info', msg: '✓ Session reset. All takeoff data cleared.' });
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
      
      {/* Mini Drag & Drop File Upload Modal */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUpload={handleModalUpload}
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
            <DrawingDropdownMenu
              drawing={drawing}
              drawingsList={drawingsList}
              onSelect={(val) => {
                setDrawing(val);
                fetchTakeoff(null, val);
              }}
              onDelete={handleDeleteDrawing}
            />

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

            <button onClick={handleRefresh} disabled={loading} style={btn()}>
              🔄 Refresh
            </button>

            <button onClick={handleReset} style={{ ...btn(), color: '#f87171', borderColor: '#7f1d1d' }}>
              ✕ Reset
            </button>
          </div>
        </div>

      {/* Floating Notification Toast Overlay */}
      {banner && (
        <div style={{
          position: 'fixed',
          top: '85px',
          right: '24px',
          zIndex: 1000,
          background: banner.type === 'success'
            ? 'linear-gradient(135deg, #064e3b 0%, #022c22 100%)'
            : banner.type === 'error'
            ? 'linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%)'
            : 'linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%)',
          border: `1px solid ${
            banner.type === 'success' ? '#10b981' : banner.type === 'error' ? '#ef4444' : '#3b82f6'
          }`,
          borderRadius: '12px',
          padding: '13px 20px',
          boxShadow: `0 10px 30px ${
            banner.type === 'success' ? 'rgba(16,185,129,0.3)' : banner.type === 'error' ? 'rgba(239,68,68,0.3)' : 'rgba(59,130,246,0.3)'
          }`,
          display: 'flex',
          alignItems: 'center',
          gap: '14px',
          maxWidth: '520px',
          animation: 'fadeIn 0.2s ease-in-out',
        }}>
          <span style={{
            fontSize: '14px',
            fontWeight: 600,
            color: banner.type === 'success' ? '#6ee7b7' : banner.type === 'error' ? '#fca5a5' : '#93c5fd',
            lineHeight: '1.4',
          }}>
            {banner.msg}
          </span>
          <button
            onClick={() => setBanner(null)}
            style={{
              background: 'rgba(255,255,255,0.1)',
              border: 'none',
              borderRadius: '50%',
              width: '24px', height: '24px',
              color: '#cbd5e1',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 700,
              display: 'flex', justifyContent: 'center', alignItems: 'center',
              flexShrink: 0,
            }}
          >
            ✕
          </button>
        </div>
      )}

        {/* View mode toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 0', flexWrap: 'wrap' }}>
          {[
            { id: 'checklist',  label: '📋 BOQ Checklist' },
            { id: 'accordion',  label: '📊 Trade Accordion' },
            { id: 'blueprint',  label: '🗺️ Blueprint Viewer' },
            { id: 'rebar',      label: '⚙️ Rebar Optimizer' },
            { id: 'parser',     label: '🔬 Parser & Signoff' },
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
              pageImage={data?.drawing?.page_image}
              comparisonImage={data?.drawing?.comparison_image}
              framingPlan={data?.framing_plan}
              suggestions={data?.suggestions}
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

          {boqView === 'parser' && (
            <ParserDashboard
              parserData={parserData}
              setParserData={setParserData}
              onSignoffComplete={(updatedGate) => {
                if (parserData?.session_id) {
                  fetchTakeoff(null, drawing, parserData.session_id);
                }
              }}
            />
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
