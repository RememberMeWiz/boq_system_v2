import React, { useState } from 'react';

// ── Provenance Badge ──────────────────────────────────────────────────────────
const PROVENANCE_CONFIG = {
  'vector_text':      { label: 'Parsed · Vector',    color: '#10b981', bg: 'rgba(16,185,129,0.12)',  icon: '🟢' },
  'vision_extracted': { label: 'Vision · Extracted',  color: '#38bdf8', bg: 'rgba(56,189,248,0.12)',  icon: '🔵' },
  'rapidocr':         { label: 'Offline · OCR',       color: '#f59e0b', bg: 'rgba(245,158,11,0.12)',  icon: '🟡' },
  'inferred':         { label: 'Assumed',              color: '#f87171', bg: 'rgba(248,113,113,0.12)', icon: '🔴' },
};

function ProvenanceBadge({ provenance }) {
  const cfg = PROVENANCE_CONFIG[provenance] || {
    label: provenance || 'Unknown', color: '#64748b',
    bg: 'rgba(100,116,139,0.12)', icon: '⚪',
  };
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '4px',
      fontSize: '10px', fontWeight: 700, letterSpacing: '0.3px',
      color: cfg.color, background: cfg.bg,
      border: `1px solid ${cfg.color}33`,
      borderRadius: '5px', padding: '2px 7px',
      fontFamily: 'JetBrains Mono, monospace',
    }}>
      {cfg.icon} {cfg.label}
    </span>
  );
}

// ── Verification Gate Card ────────────────────────────────────────────────────
function GateCard({ gate, onSignoff }) {
  if (!gate) return null;
  const isReady       = gate.status === 'READY';
  const blockingIssues = (gate.blocking_issues || []).filter(i => !i.resolved);
  const warningIssues  = (gate.warning_issues  || []).filter(i => !i.resolved);
  const resolutionLog  = gate.resolution_log   || [];

  return (
    <div style={{
      background: isReady ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)',
      border: `1px solid ${isReady ? '#10b981' : '#ef4444'}`,
      borderRadius: '10px', padding: '16px', marginBottom: '16px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
        <span style={{ fontSize: '18px' }}>{isReady ? '✅' : '🔴'}</span>
        <div>
          <div style={{ fontWeight: 800, fontSize: '13px', color: isReady ? '#10b981' : '#ef4444' }}>
            VERIFICATION GATE — {gate.status}
          </div>
          {gate.computed_at && (
            <div style={{ fontSize: '10px', color: '#64748b', fontFamily: 'JetBrains Mono, monospace' }}>
              {new Date(gate.computed_at).toLocaleString()}
            </div>
          )}
        </div>
      </div>

      {blockingIssues.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#ef4444', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            🔴 Blocking Issues
          </div>
          {blockingIssues.map(issue => (
            <IssueRow key={issue.id} issue={issue} onSignoff={onSignoff} />
          ))}
        </div>
      )}

      {warningIssues.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#f59e0b', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            ⚠️ Warnings — Requires Signoff
          </div>
          {warningIssues.map(issue => (
            <IssueRow key={issue.id} issue={issue} onSignoff={onSignoff} />
          ))}
        </div>
      )}

      {resolutionLog.length > 0 && (
        <div>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#10b981', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            ✅ Resolved ({resolutionLog.length})
          </div>
          {resolutionLog.map((r, i) => (
            <div key={i} style={{
              fontSize: '11px', color: '#6ee7b7',
              fontFamily: 'JetBrains Mono, monospace',
              background: 'rgba(16,185,129,0.06)',
              borderRadius: '5px', padding: '6px 10px', marginBottom: '4px',
            }}>
              <span style={{ color: '#34d399', fontWeight: 700 }}>{r.issue_id}</span>
              {' · '}{r.signed_off_by} · {new Date(r.signed_off_at).toLocaleTimeString()}
              {r.note && <div style={{ color: '#94a3b8', marginTop: '2px' }}>"{r.note}"</div>}
            </div>
          ))}
        </div>
      )}

      {isReady && blockingIssues.length === 0 && warningIssues.length === 0 && (
        <div style={{ fontSize: '12px', color: '#6ee7b7' }}>
          All issues resolved. Ready for takeoff computation.
        </div>
      )}
    </div>
  );
}

