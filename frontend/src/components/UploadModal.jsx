import React, { useState, useRef } from 'react';

export default function UploadModal({ isOpen, onClose, onUpload }) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleStartProcessing = () => {
    if (selectedFile) {
      onUpload(selectedFile);
      setSelectedFile(null);
      onClose();
    }
  };

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 1000,
        background: 'rgba(2, 6, 23, 0.85)',
        backdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '20px',
      }}
      onClick={onClose}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          background: '#0f172a',
          border: '1px solid #1e293b',
          borderRadius: '16px',
          maxWidth: '520px', width: '100%',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
          overflow: 'hidden',
        }}
      >
        {/* Modal Header */}
        <div style={{
          padding: '16px 20px',
          background: '#020617',
          borderBottom: '1px solid #1e293b',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '18px' }}>📥</span>
            <div>
              <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 800, color: '#f8fafc' }}>
                Import Engineering Plan / Structural Drawing
              </h3>
              <p style={{ margin: '2px 0 0', fontSize: '11px', color: '#64748b' }}>
                Upload vector PDF, CAD DXF, or DWG plan for automated 13-trade takeoff
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none', border: 'none', color: '#64748b',
              fontSize: '18px', cursor: 'pointer', padding: '4px',
            }}
          >
            ✕
          </button>
        </div>

        {/* Modal Body / Drop Zone */}
        <div style={{ padding: '24px' }}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept=".pdf,.dxf,.dwg"
            style={{ display: 'none' }}
          />

          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
            style={{
              border: `2px dashed ${isDragging ? '#10b981' : '#334155'}`,
              background: isDragging ? 'rgba(16, 185, 129, 0.05)' : '#020617',
              borderRadius: '12px',
              padding: '36px 20px',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            <div style={{ fontSize: '36px', marginBottom: '12px' }}>
              {isDragging ? '📂' : '📄'}
            </div>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#e2e8f0', marginBottom: '4px' }}>
              {isDragging ? 'Drop file to upload' : 'Drag & Drop your drawing file here'}
            </div>
            <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '16px' }}>
              or <span style={{ color: '#10b981', fontWeight: 600 }}>browse files</span> from your computer
            </div>

            {/* File type badges */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: '6px' }}>
              {['.PDF Vector', '.DXF CAD', '.DWG Drawing'].map(type => (
                <span
                  key={type}
                  style={{
                    background: '#0f172a',
                    border: '1px solid #1e293b',
                    borderRadius: '6px',
                    color: '#94a3b8',
                    fontSize: '10px',
                    fontWeight: 600,
                    padding: '3px 8px',
                  }}
                >
                  {type}
                </span>
              ))}
            </div>
          </div>

          {/* Selected file preview card */}
          {selectedFile && (
            <div style={{
              marginTop: '16px',
              background: '#020617',
              border: '1px solid #10b981',
              borderRadius: '10px',
              padding: '12px 16px',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '20px' }}>📑</span>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc' }}>
                    {selectedFile.name}
                  </div>
                  <div style={{ fontSize: '11px', color: '#10b981' }}>
                    Ready to process • {formatSize(selectedFile.size)}
                  </div>
                </div>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '16px 20px',
          background: '#020617',
          borderTop: '1px solid #1e293b',
          display: 'flex', justifyContent: 'flex-end', gap: '10px',
        }}>
          <button
            onClick={onClose}
            style={{
              background: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: '#cbd5e1',
              fontSize: '12px', fontWeight: 600,
              padding: '8px 16px', cursor: 'pointer',
            }}
          >
            Cancel
          </button>

          <button
            onClick={handleStartProcessing}
            disabled={!selectedFile}
            style={{
              background: selectedFile ? 'linear-gradient(135deg, #059669, #10b981)' : '#1e293b',
              border: 'none',
              borderRadius: '8px',
              color: selectedFile ? '#fff' : '#64748b',
              fontSize: '12px', fontWeight: 700,
              padding: '8px 20px',
              cursor: selectedFile ? 'pointer' : 'not-allowed',
              opacity: selectedFile ? 1 : 0.6,
            }}
          >
            🚀 Run Takeoff Engine
          </button>
        </div>
      </div>
    </div>
  );
}
