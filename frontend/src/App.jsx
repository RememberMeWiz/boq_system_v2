import React, { useState, useEffect } from 'react';
import BlueprintViewer from './components/BlueprintViewer';
import TradeAccordion from './components/TradeAccordion';
import RebarOptimizerView from './components/RebarOptimizerView';

export default function App() {
  const [data, setData] = useState(null);
  const [rebarData, setRebarData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('boq');

  const fetchTakeoff = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/process-drawing', { method: 'POST' });
      const json = await res.json();
      setData(json);

      const rRes = await fetch('/api/v1/optimize-rebar', { method: 'POST' });
      const rJson = await rRes.json();
      setRebarData(rJson.optimizations);
    } catch (e) {
      console.error('Takeoff processing failed — using mock data', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Attempt live fetch on mount; graceful degradation to mock data if API is down
    fetchTakeoff();
  }, []);

  const tabs = [
    { id: 'boq',      label: '📊 BOQ Accordion',      desc: '13-Trade Direct Costs' },
    { id: 'blueprint', label: '🗺️ Blueprint Viewer',   desc: 'Structural Heatmap'   },
    { id: 'rebar',    label: '⚙️ Rebar Optimizer',     desc: 'Bin-Packing Results'  },
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: '#020617',
      color: '#f8fafc',
      fontFamily: 'Inter, system-ui, sans-serif',
      padding: '0',
    }}>
      {/* ── Top Navigation Bar ── */}
      <header style={{
        background: 'linear-gradient(180deg, #0f172a 0%, #020617 100%)',
        borderBottom: '1px solid #1e293b',
        padding: '16px 32px',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {/* Brand */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <h1 style={{ margin: 0, fontSize: '22px', fontWeight: 900, letterSpacing: '-0.5px', color: '#fff' }}>
                Plan2Takeoff <span style={{ color: '#6366f1' }}>V2</span>
              </h1>
              <span style={{
                background: 'rgba(99,102,241,0.15)',
                color: '#818cf8',
                border: '1px solid rgba(99,102,241,0.3)',
                fontSize: '10px',
                fontWeight: 600,
                padding: '3px 10px',
                borderRadius: '999px',
                letterSpacing: '0.5px',
              }}>
                Automated Structural Engine
              </span>
            </div>
            <p style={{ margin: '3px 0 0', fontSize: '11px', color: '#475569' }}>
              DPWH CMPD Direct Costing · PNS 49 Rebar · CHB Masonry · 13-Trade BOQ
            </p>
          </div>

          {/* Run Button */}
          <button
            onClick={fetchTakeoff}
            disabled={loading}
            style={{
              background: loading ? '#1e293b' : 'linear-gradient(135deg, #4f46e5, #7c3aed)',
              border: 'none',
              borderRadius: '10px',
              color: '#fff',
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
              fontSize: '13px',
              padding: '10px 20px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1,
              boxShadow: loading ? 'none' : '0 4px 20px rgba(99,102,241,0.4)',
              transition: 'all 0.2s ease',
            }}
          >
            {loading ? '⏳ Processing Takeoff...' : '⚡ Run Full Drawing Takeoff'}
          </button>
        </div>

        {/* Tab Row */}
        <div style={{ maxWidth: '1400px', margin: '14px auto 0', display: 'flex', gap: '4px' }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: activeTab === tab.id ? 'rgba(99,102,241,0.2)' : 'transparent',
                border: activeTab === tab.id ? '1px solid rgba(99,102,241,0.5)' : '1px solid transparent',
                borderRadius: '8px',
                color: activeTab === tab.id ? '#a5b4fc' : '#64748b',
                fontFamily: 'Inter, sans-serif',
                fontSize: '12px',
                fontWeight: 600,
                padding: '7px 16px',
                cursor: 'pointer',
                transition: 'all 0.15s',
              }}
              onMouseEnter={e => { if (activeTab !== tab.id) e.currentTarget.style.color = '#94a3b8'; }}
              onMouseLeave={e => { if (activeTab !== tab.id) e.currentTarget.style.color = '#64748b'; }}
            >
              {tab.label}
              <span style={{ color: '#334155', fontSize: '10px', marginLeft: '6px' }}>
                {tab.desc}
              </span>
            </button>
          ))}
        </div>
      </header>

      {/* ── Main Content ── */}
      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '28px 32px' }}>
        {activeTab === 'boq' && (
          <TradeAccordion boqItems={data?.boq || []} />
        )}

        {activeTab === 'blueprint' && (
          <BlueprintViewer
            elements={data?.elements || []}
            drawingName={data?.drawing?.filename}
          />
        )}

        {activeTab === 'rebar' && (
          <RebarOptimizerView optimizations={rebarData || []} />
        )}
      </main>
    </div>
  );
}
