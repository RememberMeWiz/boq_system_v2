import React, { useState, useRef, useCallback, useMemo, useEffect } from 'react';

// ── Layer Color Definitions ──────────────────────────────────────────────────
const TYPE_COLORS = {
  footing:      { stroke: '#3b82f6', label: 'Footing',    rebar: '#ef4444' },
  column:       { stroke: '#f59e0b', label: 'Column',     rebar: '#ef4444' },
  beam:         { stroke: '#eab308', label: 'Beam',       rebar: '#f97316' },
  slab:         { stroke: '#22c55e', label: 'Slab',       rebar: '#a3e635' },
  chb_wall:     { stroke: '#06b6d4', label: 'CHB Wall',   rebar: '#fb923c' },
  unclassified: { stroke: '#a855f7', label: 'Other',      rebar: '#d946ef' },
};

const LAYER_FILTERS = [
  { id: 'all',      label: 'All Layers',  color: '#6366f1' },
  { id: 'footing',  label: 'Footings',    color: '#3b82f6' },
  { id: 'column',   label: 'Columns',     color: '#f59e0b' },
  { id: 'beam',     label: 'Beams',       color: '#eab308' },
  { id: 'slab',     label: 'Slabs',       color: '#22c55e' },
  { id: 'chb_wall', label: 'CHB Walls',   color: '#06b6d4' },
];

// ── Rebar SVG Renderer Helpers ───────────────────────────────────────────────
function renderRebarForElement(el, rebarColor) {
  if (!el.rebar || !Array.isArray(el.rebar)) return null;
  const lines = [];
  const x = el.x || 0, y = el.y || 0, w = el.width || 60, h = el.height || 60;

  el.rebar.forEach((r, ri) => {
    const count = r.count || 3;
    if (r.type === 'horizontal') {
      for (let i = 0; i < count; i++) {
        const yPos = y + (h * (i + 1)) / (count + 1);
        lines.push(
          <line key={`rh_${ri}_${i}`} x1={x + 3} y1={yPos} x2={x + w - 3} y2={yPos}
            stroke={r.color || rebarColor} strokeWidth={1.2} opacity={0.7}
            strokeDasharray={r.type === 'stirrup' ? '3,3' : 'none'} />
        );
      }
    } else if (r.type === 'vertical') {
      for (let i = 0; i < count; i++) {
        const xPos = x + (w * (i + 1)) / (count + 1);
        lines.push(
          <line key={`rv_${ri}_${i}`} x1={xPos} y1={y + 3} x2={xPos} y2={y + h - 3}
            stroke={r.color || rebarColor} strokeWidth={1.2} opacity={0.7} />
        );
      }
    } else if (r.type === 'stirrup') {
      // Stirrup ticks along the beam span
      for (let i = 0; i < count; i++) {
        const xPos = x + (w * (i + 1)) / (count + 1);
        lines.push(
          <line key={`rs_${ri}_${i}`} x1={xPos} y1={y + 2} x2={xPos} y2={y + h - 2}
            stroke={r.color || rebarColor} strokeWidth={1.0} opacity={0.6}
            strokeDasharray="2,2" />
        );
      }
    } else if (r.type === 'diagonal') {
      // Diagonal hatch for slabs
      for (let i = 0; i < count; i++) {
        const offset = (w * (i + 1)) / (count + 1);
        lines.push(
          <line key={`rd_${ri}_${i}`}
            x1={x + offset} y1={y} x2={x + Math.min(offset + h * 0.4, w)} y2={y + h}
            stroke={r.color || rebarColor} strokeWidth={0.8} opacity={0.4} />
        );
      }
    } else if (r.type === 'dots') {
      // Corner dots for column main bars
      const positions = r.positions || [[0.2, 0.2], [0.8, 0.2], [0.2, 0.8], [0.8, 0.8]];
      positions.forEach(([px, py], pi) => {
        lines.push(
          <circle key={`rd_${ri}_${pi}`}
            cx={x + w * px} cy={y + h * py} r={3}
            fill={r.color || rebarColor} opacity={0.8} />
        );
      });
    } else if (r.type === 'dowel') {
      // Vertical dowel ticks for CHB walls
      for (let i = 0; i < count; i++) {
        const xPos = x + (w * (i + 1)) / (count + 1);
        lines.push(
          <line key={`rdw_${ri}_${i}`} x1={xPos} y1={y + 2} x2={xPos} y2={y + h - 2}
            stroke={r.color || rebarColor} strokeWidth={1.5} opacity={0.6}
            strokeDasharray="4,4" />
        );
      }
    } else if (r.type === 'main') {
      // Main bars as corner dots for columns
      const positions = r.positions || [[0.2, 0.2], [0.8, 0.2], [0.2, 0.8], [0.8, 0.8]];
      positions.forEach(([px, py], pi) => {
        lines.push(
          <circle key={`rm_${ri}_${pi}`}
            cx={x + w * px} cy={y + h * py} r={3}
            fill={r.color || rebarColor} opacity={0.8} />
        );
      });
    } else if (r.type === 'tie') {
      // Horizontal tie lines for columns
      for (let i = 0; i < count; i++) {
        const yPos = y + (h * (i + 1)) / (count + 1);
        lines.push(
          <line key={`rt_${ri}_${i}`} x1={x + 3} y1={yPos} x2={x + w - 3} y2={yPos}
            stroke={r.color || rebarColor} strokeWidth={0.8} opacity={0.5}
            strokeDasharray="3,2" />
        );
      }
    }
  });

  return lines;
}

