'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

const API_BASE = 'http://localhost:8000/api';

// Sidebar Navigation
function AdminSidebar({ activeTab, setActiveTab }) {
    const tabs = [
        { id: 'dashboard', icon: '📊', label: 'Dashboard' },
        { id: 'api', icon: '🔑', label: 'API Settings' },
        { id: 'samples', icon: '🎵', label: 'Sample Library' },
        { id: 'training', icon: '🧠', label: 'Training' },
    ];

    return (
        <aside style={{
            width: '250px',
            background: 'var(--carbon)',
            borderRight: '1px solid rgba(212, 175, 55, 0.1)',
            padding: '2rem 0',
            minHeight: '100vh'
        }}>
            <div style={{ padding: '0 1.5rem', marginBottom: '2rem' }}>
                <Link href="/" style={{ textDecoration: 'none' }}>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>
                        DGB <span style={{ color: 'var(--gold)' }}>AUDIO</span>
                    </h2>
                </Link>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    Admin Dashboard
                </p>
            </div>

            <nav>
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        style={{
                            width: '100%',
                            padding: '1rem 1.5rem',
                            background: activeTab === tab.id ? 'rgba(212, 175, 55, 0.1)' : 'transparent',
                            border: 'none',
                            borderLeft: activeTab === tab.id ? '3px solid var(--gold)' : '3px solid transparent',
                            color: activeTab === tab.id ? 'var(--gold)' : 'var(--text-gray)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.75rem',
                            cursor: 'pointer',
                            fontSize: '0.9rem',
                            textAlign: 'left',
                            transition: 'all 0.2s ease'
                        }}
                    >
                        <span style={{ fontSize: '1.25rem' }}>{tab.icon}</span>
                        {tab.label}
                    </button>
                ))}
            </nav>

            <div style={{
                position: 'absolute',
                bottom: '2rem',
                left: '0',
                right: '0',
                padding: '0 1.5rem'
            }}>
                <Link href="/" className="btn btn-secondary" style={{ width: '100%', padding: '0.75rem' }}>
                    ← Back to Site
                </Link>
            </div>
        </aside>
    );
}

// Dashboard Overview
function DashboardPanel({ health }) {
    return (
        <div>
            <h1 style={{ marginBottom: '2rem' }}>Dashboard</h1>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '1.5rem',
                marginBottom: '2rem'
            }}>
                <StatCard
                    icon="🎵"
                    label="Total Samples"
                    value={health?.total_samples || 0}
                />
                <StatCard
                    icon="🔑"
                    label="OpenAI API"
                    value={health?.openai_configured ? 'Connected' : 'Not Set'}
                    status={health?.openai_configured ? 'success' : 'warning'}
                />
                <StatCard
                    icon="✨"
                    label="System Status"
                    value={health?.status === 'healthy' ? 'Online' : 'Offline'}
                    status={health?.status === 'healthy' ? 'success' : 'error'}
                />
                <StatCard
                    icon="📦"
                    label="Version"
                    value={health?.version || '1.0.0'}
                />
            </div>

            <div style={{
                background: 'rgba(26, 26, 46, 0.5)',
                borderRadius: '12px',
                padding: '1.5rem',
                border: '1px solid rgba(255,255,255,0.05)'
            }}>
                <h3 style={{ marginBottom: '1rem' }}>Quick Actions</h3>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    <button className="btn btn-primary">Upload Sample</button>
                    <button className="btn btn-secondary">Test OpenAI</button>
                    <button className="btn btn-secondary">View Logs</button>
                </div>
            </div>
        </div>
    );
}

