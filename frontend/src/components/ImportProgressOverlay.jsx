import React, { useEffect, useState } from 'react';

const STAGES = [
  { label: 'Reading PDF/DXF file...',            pct: 15 },
  { label: 'Extracting vector schedule tables...', pct: 40 },
  { label: 'Running offline OCR fallback...',     pct: 65 },
  { label: 'Assembling structural payload...',    pct: 85 },
  { label: 'Running verification gate checks...', pct: 95 },
];

/**
 * Staged progress overlay for the Import PDF/DXF flow.
 */
export default function ImportProgressOverlay({ visible }) {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    if (!visible) {
      setStageIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setStageIndex(prev => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 600); // Advances stage every 600ms
    return () => clearInterval(interval);
  }, [visible]);

  if (!visible) return null;

  const stage = STAGES[stageIndex];

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 2000,
      background: 'rgba(2, 6, 23, 0.75)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <div style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)',
        border: '1px solid #312e81', borderRadius: '16px',
        padding: '32px 40px', minWidth: '360px', textAlign: 'center',
        boxShadow: '0 0 60px rgba(99, 102, 241, 0.25)',
      }}>
        <div style={{ fontSize: '13px', color: '#94a3b8', letterSpacing: '1.5px', textTransform: 'uppercase', marginBottom: '16px' }}>
          Parsing Drawing
        </div>
        <div style={{ background: '#1e293b', borderRadius: '999px', height: '8px', overflow: 'hidden', marginBottom: '14px' }}>
          <div style={{
            width: `${stage.pct}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #6366f1, #34d399)',
            borderRadius: '999px',
            transition: 'width 0.5s ease',
          }} />
        </div>
        <div style={{ fontSize: '14px', color: '#e2e8f0', fontWeight: 600 }}>
          {stage.label}
        </div>
      </div>
    </div>
  );
}
