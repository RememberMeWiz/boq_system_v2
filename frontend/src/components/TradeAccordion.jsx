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
// Helpers
// ---------------------------------------------------------------------------

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

  const section1Total = (rows['I'] && rows['I'].length > 0)
    ? sectionTotal(rows['I'])
    : (sub2_13 > 0 ? (sub2_13 * (SECTION_I_PCTS.mobilization + SECTION_I_PCTS.temp_facilities + SECTION_I_PCTS.safety) + 18500) : 0);

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

const PREFIX_TO_SECTION = {
  'GEN': 'I',   'I': 'I',   '1': 'I',   1: 'I',
  'EW': 'II',   'II': 'II',  '2': 'II',  2: 'II',
  'CON': 'III', 'FRM': 'III', 'III': 'III', '3': 'III', 3: 'III',
  'MW': 'IV',   'MAS': 'IV', 'IV': 'IV',   '4': 'IV',  4: 'IV',
  'REB': 'V',   'STL': 'V', 'MET': 'V', 'V': 'V', '5': 'V', 5: 'V',
  'RF': 'VI',   'ROOF': 'VI', 'VI': 'VI',  '6': 'VI',  6: 'VI',
  'DR': 'VII',  'WIN': 'VII', 'VII': 'VII', '7': 'VII', 7: 'VII',
  'TL': 'VIII', 'FLR': 'VIII', 'VIII': 'VIII', '8': 'VIII', 8: 'VIII',
  'PNT': 'IX',  'IX': 'IX',  '9': 'IX',  9: 'IX',
  'PLM': 'X',   'X': 'X',    '10': 'X', 10: 'X',
  'ELC': 'XI',  'XI': 'XI',  '11': 'XI', 11: 'XI',
  'MCH': 'XII', 'XII': 'XII', '12': 'XII', 12: 'XII',
  'SP': 'XIII', 'XIII': 'XIII', '13': 'XIII', 13: 'XIII',
};

const ALL_IDS = SECTION_META.map(s => s.id);

// ---------------------------------------------------------------------------
// Main TradeAccordion export
// ---------------------------------------------------------------------------
export default function TradeAccordion({ boqItems }) {
  // Group items by section_id or item_code prefix
  const groupBoqItems = useCallback((items) => {
    const grouped = {};
    ALL_IDS.forEach(sid => { grouped[sid] = []; });
    if (items && Array.isArray(items) && items.length > 0) {
      items.forEach(item => {
        let rawPrefix = item.section_id !== undefined ? item.section_id : (item.item_code ? item.item_code.split('-')[0] : 'III');
        if (typeof rawPrefix === 'number') rawPrefix = String(rawPrefix);
        const sid = PREFIX_TO_SECTION[rawPrefix] || rawPrefix || 'III';
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
    }
    return grouped;
  }, []);

  const [rows, setRows] = useState(() => groupBoqItems(boqItems));

  // Sync rows whenever boqItems prop changes
  React.useEffect(() => {
    setRows(groupBoqItems(boqItems));
  }, [boqItems, groupBoqItems]);

  // Open state — all open by default
  const [openSections, setOpenSections] = useState(() =>
    Object.fromEntries(ALL_IDS.map(id => [id, true]))
  );
  const allOpen = ALL_IDS.every(id => openSections[id]);

  const toggleSection = useCallback((id) => {
    setOpenSections(prev => ({ ...prev, [id]: !prev[id] }));
  }, []);

  const toggleAll = useCallback(() => {
    setOpenSections(Object.fromEntries(ALL_IDS.map(id => [id, !allOpen])));
  }, [allOpen]);

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

  const totalItemCount = useMemo(() =>
    Object.values(rows).reduce((acc, list) => acc + (list ? list.length : 0), 0),
    [rows]
  );

  if (totalItemCount === 0) {
    return (
      <div style={{ background: '#0a0f1e', border: '1px solid #1e293b', borderRadius: '14px', padding: '60px 20px', textAlign: 'center', color: '#64748b', margin: '20px 0' }}>
        <div style={{ fontSize: '32px', marginBottom: '12px' }}>📊</div>
        <div style={{ fontSize: '15px', fontWeight: 700, color: '#e2e8f0', marginBottom: '6px' }}>No Trade Accordion Items Loaded</div>
        <div style={{ fontSize: '12px', color: '#94a3b8', maxWidth: '400px', margin: '0 auto' }}>
          Click <strong>"📥 Import PDF/DXF"</strong> or select a drawing plan above to compute itemized 13-trade takeoff quantities.
        </div>
      </div>
    );
  }

  return (
    <div style={{ fontFamily: 'Inter, system-ui, sans-serif', padding: '4px 0' }}>
      {/* Cost Summary Card */}
      <CostSummaryCard rows={rows} allSectionIds={ALL_IDS} />

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
