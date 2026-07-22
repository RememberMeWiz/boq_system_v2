import React, { useState, useRef } from 'react';

const TYPE_COLORS = {
  footing:      { fill: 'rgba(59,130,246,0.3)',  stroke: '#3b82f6', label: 'Footing'       },
  column:       { fill: 'rgba(249,115,22,0.3)',  stroke: '#f97316', label: 'Column'        },
  beam:         { fill: 'rgba(234,179,8,0.3)',   stroke: '#eab308', label: 'Beam'          },
  slab:         { fill: 'rgba(34,197,94,0.3)',   stroke: '#22c55e', label: 'Slab'          },
  chb_wall:     { fill: 'rgba(20,184,166,0.3)',  stroke: '#14b8a6', label: 'CHB Wall'      },
  unclassified: { fill: 'rgba(168,85,247,0.3)',  stroke: '#a855f7', label: 'Unclassified'  },
};

// Mock element overlay data (when no live API data is available)
const MOCK_ELEMENTS = [
  { element_id:'G-4a',  element_type:'footing',  label:'G-4',  bounding_box:[40,  40,  90,  80 ], location:'Grid G-4', length:1.5, width:1.5, height:0.40, count:1 },
  { element_id:'G-4b',  element_type:'footing',  label:'G-4',  bounding_box:[125, 40,  175, 80 ], location:'Grid G-4', length:1.5, width:1.5, height:0.40, count:1 },
  { element_id:'G-4c',  element_type:'footing',  label:'G-4',  bounding_box:[210, 40,  260, 80 ], location:'Grid G-4', length:1.5, width:1.5, height:0.40, count:1 },
  { element_id:'G-4d',  element_type:'footing',  label:'G-4',  bounding_box:[295, 40,  345, 80 ], location:'Grid G-4', length:1.5, width:1.5, height:0.40, count:1 },
  { element_id:'G-4e',  element_type:'footing',  label:'G-4',  bounding_box:[380, 40,  430, 80 ], location:'Grid G-4', length:1.5, width:1.5, height:0.40, count:1 },
  { element_id:'GS-5',  element_type:'slab',     label:'GS-5', bounding_box:[40,  105, 130, 195], location:'Slab GS-5', length:3.2, width:2.8, height:0.10, count:1 },
  { element_id:'W-3',   element_type:'column',   label:'W-3',  bounding_box:[185, 110, 225, 190], location:'Column W-3', length:0.30, width:0.30, height:3.0, count:1 },
  { element_id:'GS-7',  element_type:'slab',     label:'GS-7', bounding_box:[295, 105, 435, 195], location:'Slab GS-7', length:4.5, width:3.0, height:0.10, count:1 },
  { element_id:'C-1',   element_type:'column',   label:'C-1',  bounding_box:[40,  220, 85,  265], location:'Column C-1', length:0.30, width:0.30, height:3.0, count:1 },
  { element_id:'GB-1',  element_type:'beam',     label:'GB-1', bounding_box:[115, 230, 200, 260], location:'Beam GB-1',  length:3.5, width:0.25, height:0.40, count:1 },
  { element_id:'C-2',   element_type:'column',   label:'C-2',  bounding_box:[225, 220, 270, 265], location:'Column C-2', length:0.30, width:0.30, height:3.0, count:1 },
  { element_id:'GB-2',  element_type:'beam',     label:'GB-2', bounding_box:[300, 230, 385, 260], location:'Beam GB-2',  length:3.5, width:0.25, height:0.40, count:1 },
  { element_id:'C-3',   element_type:'column',   label:'C-3',  bounding_box:[405, 220, 450, 265], location:'Column C-3', length:0.30, width:0.30, height:3.0, count:1 },
];

const LEGEND_TYPES = ['footing','column','beam','slab','chb_wall','unclassified'];

