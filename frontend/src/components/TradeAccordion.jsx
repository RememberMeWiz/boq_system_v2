import React, { useState } from 'react';

export default function TradeAccordion({ boqItems, onRateChange }) {
  const [openSections, setOpenSections] = useState({
    'Division 02 — Earthworks': true,
    'Division 03 — Concrete & Formwork': true,
    'Division 04 — Masonry Works': true,
    'Division 05 — Metals & Rebar': true
  });

  const toggleSection = (division) => {
    setOpenSections(prev => ({ ...prev, [division]: !prev[division] }));
  };

  // Group items by Division
  const grouped = (boqItems || []).reduce((acc, item) => {
    const div = item.division || 'Division 03 — Concrete & Formwork';
    if (!acc[div]) acc[div] = [];
    acc[div].push(item);
    return acc;
  }, {});

  const totalProjectCost = (boqItems || []).reduce((sum, item) => sum + (item.total_amount || 0), 0);

  return (
    <div className="bg-slate-900 rounded-xl p-5 border border-slate-800 shadow-xl mt-6">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-sky-400">📊 BOQ Checklist Accordions (CSI MasterFormat / DPWH Direct Costs)</h2>
          <p className="text-xs text-slate-400">Total Direct Cost Breakdown (Material + Labor + Equipment)</p>
        </div>
        <div className="text-right font-bold text-xl text-emerald-400">
          Total Project: ₱ {totalProjectCost.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </div>
      </div>

      <div className="space-y-4">
        {Object.entries(grouped).map(([division, items]) => {
          const sectionTotal = items.reduce((sum, i) => sum + i.total_amount, 0);
          const isOpen = openSections[division];

          return (
            <div key={division} className="border border-slate-800 rounded-lg overflow-hidden bg-slate-950">
              {/* Accordion Header Banner */}
              <button
                onClick={() => toggleSection(division)}
                className="w-full px-4 py-3 bg-slate-800 hover:bg-slate-750 flex justify-between items-center text-left font-semibold text-slate-200 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <span className="text-sky-400">{isOpen ? '▼' : '▶'}</span>
                  <span>{division}</span>
                  <span className="bg-slate-700 text-slate-300 text-xs px-2 py-0.5 rounded-full">{items.length} items</span>
                </div>
                <div className="font-mono text-emerald-400 font-bold">
                  Subtotal: ₱ {sectionTotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </div>
              </button>

              {/* Accordion Content Table */}
              {isOpen && (
                <div className="p-3 overflow-x-auto">
                  <table className="w-full text-xs text-left border-collapse">
                    <thead>
                      <tr className="text-slate-400 border-b border-slate-800">
                        <th className="p-2">Code</th>
                        <th className="p-2">Description</th>
                        <th className="p-2 text-right">Qty</th>
                        <th className="p-2">Unit</th>
                        <th className="p-2 text-right">Mat. Cost</th>
                        <th className="p-2 text-right">Labor Cost</th>
                        <th className="p-2 text-right">Eqp. Cost</th>
                        <th className="p-2 text-right">Total Unit Cost</th>
                        <th className="p-2 text-right font-bold text-emerald-400">Amount (₱)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {items.map((row, idx) => (
                        <tr key={idx} className="border-b border-slate-800/60 hover:bg-slate-900/50">
                          <td className="p-2 font-mono text-sky-300">{row.item_code}</td>
                          <td className="p-2 text-slate-200">{row.description}</td>
                          <td className="p-2 text-right font-mono font-semibold">{row.qty}</td>
                          <td className="p-2 text-slate-400">{row.unit}</td>
                          <td className="p-2 text-right font-mono">₱ {row.material_unit_cost.toFixed(2)}</td>
                          <td className="p-2 text-right font-mono">₱ {row.labor_unit_cost.toFixed(2)}</td>
                          <td className="p-2 text-right font-mono">₱ {row.equipment_unit_cost.toFixed(2)}</td>
                          <td className="p-2 text-right font-mono font-bold text-slate-200">₱ {row.total_unit_cost.toFixed(2)}</td>
                          <td className="p-2 text-right font-mono font-bold text-emerald-400">₱ {row.total_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
