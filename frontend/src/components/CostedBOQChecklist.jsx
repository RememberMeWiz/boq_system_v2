import React, { useState, useMemo } from 'react';

// ---------------------------------------------------------------------------
// DPWH CMPD reference rates (mirrors backend/engine/fajardo.py DPWH_RATES)
// ---------------------------------------------------------------------------
const CMPD_RATES = {
  'CON': { mat: 5600.00, lab: 850.00, eqp: 250.00 },   // Concrete per m3
  'REB': { mat: 42.68,   lab: 12.00,  eqp: 2.50  },    // Rebar per kg
  'CHB': { mat: 22.32,   lab: 19.20,  eqp: 1.20  },    // 150mm CHB per pc
  'FW':  { mat: 750.00,  lab: 210.00, eqp: 0.00  },    // Formwork per m2
  'EW':  { mat: 0.00,    lab: 350.00, eqp: 0.00  },    // Earthworks per m3
  'RF':  { mat: 620.00,  lab: 180.00, eqp: 0.00  },    // Roofing per m2
  'PL':  { mat: 620.00,  lab: 150.00, eqp: 0.00  },    // Plumbing per pc
  'EL':  { mat: 32.00,   lab: 18.00,  eqp: 0.00  },    // Electrical per m
  'PW':  { mat: 220.00,  lab: 85.00,  eqp: 0.00  },    // Painting per m2
  'TF':  { mat: 850.00,  lab: 220.00, eqp: 0.00  },    // Tile per m2
  'SW':  { mat: 1450.00, lab: 350.00, eqp: 0.00  },    // Special works per m
  'MC':  { mat: 28000.0, lab: 3500.0, eqp: 0.00  },    // Mech/AC per ton
  'GR':  { mat: 0.00,    lab: 0.00,   eqp: 0.00  },    // Gen. Req lump
};

// ---------------------------------------------------------------------------
// Mock BOQ rows seeded from fajardo.py worked cases
// backup_qty = reference/engineer's estimate quantity
// ---------------------------------------------------------------------------
const INITIAL_ROWS = [
  { id:'CON-1.1', trade:'Concrete Works',         desc:'Concrete Works — Isolated Footings (Class A)',   qty:3.78,   backup:3.60,  unit:'cu.m.', prefix:'CON', status:'Confirmed' },
  { id:'CON-1.2', trade:'Concrete Works',         desc:'Concrete Works — Columns (Class A)',             qty:2.62,   backup:2.62,  unit:'cu.m.', prefix:'CON', status:'Confirmed' },
  { id:'CON-1.3', trade:'Concrete Works',         desc:'Concrete Works — Beams (Class A)',               qty:3.15,   backup:3.00,  unit:'cu.m.', prefix:'CON', status:'Confirmed' },
  { id:'CON-1.4', trade:'Concrete Works',         desc:'Concrete Works — Slab-on-Grade (Class B)',       qty:12.00,  backup:12.00, unit:'cu.m.', prefix:'CON', status:'Confirmed' },
  { id:'FW-1.1',  trade:'Concrete Works',         desc:'Formwork — Marine Plywood 1/2"',                qty:54.20,  backup:52.00, unit:'sq.m.', prefix:'FW',  status:'Pending'   },
  { id:'EW-2.1',  trade:'Earthworks',             desc:'Excavation — Isolated Footings',                qty:18.20,  backup:18.50, unit:'cu.m.', prefix:'EW',  status:'Confirmed' },
  { id:'EW-2.2',  trade:'Earthworks',             desc:'Structural Backfill (Compacted)',               qty:11.40,  backup:10.80, unit:'cu.m.', prefix:'EW',  status:'Flagged'   },
  { id:'REB-2.1', trade:'Steel Reinforcement',    desc:'Deformed Rebar Ø16mm — Footing Mat',            qty:218.90, backup:218.9, unit:'kg',    prefix:'REB', status:'Confirmed' },
  { id:'REB-2.2', trade:'Steel Reinforcement',    desc:'Deformed Rebar Ø20mm — Column Main Bars',       qty:185.40, backup:180.0, unit:'kg',    prefix:'REB', status:'Confirmed' },
  { id:'REB-2.3', trade:'Steel Reinforcement',    desc:'Deformed Rebar Ø10mm — Beam Stirrups',          qty:47.50,  backup:47.50, unit:'kg',    prefix:'REB', status:'Confirmed' },
  { id:'REB-2.4', trade:'Steel Reinforcement',    desc:'Deformed Rebar Ø10mm — Column Ties',            qty:38.60,  backup:38.00, unit:'kg',    prefix:'REB', status:'Pending'   },
  { id:'REB-2.5', trade:'Steel Reinforcement',    desc:'#16 G.I. Tie Wire',                             qty:9.54,   backup:9.20,  unit:'kg',    prefix:'REB', status:'Confirmed' },
  { id:'CHB-3.1', trade:'Masonry Works',          desc:'150mm CHB Laying — Exterior Walls',             qty:338.00, backup:337.5, unit:'pc',    prefix:'CHB', status:'Confirmed' },
  { id:'CHB-3.2', trade:'Masonry Works',          desc:'Plaster — 16mm Scratch & Finish (2 Faces)',     qty:54.00,  backup:52.00, unit:'sq.m.', prefix:'CHB', status:'Pending'   },
  { id:'RF-4.1',  trade:'Roofing & Ceiling',      desc:'Long-span Corrugated Roof Sheets (+12% lap)',   qty:118.90, backup:115.0, unit:'sq.m.', prefix:'RF',  status:'Confirmed' },
  { id:'RF-4.2',  trade:'Roofing & Ceiling',      desc:'Hardiflex Ceiling Panels (+5% waste)',           qty:94.50,  backup:90.00, unit:'sq.m.', prefix:'RF',  status:'Pending'   },
  { id:'TF-5.1',  trade:'Tile & Flooring',        desc:'60×60 Ceramic Floor Tiles (+8% waste)',         qty:86.40,  backup:83.00, unit:'sq.m.', prefix:'TF',  status:'Confirmed' },
  { id:'TF-5.2',  trade:'Tile & Flooring',        desc:'30×60 Wall Tiles — CR & Kitchen',               qty:32.40,  backup:32.40, unit:'sq.m.', prefix:'TF',  status:'Confirmed' },
  { id:'PW-6.1',  trade:'Painting Works',         desc:'Acrylic Latex Topcoat (2 coats) — All Walls',   qty:200.00, backup:195.0, unit:'sq.m.', prefix:'PW',  status:'Confirmed' },
  { id:'PL-7.1',  trade:'Plumbing Works',         desc:'4" UPVC Sanitary Sewer Pipe (3m)',              qty:18.00,  backup:18.00, unit:'pc',    prefix:'PL',  status:'Confirmed' },
  { id:'EL-8.1',  trade:'Electrical Works',       desc:'THHN Wire 3.5mm² (Homerun)',                    qty:67.20,  backup:65.00, unit:'lin.m', prefix:'EL',  status:'Confirmed' },
  { id:'MC-9.1',  trade:'Sanitary/Mechanical',    desc:'Split-type AC Unit (1.5 HP)',                   qty:2.50,   backup:2.50,  unit:'TR',    prefix:'MC',  status:'Confirmed' },
  { id:'SW-10.1', trade:'Special Works',          desc:'Stainless Steel Handrail (Balcony)',             qty:8.00,   backup:8.00,  unit:'lin.m', prefix:'SW',  status:'Confirmed' },
];