export default function BlueprintViewer({ elements, drawingName, onElementSelect }) {
  const [viewMode, setViewMode] = useState('type'); // 'type' | 'confidence'
  const [fitKey, setFitKey] = useState(0);
  const [selectedId, setSelectedId] = useState(null);

  const displayElements = (elements && elements.length > 0) ? elements : MOCK_ELEMENTS;

  const getStyle = (el) => {
    if (viewMode === 'confidence') {
      const conf = el.confidence ?? 0.85;
      const g = Math.round(conf * 200);
      return { fill: `rgba(0,${g},80,0.3)`, stroke: `rgb(0,${g},80)` };
    }
    return TYPE_COLORS[el.element_type?.toLowerCase()] || TYPE_COLORS.unclassified;
  };

  const handleSelect = (el) => {
    setSelectedId(el.element_id);
    onElementSelect && onElementSelect(el);
  };

  return (
    <div style={{ background: '#0a0f1e', border: '1px solid #1e293b', borderRadius: '14px', overflow: 'hidden', marginBottom: '14px' }}>
      {/* Viewer Toolbar */}
      <div style={{
        padding: '10px 16px',
        background: '#0f172a',
        borderBottom: '1px solid #1e293b',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '8px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '12px', fontWeight: 700, color: '#60a5fa' }}>
            🗺️ STRUCTURAL FRAMING PLAN VIEW
          </span>
          <span style={{ fontSize: '10px', color: '#475569', fontFamily: 'JetBrains Mono, monospace' }}>
            {drawingName || 'plan part 1.pdf (A-1)'}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={() => setFitKey(k => k + 1)}
            style={{
              background: '#1e293b', border: '1px solid #334155',
              borderRadius: '6px', color: '#94a3b8',
              fontSize: '11px', fontWeight: 600, padding: '4px 10px', cursor: 'pointer',
              fontFamily: 'Inter, sans-serif',
            }}
          >
            Fit to view
          </button>
          {/* By type / By confidence toggle */}
          <div style={{ display: 'flex', borderRadius: '7px', overflow: 'hidden', border: '1px solid #334155' }}>
            {['type','confidence'].map(mode => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                style={{
                  background: viewMode === mode ? '#3b82f6' : '#1e293b',
                  border: 'none', color: viewMode === mode ? '#fff' : '#64748b',
                  fontSize: '11px', fontWeight: 600, padding: '4px 12px', cursor: 'pointer',
                  fontFamily: 'Inter, sans-serif',
                  transition: 'all 0.15s',
                }}
              >
                By {mode}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Canvas */}
      <div style={{ position: 'relative', background: '#020617', height: '300px', overflow: 'hidden' }}>
        {/* Grid pattern */}
        <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0.07 }}>
          <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#38bdf8" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>

        {/* Scale label */}
        <span style={{ position: 'absolute', top: '8px', left: '12px', fontSize: '9px', fontFamily: 'JetBrains Mono, monospace', color: '#334155' }}>
          SCALE 1:100 | VECTOR PATH LAYER ACTIVE
        </span>
        <span style={{ position: 'absolute', bottom: '8px', right: '12px', fontSize: '9px', color: '#1e293b' }}>
          scroll to zoom · drag to pan
        </span>

        {/* Element overlays */}
        <svg key={fitKey} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}>
          {displayElements.map(el => {
            const box = el.bounding_box || [50, 50, 130, 100];
            const s = getStyle(el);
            const isSelected = el.element_id === selectedId;
            return (
              <g key={el.element_id} onClick={() => handleSelect(el)} style={{ cursor: 'pointer' }}>
                <rect
                  x={box[0]} y={box[1]}
                  width={box[2] - box[0]} height={box[3] - box[1]}
                  fill={s.fill}
                  stroke={isSelected ? '#fff' : s.stroke}
                  strokeWidth={isSelected ? 2.5 : 1.5}
                  rx={3}
                  style={{ transition: 'stroke 0.1s' }}
                />
                <text
                  x={(box[0] + box[2]) / 2}
                  y={(box[1] + box[3]) / 2 + 4}
                  textAnchor="middle"
                  style={{ fontSize: '9px', fill: '#fff', fontFamily: 'JetBrains Mono, monospace', fontWeight: 700, pointerEvents: 'none' }}
                >
                  {el.label || el.element_id}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div style={{
        padding: '8px 16px',
        background: '#0f172a',
        borderTop: '1px solid #1e293b',
        display: 'flex',
        gap: '16px',
        flexWrap: 'wrap',
      }}>
        {LEGEND_TYPES.map(type => {
          const s = TYPE_COLORS[type];
          return (
            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '2px', background: s.fill, border: `1.5px solid ${s.stroke}`, flexShrink: 0 }} />
              <span style={{ fontSize: '10px', color: '#64748b', fontWeight: 500 }}>{s.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
