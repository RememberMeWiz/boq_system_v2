import React, { useState, useCallback, useMemo } from 'react';

// ---------------------------------------------------------------------------
// Static 13-trade section metadata
// ---------------------------------------------------------------------------
const SECTION_META = [
  { id: 'I',    label: 'General Requirements',       icon: '🏗️',  color: 'text-slate-400',   accent: '#64748b' },
  { id: 'II',   label: 'Earthworks',                 icon: '⛏️',  color: 'text-amber-400',   accent: '#f59e0b' },
  { id: 'III',  label: 'Concrete Works & Formworks', icon: '🧱',  color: 'text-orange-400',  accent: '#f97316' },
  { id: 'IV',   label: 'Masonry Works',              icon: '🪨',  color: 'text-yellow-400',  accent: '#eab308' },
  { id: 'V',    label: 'Metals & Steel Reinforcement', icon: '⚙️', color: 'text-cyan-400',   accent: '#06b6d4' },
  { id: 'VI',   label: 'Roofing & Ceiling Works',    icon: '🏠',  color: 'text-teal-400',    accent: '#14b8a6' },
  { id: 'VII',  label: 'Doors & Windows',            icon: '🚪',  color: 'text-sky-400',     accent: '#0ea5e9' },
  { id: 'VIII', label: 'Tile & Flooring Works',      icon: '🪟',  color: 'text-blue-400',    accent: '#3b82f6' },
  { id: 'IX',   label: 'Painting Works',             icon: '🎨',  color: 'text-violet-400',  accent: '#8b5cf6' },
  { id: 'X',    label: 'Plumbing Works',             icon: '🔧',  color: 'text-purple-400',  accent: '#a855f7' },
  { id: 'XI',   label: 'Electrical Works',           icon: '⚡',  color: 'text-pink-400',    accent: '#ec4899' },
  { id: 'XII',  label: 'Sanitary / Mechanical',      icon: '❄️',  color: 'text-rose-400',    accent: '#f43f5e' },
  { id: 'XIII', label: 'Special Works',              icon: '✨',  color: 'text-emerald-400', accent: '#10b981' },
];