function IssueRow({ issue, onSignoff }) {
  return (
    <div style={{
      background: 'rgba(0,0,0,0.3)', borderRadius: '6px', padding: '8px 10px', marginBottom: '6px',
      border: '1px solid rgba(255,255,255,0.05)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px' }}>
        <div style={{ flex: 1 }}>
          <span style={{ fontSize: '10px', fontWeight: 700, color: '#94a3b8', fontFamily: 'JetBrains Mono, monospace' }}>
            [{issue.severity}] {issue.category}
          </span>
          <div style={{ fontSize: '12px', color: '#cbd5e1', marginTop: '2px' }}>{issue.message}</div>
          {issue.affected_elements?.length > 0 && (
            <div style={{ fontSize: '10px', color: '#64748b', marginTop: '2px' }}>
              Affects: {issue.affected_elements.join(', ')}
            </div>
          )}
        </div>
        <button
          onClick={() => onSignoff(issue)}
          style={{
            background: 'rgba(245,158,11,0.15)', border: '1px solid #f59e0b',
            color: '#fbbf24', fontSize: '11px', fontWeight: 700,
            padding: '4px 10px', borderRadius: '6px', cursor: 'pointer',
            whiteSpace: 'nowrap', flexShrink: 0,
          }}
        >
          ✍ Sign Off
        </button>
      </div>
    </div>
  );
}

