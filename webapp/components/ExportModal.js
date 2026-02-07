'use client';

import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api';

/**
 * ExportModal - Professional export dialog with DAW recommendations
 * 
 * Props:
 *  - isOpen: boolean
 *  - onClose: function
 *  - project: { id, name, bpm, key, genre }
 *  - token: user auth token
 */
export default function ExportModal({ isOpen, onClose, project = {}, token }) {
    const [daws, setDaws] = useState(null);
    const [selectedDaw, setSelectedDaw] = useState('protools');
    const [settings, setSettings] = useState(null);
    const [includeMidi, setIncludeMidi] = useState(true);
    const [includeAudio, setIncludeAudio] = useState(true);
    const [includeStems, setIncludeStems] = useState(false);
    const [exporting, setExporting] = useState(false);
    const [exportResult, setExportResult] = useState(null);
    const [error, setError] = useState(null);

    // Load DAW options on mount
    useEffect(() => {
        if (isOpen) {
            loadDawOptions();
        }
    }, [isOpen]);

    // Load settings when DAW changes
    useEffect(() => {
        if (selectedDaw) {
            loadDawSettings(selectedDaw);
        }
    }, [selectedDaw]);

    const loadDawOptions = async () => {
        try {
            const res = await fetch(`${API_BASE}/export/daws`);
            const data = await res.json();
            setDaws(data.daws);
        } catch (err) {
            console.error('Error loading DAW options:', err);
        }
    };

    const loadDawSettings = async (dawId) => {
        try {
            const res = await fetch(`${API_BASE}/export/settings/${dawId}`);
            const data = await res.json();
            setSettings(data);
        } catch (err) {
            console.error('Error loading DAW settings:', err);
        }
    };

    const handleExport = async () => {
        setExporting(true);
        setError(null);
        setExportResult(null);

        try {
            const res = await fetch(`${API_BASE}/export/project?token=${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_id: project.id || 'demo_project',
                    project_name: project.name || 'Mi Proyecto',
                    daw: selectedDaw,
                    include_midi: includeMidi,
                    include_audio: includeAudio,
                    include_stems: includeStems,
                    bpm: project.bpm || 120,
                    key: project.key || 'Am',
                    genre: project.genre || 'bachata'
                })
            });

            const data = await res.json();

            if (data.success) {
                setExportResult(data);
            } else {
                setError(data.error || 'Error al exportar');
            }
        } catch (err) {
            setError('Error de conexión: ' + err.message);
        } finally {
            setExporting(false);
        }
    };

    if (!isOpen) return null;

    const modalStyles = {
        overlay: {
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10000,
            backdropFilter: 'blur(10px)'
        },
        modal: {
            background: 'linear-gradient(180deg, #1a1a2e 0%, #16162a 100%)',
            borderRadius: '20px',
            padding: '30px',
            maxWidth: '700px',
            width: '95%',
            maxHeight: '90vh',
            overflowY: 'auto',
            border: '1px solid rgba(255,255,255,0.1)',
            boxShadow: '0 20px 60px rgba(0,0,0,0.5)'
        },
        header: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '25px'
        },
        title: {
            fontSize: '1.8rem',
            fontWeight: 'bold',
            background: 'linear-gradient(90deg, #00d4ff, #00ff88)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
        },
        closeBtn: {
            background: 'rgba(255,255,255,0.1)',
            border: 'none',
            color: 'white',
            fontSize: '1.5rem',
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            cursor: 'pointer'
        },
        section: {
            marginBottom: '25px'
        },
        sectionTitle: {
            fontSize: '1.1rem',
            fontWeight: 'bold',
            color: '#fff',
            marginBottom: '15px'
        },
        dawGrid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
            gap: '12px'
        },
        dawCard: (isSelected) => ({
            background: isSelected
                ? 'linear-gradient(135deg, rgba(0,212,255,0.3), rgba(0,255,136,0.3))'
                : 'rgba(255,255,255,0.05)',
            border: isSelected ? '2px solid #00d4ff' : '2px solid transparent',
            borderRadius: '12px',
            padding: '15px',
            cursor: 'pointer',
            textAlign: 'center',
            transition: 'all 0.2s'
        }),
        dawIcon: {
            fontSize: '2rem',
            marginBottom: '8px'
        },
        dawName: {
            fontSize: '0.9rem',
            fontWeight: '600',
            color: '#fff'
        },
        dawFormat: {
            fontSize: '0.75rem',
            color: 'rgba(255,255,255,0.6)',
            marginTop: '4px'
        },
        checkbox: {
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '12px',
            cursor: 'pointer'
        },
        checkboxInput: {
            width: '20px',
            height: '20px',
            cursor: 'pointer'
        },
        infoBox: {
            background: 'rgba(0,212,255,0.1)',
            border: '1px solid rgba(0,212,255,0.3)',
            borderRadius: '12px',
            padding: '15px',
            marginTop: '15px'
        },
        infoTitle: {
            fontWeight: 'bold',
            color: '#00d4ff',
            marginBottom: '10px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
        },
        infoText: {
            color: 'rgba(255,255,255,0.8)',
            fontSize: '0.9rem',
            lineHeight: '1.6',
            whiteSpace: 'pre-line'
        },
        exportBtn: {
            background: 'linear-gradient(135deg, #00d4ff 0%, #00ff88 100%)',
            border: 'none',
            color: '#000',
            fontWeight: 'bold',
            padding: '15px 40px',
            borderRadius: '25px',
            fontSize: '1.1rem',
            cursor: 'pointer',
            width: '100%',
            marginTop: '20px',
            transition: 'transform 0.2s'
        },
        resultBox: {
            background: 'rgba(0,255,136,0.1)',
            border: '1px solid rgba(0,255,136,0.3)',
            borderRadius: '12px',
            padding: '20px',
            marginTop: '20px',
            textAlign: 'center'
        },
        errorBox: {
            background: 'rgba(255,68,68,0.1)',
            border: '1px solid rgba(255,68,68,0.3)',
            borderRadius: '12px',
            padding: '15px',
            marginTop: '15px',
            color: '#ff6b6b'
        }
    };

    return (
        <div style={modalStyles.overlay} onClick={onClose}>
            <div style={modalStyles.modal} onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div style={modalStyles.header}>
                    <h2 style={modalStyles.title}>📦 Exportar Proyecto</h2>
                    <button style={modalStyles.closeBtn} onClick={onClose}>×</button>
                </div>

                {/* Success Result */}
                {exportResult && (
                    <div style={modalStyles.resultBox}>
                        <div style={{ fontSize: '3rem', marginBottom: '15px' }}>✅</div>
                        <h3 style={{ color: '#00ff88', marginBottom: '10px' }}>
                            ¡Proyecto Exportado!
                        </h3>
                        <p style={{ color: 'rgba(255,255,255,0.8)', marginBottom: '15px' }}>
                            Formato: <strong>{exportResult.format?.toUpperCase()}</strong> para {exportResult.daw}
                        </p>
                        <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.9rem' }}>
                            📁 {exportResult.filename}<br />
                            📊 {exportResult.size_mb} MB • {exportResult.tracks_exported} tracks
                        </p>
                        <button
                            style={{ ...modalStyles.exportBtn, marginTop: '15px' }}
                            onClick={() => {
                                // In desktop app, this would trigger file dialog
                                // For now, we show the path
                                alert(`Archivo guardado en:\n${exportResult.path}`);
                            }}
                        >
                            📥 Descargar ZIP
                        </button>
                    </div>
                )}

                {/* Error */}
                {error && (
                    <div style={modalStyles.errorBox}>
                        ❌ {error}
                    </div>
                )}

                {/* DAW Selection */}
                {!exportResult && (
                    <>
                        <div style={modalStyles.section}>
                            <h3 style={modalStyles.sectionTitle}>
                                🎛️ Selecciona tu DAW
                            </h3>
                            <div style={modalStyles.dawGrid}>
                                {daws && Object.entries(daws).map(([id, daw]) => (
                                    <div
                                        key={id}
                                        style={modalStyles.dawCard(selectedDaw === id)}
                                        onClick={() => setSelectedDaw(id)}
                                    >
                                        <div style={modalStyles.dawIcon}>{daw.icon}</div>
                                        <div style={modalStyles.dawName}>{daw.name}</div>
                                        <div style={modalStyles.dawFormat}>
                                            {daw.audio_format.toUpperCase()} • {daw.sample_rate / 1000}kHz
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Export Options */}
                        <div style={modalStyles.section}>
                            <h3 style={modalStyles.sectionTitle}>
                                📁 Contenido a Exportar
                            </h3>
                            <label style={modalStyles.checkbox}>
                                <input
                                    type="checkbox"
                                    checked={includeMidi}
                                    onChange={(e) => setIncludeMidi(e.target.checked)}
                                    style={modalStyles.checkboxInput}
                                />
                                <span>🎹 Archivos MIDI (para editar notas)</span>
                            </label>
                            <label style={modalStyles.checkbox}>
                                <input
                                    type="checkbox"
                                    checked={includeAudio}
                                    onChange={(e) => setIncludeAudio(e.target.checked)}
                                    style={modalStyles.checkboxInput}
                                />
                                <span>🔊 Audio renderizado ({settings?.audio_format?.toUpperCase() || 'WAV'})</span>
                            </label>
                            <label style={modalStyles.checkbox}>
                                <input
                                    type="checkbox"
                                    checked={includeStems}
                                    onChange={(e) => setIncludeStems(e.target.checked)}
                                    style={modalStyles.checkboxInput}
                                />
                                <span>🎚️ Stems mezclados (melodía + percusión)</span>
                            </label>
                        </div>

                        {/* DAW Info */}
                        {settings && (
                            <div style={modalStyles.infoBox}>
                                <div style={modalStyles.infoTitle}>
                                    💡 Cómo importar en {settings.name}
                                </div>
                                <div style={modalStyles.infoText}>
                                    {settings.instructions}
                                </div>
                                <div style={{ marginTop: '15px', fontSize: '0.85rem', color: 'rgba(255,255,255,0.6)' }}>
                                    <strong>Formato:</strong> {settings.audio_format?.toUpperCase()} •
                                    <strong> Sample Rate:</strong> {settings.sample_rate} Hz •
                                    <strong> Bit Depth:</strong> {settings.bit_depth}-bit
                                </div>
                            </div>
                        )}

                        {/* Export Button */}
                        <button
                            style={{
                                ...modalStyles.exportBtn,
                                opacity: exporting ? 0.7 : 1,
                                cursor: exporting ? 'wait' : 'pointer'
                            }}
                            onClick={handleExport}
                            disabled={exporting}
                        >
                            {exporting ? '⏳ Exportando...' : `📦 Exportar para ${settings?.name || 'Pro Tools'}`}
                        </button>
                    </>
                )}
            </div>
        </div>
    );
}
