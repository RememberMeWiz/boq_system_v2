import React, { useState, useEffect } from 'react';
import BlueprintViewer from './components/BlueprintViewer';
import TradeAccordion from './components/TradeAccordion';
import RebarOptimizerView from './components/RebarOptimizerView';

export default function App() {
  const [data, setData] = useState(null);
  const [rebarData, setRebarData] = useState(null);
  const [loading, setLoading] = useState(false);

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
      console.error("Takeoff processing failed", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTakeoff();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      {/* Header Banner */}
      <header className="flex justify-between items-center pb-6 mb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black tracking-tight text-white">Plan2Takeoff <span className="text-blue-500">V2</span></h1>
            <span className="bg-blue-600/20 text-blue-400 border border-blue-500/30 text-xs font-semibold px-2.5 py-0.5 rounded-full">
              Automated Structural Engine
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">Direct Costing (Material + Labor + Equipment) | Native Vector Blueprint Heatmaps | Rebar Bin Packing</p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={fetchTakeoff}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg text-sm transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50"
          >
            {loading ? 'Processing Takeoff...' : '⚡ Run Full Drawing Takeoff'}
          </button>
        </div>
      </header>

      {/* Main Content Layout */}
      <main className="max-w-7xl mx-auto space-y-6">
        <BlueprintViewer
          elements={data?.elements || []}
          drawingName={data?.drawing?.filename}
        />

        <TradeAccordion
          boqItems={data?.boq || []}
        />

        <RebarOptimizerView
          optimizations={rebarData || []}
        />
      </main>
    </div>
  );
}