// ── Source Badge Component ────────────────────────────────────────────────────
function SourceBadge({ source, x, y }) {
  const isParsed = source === 'parsed';
  return (
    <g pointerEvents="none">
      <rect x={x} y={y} width={isParsed ? 46 : 55} height={13}
        fill={isParsed ? '#064e3b' : '#78350f'} stroke={isParsed ? '#10b981' : '#f59e0b'}
        strokeWidth={0.8} rx={3} opacity={0.9} />
      <text x={x + 4} y={y + 10} fontSize="8" fontWeight="700"
        fontFamily="JetBrains Mono, monospace"
        fill={isParsed ? '#6ee7b7' : '#fcd34d'}>
        {isParsed ? '🟢 Parsed' : '🟡 Assumed'}
      </text>
    </g>
  );
}


// ══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ══════════════════════════════════════════════════════════════════════════════

export default function BlueprintViewer({
  elements, drawingName, pageImage, comparisonImage,
  framingPlan, suggestions, onElementSelect
}) {
  // ── View mode state ──
  const [viewMode, setViewMode] = useState('original'); // 'original' | 'takeoff'
  const [activeFilter, setActiveFilter] = useState('all');
  const [showLabels, setShowLabels] = useState(false);
  const [showRebar, setShowRebar] = useState(true);
  const [selectedId, setSelectedId] = useState(null);
  const [hoveredEl, setHoveredEl] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(true);

  // ── Zoom & Pan state ──
  const [zoom, setZoom] = useState(1.0);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const viewportRef = useRef(null);

  // ── Mouse wheel zoom (centered at cursor) ──
  const handleWheel = useCallback((e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.12 : 0.12;
    setZoom(prev => Math.min(4.0, Math.max(0.3, prev + delta)));
  }, []);

  // ── Drag-to-pan handlers ──
  const handleMouseDown = useCallback((e) => {
    if (e.button !== 0) return; // left click only
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  }, [pan]);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging) return;
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
  }, [isDragging, dragStart]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Attach wheel listener with passive: false for preventDefault
  useEffect(() => {
    const el = viewportRef.current;
    if (!el) return;
    el.addEventListener('wheel', handleWheel, { passive: false });
    return () => el.removeEventListener('wheel', handleWheel);
  }, [handleWheel]);

  const resetView = () => { setZoom(1.0); setPan({ x: 0, y: 0 }); };

  // ── Clean elements for Original Drawing mode ──
  const cleanElements = useMemo(() => {
    if (!elements || !Array.isArray(elements)) return [];
    return elements.map((el, idx) => {
      const box = el.bounding_box || [50, 50, 130, 100];
      const etype = el.element_type?.toLowerCase() || 'unclassified';
      const label = (el.label && !el.label.includes('VectorPath'))
        ? el.label : `${etype.toUpperCase()}-${idx + 1}`;
      return { ...el, element_id: el.element_id || `el_${idx + 1}`, element_type: etype, label, bounding_box: box };
    });
  }, [elements]);

  // ── Filter elements by active layer ──
  const filteredElements = useMemo(() => {
    if (activeFilter === 'all') return cleanElements;
    return cleanElements.filter(el => el.element_type === activeFilter);
  }, [cleanElements, activeFilter]);

  // ── Filter framing plan by active layer ──
  const filteredFraming = useMemo(() => {
    if (!framingPlan || !Array.isArray(framingPlan)) return [];
    if (activeFilter === 'all') return framingPlan;
    return framingPlan.filter(el => el.type === activeFilter);
  }, [framingPlan, activeFilter]);

  // ── Filtered suggestions ──
  const filteredSuggestions = useMemo(() => {
    if (!suggestions || !Array.isArray(suggestions)) return [];
    return suggestions;
  }, [suggestions]);

  const handleSelect = (el) => {
    setSelectedId(el.id || el.element_id);
    if (onElementSelect) onElementSelect(el);
  };

  // ── Toolbar button style ──
  const tbtn = (active, color = '#6366f1') => ({
    background: active ? `${color}20` : 'transparent',
    border: `1px solid ${active ? color : '#334155'}`,
    borderRadius: '7px',
    color: active ? '#fff' : '#94a3b8',
    fontSize: '11px', fontWeight: 600,
    padding: '5px 12px', cursor: 'pointer',
    transition: 'all 0.15s', whiteSpace: 'nowrap',
  });

  // ── Canvas dimensions for Generated Takeoff Plan ──
  const CANVAS_W = 800, CANVAS_H = 600;

  return (
    <div style={{
      background: '#0a0f1e', border: '1px solid #1e293b', borderRadius: '14px',
      overflow: 'hidden', marginBottom: '14px', boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
    }}>

      {/* ═══ TOP TOOLBAR ═══ */}
      <div style={{
        padding: '10px 18px', background: 'linear-gradient(180deg, #0f172a 0%, #0a0f1e 100%)',
        borderBottom: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', flexWrap: 'wrap', gap: '10px',
      }}>
        {/* Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '16px' }}>🗺️</span>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#f8fafc' }}>
              {viewMode === 'original' ? 'BLUEPRINT VECTOR OVERLAY' : 'GENERATED TAKEOFF PLAN'}
            </div>
            <div style={{ fontSize: '10px', color: '#64748b', fontFamily: 'JetBrains Mono, monospace' }}>
              {drawingName || 'No drawing'} | {viewMode === 'original' ? `${filteredElements.length} vectors` : `${filteredFraming.length} structural elements`} | {Math.round(zoom * 100)}%
            </div>
          </div>
        </div>

        {/* Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          {/* View Mode Toggle */}
          <button onClick={() => setViewMode(viewMode === 'original' ? 'takeoff' : 'original')}
            style={{
              background: viewMode === 'takeoff'
                ? 'linear-gradient(135deg,#4f46e5,#6366f1)' : 'linear-gradient(135deg,#059669,#10b981)',
              border: 'none', borderRadius: '7px', color: '#fff',
              fontSize: '11px', fontWeight: 700, padding: '6px 14px', cursor: 'pointer',
            }}>
            {viewMode === 'original' ? '📐 Switch to Generated Takeoff Plan' : '📄 Switch to Original Drawing'}
          </button>

          {/* Labels Toggle */}
          <button onClick={() => setShowLabels(!showLabels)} style={tbtn(showLabels)}>
            🏷️ {showLabels ? 'Hide Labels' : 'Show Labels'}
          </button>

          {/* Rebar Toggle (Takeoff mode only) */}
          {viewMode === 'takeoff' && (
            <button onClick={() => setShowRebar(!showRebar)} style={tbtn(showRebar, '#ef4444')}>
              🔩 {showRebar ? 'Hide Rebar' : 'Show Rebar'}
            </button>
          )}

          {/* Reset View */}
          <button onClick={resetView} style={tbtn(false)}>
            🎯 Reset View
          </button>
        </div>
      </div>

      {/* ═══ LAYER FILTER BAR ═══ */}
      <div style={{
        padding: '6px 18px', background: '#0f172a', borderBottom: '1px solid #1e293b',
        display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap',
      }}>
        <span style={{ fontSize: '10px', color: '#64748b', fontWeight: 600 }}>Layers:</span>
        {LAYER_FILTERS.map(t => (
          <button key={t.id} onClick={() => setActiveFilter(t.id)} style={tbtn(activeFilter === t.id, t.color)}>
            <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: t.color, display: 'inline-block', marginRight: '4px' }} />
            {t.label}
          </button>
        ))}
      </div>

      {/* ═══ MAIN CANVAS VIEWPORT ═══ */}
      <div
        ref={viewportRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{
          position: 'relative', background: viewMode === 'takeoff' ? '#020617' : '#0a0f1e',
          minHeight: '520px', overflow: 'hidden',
          cursor: isDragging ? 'grabbing' : 'grab',
          userSelect: 'none',
        }}
      >
        <div style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          transformOrigin: 'center center',
          transition: isDragging ? 'none' : 'transform 0.12s ease-out',
          width: '100%', position: 'relative',
        }}>

          {/* ─── ORIGINAL DRAWING MODE ─── */}
          {viewMode === 'original' && (
            <>
              {pageImage ? (
                <img src={pageImage} alt="Blueprint" draggable={false}
                  style={{ width: '100%', height: 'auto', maxHeight: '720px', objectFit: 'contain', opacity: 0.92, filter: 'contrast(1.08) brightness(0.95)', pointerEvents: 'none' }} />
              ) : (
                <svg style={{ width: '100%', height: '500px', opacity: 0.06 }}>
                  <defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#38bdf8" strokeWidth="0.5" />
                  </pattern></defs>
                  <rect width="100%" height="100%" fill="url(#grid)" />
                </svg>
              )}

              {/* Vector Outline Overlays */}
              <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}>
                {filteredElements.map(el => {
                  const box = el.bounding_box;
                  const tc = TYPE_COLORS[el.element_type] || TYPE_COLORS.unclassified;
                  const isSelected = el.element_id === selectedId;
                  const isHovered = hoveredEl?.element_id === el.element_id;
                  const bw = Math.max(10, box[2] - box[0]);
                  const bh = Math.max(10, box[3] - box[1]);

                  return (
                    <g key={el.element_id}
                      onClick={(e) => { e.stopPropagation(); handleSelect(el); }}
                      onMouseEnter={() => setHoveredEl(el)}
                      onMouseLeave={() => setHoveredEl(null)}
                      style={{ cursor: 'pointer' }}>
                      <rect x={box[0]} y={box[1]} width={bw} height={bh}
                        fill="none"
                        stroke={isSelected ? '#ffffff' : isHovered ? '#00ffcc' : tc.stroke}
                        strokeWidth={isSelected ? 2.5 : isHovered ? 2 : 1.2}
                        strokeDasharray={el.element_type === 'unclassified' ? '4,3' : 'none'}
                        rx={2} opacity={isHovered || isSelected ? 1 : 0.7}
                        style={{ transition: 'all 0.12s' }} />
                      {(showLabels || isHovered || isSelected) && (
                        <g pointerEvents="none">
                          <rect x={box[0]} y={box[1] - 16} width={Math.max(50, el.label.length * 6.5)} height={14}
                            fill="#0f172a" stroke={tc.stroke} strokeWidth={0.8} rx={3} opacity={0.92} />
                          <text x={box[0] + 4} y={box[1] - 5} fill="#fff" fontSize="8.5" fontWeight="700"
                            fontFamily="JetBrains Mono, monospace">{el.label}</text>
                        </g>
                      )}
                    </g>
                  );
                })}
              </svg>
            </>
          )}

          {/* ─── GENERATED TAKEOFF PLAN MODE ─── */}
          {viewMode === 'takeoff' && (
            <svg viewBox={`0 0 ${CANVAS_W} ${CANVAS_H}`}
              style={{ width: '100%', height: 'auto', minHeight: '500px' }}>

              {/* Background grid */}
              <defs>
                <pattern id="takeoffGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" strokeWidth="0.5" />
                </pattern>
              </defs>
              <rect width={CANVAS_W} height={CANVAS_H} fill="url(#takeoffGrid)" />

              {/* Title block */}
              <text x={CANVAS_W / 2} y={24} textAnchor="middle" fill="#94a3b8" fontSize="14" fontWeight="800"
                fontFamily="Inter, sans-serif">
                GENERATED STRUCTURAL TAKEOFF PLAN — {(drawingName || 'Untitled').toUpperCase()}
              </text>
              <line x1={40} y1={34} x2={CANVAS_W - 40} y2={34} stroke="#1e293b" strokeWidth={1} />

              {/* Render structural elements */}
              {filteredFraming.map(el => {
                const tc = TYPE_COLORS[el.type] || TYPE_COLORS.unclassified;
                const isSelected = selectedId === el.id;
                const isHovered = hoveredEl?.id === el.id;

                return (
                  <g key={el.id}
                    onClick={(e) => { e.stopPropagation(); handleSelect(el); }}
                    onMouseEnter={() => setHoveredEl(el)}
                    onMouseLeave={() => setHoveredEl(null)}
                    style={{ cursor: 'pointer' }}>

                    {/* Structural outline */}
                    <rect x={el.x} y={el.y} width={el.width} height={el.height}
                      fill={isHovered || isSelected ? `${tc.stroke}15` : 'none'}
                      stroke={isSelected ? '#ffffff' : isHovered ? '#00ffcc' : tc.stroke}
                      strokeWidth={isSelected ? 2.5 : isHovered ? 2 : 1.5}
                      rx={2}
                      style={{ transition: 'all 0.12s' }} />

                    {/* Rebar lines */}
                    {showRebar && renderRebarForElement(el, tc.rebar)}

                    {/* Label */}
                    {(showLabels || isHovered || isSelected) && (
                      <g pointerEvents="none">
                        <rect x={el.x} y={el.y - 18}
                          width={Math.max(60, (el.label || el.id).length * 6.5)} height={15}
                          fill="#0f172a" stroke={tc.stroke} strokeWidth={0.8} rx={3} opacity={0.92} />
                        <text x={el.x + 4} y={el.y - 7} fill="#fff" fontSize="9" fontWeight="700"
                          fontFamily="JetBrains Mono, monospace">
                          {el.label || el.id}
                        </text>
                      </g>
                    )}

                    {/* Source badge (parsed vs assumed) */}
                    {(isHovered || isSelected) && el.source && (
                      <SourceBadge source={el.source} x={el.x + el.width + 4} y={el.y} />
                    )}

                    {/* Dimension annotation */}
                    {el.dimensions && (isHovered || isSelected || showLabels) && (
                      <text x={el.x + el.width / 2} y={el.y + el.height + 14}
                        textAnchor="middle" fill="#64748b" fontSize="8"
                        fontFamily="JetBrains Mono, monospace">
                        {el.dimensions.length_m && el.dimensions.width_m
                          ? `${el.dimensions.length_m}m × ${el.dimensions.width_m}m`
                          : el.dimensions.area_m2
                          ? `${el.dimensions.area_m2} sq.m`
                          : el.dimensions.span_m
                          ? `span ${el.dimensions.span_m}m`
                          : ''}
                        {el.dimensions.depth_m ? ` × ${el.dimensions.depth_m}m deep` : ''}
                      </text>
                    )}
                  </g>
                );
              })}

              {/* Legend */}
              <g transform={`translate(${CANVAS_W - 170}, ${CANVAS_H - 130})`}>
                <rect x={0} y={0} width={160} height={120} fill="#0f172a" stroke="#1e293b" strokeWidth={1} rx={6} opacity={0.9} />
                <text x={10} y={16} fill="#94a3b8" fontSize="9" fontWeight="700" fontFamily="Inter, sans-serif">LEGEND</text>
                {Object.entries(TYPE_COLORS).filter(([k]) => k !== 'unclassified').map(([key, val], i) => (
                  <g key={key} transform={`translate(10, ${26 + i * 17})`}>
                    <rect x={0} y={0} width={12} height={10} fill="none" stroke={val.stroke} strokeWidth={1.5} rx={1} />
                    <text x={18} y={9} fill="#cbd5e1" fontSize="8.5" fontFamily="JetBrains Mono, monospace">{val.label}</text>
                    <line x1={90} y1={5} x2={115} y2={5} stroke={val.rebar} strokeWidth={1.2} opacity={0.7} />
                    <text x={120} y={9} fill="#64748b" fontSize="7" fontFamily="JetBrains Mono, monospace">rebar</text>
                  </g>
                ))}
              </g>

              {/* Empty state for takeoff mode */}
              {filteredFraming.length === 0 && (
                <g>
                  <text x={CANVAS_W / 2} y={CANVAS_H / 2 - 10} textAnchor="middle" fill="#64748b" fontSize="14" fontWeight="700">
                    No Framing Plan Data Available
                  </text>
                  <text x={CANVAS_W / 2} y={CANVAS_H / 2 + 14} textAnchor="middle" fill="#475569" fontSize="11">
                    Upload and process a drawing to generate the takeoff plan
                  </text>
                </g>
              )}
            </svg>
          )}
        </div>

        {/* ── Hover Tooltip Card ── */}
        {hoveredEl && !isDragging && (
          <div style={{
            position: 'absolute', bottom: '16px', left: '16px',
            background: 'rgba(15,23,42,0.96)',
            border: `1px solid ${TYPE_COLORS[hoveredEl.element_type || hoveredEl.type]?.stroke || '#3b82f6'}`,
            borderRadius: '8px', padding: '10px 14px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.8)',
            pointerEvents: 'none', zIndex: 10, maxWidth: '280px',
          }}>
            <div style={{ fontSize: '12px', fontWeight: 800, color: '#f8fafc' }}>
              {hoveredEl.label || hoveredEl.id}
            </div>
            <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '3px' }}>
              Type: <strong style={{ color: '#38bdf8' }}>{(hoveredEl.element_type || hoveredEl.type || '').toUpperCase()}</strong>
              {hoveredEl.source && (
                <span style={{ marginLeft: '8px', color: hoveredEl.source === 'parsed' ? '#6ee7b7' : '#fcd34d' }}>
                  {hoveredEl.source === 'parsed' ? '🟢 Parsed' : '🟡 Assumed'}
                </span>
              )}
            </div>
            {hoveredEl.dimensions && (
              <div style={{ fontSize: '10px', color: '#64748b', marginTop: '2px' }}>
                {hoveredEl.dimensions.length_m && `${hoveredEl.dimensions.length_m}m × ${hoveredEl.dimensions.width_m}m`}
                {hoveredEl.dimensions.depth_m && ` × ${hoveredEl.dimensions.depth_m}m`}
                {hoveredEl.dimensions.area_m2 && `${hoveredEl.dimensions.area_m2} sq.m`}
              </div>
            )}
          </div>
        )}
      </div>

      {/* ═══ SUGGESTIONS PANEL ═══ */}
      {viewMode === 'takeoff' && filteredSuggestions.length > 0 && (
        <div style={{
          borderTop: '1px solid #1e293b', background: '#0f172a',
        }}>
          <div
            onClick={() => setShowSuggestions(!showSuggestions)}
            style={{
              padding: '8px 18px', display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', cursor: 'pointer',
            }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#f59e0b' }}>
              ⚠️ Parser Quality Suggestions ({filteredSuggestions.length})
            </span>
            <span style={{ fontSize: '10px', color: '#64748b' }}>{showSuggestions ? '▲ Collapse' : '▼ Expand'}</span>
          </div>

          {showSuggestions && (
            <div style={{ padding: '0 18px 12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {filteredSuggestions.map((sug, i) => (
                <div key={sug.id || i}
                  onClick={() => {
                    if (sug.element_id) {
                      setSelectedId(sug.element_id);
                      const target = filteredFraming.find(f => f.id === sug.element_id);
                      if (target && onElementSelect) onElementSelect(target);
                    }
                  }}
                  style={{
                    background: sug.severity === 'alert' ? '#450a0a' : sug.severity === 'warning' ? '#78350f20' : '#0f172a',
                    border: `1px solid ${sug.severity === 'alert' ? '#ef4444' : sug.severity === 'warning' ? '#f59e0b40' : '#1e293b'}`,
                    borderRadius: '6px', padding: '8px 12px', cursor: sug.element_id ? 'pointer' : 'default',
                    transition: 'background 0.15s',
                  }}>
                  <div style={{ fontSize: '11px', color: '#e2e8f0' }}>
                    <span style={{ marginRight: '6px' }}>{sug.icon || '💡'}</span>
                    {sug.message}
                  </div>
                  {sug.element_id && (
                    <div style={{ fontSize: '9px', color: '#64748b', marginTop: '3px' }}>
                      Click to highlight element: <strong style={{ color: '#38bdf8' }}>{sug.element_id}</strong>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ═══ FOOTER ═══ */}
      <div style={{
        padding: '6px 18px', background: '#0f172a', borderTop: '1px solid #1e293b',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        fontSize: '10px', color: '#64748b',
      }}>
        <span>
          {viewMode === 'original'
            ? `${filteredElements.length} vector paths | Scroll to zoom • Drag to pan • Click to inspect`
            : `${filteredFraming.length} structural elements | ${filteredSuggestions.length} suggestions`}
        </span>
        <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>
          ZOOM {Math.round(zoom * 100)}% | {viewMode === 'original' ? 'ORIGINAL OVERLAY' : 'TAKEOFF PLAN'} MODE
        </span>
      </div>
    </div>
  );
}