// ── Signoff Modal ─────────────────────────────────────────────────────────────
function SignoffModal({ issue, onSubmit, onClose }) {
  const [form, setForm]         = useState({ signed_off_by: '', note: '' });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.signed_off_by.trim() || !form.note.trim()) return;
    setSubmitting(true);
    await onSubmit(issue, form);
    setSubmitting(false);
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 500,
      background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <div style={{
        background: '#0f172a', border: '1px solid #f59e0b',
        borderRadius: '14px', padding: '28px', width: '460px', maxWidth: '95vw',
        boxShadow: '0 20px 60px rgba(245,158,11,0.2)',
      }}>
        <div style={{ fontSize: '16px', fontWeight: 800, color: '#fbbf24', marginBottom: '6px' }}>
          ✍️ Engineer Signoff Required
        </div>
        <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '20px' }}>
          Issue: <span style={{ color: '#e2e8f0', fontFamily: 'JetBrains Mono, monospace' }}>{issue.id}</span>
          <div style={{ marginTop: '4px', color: '#cbd5e1' }}>{issue.message}</div>
        </div>

        <form onSubmit={handleSubmit}>
          <label style={{ display: 'block', marginBottom: '14px' }}>
            <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', marginBottom: '5px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Signed Off By *
            </div>
            <input
              id="signoff-by"
              type="text"
              placeholder="Engr. Juan Dela Cruz, PRC #12345"
              value={form.signed_off_by}
              onChange={e => setForm(f => ({ ...f, signed_off_by: e.target.value }))}
              required
              style={{
                width: '100%', background: '#1e293b', border: '1px solid #334155',
                borderRadius: '7px', color: '#e2e8f0', fontSize: '13px',
                padding: '9px 12px', fontFamily: 'Inter, sans-serif', boxSizing: 'border-box',
              }}
            />
          </label>

          <label style={{ display: 'block', marginBottom: '20px' }}>
            <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', marginBottom: '5px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Signoff Note *
            </div>
            <textarea
              id="signoff-note"
              placeholder="e.g. Verified column tie spacing against Sheet S-4 structural schedule table."
              value={form.note}
              onChange={e => setForm(f => ({ ...f, note: e.target.value }))}
              required
              rows={3}
              style={{
                width: '100%', background: '#1e293b', border: '1px solid #334155',
                borderRadius: '7px', color: '#e2e8f0', fontSize: '13px',
                padding: '9px 12px', fontFamily: 'Inter, sans-serif',
                resize: 'vertical', boxSizing: 'border-box',
              }}
            />
          </label>

          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <button type="button" onClick={onClose} style={{
              background: 'transparent', border: '1px solid #334155', borderRadius: '7px',
              color: '#94a3b8', fontSize: '13px', fontWeight: 600, padding: '8px 18px', cursor: 'pointer',
            }}>
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || !form.signed_off_by || !form.note}
              style={{
                background: submitting ? '#92400e' : 'linear-gradient(135deg,#d97706,#f59e0b)',
                border: 'none', borderRadius: '7px', color: '#fff',
                fontSize: '13px', fontWeight: 700, padding: '8px 20px', cursor: 'pointer',
                opacity: (!form.signed_off_by || !form.note) ? 0.5 : 1,
              }}
            >
              {submitting ? '⏳ Submitting...' : '✅ Submit Signoff'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Schedule Table with Provenance Badges ─────────────────────────────────────
const HIGH_RISK_FIELDS = ['MAIN BAR', 'TIES', 'BAR X', 'BAR Y'];

function ScheduleTable({ title, rows, icon }) {
  if (!rows || rows.length === 0) return null;
  const allKeys = Array.from(
    new Set(rows.flatMap(r => Object.keys(r)))
  ).filter(k => k !== 'provenance');

  return (
    <div style={{ marginBottom: '20px' }}>
      <div style={{ fontSize: '12px', fontWeight: 800, color: '#94a3b8', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '1px' }}>
        {icon} {title}
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
          <thead>
            <tr>
              {allKeys.map(k => (
                <th key={k} style={{
                  padding: '7px 10px', textAlign: 'left', fontSize: '10px',
                  fontWeight: 700, color: '#64748b', textTransform: 'uppercase',
                  borderBottom: '1px solid #1e293b', letterSpacing: '0.5px',
                  background: '#0a0f1e', whiteSpace: 'nowrap',
                }}>{k}</th>
              ))}
              <th style={{
                padding: '7px 10px', textAlign: 'left', fontSize: '10px',
                fontWeight: 700, color: '#64748b', background: '#0a0f1e',
                borderBottom: '1px solid #1e293b',
              }}>SOURCE</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => {
              const provenance = row.provenance || 'inferred';
              return (
                <tr key={i} style={{ borderBottom: '1px solid rgba(30,41,59,0.6)' }}>
                  {allKeys.map(k => {
                    const isHighRisk = HIGH_RISK_FIELDS.includes(k);
                    const val = row[k];
                    const displayVal = typeof val === 'object' && val !== null
                      ? JSON.stringify(val) : (val ?? '—');
                    return (
                      <td key={k} style={{
                        padding: '8px 10px',
                        color: isHighRisk ? '#fbbf24' : '#cbd5e1',
                        fontFamily: 'JetBrains Mono, monospace',
                        background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
                        whiteSpace: 'nowrap', maxWidth: '200px',
                        overflow: 'hidden', textOverflow: 'ellipsis',
                      }}>
                        {displayVal}
                        {isHighRisk && displayVal !== '—' && (
                          <span title="Verify against drawing" style={{ marginLeft: '4px', cursor: 'help' }}>👁</span>
                        )}
                      </td>
                    );
                  })}
                  <td style={{
                    padding: '8px 10px',
                    background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
                  }}>
                    <ProvenanceBadge provenance={provenance} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── SVG Reconstruction Panel ──────────────────────────────────────────────────
function ReconstructionPanel({ svgCode }) {
  if (!svgCode) return null;
  return (
    <div style={{
      background: '#0a0f1e', border: '1px solid #1e293b',
      borderRadius: '10px', padding: '16px', marginBottom: '20px',
    }}>
      <div style={{ fontSize: '12px', fontWeight: 700, color: '#64748b', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '1px' }}>
        🗺️ Reconstructed Structural Drawing
      </div>
      <div style={{
        borderRadius: '8px', overflow: 'hidden', border: '1px solid #1e293b',
        background: '#020617',
      }}
        dangerouslySetInnerHTML={{ __html: svgCode }}
      />
      <div style={{ fontSize: '10px', color: '#475569', marginTop: '8px', fontFamily: 'JetBrains Mono, monospace' }}>
        ⚠ Rendered from extracted schedule data only — not a copy of the original drawing.
        Fields labeled <span style={{ color: '#fbbf24' }}>400x400mm?</span> require manual dimension verification.
      </div>
    </div>
  );
}

// ── Main ParserDashboard Component ────────────────────────────────────────────
export default function ParserDashboard({ parserData, setParserData }) {
  const [signoffIssue, setSignoffIssue] = useState(null);
  const [svgCode, setSvgCode]           = useState(null);
  const [loadingSvg, setLoadingSvg]     = useState(false);
  const [error, setError]               = useState(null);

  const sessionId = parserData?.session_id;
  const payload   = parserData?.payload;
  const gate      = payload?.verification_gate;
  const schedules = payload?.schedules || {};

  // Fetch SVG reconstruction when parserData arrives and we don't have one yet
  React.useEffect(() => {
    if (!sessionId || svgCode) return;
    setLoadingSvg(true);
    fetch('/api/v1/parser/reconstruct', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    })
      .then(r => r.json())
      .then(j => { if (j.svg_code) setSvgCode(j.svg_code); })
      .catch(() => {})
      .finally(() => setLoadingSvg(false));
  }, [sessionId]);

  // Signoff submission
  const handleSignoffSubmit = async (issue, form) => {
    try {
      const res = await fetch('/api/v1/parser/signoff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          resolutions: [{
            issue_id: issue.id,
            action: issue.resolution_required?.[0] || 'manual_confirm',
            signed_off_by: form.signed_off_by,
            timestamp: new Date().toISOString(),
            note: form.note,
          }],
        }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || 'Signoff failed');
      // Merge updated gate back into parserData
      setParserData(prev => ({
        ...prev,
        payload: { ...prev.payload, verification_gate: json.verification_gate },
      }));
      setSignoffIssue(null);
    } catch (err) {
      setError(err.message);
    }
  };

  // ── Empty state ──────────────────────────────────────────────────────────────
  if (!parserData) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        minHeight: '340px', gap: '14px', color: '#475569', textAlign: 'center',
      }}>
        <div style={{ fontSize: '48px', opacity: 0.4 }}>🔬</div>
        <div style={{ fontSize: '15px', fontWeight: 700, color: '#64748b' }}>
          No drawing loaded
        </div>
        <div style={{ fontSize: '13px', color: '#475569', maxWidth: '340px', lineHeight: 1.6 }}>
          Use the{' '}
          <span style={{
            background: 'linear-gradient(135deg,#059669,#10b981)',
            color: '#fff', borderRadius: '5px', padding: '2px 8px',
            fontWeight: 700, fontSize: '12px',
          }}>
            📥 Import PDF/DXF
          </span>
          {' '}button above to upload a structural drawing.<br />
          The Parser & Signoff tab will populate automatically.
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '20px 0' }}>

      {signoffIssue && (
        <SignoffModal
          issue={signoffIssue}
          onSubmit={handleSignoffSubmit}
          onClose={() => setSignoffIssue(null)}
        />
      )}

      {error && (
        <div style={{
          background: 'rgba(239,68,68,0.08)', border: '1px solid #ef4444',
          borderRadius: '8px', padding: '10px 16px', marginBottom: '16px',
          fontSize: '13px', color: '#fca5a5', fontWeight: 600,
        }}>
          ❌ {error}
          <button onClick={() => setError(null)} style={{ marginLeft: '12px', background: 'none', border: 'none', color: '#f87171', cursor: 'pointer', fontWeight: 700 }}>✕</button>
        </div>
      )}

      {loadingSvg && (
        <div style={{
          background: 'rgba(56,189,248,0.08)', border: '1px solid #38bdf8',
          borderRadius: '8px', padding: '10px 16px', marginBottom: '16px',
          fontSize: '13px', color: '#93c5fd', fontWeight: 600,
        }}>
          🗺️ Rendering structural reconstruction...
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '20px', alignItems: 'flex-start' }}>

        {/* Left: SVG + Schedule Tables */}
        <div>
          <ReconstructionPanel svgCode={svgCode} />

          <ScheduleTable title="Footing Schedule"  icon="🏗️" rows={schedules.footings} />
          <ScheduleTable title="Column Schedule"   icon="🏛️" rows={schedules.columns}  />
          <ScheduleTable title="Beam Schedule"     icon="━"   rows={schedules.beams}    />
          <ScheduleTable title="Slab Schedule"     icon="⬜"  rows={schedules.slabs}    />
        </div>

        {/* Right: Verification Gate + Legend */}
        <div style={{ position: 'sticky', top: '130px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '1px' }}>
            🔒 Verification Gate
          </div>
          <GateCard gate={gate} onSignoff={setSignoffIssue} />

          {/* Provenance Legend */}
          <div style={{
            background: '#0f172a', border: '1px solid #1e293b',
            borderRadius: '10px', padding: '14px',
          }}>
            <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '1px' }}>
              📊 Provenance Legend
            </div>
            {Object.entries(PROVENANCE_CONFIG).map(([key, cfg]) => (
              <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <ProvenanceBadge provenance={key} />
                <span style={{ fontSize: '11px', color: '#64748b' }}>
                  {key === 'vision_extracted' && '— Gemini Vision OCR'}
                  {key === 'vector_text'      && '— Deterministic PDF text'}
                  {key === 'rapidocr'         && '— Local offline OCR'}
                  {key === 'inferred'         && '— Assumed / unverified'}
                </span>
              </div>
            ))}
            <div style={{ marginTop: '8px', fontSize: '10px', color: '#475569' }}>
              Fields marked 👁 (MAIN BAR, TIES) have known OCR reliability gaps — verify against drawing.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
