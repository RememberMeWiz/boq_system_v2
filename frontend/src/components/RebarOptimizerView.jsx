import React from 'react';

export default function RebarOptimizerView({ optimizations }) {
  if (!optimizations || optimizations.length === 0) {
    return (
      <div style={{ background: '#0a0f1e', border: '1px solid #1e293b', borderRadius: '14px', padding: '60px 20px', textAlign: 'center', color: '#64748b', margin: '20px 0' }}>
        <div style={{ fontSize: '32px', marginBottom: '12px' }}>⚙️</div>
        <div style={{ fontSize: '15px', fontWeight: 700, color: '#e2e8f0', marginBottom: '6px' }}>No Rebar Cut List Data</div>
        <div style={{ fontSize: '12px', color: '#94a3b8', maxWidth: '400px', margin: '0 auto' }}>
          Click <strong>"📥 Import PDF/DXF"</strong> or process a drawing plan to run 1D commercial rebar stock optimization.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 rounded-xl p-5 border border-slate-800 shadow-xl mt-6">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-amber-400">✂️ 1D Commercial Rebar Cutting Stock Optimizer</h2>
          <p className="text-xs text-slate-400">Bin-Packing Cut List Mapping against Standard Commercial Stock Lengths (6m, 9m, 12m)</p>
        </div>
        <div className="bg-emerald-900/50 text-emerald-300 border border-emerald-700/50 px-3 py-1 rounded-full text-xs font-bold">
          Target Scrap: &lt; 3.0%
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {optimizations.map((opt, idx) => (
          <div key={idx} className="bg-slate-950 p-4 rounded-lg border border-slate-800">
            <div className="flex justify-between items-center mb-2">
              <span className="font-bold text-amber-300 text-sm">{opt.diameter_mm}mm Deformed Rebar</span>
              <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${opt.scrap_percentage < 3 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400'}`}>
                Scrap: {opt.scrap_percentage}%
              </span>
            </div>

            <div className="space-y-1 text-xs font-mono text-slate-300 mb-3">
              <div className="flex justify-between">
                <span>Required Net Weight:</span>
                <span>{opt.total_required_kg} kg</span>
              </div>
              <div className="flex justify-between">
                <span>Purchased Gross Weight:</span>
                <span>{opt.total_purchased_kg} kg</span>
              </div>
              <div className="flex justify-between text-rose-400">
                <span>Cutting Scrap Loss:</span>
                <span>{opt.scrap_kg} kg</span>
              </div>
            </div>

            <div className="border-t border-slate-800 pt-2 text-xs">
              <span className="text-slate-400 block mb-1 font-semibold">Commercial Bar Purchase Breakdown:</span>
              <div className="flex gap-2 text-center font-mono">
                <div className="flex-1 bg-slate-900 p-1.5 rounded border border-slate-800">
                  <span className="block text-[10px] text-slate-400">12m Bars</span>
                  <span className="font-bold text-sky-400 text-sm">{opt.purchased_bars['12.0'] || 0} pcs</span>
                </div>
                <div className="flex-1 bg-slate-900 p-1.5 rounded border border-slate-800">
                  <span className="block text-[10px] text-slate-400">9m Bars</span>
                  <span className="font-bold text-sky-400 text-sm">{opt.purchased_bars['9.0'] || 0} pcs</span>
                </div>
                <div className="flex-1 bg-slate-900 p-1.5 rounded border border-slate-800">
                  <span className="block text-[10px] text-slate-400">6m Bars</span>
                  <span className="font-bold text-sky-400 text-sm">{opt.purchased_bars['6.0'] || 0} pcs</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
