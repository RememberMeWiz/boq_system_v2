import React, { useState } from 'react';

export default function BlueprintViewer({ elements, drawingName }) {
  const [selectedElement, setSelectedElement] = useState(null);

  const getHeatmapColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'footing':
      case 'column':
        return { bg: 'rgba(59, 130, 246, 0.35)', border: '#3b82f6', label: '🟦 Concrete' };
      case 'beam':
      case 'slab':
        return { bg: 'rgba(249, 115, 22, 0.35)', border: '#f97316', label: '🟧 Beam/Slab' };
      case 'chb_wall':
        return { bg: 'rgba(34, 197, 94, 0.35)', border: '#22c55e', label: '🟩 Masonry Wall' };
      default:
        return { bg: 'rgba(168, 85, 247, 0.35)', border: '#a855f7', label: '🟪 Structural' };
    }
  };

  return (
    <div className="bg-slate-900 rounded-xl p-5 border border-slate-800 shadow-xl">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-blue-400">📐 Native Blueprint Vector Heatmap Overlay</h2>
          <p className="text-xs text-slate-400">Active Drawing Sheet: <span className="text-slate-200 font-mono">{drawingName || 'Residential_House_Structural_Plan.pdf'}</span></p>
        </div>
        <div className="flex gap-3 text-xs">
          <span className="flex items-center gap-1 text-blue-400 font-semibold"><span className="w-2.5 h-2.5 bg-blue-500 rounded-full inline-block"></span> Concrete</span>
          <span className="flex items-center gap-1 text-orange-400 font-semibold"><span className="w-2.5 h-2.5 bg-orange-500 rounded-full inline-block"></span> Beams/Slabs</span>
          <span className="flex items-center gap-1 text-green-400 font-semibold"><span className="w-2.5 h-2.5 bg-green-500 rounded-full inline-block"></span> CHB Walls</span>
        </div>
      </div>

      {/* Drawing Blueprint Canvas Container */}
      <div className="relative w-full h-[360px] bg-slate-950 rounded-lg border-2 border-dashed border-slate-700 overflow-hidden flex items-center justify-center">
        {/* Background Grid Pattern simulating CAD CAD blueprint */}
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:16px_16px]"></div>
        
        <span className="absolute top-3 left-3 text-xs font-mono text-slate-500">SCALE: 1:100 | VECTOR PATH LAYER ACTIVE</span>

        {/* Heatmap Bounding Box Overlays */}
        {elements && elements.length > 0 ? (
          elements.map((elem) => {
            const style = getHeatmapColor(elem.element_type);
            const box = elem.bounding_box || [100, 100, 200, 200];
            const width = box[2] - box[0];
            const height = box[3] - box[1];

            return (
              <div
                key={elem.element_id}
                onClick={() => setSelectedElement(elem)}
                style={{
                  position: 'absolute',
                  left: `${box[0]}px`,
                  top: `${box[1]}px`,
                  width: `${width}px`,
                  height: `${height}px`,
                  backgroundColor: style.bg,
                  borderColor: style.border,
                  borderWidth: '2px',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
                className="transition-all hover:scale-[1.02] flex items-center justify-center text-[10px] font-bold text-white shadow-lg"
              >
                {elem.label}
              </div>
            );
          })
        ) : (
          <div className="text-center text-slate-500 text-sm">
            No element heatmaps generated. Process drawing to inspect overlays.
          </div>
        )}
      </div>

      {/* Selected Element Inspector */}
      {selectedElement && (
        <div className="mt-4 p-3 bg-slate-800/80 rounded-lg border border-slate-700 text-xs flex justify-between items-center">
          <div>
            <span className="font-bold text-blue-400">{selectedElement.label}</span> ({selectedElement.element_type}) — Location: <span className="text-slate-300">{selectedElement.location}</span>
          </div>
          <div className="font-mono text-slate-300">
            Dimensions: {selectedElement.length}m × {selectedElement.width}m × {selectedElement.height}m (Qty: {selectedElement.count})
          </div>
        </div>
      )}
    </div>
  );
}