function StatCard({ icon, label, value, status }) {
    const statusColors = {
        success: 'var(--success-green)',
        warning: 'var(--gold)',
        error: '#ff4444'
    };

    return (
        <div style={{
            background: 'rgba(26, 26, 46, 0.5)',
            borderRadius: '12px',
            padding: '1.5rem',
            border: '1px solid rgba(255,255,255,0.05)'
        }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{icon}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>{label}</div>
            <div style={{
                fontSize: '1.5rem',
                fontWeight: 700,
                color: status ? statusColors[status] : 'var(--text-white)'
            }}>
                {value}
            </div>
        </div>
    );
}

// API Settings Panel
function APISettingsPanel({ config, setConfig, onSave }) {
    const [apiKey, setApiKey] = useState('');
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState(null);

    const handleSave = async () => {
        const newConfig = {
            openai_api_key: apiKey || undefined,
            default_genre: config.default_genre,
            default_bpm: config.default_bpm,
            sample_rate: config.sample_rate
        };

        try {
            const res = await fetch(`${API_BASE}/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newConfig)
            });

            if (res.ok) {
                onSave();
                setApiKey('');
            }
        } catch (err) {
            console.error('Failed to save config:', err);
        }
    };

    const testConnection = async () => {
        setTesting(true);
        setTestResult(null);

        try {
            const res = await fetch(`${API_BASE}/config/test-openai`);
            const data = await res.json();

            if (res.ok) {
                setTestResult({ success: true, message: 'Connection successful!', models: data.models });
            } else {
                setTestResult({ success: false, message: data.detail });
            }
        } catch (err) {
            setTestResult({ success: false, message: 'Failed to connect to backend' });
        }

        setTesting(false);
    };

    return (
        <div>
            <h1 style={{ marginBottom: '2rem' }}>API Settings</h1>

            {/* OpenAI Section */}
            <div style={{
                background: 'rgba(26, 26, 46, 0.5)',
                borderRadius: '12px',
                padding: '1.5rem',
                marginBottom: '1.5rem',
                border: '1px solid rgba(255,255,255,0.05)'
            }}>
                <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    🔑 OpenAI API
                    {config.openai_api_key_set && (
                        <span style={{
                            background: 'var(--success-green)',
                            color: 'black',
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.7rem',
                            fontWeight: 600
                        }}>
                            CONFIGURED
                        </span>
                    )}
                </h3>

                {config.openai_api_key_set && (
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '1rem' }}>
                        Current key: {config.openai_api_key_masked}
                    </p>
                )}

                <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>
                        {config.openai_api_key_set ? 'Update API Key' : 'Enter API Key'}
                    </label>
                    <input
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="sk-..."
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            background: 'rgba(0,0,0,0.3)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                            color: 'white',
                            fontSize: '1rem'
                        }}
                    />
                </div>

                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button
                        className="btn btn-primary"
                        onClick={handleSave}
                        disabled={!apiKey}
                        style={{ opacity: apiKey ? 1 : 0.5 }}
                    >
                        Save Key
                    </button>
                    <button
                        className="btn btn-secondary"
                        onClick={testConnection}
                        disabled={testing || !config.openai_api_key_set}
                        style={{ opacity: config.openai_api_key_set ? 1 : 0.5 }}
                    >
                        {testing ? 'Testing...' : 'Test Connection'}
                    </button>
                </div>

                {testResult && (
                    <div style={{
                        marginTop: '1rem',
                        padding: '1rem',
                        borderRadius: '8px',
                        background: testResult.success ? 'rgba(0, 255, 136, 0.1)' : 'rgba(255, 68, 68, 0.1)',
                        border: `1px solid ${testResult.success ? 'var(--success-green)' : '#ff4444'}`
                    }}>
                        {testResult.success ? '✅' : '❌'} {testResult.message}
                    </div>
                )}
            </div>

            {/* Default Settings */}
            <div style={{
                background: 'rgba(26, 26, 46, 0.5)',
                borderRadius: '12px',
                padding: '1.5rem',
                border: '1px solid rgba(255,255,255,0.05)'
            }}>
                <h3 style={{ marginBottom: '1rem' }}>⚙️ Default Generation Settings</h3>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>
                            Default Genre
                        </label>
                        <select
                            value={config.default_genre}
                            onChange={(e) => setConfig({ ...config, default_genre: e.target.value })}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                background: 'rgba(0,0,0,0.3)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '8px',
                                color: 'white'
                            }}
                        >
                            <option value="bachata">Bachata</option>
                            <option value="salsa">Salsa</option>
                            <option value="merengue">Merengue</option>
                            <option value="bolero">Bolero</option>
                        </select>
                    </div>

                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>
                            Default BPM
                        </label>
                        <input
                            type="number"
                            value={config.default_bpm}
                            onChange={(e) => setConfig({ ...config, default_bpm: parseInt(e.target.value) })}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                background: 'rgba(0,0,0,0.3)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '8px',
                                color: 'white'
                            }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

// Sample Library Panel
function SampleLibraryPanel({ samples, onRefresh }) {
    const [uploading, setUploading] = useState(false);
    const [uploadForm, setUploadForm] = useState({
        project: 'default',
        genre: 'bolero',
        instrument: 'full_mix',
        category: 'stem',
        tags: ''
    });
    const [uploadProgress, setUploadProgress] = useState(null);
    const [editingSample, setEditingSample] = useState(null);

    const handleUpload = async (e) => {
        const files = Array.from(e.target.files);
        if (!files.length) return;

        setUploading(true);
        setUploadProgress({ current: 0, total: files.length });

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            setUploadProgress({ current: i + 1, total: files.length });

            const formData = new FormData();
            formData.append('file', file);
            formData.append('project', uploadForm.project);
            formData.append('genre', uploadForm.genre);
            formData.append('instrument', uploadForm.instrument);
            formData.append('category', uploadForm.category);
            formData.append('tags', uploadForm.tags);

            try {
                await fetch(`${API_BASE}/samples/upload`, {
                    method: 'POST',
                    body: formData
                });
            } catch (err) {
                console.error(`Upload failed for ${file.name}:`, err);
            }
        }

        onRefresh();
        setUploading(false);
        setUploadProgress(null);
        // Reset file input
        e.target.value = '';
    };

    const handleDelete = async (sampleId) => {
        if (!confirm('Delete this sample?')) return;

        try {
            await fetch(`${API_BASE}/samples/${sampleId}`, { method: 'DELETE' });
            onRefresh();
        } catch (err) {
            console.error('Delete failed:', err);
        }
    };

    const handleConvert = async (sampleId) => {
        try {
            const res = await fetch(`${API_BASE}/convert/audio-to-midi?sample_id=${sampleId}`, {
                method: 'POST'
            });
            const data = await res.json();

            if (res.ok) {
                alert(`MIDI created: ${data.midi_path}`);
            } else {
                alert(`Conversion failed: ${data.detail}`);
            }
        } catch (err) {
            alert('Conversion failed');
        }
    };

    const handleEdit = (sample) => {
        setEditingSample({
            id: sample.id,
            genre: sample.genre || 'bolero',
            instrument: sample.instrument || 'full_mix',
            category: sample.category || 'stem'
        });
    };

    const handleSaveEdit = async () => {
        if (!editingSample) return;

        try {
            const res = await fetch(`${API_BASE}/samples/${editingSample.id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    genre: editingSample.genre,
                    instrument: editingSample.instrument,
                    category: editingSample.category
                })
            });

            if (res.ok) {
                onRefresh();
                setEditingSample(null);
            } else {
                alert('Error al guardar');
            }
        } catch (err) {
            console.error('Edit failed:', err);
            alert('Error al guardar');
        }
    };

    return (
        <div>
            <h1 style={{ marginBottom: '2rem' }}>Sample Library</h1>

            {/* Upload Section */}
            <div style={{
                background: 'rgba(26, 26, 46, 0.5)',
                borderRadius: '12px',
                padding: '1.5rem',
                marginBottom: '1.5rem',
                border: '1px solid rgba(255,255,255,0.05)'
            }}>
                <h3 style={{ marginBottom: '1rem' }}>📤 Upload New Sample</h3>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--electric-blue)', fontWeight: 600 }}>
                            📁 Proyecto
                        </label>
                        <input
                            type="text"
                            value={uploadForm.project}
                            onChange={(e) => setUploadForm({ ...uploadForm, project: e.target.value.replace(/\s+/g, '_') })}
                            placeholder="mi_proyecto"
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                background: 'rgba(0, 212, 255, 0.1)',
                                border: '1px solid var(--electric-blue)',
                                borderRadius: '8px',
                                color: 'white',
                                fontWeight: 500
                            }}
                        />
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--gold)', fontWeight: 600 }}>
                            🎵 Género Musical
                        </label>
                        <select
                            value={uploadForm.genre}
                            onChange={(e) => setUploadForm({ ...uploadForm, genre: e.target.value })}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                background: 'rgba(212, 175, 55, 0.1)',
                                border: '1px solid var(--gold)',
                                borderRadius: '8px',
                                color: 'white',
                                fontWeight: 500
                            }}
                        >
                            <optgroup label="🇲🇩 Tropical Dominicano">
                                <option value="bolero">Bolero</option>
                                <option value="bachata_popular">Bachata Popular</option>
                                <option value="bachata_tradicional">Bachata Tradicional</option>
                                <option value="merengue_orquesta">Merengue de Orquesta</option>
                                <option value="merengue_tipico">Merengue Típico</option>
                            </optgroup>
                            <optgroup label="🇵🇷 Salsa & Latín">
                                <option value="salsa">Salsa</option>
                                <option value="salsa_romantica">Salsa Romántica</option>
                                <option value="son_cubano">Son Cubano</option>
                            </optgroup>
                            <optgroup label="🇨🇴 Colombia">
                                <option value="vallenato">Vallenato</option>
                                <option value="cumbia">Cumbia</option>
                            </optgroup>
                            <optgroup label="🎹 Otros">
                                <option value="balada">Balada</option>
                                <option value="pop_latino">Pop Latino</option>
                                <option value="other">Otro</option>
                            </optgroup>
                        </select>
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>
                            Instrumento
                        </label>
                        <select
                            value={uploadForm.instrument}
                            onChange={(e) => setUploadForm({ ...uploadForm, instrument: e.target.value })}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                background: 'rgba(0,0,0,0.3)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '8px',
                                color: 'white'
                            }}
                        >
                            <optgroup label="🎸 Guitarras">
                                <option value="requinto">Requinto</option>
                                <option value="segunda">Segunda Guitarra</option>
                                <option value="acoustic_guitar">Guitarra Acústica</option>
                                <option value="electric_guitar">Guitarra Eléctrica</option>
                            </optgroup>
                            <optgroup label="🎹 Teclados">
                                <option value="piano">Piano</option>
                                <option value="keys">Teclados/Synth</option>
                                <option value="organ">Órgano</option>
                            </optgroup>
                            <optgroup label="🎻 Cuerdas">
                                <option value="strings">Cuerdas (Ensemble)</option>
                                <option value="violin">Violín</option>
                                <option value="viola">Viola</option>
                                <option value="cello">Cello</option>
                                <option value="contrabass">Contrabajo</option>
                            </optgroup>
                            <optgroup label="🥁 Percusión">
                                <option value="bongo">Bongo</option>
                                <option value="congas">Congas</option>
                                <option value="timbales">Timbales</option>
                                <option value="tambora">Tambora</option>
                                <option value="guira">Güira</option>
                                <option value="drums">Drums Kit</option>
                            </optgroup>
                            <optgroup label="🎷 Vientos">
                                <option value="saxophone">Saxofón</option>
                                <option value="trumpet">Trompeta</option>
                                <option value="trombone">Trombón</option>
                                <option value="brass">Metales (Ensemble)</option>
                                <option value="horns">Cuernos</option>
                            </optgroup>
                            <optgroup label="🎤 Voces">
                                <option value="vocals">Voz Principal</option>
                                <option value="backing_vocals">Coros</option>
                            </optgroup>
                            <optgroup label="🎵 Otros">
                                <option value="bass">Bajo</option>
                                <option value="fx">Efectos/FX</option>
                                <option value="full_mix">Mezcla Completa</option>
                            </optgroup>
                        </select>
                    </div>

                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>
                            Category
                        </label>
                        <select
                            value={uploadForm.category}
                            onChange={(e) => setUploadForm({ ...uploadForm, category: e.target.value })}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                background: 'rgba(0,0,0,0.3)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '8px',
                                color: 'white'
                            }}
                        >
                            <optgroup label="📁 Proyecto">
                                <option value="stem">Stem (Track Completo)</option>
                                <option value="full_track">Track Completo</option>
                                <option value="loop">Loop</option>
                            </optgroup>
                            <optgroup label="🎵 Samples">
                                <option value="notes">Notas Individuales</option>
                                <option value="chords">Acordes</option>
                                <option value="phrases">Frases/Melodías</option>
                                <option value="arpeggios">Arpegios</option>
                            </optgroup>
                            <optgroup label="🥁 Percusión">
                                <option value="hits">Hits/One-shots</option>
                                <option value="patterns">Patrones Rítmicos</option>
                            </optgroup>
                            <optgroup label="🎸 Técnicas">
                                <option value="mordentes">Mordentes/Ornamentos</option>
                                <option value="slides">Slides/Glissandos</option>
                                <option value="vibrato">Vibrato</option>
                            </optgroup>
                        </select>
                    </div>

                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>
                            Tags (comma-separated)
                        </label>
                        <input
                            type="text"
                            value={uploadForm.tags}
                            onChange={(e) => setUploadForm({ ...uploadForm, tags: e.target.value })}
                            placeholder="vibrato, E4, soft"
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                background: 'rgba(0,0,0,0.3)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '8px',
                                color: 'white'
                            }}
                        />
                    </div>
                </div>

                <label className="btn btn-primary" style={{ cursor: 'pointer' }}>
                    {uploading
                        ? `Uploading ${uploadProgress?.current}/${uploadProgress?.total}...`
                        : '📁 Choose Audio Files'}
                    <input
                        type="file"
                        accept=".wav,.mp3,.aiff,.flac"
                        onChange={handleUpload}
                        style={{ display: 'none' }}
                        disabled={uploading}
                        multiple
                    />
                </label>
                <span style={{ marginLeft: '1rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    WAV, MP3, AIFF, FLAC (48kHz recommended) - Selecciona múltiples archivos
                </span>
            </div>

            {/* Samples List */}
            <div style={{
                background: 'rgba(26, 26, 46, 0.5)',
                borderRadius: '12px',
                padding: '1.5rem',
                border: '1px solid rgba(255,255,255,0.05)'
            }}>
                <h3 style={{ marginBottom: '1rem' }}>
                    🎵 Samples ({samples.length})
                </h3>

                {samples.length === 0 ? (
                    <p style={{ color: 'var(--text-muted)' }}>
                        No samples uploaded yet. Upload your first sample above!
                    </p>
                ) : (
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                <th style={{ padding: '0.75rem', textAlign: 'left', color: 'var(--text-muted)' }}>File</th>
                                <th style={{ padding: '0.75rem', textAlign: 'left', color: 'var(--gold)' }}>Género</th>
                                <th style={{ padding: '0.75rem', textAlign: 'left', color: 'var(--text-muted)' }}>Instrumento</th>
                                <th style={{ padding: '0.75rem', textAlign: 'left', color: 'var(--text-muted)' }}>Categoría</th>
                                <th style={{ padding: '0.75rem', textAlign: 'left', color: 'var(--text-muted)' }}>Duración</th>
                                <th style={{ padding: '0.75rem', textAlign: 'right', color: 'var(--text-muted)' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {samples.map(sample => (
                                <tr key={sample.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                    <td style={{ padding: '0.75rem' }}>
                                        <span style={{ color: 'var(--gold)' }}>{sample.original_filename}</span>
                                    </td>
                                    <td style={{ padding: '0.75rem', textTransform: 'capitalize', color: 'var(--electric-blue)' }}>{sample.genre || 'N/A'}</td>
                                    <td style={{ padding: '0.75rem', textTransform: 'capitalize' }}>{sample.instrument}</td>
                                    <td style={{ padding: '0.75rem', textTransform: 'capitalize' }}>{sample.category}</td>
                                    <td style={{ padding: '0.75rem' }}>{sample.duration?.toFixed(2) || 0}s</td>
                                    <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                                        <button
                                            onClick={() => handleEdit(sample)}
                                            style={{
                                                background: 'rgba(212, 175, 55, 0.2)',
                                                border: '1px solid var(--gold)',
                                                color: 'var(--gold)',
                                                padding: '0.25rem 0.75rem',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                marginRight: '0.5rem'
                                            }}
                                        >
                                            ✏️ Edit
                                        </button>
                                        <button
                                            onClick={() => handleConvert(sample.id)}
                                            style={{
                                                background: 'rgba(0, 212, 255, 0.2)',
                                                border: '1px solid var(--electric-blue)',
                                                color: 'var(--electric-blue)',
                                                padding: '0.25rem 0.75rem',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                marginRight: '0.5rem'
                                            }}
                                        >
                                            → MIDI
                                        </button>
                                        <button
                                            onClick={() => handleDelete(sample.id)}
                                            style={{
                                                background: 'rgba(255, 68, 68, 0.2)',
                                                border: '1px solid #ff4444',
                                                color: '#ff4444',
                                                padding: '0.25rem 0.75rem',
                                                borderRadius: '4px',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Edit Modal */}
            {editingSample && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0,0,0,0.8)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000
                }}>
                    <div style={{
                        background: 'var(--carbon)',
                        borderRadius: '12px',
                        padding: '2rem',
                        minWidth: '400px',
                        border: '1px solid var(--gold)'
                    }}>
                        <h3 style={{ marginBottom: '1.5rem' }}>✏️ Editar Sample</h3>

                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--gold)' }}>Género</label>
                            <select
                                value={editingSample.genre}
                                onChange={(e) => setEditingSample({ ...editingSample, genre: e.target.value })}
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    background: 'rgba(0,0,0,0.3)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px',
                                    color: 'white'
                                }}
                            >
                                <option value="bolero">Bolero</option>
                                <option value="bachata_popular">Bachata Popular</option>
                                <option value="bachata_tradicional">Bachata Tradicional</option>
                                <option value="merengue_orquesta">Merengue de Orquesta</option>
                                <option value="merengue_tipico">Merengue Típico</option>
                                <option value="salsa">Salsa</option>
                                <option value="salsa_romantica">Salsa Romántica</option>
                                <option value="vallenato">Vallenato</option>
                                <option value="cumbia">Cumbia</option>
                                <option value="balada">Balada</option>
                                <option value="pop_latino">Pop Latino</option>
                            </select>
                        </div>

                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>Instrumento</label>
                            <select
                                value={editingSample.instrument}
                                onChange={(e) => setEditingSample({ ...editingSample, instrument: e.target.value })}
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    background: 'rgba(0,0,0,0.3)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px',
                                    color: 'white'
                                }}
                            >
                                <option value="full_mix">Mezcla Completa</option>
                                <option value="requinto">Requinto</option>
                                <option value="segunda">Segunda Guitarra</option>
                                <option value="piano">Piano</option>
                                <option value="strings">Cuerdas</option>
                                <option value="violin">Violín</option>
                                <option value="bongo">Bongo</option>
                                <option value="congas">Congas</option>
                                <option value="bass">Bajo</option>
                                <option value="vocals">Voz</option>
                                <option value="backing_vocals">Coros</option>
                            </select>
                        </div>

                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>Categoría</label>
                            <select
                                value={editingSample.category}
                                onChange={(e) => setEditingSample({ ...editingSample, category: e.target.value })}
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    background: 'rgba(0,0,0,0.3)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px',
                                    color: 'white'
                                }}
                            >
                                <option value="stem">Stem (Track Completo)</option>
                                <option value="full_track">Full Track</option>
                                <option value="loop">Loop</option>
                                <option value="notes">Notas</option>
                                <option value="chords">Acordes</option>
                                <option value="phrases">Frases</option>
                            </select>
                        </div>

                        <div style={{ display: 'flex', gap: '1rem' }}>
                            <button
                                onClick={handleSaveEdit}
                                className="btn btn-primary"
                            >
                                💾 Guardar
                            </button>
                            <button
                                onClick={() => setEditingSample(null)}
                                className="btn btn-secondary"
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

// Training Panel
function TrainingPanel({ trainingStatus }) {
    return (
        <div>
            <h1 style={{ marginBottom: '2rem' }}>Training</h1>

            <div style={{
                background: 'rgba(26, 26, 46, 0.5)',
                borderRadius: '12px',
                padding: '1.5rem',
                marginBottom: '1.5rem',
                border: '1px solid rgba(255,255,255,0.05)'
            }}>
                <h3 style={{ marginBottom: '1rem' }}>📊 Training Status</h3>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--gold)' }}>
                            {trainingStatus?.total_samples || 0}
                        </div>
                        <div style={{ color: 'var(--text-muted)' }}>Total Samples</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{
                            fontSize: '2rem',
                            fontWeight: 700,
                            color: trainingStatus?.training_ready ? 'var(--success-green)' : 'var(--text-muted)'
                        }}>
                            {trainingStatus?.training_ready ? 'Ready' : 'Not Ready'}
                        </div>
                        <div style={{ color: 'var(--text-muted)' }}>Training Status</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 700 }}>
                            {trainingStatus?.model_version || '1.0.0'}
                        </div>
                        <div style={{ color: 'var(--text-muted)' }}>Model Version</div>
                    </div>
                </div>

                {/* Samples by Instrument */}
                {trainingStatus?.by_instrument && Object.keys(trainingStatus.by_instrument).length > 0 && (
                    <div>
                        <h4 style={{ marginBottom: '0.75rem', color: 'var(--text-gray)' }}>Samples by Instrument</h4>
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                            {Object.entries(trainingStatus.by_instrument).map(([inst, count]) => (
                                <span key={inst} style={{
                                    background: 'rgba(212, 175, 55, 0.2)',
                                    border: '1px solid var(--gold)',
                                    padding: '0.25rem 0.75rem',
                                    borderRadius: '20px',
                                    fontSize: '0.875rem'
                                }}>
                                    {inst}: {count}
                                </span>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Training Requirements */}
            <div style={{
                background: 'rgba(26, 26, 46, 0.5)',
                borderRadius: '12px',
                padding: '1.5rem',
                marginBottom: '1.5rem',
                border: '1px solid rgba(255,255,255,0.05)'
            }}>
                <h3 style={{ marginBottom: '1rem' }}>📋 Requirements for Training</h3>

                <ul style={{ listStyle: 'none', padding: 0 }}>
                    <li style={{
                        padding: '0.5rem 0',
                        display: 'flex',
                        alignItems: 'center',
                        color: trainingStatus?.total_samples >= 10 ? 'var(--success-green)' : 'var(--text-gray)'
                    }}>
                        <span style={{ marginRight: '0.75rem' }}>
                            {trainingStatus?.total_samples >= 10 ? '✅' : '⬜'}
                        </span>
                        Minimum 10 samples uploaded
                    </li>
                    <li style={{ padding: '0.5rem 0', display: 'flex', alignItems: 'center', color: 'var(--text-gray)' }}>
                        <span style={{ marginRight: '0.75rem' }}>⬜</span>
                        At least 2 different instruments
                    </li>
                    <li style={{ padding: '0.5rem 0', display: 'flex', alignItems: 'center', color: 'var(--text-gray)' }}>
                        <span style={{ marginRight: '0.75rem' }}>⬜</span>
                        OpenAI API configured
                    </li>
                </ul>
            </div>

            <button
                className="btn btn-primary"
                disabled={!trainingStatus?.training_ready}
                style={{ opacity: trainingStatus?.training_ready ? 1 : 0.5 }}
            >
                🚀 Start Training
            </button>
        </div>
    );
}

// Main Admin Page
export default function AdminPage() {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [health, setHealth] = useState(null);
    const [config, setConfig] = useState({
        default_genre: 'bachata',
        default_bpm: 115,
        sample_rate: 48000,
        openai_api_key_set: false,
        openai_api_key_masked: ''
    });
    const [samples, setSamples] = useState([]);
    const [trainingStatus, setTrainingStatus] = useState(null);
    const [backendError, setBackendError] = useState(false);

    const fetchData = async () => {
        try {
            // Health check
            const healthRes = await fetch(`${API_BASE}/health`);
            if (healthRes.ok) {
                setHealth(await healthRes.json());
                setBackendError(false);
            }

            // Config
            const configRes = await fetch(`${API_BASE}/config`);
            if (configRes.ok) {
                setConfig(await configRes.json());
            }

            // Samples
            const samplesRes = await fetch(`${API_BASE}/samples`);
            if (samplesRes.ok) {
                const data = await samplesRes.json();
                setSamples(data.samples);
            }

            // Training status
            const trainingRes = await fetch(`${API_BASE}/training/status`);
            if (trainingRes.ok) {
                setTrainingStatus(await trainingRes.json());
            }
        } catch (err) {
            console.error('Backend not available:', err);
            setBackendError(true);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    return (
        <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--primary-black)' }}>
            <AdminSidebar activeTab={activeTab} setActiveTab={setActiveTab} />

            <main style={{ flex: 1, padding: '2rem 3rem', overflowY: 'auto' }}>
                {backendError && (
                    <div style={{
                        background: 'rgba(255, 68, 68, 0.1)',
                        border: '1px solid #ff4444',
                        borderRadius: '8px',
                        padding: '1rem',
                        marginBottom: '1.5rem'
                    }}>
                        ⚠️ <strong>Backend not running.</strong> Start it with:
                        <code style={{
                            background: 'rgba(0,0,0,0.3)',
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            marginLeft: '0.5rem'
                        }}>
                            cd backend && uvicorn main:app --reload
                        </code>
                    </div>
                )}

                {activeTab === 'dashboard' && <DashboardPanel health={health} />}
                {activeTab === 'api' && <APISettingsPanel config={config} setConfig={setConfig} onSave={fetchData} />}
                {activeTab === 'samples' && <SampleLibraryPanel samples={samples} onRefresh={fetchData} />}
                {activeTab === 'training' && <TrainingPanel trainingStatus={trainingStatus} />}
            </main>
        </div>
    );
}