// ---------------------------------------------------------------------------
// Mock BOQ line items — one seeded dataset per section
// Replace with live API data by swapping buildInitialRows() return value
// ---------------------------------------------------------------------------
function buildInitialRows() {
  return {
    I: [
      { id: 'I-01', code: 'GR-001', desc: 'Mobilization & Demobilization', qty: 1,    unit: 'lot',   mat: 0,       lab: 18500, eqp: 5000 },
      { id: 'I-02', code: 'GR-002', desc: 'Temporary Facilities & Utilities', qty: 1, unit: 'lot',   mat: 12000,   lab: 8500,  eqp: 0    },
      { id: 'I-03', code: 'GR-003', desc: 'Safety, Health & PPE Program',   qty: 1,   unit: 'lot',   mat: 4500,    lab: 3000,  eqp: 0    },
      { id: 'I-04', code: 'GR-004', desc: 'Permits & Government Clearances', qty: 1,  unit: 'lot',   mat: 18500,   lab: 0,     eqp: 0    },
    ],
    II: [
      { id: 'II-01', code: 'EW-001', desc: 'Site Clearing & Grubbing',        qty: 120,  unit: 'sq.m.',  mat: 0,      lab: 85,    eqp: 65   },
      { id: 'II-02', code: 'EW-002', desc: 'Excavation for Isolated Footings', qty: 18.2, unit: 'cu.m.', mat: 0,      lab: 350,   eqp: 0    },
      { id: 'II-03', code: 'EW-003', desc: 'Structural Backfill (Compacted)',  qty: 11.4, unit: 'cu.m.', mat: 0,      lab: 280,   eqp: 0    },
      { id: 'II-04', code: 'EW-004', desc: 'Gravel Bedding (100mm under Ftg)', qty: 0.9, unit: 'cu.m.', mat: 1650,   lab: 0,     eqp: 0    },
      { id: 'II-05', code: 'EW-005', desc: 'Soil Poisoning (Anti-termite)',    qty: 600,  unit: 'ltr',   mat: 185,    lab: 25,    eqp: 0    },
    ],
    III: [
      { id: 'III-01', code: 'CW-001', desc: 'Isolated Footing Conc. Class A (4 pcs)', qty: 3.78,  unit: 'cu.m.', mat: 5600,  lab: 850,  eqp: 250 },
      { id: 'III-02', code: 'CW-002', desc: 'Column Concrete Class A (6 cols)',        qty: 2.62,  unit: 'cu.m.', mat: 5600,  lab: 850,  eqp: 250 },
      { id: 'III-03', code: 'CW-003', desc: 'Beam Concrete Class A',                   qty: 3.15,  unit: 'cu.m.', mat: 5600,  lab: 850,  eqp: 250 },
      { id: 'III-04', code: 'CW-004', desc: 'Slab-on-Grade Conc. Class B (100mm)',     qty: 12.00, unit: 'cu.m.', mat: 5100,  lab: 850,  eqp: 250 },
      { id: 'III-05', code: 'FW-001', desc: 'Formwork — Marine Plywood (1/2")',         qty: 54.2,  unit: 'sq.m.', mat: 750,   lab: 210,  eqp: 0   },
      { id: 'III-06', code: 'FW-002', desc: 'Form Lumber (Scaffolding & Shores)',       qty: 379.4, unit: 'bd.ft', mat: 48,    lab: 12,   eqp: 0   },
    ],
    IV: [
      { id: 'IV-01', code: 'MW-001', desc: '150mm CHB Laying (Exterior Walls)',   qty: 338,  unit: 'pc',    mat: 22.32, lab: 19.20, eqp: 1.20 },
      { id: 'IV-02', code: 'MW-002', desc: 'Mortar Class B — CHB Bedding',        qty: 8.45, unit: 'bags',  mat: 205.36, lab: 0,    eqp: 0    },
      { id: 'IV-03', code: 'MW-003', desc: 'Plaster — 16mm Scratch & Finish (2 Faces)', qty: 54.0, unit: 'sq.m.', mat: 0,  lab: 85,   eqp: 0    },
      { id: 'IV-04', code: 'MW-004', desc: 'Sand (Mortar + Plastering)',           qty: 0.72, unit: 'cu.m.', mat: 1473.21, lab: 0, eqp: 0    },
    ],
    V: [
      { id: 'V-01', code: 'RB-001', desc: 'Footing Mat — 16mmø Rebar (PNS 49)',       qty: 218.9, unit: 'kg',  mat: 42.68, lab: 12,   eqp: 2.50 },
      { id: 'V-02', code: 'RB-002', desc: 'Column Main Bars — 20mmø (40db Splice)',   qty: 185.4, unit: 'kg',  mat: 42.68, lab: 12,   eqp: 2.50 },
      { id: 'V-03', code: 'RB-003', desc: 'Beam Main Bars — 16mmø',                  qty: 145.2, unit: 'kg',  mat: 42.68, lab: 12,   eqp: 2.50 },
      { id: 'V-04', code: 'RB-004', desc: 'Beam Stirrups — 10mmø (135° Seismic Hook)', qty: 47.5, unit: 'kg', mat: 42.68, lab: 12,   eqp: 2.50 },
      { id: 'V-05', code: 'RB-005', desc: 'Column Ties — 10mmø',                     qty: 38.6,  unit: 'kg',  mat: 42.68, lab: 12,   eqp: 2.50 },
      { id: 'V-06', code: 'RB-006', desc: '#16 G.I. Tie Wire',                        qty: 9.54,  unit: 'kg',  mat: 62.50, lab: 12,   eqp: 0    },
      { id: 'V-07', code: 'SS-001', desc: 'Structural Steel Members (Beams/Lintels)', qty: 850,   unit: 'kg',  mat: 68,    lab: 15,   eqp: 5    },
    ],
    VI: [
      { id: 'VI-01', code: 'RF-001', desc: 'Long-span Corrugated Roof Sheets (+12% lap)', qty: 118.9, unit: 'sq.m.', mat: 620,  lab: 180, eqp: 0 },
      { id: 'VI-02', code: 'RF-002', desc: 'Roofing Rivets & Lead Washers',               qty: 3092,  unit: 'pc',    mat: 3.50, lab: 0,   eqp: 0 },
      { id: 'VI-03', code: 'CG-001', desc: 'Hardiflex Ceiling Panels (+5% waste)',         qty: 94.5,  unit: 'sq.m.', mat: 295,  lab: 120, eqp: 0 },
      { id: 'VI-04', code: 'CG-002', desc: 'Metal Furring (C-Runners & Wall Angles)',      qty: 225.0, unit: 'lin.m', mat: 45,   lab: 15,  eqp: 0 },
    ],
    VII: [
      { id: 'VII-01', code: 'DW-001', desc: 'Aluminum Sliding Windows (Grade A)',    qty: 12.0, unit: 'sq.m.', mat: 4200,  lab: 650, eqp: 0 },
      { id: 'VII-02', code: 'DW-002', desc: 'Panel Door Set (90cm x 210cm)',          qty: 3,    unit: 'set',   mat: 8500,  lab: 900, eqp: 0 },
      { id: 'VII-03', code: 'DW-003', desc: 'Flush Door Set (Comfort Rooms)',         qty: 2,    unit: 'set',   mat: 4200,  lab: 700, eqp: 0 },
      { id: 'VII-04', code: 'DW-004', desc: 'Door Frame Lumber (Yakal)',              qty: 40.0, unit: 'bd.ft', mat: 48,    lab: 12,  eqp: 0 },
    ],
    VIII: [
      { id: 'VIII-01', code: 'TF-001', desc: '60x60 Ceramic Floor Tiles (+8% waste)', qty: 86.4, unit: 'sq.m.', mat: 850,   lab: 220, eqp: 0 },
      { id: 'VIII-02', code: 'TF-002', desc: '30x60 Wall Tiles — CR & Kitchen',       qty: 32.4, unit: 'sq.m.', mat: 750,   lab: 220, eqp: 0 },
      { id: 'VIII-03', code: 'TF-003', desc: 'Tile Mortar Bed (20mm 1:4)',             qty: 19.2, unit: 'bags',  mat: 205.36, lab: 60, eqp: 0 },
      { id: 'VIII-04', code: 'TF-004', desc: 'Tile Grout & Joint Filler',              qty: 24.0, unit: 'kg',    mat: 95,    lab: 0,   eqp: 0 },
    ],
    IX: [
      { id: 'IX-01', code: 'PW-001', desc: 'Concrete Neutralizer (Masonry)',         qty: 20.0, unit: 'ltr', mat: 185, lab: 0,  eqp: 0 },
      { id: 'IX-02', code: 'PW-002', desc: 'Masonry Primer / Sealer',               qty: 24.0, unit: 'ltr', mat: 220, lab: 0,  eqp: 0 },
      { id: 'IX-03', code: 'PW-003', desc: 'Acrylic Latex Topcoat (2 coats)',        qty: 50.0, unit: 'ltr', mat: 280, lab: 0,  eqp: 0 },
      { id: 'IX-04', code: 'PW-004', desc: 'Ceiling Latex Paint',                   qty: 14.0, unit: 'ltr', mat: 260, lab: 0,  eqp: 0 },
      { id: 'IX-05', code: 'PW-005', desc: 'Red Oxide Metal Primer',                qty: 1.5,  unit: 'ltr', mat: 240, lab: 0,  eqp: 0 },
      { id: 'IX-06', code: 'PW-006', desc: 'Painting Labor — All Surfaces',         qty: 250,  unit: 'sq.m.', mat: 0,  lab: 85, eqp: 0 },
    ],
    X: [
      { id: 'X-01', code: 'PL-001', desc: '4" UPVC Sanitary Sewer Pipe (3m)',  qty: 18, unit: 'pc',  mat: 620,  lab: 150, eqp: 0 },
      { id: 'X-02', code: 'PL-002', desc: '2" UPVC Vent Pipe (3m)',            qty: 9,  unit: 'pc',  mat: 280,  lab: 120, eqp: 0 },
      { id: 'X-03', code: 'PL-003', desc: 'PPR Pressure Pipe (Water Supply)',  qty: 14, unit: 'pc',  mat: 350,  lab: 120, eqp: 0 },
      { id: 'X-04', code: 'PL-004', desc: 'Fixture Set (Lavatory, WC, Sink)',  qty: 4,  unit: 'set', mat: 4500, lab: 850, eqp: 0 },
      { id: 'X-05', code: 'PL-005', desc: 'Catch Basin (Pre-cast)',            qty: 1,  unit: 'lot', mat: 6500, lab: 1800, eqp: 0 },
    ],
    XI: [
      { id: 'XI-01', code: 'EL-001', desc: 'THHN Wire 3.5mm² (Homerun)',        qty: 67.2, unit: 'lin.m', mat: 32,  lab: 18,  eqp: 0 },
      { id: 'XI-02', code: 'EL-002', desc: 'PVC Conduit 20mm (3m)',             qty: 20,   unit: 'pc',    mat: 95,  lab: 40,  eqp: 0 },
      { id: 'XI-03', code: 'EL-003', desc: 'Convenience Outlet (2G 15A)',       qty: 16,   unit: 'pc',    mat: 180, lab: 120, eqp: 0 },
      { id: 'XI-04', code: 'EL-004', desc: 'LED Panel Light (600x600 40W)',     qty: 6,    unit: 'pc',    mat: 850, lab: 150, eqp: 0 },
      { id: 'XI-05', code: 'EL-005', desc: 'Load Center / Panel Board (12-CT)', qty: 1,    unit: 'pc',    mat: 650, lab: 200, eqp: 0 },
    ],
    XII: [
      { id: 'XII-01', code: 'MC-001', desc: 'Split-type AC Unit (1.5 HP)',        qty: 2.5,  unit: 'TR',    mat: 28000, lab: 3500, eqp: 0 },
      { id: 'XII-02', code: 'MC-002', desc: 'Copper Refrigerant Piping (1/4"+3/8")', qty: 11.0, unit: 'lin.m', mat: 650, lab: 180, eqp: 0 },
      { id: 'XII-03', code: 'MC-003', desc: 'Commissioning & Testing',            qty: 1,    unit: 'lot',   mat: 0,     lab: 5000, eqp: 0 },
    ],
    XIII: [
      { id: 'XIII-01', code: 'SW-001', desc: 'Stainless Steel Handrail (Balcony)', qty: 8.0,  unit: 'lin.m', mat: 1450, lab: 350, eqp: 0 },
      { id: 'XIII-02', code: 'SW-002', desc: 'Aluminum Composite Panel Cladding', qty: 16.2, unit: 'sq.m.', mat: 1850, lab: 350, eqp: 0 },
      { id: 'XIII-03', code: 'SW-003', desc: 'Elastomeric Waterproofing (2-coat)', qty: 36.0, unit: 'kg',    mat: 145,  lab: 0,   eqp: 0 },
      { id: 'XIII-04', code: 'SW-004', desc: 'Waterproofing Labor (Roof Deck)',    qty: 30.0, unit: 'sq.m.', mat: 0,    lab: 65,  eqp: 0 },
    ],
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const fmt = (n) => `₱ ${Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const lineTotal = (row) => row.qty * (row.mat + row.lab + row.eqp);
const sectionTotal = (rows) => rows.reduce((s, r) => s + lineTotal(r), 0);

// Section I auto-calculates as % of Sections II–XIII subtotal
const SECTION_I_PCTS = {
  mobilization: 0.010,
  temp_facilities: 0.015,
  safety: 0.0075,
};

// ---------------------------------------------------------------------------
// Cost Summary Card
// ---------------------------------------------------------------------------
function CostSummaryCard({ rows, allSectionIds }) {
  const sectionTotals = useMemo(() =>
    allSectionIds.reduce((acc, sid) => {
      acc[sid] = sectionTotal(rows[sid] || []);
      return acc;
    }, {}),
    [rows, allSectionIds]
  );

  const sub2_13 = allSectionIds
    .filter(s => s !== 'I')
    .reduce((s, sid) => s + (sectionTotals[sid] || 0), 0);

  const section1Total = sectionTotals['I'] ||
    (sub2_13 * (SECTION_I_PCTS.mobilization + SECTION_I_PCTS.temp_facilities + SECTION_I_PCTS.safety) + 18500);

  const grandTotal = sub2_13 + section1Total;

  const totalMat = allSectionIds.reduce((s, sid) =>
    s + (rows[sid] || []).reduce((x, r) => x + r.qty * r.mat, 0), 0);
  const totalLab = allSectionIds.reduce((s, sid) =>
    s + (rows[sid] || []).reduce((x, r) => x + r.qty * r.lab, 0), 0);
  const totalEqp = allSectionIds.reduce((s, sid) =>
    s + (rows[sid] || []).reduce((x, r) => x + r.qty * r.eqp, 0), 0);

  const pct = (v) => grandTotal > 0 ? ((v / grandTotal) * 100).toFixed(1) : '0.0';

  return (
    <div style={{
      background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)',
      border: '1px solid #312e81',
      borderRadius: '16px',
      padding: '24px',
      marginBottom: '20px',
      boxShadow: '0 0 40px rgba(99, 102, 241, 0.15)',
    }}>
      {/* Grand Total */}
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <div style={{ fontSize: '11px', color: '#94a3b8', letterSpacing: '2px', textTransform: 'uppercase', marginBottom: '4px' }}>
          Grand Total Direct Cost
        </div>
        <div style={{ fontSize: '36px', fontWeight: 900, color: '#34d399', letterSpacing: '-1px' }}>
          {fmt(grandTotal)}
        </div>
        <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>
          Material + Labor + Equipment | Sections I – XIII
        </div>
      </div>

      {/* Cost Breakdown Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '20px' }}>
        {[
          { label: 'Total Material', value: totalMat, color: '#60a5fa', bar: '#1d4ed8' },
          { label: 'Total Labor',    value: totalLab, color: '#34d399', bar: '#059669' },
          { label: 'Total Equipment', value: totalEqp, color: '#f59e0b', bar: '#b45309' },
        ].map(({ label, value, color, bar }) => (
          <div key={label} style={{
            background: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '12px',
            padding: '16px',
          }}>
            <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '1px' }}>{label}</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color, fontFamily: 'JetBrains Mono, monospace' }}>
              {fmt(value)}
            </div>
            <div style={{ marginTop: '10px', background: '#1e293b', borderRadius: '4px', height: '6px', overflow: 'hidden' }}>
              <div style={{
                width: `${pct(value)}%`,
                maxWidth: '100%',
                background: `linear-gradient(90deg, ${bar}, ${color})`,
                height: '100%',
                borderRadius: '4px',
                transition: 'width 0.3s ease',
              }} />
            </div>
            <div style={{ fontSize: '11px', color: '#475569', marginTop: '4px' }}>{pct(value)}% of total</div>
          </div>
        ))}
      </div>

      {/* Section I breakdown line */}
      <div style={{
        background: '#0f172a',
        border: '1px solid #1e293b',
        borderRadius: '10px',
        padding: '12px 16px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span style={{ fontSize: '12px', color: '#94a3b8' }}>
          📋 Section I — General Requirements (auto-computed @ 2.5% + ₱18,500 permits)
        </span>
        <span style={{ fontSize: '14px', fontWeight: 700, color: '#94a3b8', fontFamily: 'JetBrains Mono, monospace' }}>
          {fmt(section1Total)}
        </span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Editable rate input
// ---------------------------------------------------------------------------
function RateInput({ value, onChange, color = '#f8fafc' }) {
  return (
    <input
      type="number"
      step="0.01"
      min="0"
      value={value}
      onChange={e => onChange(parseFloat(e.target.value) || 0)}
      style={{
        width: '72px',
        background: '#0f172a',
        border: '1px solid #334155',
        borderRadius: '6px',
        padding: '3px 6px',
        color,
        fontSize: '11px',
        fontFamily: 'JetBrains Mono, monospace',
        textAlign: 'right',
        outline: 'none',
        transition: 'border-color 0.15s',
      }}
      onFocus={e => { e.target.style.borderColor = '#6366f1'; }}
      onBlur={e => { e.target.style.borderColor = '#334155'; }}
    />
  );
}

// ---------------------------------------------------------------------------
// Section panel
// ---------------------------------------------------------------------------
function SectionPanel({ meta, rows, isOpen, onToggle, onRateChange }) {
  const total = sectionTotal(rows);

  return (
    <div style={{
      border: `1px solid #1e293b`,
      borderRadius: '12px',
      overflow: 'hidden',
      background: '#020617',
      boxShadow: isOpen ? `0 0 20px ${meta.accent}18` : 'none',
      transition: 'box-shadow 0.25s ease',
    }}>
      {/* Header */}
      <button
        onClick={onToggle}
        style={{
          width: '100%',
          padding: '14px 18px',
          background: isOpen
            ? `linear-gradient(90deg, ${meta.accent}22, #1e293b)`
            : '#0f172a',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          border: 'none',
          borderBottom: isOpen ? `1px solid ${meta.accent}44` : 'none',
          transition: 'background 0.2s ease',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{
            fontSize: '16px',
            transform: isOpen ? 'rotate(90deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s ease',
            display: 'inline-block',
            color: '#64748b',
          }}>▶</span>
          <span style={{ fontSize: '16px' }}>{meta.icon}</span>
          <span style={{ fontWeight: 700, color: '#e2e8f0', fontSize: '14px' }}>
            Section {meta.id} — {meta.label}
          </span>
          <span style={{
            background: `${meta.accent}22`,
            color: meta.accent,
            border: `1px solid ${meta.accent}55`,
            fontSize: '10px',
            fontWeight: 600,
            padding: '2px 8px',
            borderRadius: '999px',
          }}>
            {rows.length} items
          </span>
        </div>

        <div style={{
          fontFamily: 'JetBrains Mono, monospace',
          fontWeight: 800,
          fontSize: '15px',
          color: '#34d399',
        }}>
          {fmt(total)}
        </div>
      </button>

      {/* Table */}
      {isOpen && (
        <div style={{ overflowX: 'auto', padding: '0' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead>
              <tr style={{ background: '#0f172a', color: '#64748b', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
                <th style={{ padding: '10px 12px', textAlign: 'left', whiteSpace: 'nowrap' }}>Code</th>
                <th style={{ padding: '10px 12px', textAlign: 'left' }}>Description</th>
                <th style={{ padding: '10px 12px', textAlign: 'right', whiteSpace: 'nowrap' }}>Qty</th>
                <th style={{ padding: '10px 8px', textAlign: 'left' }}>Unit</th>
                <th style={{ padding: '10px 12px', textAlign: 'right', whiteSpace: 'nowrap' }}>Mat. Rate (₱)</th>
                <th style={{ padding: '10px 12px', textAlign: 'right', whiteSpace: 'nowrap' }}>Labor Rate (₱)</th>
                <th style={{ padding: '10px 12px', textAlign: 'right', whiteSpace: 'nowrap' }}>Eqp. Rate (₱)</th>
                <th style={{ padding: '10px 12px', textAlign: 'right', whiteSpace: 'nowrap' }}>Unit Total</th>
                <th style={{ padding: '10px 12px', textAlign: 'right', whiteSpace: 'nowrap', color: '#34d399' }}>Amount (₱)</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => {
                const amount = lineTotal(row);
                const unitTotal = row.mat + row.lab + row.eqp;
                return (
                  <tr
                    key={row.id}
                    style={{
                      borderBottom: '1px solid #1e293b',
                      background: idx % 2 === 0 ? '#020617' : '#050d1a',
                      transition: 'background 0.1s',
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = '#0f172a'}
                    onMouseLeave={e => e.currentTarget.style.background = idx % 2 === 0 ? '#020617' : '#050d1a'}
                  >
                    <td style={{ padding: '9px 12px', fontFamily: 'JetBrains Mono, monospace', color: meta.accent, whiteSpace: 'nowrap' }}>{row.code}</td>
                    <td style={{ padding: '9px 12px', color: '#cbd5e1', maxWidth: '240px' }}>{row.desc}</td>
                    <td style={{ padding: '9px 12px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600, color: '#e2e8f0' }}>
                      {row.qty.toLocaleString('en-US', { maximumFractionDigits: 2 })}
                    </td>
                    <td style={{ padding: '9px 8px', color: '#64748b', whiteSpace: 'nowrap' }}>{row.unit}</td>
                    <td style={{ padding: '9px 12px', textAlign: 'right' }}>
                      <RateInput value={row.mat} color="#60a5fa"
                        onChange={v => onRateChange(row.id, 'mat', v)} />
                    </td>
                    <td style={{ padding: '9px 12px', textAlign: 'right' }}>
                      <RateInput value={row.lab} color="#34d399"
                        onChange={v => onRateChange(row.id, 'lab', v)} />
                    </td>
                    <td style={{ padding: '9px 12px', textAlign: 'right' }}>
                      <RateInput value={row.eqp} color="#f59e0b"
                        onChange={v => onRateChange(row.id, 'eqp', v)} />
                    </td>
                    <td style={{ padding: '9px 12px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', color: '#94a3b8' }}>
                      {unitTotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </td>
                    <td style={{ padding: '9px 12px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 700, color: '#34d399', whiteSpace: 'nowrap' }}>
                      {fmt(amount)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
            {/* Section subtotal footer */}
            <tfoot>
              <tr style={{ background: `${meta.accent}11`, borderTop: `1px solid ${meta.accent}33` }}>
                <td colSpan={8} style={{ padding: '10px 12px', textAlign: 'right', color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Section {meta.id} Subtotal
                </td>
                <td style={{ padding: '10px 12px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 800, color: meta.accent, whiteSpace: 'nowrap' }}>
                  {fmt(total)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main TradeAccordion export
// ---------------------------------------------------------------------------
export default function TradeAccordion({ boqItems }) {
  const allIds = SECTION_META.map(s => s.id);

  // Seed from live API data if provided, otherwise use mock data
  const [rows, setRows] = useState(() => {
    if (boqItems && boqItems.length > 0) {
      const grouped = {};
      allIds.forEach(sid => { grouped[sid] = []; });
      boqItems.forEach(item => {
        const sid = item.section_id || 'III';
        if (!grouped[sid]) grouped[sid] = [];
        grouped[sid].push({
          id: item.item_code || `${sid}-${Math.random()}`,
          code: item.item_code || '—',
          desc: item.description || '',
          qty: item.quantity || 0,
          unit: item.unit || '',
          mat: item.material_unit_cost || 0,
          lab: item.labor_unit_cost || 0,
          eqp: item.equipment_unit_cost || 0,
        });
      });
      return grouped;
    }
    return buildInitialRows();
  });

  // Open state — all open by default
  const [openSections, setOpenSections] = useState(() =>
    Object.fromEntries(allIds.map(id => [id, true]))
  );
  const allOpen = allIds.every(id => openSections[id]);

  const toggleSection = useCallback((id) => {
    setOpenSections(prev => ({ ...prev, [id]: !prev[id] }));
  }, []);

  const toggleAll = useCallback(() => {
    setOpenSections(Object.fromEntries(allIds.map(id => [id, !allOpen])));
  }, [allOpen, allIds]);

  const onRateChange = useCallback((rowId, field, value) => {
    setRows(prev => {
      const next = { ...prev };
      for (const sid of Object.keys(next)) {
        const idx = next[sid].findIndex(r => r.id === rowId);
        if (idx !== -1) {
          next[sid] = [...next[sid]];
          next[sid][idx] = { ...next[sid][idx], [field]: value };
          break;
        }
      }
      return next;
    });
  }, []);

  return (
    <div style={{ fontFamily: 'Inter, system-ui, sans-serif', padding: '4px 0' }}>
      {/* Cost Summary Card */}
      <CostSummaryCard rows={rows} allSectionIds={allIds} />

      {/* Toolbar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 800, color: '#e2e8f0' }}>
            📊 DPWH Direct Cost — 13-Trade BOQ Accordion
          </h2>
          <p style={{ margin: '2px 0 0', fontSize: '11px', color: '#475569' }}>
            Inline editing updates section subtotals and grand total in real-time
          </p>
        </div>
        <button
          onClick={toggleAll}
          style={{
            background: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#94a3b8',
            fontSize: '12px',
            padding: '7px 14px',
            cursor: 'pointer',
            transition: 'all 0.15s',
            fontFamily: 'Inter, sans-serif',
          }}
          onMouseEnter={e => { e.target.style.background = '#334155'; e.target.style.color = '#e2e8f0'; }}
          onMouseLeave={e => { e.target.style.background = '#1e293b'; e.target.style.color = '#94a3b8'; }}
        >
          {allOpen ? '▲ Collapse All' : '▼ Expand All'}
        </button>
      </div>

      {/* 13 Section Panels */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {SECTION_META.map(meta => (
          <SectionPanel
            key={meta.id}
            meta={meta}
            rows={rows[meta.id] || []}
            isOpen={openSections[meta.id]}
            onToggle={() => toggleSection(meta.id)}
            onRateChange={onRateChange}
          />
        ))}
      </div>
    </div>
  );
}