const DIVERGENCE_THRESHOLD = 0.05; // 5%

function getDivergence(qty, backup) {
  if (!backup || backup === 0) return 0;
  return Math.abs(qty - backup) / backup;
}

const STATUS_COLORS = {
  'Confirmed': { bg: '#052e16', color: '#34d399', border: '#065f46' },
  'Pending':   { bg: '#1c1917', color: '#fbbf24', border: '#78350f' },
  'Flagged':   { bg: '#2d0a0a', color: '#f87171', border: '#7f1d1d' },
};

// ---------------------------------------------------------------------------
export default function CostedBOQChecklist({ boqData, onRowSelect, onTotalsChange }) {
  const [rows, setRows] = useState(() =>
    INITIAL_ROWS.map(r => {
      const rate = CMPD_RATES[r.prefix] || { mat: 0, lab: 0, eqp: 0 };
      return { ...r, mat: rate.mat, lab: rate.lab, eqp: rate.eqp, usingCmpd: false };
    })
  );

  // Sync rows whenever backend returns new BOQ data
  React.useEffect(() => {
    if (boqData && Array.isArray(boqData) && boqData.length > 0) {
      const mapped = boqData.map(b => {
        const prefix = (b.item_code || 'CON').split('-')[0];
        const rate = CMPD_RATES[prefix] || { mat: b.material_unit_cost || 0, lab: b.labor_unit_cost || 0, eqp: b.equipment_unit_cost || 0 };
        return {
          id: b.item_code || 'ITEM',
          trade: b.trade || b.division || 'General',
          desc: b.description || 'Line Item',
          qty: b.quantity || 0,
          backup: b.backup_qty || b.quantity * 0.97,
          unit: b.unit || 'unit',
          prefix,
          mat: b.material_unit_cost ?? rate.mat,
          lab: b.labor_unit_cost ?? rate.lab,
          eqp: b.equipment_unit_cost ?? rate.eqp,
          usingCmpd: false,
          status: b.status || 'Confirmed',
        };
      });
      setRows(mapped);
    }
  }, [boqData]);
  const [showDivOnly, setShowDivOnly] = useState(false);
  const [selectedId, setSelectedId] = useState(null);

  const computedRows = useMemo(() => rows.map(r => ({
    ...r,
    unitCost: r.mat + r.lab + r.eqp,
    amount: r.qty * (r.mat + r.lab + r.eqp),
    divergence: getDivergence(r.qty, r.backup),
  })), [rows]);

  // Emit totals to parent for Executive Summary
  const tradeTotals = useMemo(() => {
    const totals = {};
    computedRows.forEach(r => {
      totals[r.trade] = (totals[r.trade] || 0) + r.amount;
    });
    return totals;
  }, [computedRows]);

  React.useEffect(() => {
    onTotalsChange && onTotalsChange(tradeTotals);
  }, [tradeTotals]);

  const applyOneCmpd = (id) => {
    setRows(prev => prev.map(r => {
      if (r.id !== id) return r;
      const rate = CMPD_RATES[r.prefix] || { mat: r.mat, lab: r.lab, eqp: r.eqp };
      return { ...r, mat: rate.mat, lab: rate.lab, eqp: rate.eqp, usingCmpd: true };
    }));
  };

  const applyAllCmpd = () => {
    setRows(prev => prev.map(r => {
      const rate = CMPD_RATES[r.prefix] || { mat: r.mat, lab: r.lab, eqp: r.eqp };
      return { ...r, mat: rate.mat, lab: rate.lab, eqp: rate.eqp, usingCmpd: true };
    }));
  };

  const setStatus = (id, status) => {
    setRows(prev => prev.map(r => r.id === id ? { ...r, status } : r));
  };

  const displayRows = showDivOnly
    ? computedRows.filter(r => r.divergence > DIVERGENCE_THRESHOLD)
    : computedRows;

  const grandTotal = computedRows.reduce((s, r) => s + r.amount, 0);
  const fmt = n => `₱${Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  return (
    <div style={{ background: '#0a0f1e', border: '1px solid #1e293b', borderRadius: '14px', overflow: 'hidden' }}>
      {/* Toolbar */}
      <div style={{
        padding: '12px 18px',
        background: '#0f172a',
        borderBottom: '1px solid #1e293b',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '10px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h2 style={{ margin: 0, fontSize: '14px', fontWeight: 800, color: '#e2e8f0' }}>
            Costed BOQ Checklist
          </h2>
          <button
            onClick={applyAllCmpd}
            style={{
              background: 'linear-gradient(135deg, #b45309, #d97706)',
              border: 'none',
              borderRadius: '6px',
              color: '#fff',
              fontSize: '11px',
              fontWeight: 700,
              padding: '5px 12px',
              cursor: 'pointer',
              letterSpacing: '0.3px',
            }}
          >
            Use CMPD Values for All
          </button>
        </div>

        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', color: '#94a3b8', fontSize: '12px' }}>
          <input
            type="checkbox"
            checked={showDivOnly}
            onChange={e => setShowDivOnly(e.target.checked)}
            style={{ accentColor: '#f59e0b', width: '14px', height: '14px' }}
          />
          Show divergence flags only
          {showDivOnly && (
            <span style={{
              background: '#7f1d1d',
              color: '#fca5a5',
              fontSize: '10px',
              padding: '1px 7px',
              borderRadius: '999px',
              fontWeight: 700,
            }}>
              {computedRows.filter(r => r.divergence > DIVERGENCE_THRESHOLD).length} flagged
            </span>
          )}
        </label>
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', minWidth: '900px' }}>
          <thead>
            <tr style={{
              background: '#0f172a',
              color: '#64748b',
              fontSize: '10px',
              textTransform: 'uppercase',
              letterSpacing: '0.8px',
            }}>
              {['ITEM', 'DESCRIPTION', 'QTY', 'BACKUP #', 'UNIT COST (₱)', 'AMOUNT', 'STATUS', 'CHECK'].map(h => (
                <th key={h} style={{
                  padding: '10px 12px',
                  textAlign: h === 'DESCRIPTION' ? 'left' : 'right',
                  whiteSpace: 'nowrap',
                  borderBottom: '1px solid #1e293b',
                  ...(h === 'ITEM' || h === 'DESCRIPTION' ? { textAlign: 'left' } : {}),
                }}>
                  {h}
                </th>
              ))}
              <th style={{ padding: '10px 12px', borderBottom: '1px solid #1e293b' }}></th>
            </tr>
          </thead>
          <tbody>
            {displayRows.map((row, idx) => {
              const divPct = (row.divergence * 100).toFixed(1);
              const isDiverging = row.divergence > DIVERGENCE_THRESHOLD;
              const isSelected = row.id === selectedId;
              const sc = STATUS_COLORS[row.status] || STATUS_COLORS['Pending'];

              return (
                <tr
                  key={row.id}
                  onClick={() => { setSelectedId(row.id); onRowSelect && onRowSelect(row); }}
                  style={{
                    borderBottom: '1px solid #1e293b',
                    background: isSelected ? '#1e3a5f' : idx % 2 === 0 ? '#020617' : '#050d1a',
                    cursor: 'pointer',
                    transition: 'background 0.1s',
                  }}
                  onMouseEnter={e => { if (!isSelected) e.currentTarget.style.background = '#0f172a'; }}
                  onMouseLeave={e => { if (!isSelected) e.currentTarget.style.background = idx % 2 === 0 ? '#020617' : '#050d1a'; }}
                >
                  {/* ITEM */}
                  <td style={{ padding: '9px 12px', fontFamily: 'JetBrains Mono, monospace', color: '#7dd3fc', whiteSpace: 'nowrap', fontSize: '11px' }}>
                    {row.id}
                  </td>
                  {/* DESCRIPTION */}
                  <td style={{ padding: '9px 12px', color: '#cbd5e1', maxWidth: '280px' }}>
                    {row.desc}
                  </td>
                  {/* QTY */}
                  <td style={{ padding: '9px 12px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600, color: '#e2e8f0' }}>
                    {row.qty.toLocaleString('en-US', { maximumFractionDigits: 2 })}
                  </td>
                  {/* BACKUP # */}
                  <td style={{ padding: '9px 12px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', color: '#64748b' }}>
                    {row.backup.toLocaleString('en-US', { maximumFractionDigits: 2 })}
                  </td>
                  {/* UNIT COST */}
                  <td style={{ padding: '9px 12px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', color: row.usingCmpd ? '#fbbf24' : '#94a3b8' }}>
                    {row.unitCost.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                  {/* AMOUNT */}
                  <td style={{ padding: '9px 12px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 700, color: '#34d399', whiteSpace: 'nowrap' }}>
                    {fmt(row.amount)}
                  </td>
                  {/* STATUS */}
                  <td style={{ padding: '9px 12px', textAlign: 'center' }}>
                    <select
                      value={row.status}
                      onChange={e => { e.stopPropagation(); setStatus(row.id, e.target.value); }}
                      onClick={e => e.stopPropagation()}
                      style={{
                        background: sc.bg,
                        color: sc.color,
                        border: `1px solid ${sc.border}`,
                        borderRadius: '6px',
                        fontSize: '10px',
                        fontWeight: 700,
                        padding: '3px 6px',
                        cursor: 'pointer',
                        outline: 'none',
                        fontFamily: 'Inter, sans-serif',
                      }}
                    >
                      <option value="Confirmed">✓ Confirmed</option>
                      <option value="Pending">⏳ Pending</option>
                      <option value="Flagged">⚠️ Flagged</option>
                    </select>
                  </td>
                  {/* CHECK divergence */}
                  <td style={{ padding: '9px 12px', textAlign: 'right' }}>
                    <span style={{
                      fontFamily: 'JetBrains Mono, monospace',
                      fontSize: '11px',
                      fontWeight: 700,
                      color: isDiverging ? '#f87171' : '#22c55e',
                    }}>
                      {isDiverging ? '⚠ ' : '✓ '}{divPct}%
                    </span>
                  </td>
                  {/* CMPD Button */}
                  <td style={{ padding: '9px 12px', textAlign: 'center' }}>
                    <button
                      onClick={e => { e.stopPropagation(); applyOneCmpd(row.id); }}
                      style={{
                        background: row.usingCmpd ? '#052e16' : '#1c1917',
                        border: `1px solid ${row.usingCmpd ? '#065f46' : '#78350f'}`,
                        borderRadius: '6px',
                        color: row.usingCmpd ? '#34d399' : '#fbbf24',
                        fontSize: '10px',
                        fontWeight: 600,
                        padding: '3px 8px',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {row.usingCmpd ? '✓ CMPD' : 'Use CMPD Value'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            <tr style={{ background: '#0f172a', borderTop: '2px solid #1e3a5f' }}>
              <td colSpan={5} style={{ padding: '12px 18px', textAlign: 'right', color: '#64748b', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                Grand Total Direct Cost
              </td>
              <td colSpan={4} style={{ padding: '12px 18px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 900, fontSize: '16px', color: '#34d399' }}>
                {fmt(grandTotal)}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
