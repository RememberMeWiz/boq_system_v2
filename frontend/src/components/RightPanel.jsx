import React, { useState } from 'react';

// ---------------------------------------------------------------------------
// BOQ Executive Cost Summary + Element Inspector — Right Sidebar
// ---------------------------------------------------------------------------

const TRADE_ORDER = [
  'Concrete Works',
  'Steel Reinforcement',
  'Masonry Works',
  'Earthworks',
  'Roofing & Ceiling',
  'Tile & Flooring',
  'Painting Works',
  'Plumbing Works',
  'Electrical Works',
  'Sanitary/Mechanical',
  'Special Works',
];

const TRADE_COLORS = {
  'Concrete Works':      '#f97316',
  'Steel Reinforcement': '#06b6d4',
  'Masonry Works':       '#eab308',
  'Earthworks':          '#f59e0b',
  'Roofing & Ceiling':   '#14b8a6',
  'Tile & Flooring':     '#3b82f6',
  'Painting Works':      '#8b5cf6',
  'Plumbing Works':      '#a855f7',
  'Electrical Works':    '#ec4899',
  'Sanitary/Mechanical': '#f43f5e',
  'Special Works':       '#10b981',
};

const fmt = n => `₱${Number(n || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

// ---------------------------------------------------------------------------
function ExecutiveSummary({ tradeTotals }) {
  const [collapsed, setCollapsed] = useState(false);

  const grandTotal = Object.values(tradeTotals || {}).reduce((s, v) => s + v, 0);
  const genReq = grandTotal * 0.0325 + 18500; // 1% mob + 1.5% temp + 0.75% safety + ₱18,500 permits
  const overallTotal = grandTotal + genReq;

  return (
    <div style={{
      background: '#0a0f1e',
      border: '1px solid #1e293b',
      borderRadius: '14px',
      overflow: 'hidden',
      marginBottom: '14px',
    }}>
      {/* Header */}
      <div style={{
        padding: '12px 16px',
        background: '#0f172a',
        borderBottom: collapsed ? 'none' : '1px solid #1e293b',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span style={{ fontSize: '11px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1.5px' }}>
          BOQ Executive Cost Summary
        </span>
        <button
          onClick={() => setCollapsed(c => !c)}
          style={{
            background: 'none', border: 'none',
            color: '#475569', cursor: 'pointer',
            fontSize: '11px', fontWeight: 600,
            fontFamily: 'Inter, sans-serif',
          }}
        >
          {collapsed ? '[+]' : '[-]'} {collapsed ? 'Expand' : 'Collapse'}
        </button>
      </div>

      {!collapsed && (
        <div style={{ padding: '12px 16px' }}>
          {/* Per-trade rows */}
          {TRADE_ORDER.map((trade, i) => {
            const amount = tradeTotals?.[trade] || 0;
            if (amount === 0) return null;
            const color = TRADE_COLORS[trade] || '#64748b';
            return (
              <div key={trade} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '6px 0',
                borderBottom: '1px solid #0f172a',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: color, flexShrink: 0 }} />
                  <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                    Trade {['I','II','III','IV','V','VI','VII','VIII','IX','X','XI'][i] || (i+1)}: {trade}
                  </span>
                </div>
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '12px', fontWeight: 700, color }}>
                  {fmt(amount)}
                </span>
              </div>
            );
          })}

          {/* Section I General Requirements */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '6px 0',
            borderBottom: '1px solid #0f172a',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#64748b', flexShrink: 0 }} />
              <span style={{ fontSize: '11px', color: '#64748b' }}>General Requirements</span>
            </div>
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '12px', fontWeight: 700, color: '#64748b' }}>
              {fmt(genReq)}
            </span>
          </div>

          {/* Grand Total */}
          <div style={{
            marginTop: '12px',
            padding: '12px',
            background: 'linear-gradient(135deg, #052e16, #0a1628)',
            border: '1px solid #065f46',
            borderRadius: '10px',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '10px', color: '#6ee7b7', letterSpacing: '1.5px', textTransform: 'uppercase', marginBottom: '4px' }}>
              Grand Total Direct Cost
            </div>
            <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '20px', fontWeight: 900, color: '#34d399' }}>
              {fmt(overallTotal)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
function ElementInspector({ element }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div style={{
      background: '#0a0f1e',
      border: '1px solid #1e293b',
      borderRadius: '14px',
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        padding: '12px 16px',
        background: '#0f172a',
        borderBottom: collapsed ? 'none' : '1px solid #1e293b',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span style={{ fontSize: '11px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1.5px' }}>
          Element Inspector
        </span>
        <button
          onClick={() => setCollapsed(c => !c)}
          style={{
            background: 'none', border: 'none',
            color: '#475569', cursor: 'pointer',
            fontSize: '11px', fontWeight: 600,
            fontFamily: 'Inter, sans-serif',
          }}
        >
          {collapsed ? '[+]' : '[-]'} {collapsed ? 'Expand' : 'Collapse'}
        </button>
      </div>

      {!collapsed && (
        <div style={{ padding: '14px 16px' }}>
          {!element ? (
            <p style={{ fontSize: '11px', color: '#475569', textAlign: 'center', lineHeight: '1.6', margin: 0 }}>
              Select an element on the drawing canvas or a row in the BOQ checklist table to review or override its classification.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {[
                { label: 'Element ID',    value: element.id || element.element_id },
                { label: 'Type',          value: element.trade || element.element_type },
                { label: 'Description',   value: element.desc || element.description },
                { label: 'Qty',           value: `${element.qty ?? element.quantity ?? '—'} ${element.unit || ''}` },
                { label: 'Backup #',      value: element.backup ?? '—' },
                { label: 'Unit Cost',     value: element.unitCost != null ? `₱${element.unitCost.toFixed(2)}` : '—' },
                { label: 'Amount',        value: element.amount != null ? `₱${element.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}` : '—' },
                { label: 'Status',        value: element.status || '—' },
              ].map(({ label, value }) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', fontSize: '11px' }}>
                  <span style={{ color: '#64748b', flexShrink: 0 }}>{label}</span>
                  <span style={{ color: '#cbd5e1', fontFamily: 'JetBrains Mono, monospace', textAlign: 'right', wordBreak: 'break-all' }}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
export default function RightPanel({ tradeTotals, selectedElement }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
      <ExecutiveSummary tradeTotals={tradeTotals} />
      <ElementInspector element={selectedElement} />
    </div>
  );
}
