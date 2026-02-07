'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import '../globals.css';

const API_BASE = 'http://localhost:8000/api';

/**
 * DGB AUDIO STUDIO
 * ================
 * Integrated ACE-Step workflows:
 * - Text2Music: Generate from prompts and lyrics
 * - Retake: Variations with different creative levels
 * - Repaint: Re-generate specific sections
 * - Edit: Modify lyrics keeping melody
 * - Extend: Add music before/after
 */

export default function StudioPage() {
    const router = useRouter();
    const [user, setUser] = useState(null);
    const [activeTab, setActiveTab] = useState('create');

    // ACE-Step Health
    const [aceStepConnected, setAceStepConnected] = useState(false);

    // Generation State
    const [isGenerating, setIsGenerating] = useState(false);
    const [generationProgress, setGenerationProgress] = useState(0);
    const [generatedAudio, setGeneratedAudio] = useState(null);
    const audioRef = useRef(null);

    // Create Tab State
    const [prompt, setPrompt] = useState('');
    const [lyrics, setLyrics] = useState('');
    const [duration, setDuration] = useState(60);
    const [antigravity, setAntigravity] = useState(50);
    const [selectedPreset, setSelectedPreset] = useState('');
    const [presets, setPresets] = useState([]);

    // Playback State
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [totalDuration, setTotalDuration] = useState(0);

    // History
    const [generations, setGenerations] = useState([]);

    // Auth check and initial data load
    useEffect(() => {
        const token = localStorage.getItem('dgb_token');
        if (!token) {
            router.push('/auth');
            return;
        }
        const storedUser = localStorage.getItem('dgb_user');
        if (storedUser) setUser(JSON.parse(storedUser));

        // Check ACE-Step connection
        checkAceStepHealth();
        loadPresets();
    }, [router]);

    const checkAceStepHealth = async () => {
        try {
            const res = await fetch(`${API_BASE}/acestep/health`);
            const data = await res.json();
            setAceStepConnected(data.connected);
        } catch {
            setAceStepConnected(false);
        }
    };

    const loadPresets = async () => {
        try {
            const res = await fetch(`${API_BASE}/acestep/presets`);
            const data = await res.json();
            setPresets(data.presets || []);
        } catch (e) {
            console.error('Failed to load presets:', e);
        }
    };

    // Generate music
    const handleGenerate = async () => {
        const token = localStorage.getItem('dgb_token');
        if (!token) return;

        setIsGenerating(true);
        setGenerationProgress(0);

        // Simulate progress
        const progressInterval = setInterval(() => {
            setGenerationProgress(prev => Math.min(prev + 5, 95));
        }, 1000);

        try {
            const res = await fetch(`${API_BASE}/generate/music?token=${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: selectedPreset ? presets.find(p => p.id === selectedPreset)?.prompt + ', ' + prompt : prompt,
                    lyrics,
                    duration,
                    antigravity,
                    genre: selectedPreset || 'tropical',
                    bpm: 120,
                    key: 'Am'
                })
            });

            const data = await res.json();
            clearInterval(progressInterval);
            setGenerationProgress(100);

            if (data.success) {
                setGeneratedAudio(data);
                setGenerations(prev => [data, ...prev.slice(0, 9)]);
            } else {
                alert(data.error || 'Generation failed');
            }
        } catch (e) {
            console.error('Generation error:', e);
            alert('Error connecting to server');
        } finally {
            clearInterval(progressInterval);
            setIsGenerating(false);
        }
    };

    // Retake (variation) generation
    const handleRetake = async () => {
        if (!generatedAudio) return;
        // Re-generate with same prompt but different seed
        setAntigravity(prev => Math.min(prev + 10, 100));
        await handleGenerate();
    };

    // Audio playback controls
    const togglePlayback = () => {
        if (audioRef.current) {
            if (isPlaying) {
                audioRef.current.pause();
            } else {
                audioRef.current.play();
            }
            setIsPlaying(!isPlaying);
        }
    };

    const handleTimeUpdate = () => {
        if (audioRef.current) {
            setCurrentTime(audioRef.current.currentTime);
            setTotalDuration(audioRef.current.duration || 0);
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // Antigravity mode label
    const getAntigravityMode = () => {
        if (antigravity < 20) return { name: 'Tradicional', emoji: '🎸', color: '#4ade80' };
        if (antigravity < 50) return { name: 'Balanceado', emoji: '🎹', color: '#60a5fa' };
        if (antigravity < 80) return { name: 'Creativo', emoji: '🚀', color: '#f472b6' };
        return { name: 'Experimental', emoji: '🌀', color: '#c084fc' };
    };

    const antigravityMode = getAntigravityMode();

    // Styles
    const styles = {
        container: {
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            background: 'linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #0a0a0f 100%)',
            color: 'white',
            overflow: 'hidden'
        },
        header: {
            padding: '1rem 2rem',
            borderBottom: '1px solid rgba(255,255,255,0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'rgba(0,0,0,0.4)',
            backdropFilter: 'blur(10px)'
        },
        logo: {
            fontSize: '1.5rem',
            fontWeight: 'bold',
            background: 'linear-gradient(90deg, #00d4ff, #00ff88)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
        },
        statusBadge: {
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '20px',
            fontSize: '0.85rem',
            background: aceStepConnected ? 'rgba(0,255,136,0.1)' : 'rgba(255,100,100,0.1)',
            border: aceStepConnected ? '1px solid rgba(0,255,136,0.3)' : '1px solid rgba(255,100,100,0.3)'
        },
        mainContent: {
            flex: 1,
            display: 'flex',
            overflow: 'hidden'
        },
        sidebar: {
            width: '280px',
            background: 'rgba(0,0,0,0.3)',
            borderRight: '1px solid rgba(255,255,255,0.1)',
            padding: '1.5rem',
            overflowY: 'auto'
        },
        workArea: {
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
        },
        tabs: {
            display: 'flex',
            gap: '0.5rem',
            padding: '1rem 2rem',
            borderBottom: '1px solid rgba(255,255,255,0.1)'
        },
        tab: (active) => ({
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            background: active ? 'linear-gradient(135deg, #00d4ff20, #00ff8820)' : 'transparent',
            border: active ? '1px solid rgba(0,212,255,0.3)' : '1px solid rgba(255,255,255,0.1)',
            cursor: 'pointer',
            transition: 'all 0.3s',
            color: active ? '#00d4ff' : 'rgba(255,255,255,0.7)'
        }),
        canvas: {
            flex: 1,
            padding: '2rem',
            overflowY: 'auto'
        },
        card: {
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '16px',
            border: '1px solid rgba(255,255,255,0.1)',
            padding: '1.5rem',
            marginBottom: '1.5rem'
        },
        label: {
            display: 'block',
            marginBottom: '0.5rem',
            color: 'rgba(255,255,255,0.7)',
            fontSize: '0.9rem'
        },
        input: {
            width: '100%',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            border: '1px solid rgba(255,255,255,0.2)',
            background: 'rgba(0,0,0,0.3)',
            color: 'white',
            fontSize: '1rem',
            outline: 'none'
        },
        textarea: {
            width: '100%',
            padding: '1rem',
            borderRadius: '8px',
            border: '1px solid rgba(255,255,255,0.2)',
            background: 'rgba(0,0,0,0.3)',
            color: 'white',
            fontSize: '1rem',
            minHeight: '150px',
            resize: 'vertical',
            outline: 'none',
            fontFamily: 'monospace'
        },
        slider: {
            width: '100%',
            height: '8px',
            borderRadius: '4px',
            appearance: 'none',
            background: `linear-gradient(90deg, #4ade80 0%, #60a5fa 33%, #f472b6 66%, #c084fc 100%)`,
            cursor: 'pointer'
        },
        primaryButton: {
            width: '100%',
            padding: '1rem',
            borderRadius: '12px',
            border: 'none',
            background: 'linear-gradient(135deg, #00d4ff, #00ff88)',
            color: '#000',
            fontSize: '1.1rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            transition: 'transform 0.2s'
        },
        presetButton: (selected) => ({
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            border: selected ? '2px solid #00d4ff' : '1px solid rgba(255,255,255,0.2)',
            background: selected ? 'rgba(0,212,255,0.2)' : 'rgba(255,255,255,0.05)',
            color: selected ? '#00d4ff' : 'white',
            cursor: 'pointer',
            textAlign: 'left',
            width: '100%',
            marginBottom: '0.5rem'
        }),
        player: {
            background: 'rgba(0,0,0,0.4)',
            borderTop: '1px solid rgba(255,255,255,0.1)',
            padding: '1rem 2rem',
            display: 'flex',
            alignItems: 'center',
            gap: '1.5rem'
        },
        playButton: {
            width: '50px',
            height: '50px',
            borderRadius: '50%',
            border: 'none',
            background: 'linear-gradient(135deg, #00d4ff, #00ff88)',
            color: '#000',
            fontSize: '1.2rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        },
        progressBar: {
            flex: 1,
            height: '6px',
            borderRadius: '3px',
            background: 'rgba(255,255,255,0.2)',
            position: 'relative',
            cursor: 'pointer'
        }
    };

    return (
        <div style={styles.container}>
            {/* Header */}
            <header style={styles.header}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                    <span style={styles.logo}>🎸 DGB STUDIO</span>
                    <div style={styles.statusBadge}>
                        <span style={{
                            width: '8px', height: '8px', borderRadius: '50%',
                            background: aceStepConnected ? '#00ff88' : '#ff6464'
                        }} />
                        {aceStepConnected ? 'ACE-Step Conectado' : 'ACE-Step Offline'}
                    </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <span style={{ color: 'rgba(255,255,255,0.7)' }}>
                        Hola, {user?.name || 'Usuario'}
                    </span>
                    <button
                        onClick={() => router.push('/dashboard')}
                        style={{ padding: '0.5rem 1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.2)', background: 'transparent', color: 'white', cursor: 'pointer' }}
                    >
                        Dashboard
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <div style={styles.mainContent}>
                {/* Sidebar - Presets */}
                <aside style={styles.sidebar}>
                    <h3 style={{ marginBottom: '1rem', fontSize: '1rem', color: 'rgba(255,255,255,0.5)' }}>
                        🎼 PRESETS DGB
                    </h3>
                    {presets.map(preset => (
                        <button
                            key={preset.id}
                            onClick={() => setSelectedPreset(preset.id === selectedPreset ? '' : preset.id)}
                            style={styles.presetButton(preset.id === selectedPreset)}
                        >
                            <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
                                {preset.id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </div>
                            <div style={{ fontSize: '0.75rem', opacity: 0.7 }}>
                                {preset.bpm} BPM • {preset.key}
                            </div>
                        </button>
                    ))}

                    <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.1)', margin: '1.5rem 0' }} />

                    <h3 style={{ marginBottom: '1rem', fontSize: '1rem', color: 'rgba(255,255,255,0.5)' }}>
                        📜 HISTORIAL
                    </h3>
                    {generations.length === 0 ? (
                        <p style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.5)' }}>
                            Sin generaciones aún
                        </p>
                    ) : (
                        generations.map((gen, i) => (
                            <div
                                key={gen.job_id}
                                onClick={() => setGeneratedAudio(gen)}
                                style={{
                                    padding: '0.75rem',
                                    borderRadius: '8px',
                                    background: generatedAudio?.job_id === gen.job_id ? 'rgba(0,212,255,0.2)' : 'rgba(255,255,255,0.05)',
                                    marginBottom: '0.5rem',
                                    cursor: 'pointer',
                                    fontSize: '0.85rem'
                                }}
                            >
                                <div>🎵 {gen.job_id.slice(0, 12)}...</div>
                                <div style={{ fontSize: '0.75rem', opacity: 0.6 }}>
                                    Antigravity: {gen.antigravity_params?.antigravity_level || 50}
                                </div>
                            </div>
                        ))
                    )}
                </aside>

                {/* Work Area */}
                <main style={styles.workArea}>
                    {/* Tabs */}
                    <nav style={styles.tabs}>
                        <button style={styles.tab(activeTab === 'create')} onClick={() => setActiveTab('create')}>
                            ✨ Crear
                        </button>
                        <button style={styles.tab(activeTab === 'retake')} onClick={() => setActiveTab('retake')}>
                            🔄 Variaciones
                        </button>
                        <button style={styles.tab(activeTab === 'repaint')} onClick={() => setActiveTab('repaint')}>
                            🎨 Repintar
                        </button>
                        <button style={styles.tab(activeTab === 'edit')} onClick={() => setActiveTab('edit')}>
                            ✏️ Editar
                        </button>
                        <button style={styles.tab(activeTab === 'extend')} onClick={() => setActiveTab('extend')}>
                            ➕ Extender
                        </button>
                    </nav>

                    {/* Canvas Area */}
                    <div style={styles.canvas}>
                        {/* CREATE TAB */}
                        {activeTab === 'create' && (
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                                {/* Left Column - Inputs */}
                                <div>
                                    <div style={styles.card}>
                                        <h2 style={{ marginBottom: '1.5rem', fontSize: '1.3rem' }}>
                                            🎵 Text2Music
                                        </h2>

                                        <label style={styles.label}>Estilo / Tags</label>
                                        <input
                                            type="text"
                                            value={prompt}
                                            onChange={(e) => setPrompt(e.target.value)}
                                            placeholder="romantic guitar, sensual vocals, Caribbean..."
                                            style={styles.input}
                                        />

                                        <label style={{ ...styles.label, marginTop: '1rem' }}>
                                            Letras (con [Verse], [Chorus], etc.)
                                        </label>
                                        <textarea
                                            value={lyrics}
                                            onChange={(e) => setLyrics(e.target.value)}
                                            placeholder="[Verse 1]
Bajo la luna de Santo Domingo
Tu mirada me tiene perdido

[Chorus]
Bailando bachata contigo
El tiempo se detiene..."
                                            style={styles.textarea}
                                        />
                                    </div>

                                    <div style={styles.card}>
                                        <label style={styles.label}>Duración: {duration}s</label>
                                        <input
                                            type="range"
                                            min="30"
                                            max="240"
                                            value={duration}
                                            onChange={(e) => setDuration(parseInt(e.target.value))}
                                            style={{ ...styles.slider, background: 'rgba(255,255,255,0.3)' }}
                                        />
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', opacity: 0.5, marginTop: '0.5rem' }}>
                                            <span>30s</span>
                                            <span>4 min</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Right Column - Antigravity & Generate */}
                                <div>
                                    <div style={styles.card}>
                                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                            <h2 style={{ fontSize: '1.3rem' }}>🌀 Antigravity Engine</h2>
                                            <div style={{
                                                padding: '0.5rem 1rem',
                                                borderRadius: '20px',
                                                background: `${antigravityMode.color}20`,
                                                border: `1px solid ${antigravityMode.color}50`,
                                                color: antigravityMode.color,
                                                fontSize: '0.9rem'
                                            }}>
                                                {antigravityMode.emoji} {antigravityMode.name}
                                            </div>
                                        </div>

                                        <div style={{
                                            fontSize: '3rem',
                                            fontWeight: 'bold',
                                            textAlign: 'center',
                                            background: `linear-gradient(90deg, #4ade80, #60a5fa, #f472b6, #c084fc)`,
                                            WebkitBackgroundClip: 'text',
                                            WebkitTextFillColor: 'transparent',
                                            marginBottom: '1rem'
                                        }}>
                                            {antigravity}
                                        </div>

                                        <input
                                            type="range"
                                            min="0"
                                            max="100"
                                            value={antigravity}
                                            onChange={(e) => setAntigravity(parseInt(e.target.value))}
                                            style={styles.slider}
                                        />

                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.75rem', fontSize: '0.8rem' }}>
                                            <span style={{ color: '#4ade80' }}>🎸 Tradicional</span>
                                            <span style={{ color: '#c084fc' }}>🌀 Experimental</span>
                                        </div>

                                        <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'rgba(255,255,255,0.6)', textAlign: 'center' }}>
                                            {antigravity < 20 && "Sonido auténtico y fiel al género seleccionado"}
                                            {antigravity >= 20 && antigravity < 50 && "Equilibrio entre tradición e innovación"}
                                            {antigravity >= 50 && antigravity < 80 && "Explorando nuevos territorios sonoros"}
                                            {antigravity >= 80 && "¡Rompiendo todas las reglas musicales!"}
                                        </p>
                                    </div>

                                    <button
                                        onClick={handleGenerate}
                                        disabled={isGenerating || !aceStepConnected}
                                        style={{
                                            ...styles.primaryButton,
                                            opacity: isGenerating || !aceStepConnected ? 0.6 : 1,
                                            cursor: isGenerating || !aceStepConnected ? 'not-allowed' : 'pointer'
                                        }}
                                    >
                                        {isGenerating ? (
                                            <>
                                                <span className="spinner">⏳</span>
                                                Generando... {generationProgress}%
                                            </>
                                        ) : (
                                            <>
                                                ✨ Generar Música
                                            </>
                                        )}
                                    </button>

                                    {isGenerating && (
                                        <div style={{ marginTop: '1rem' }}>
                                            <div style={{
                                                height: '4px',
                                                borderRadius: '2px',
                                                background: 'rgba(255,255,255,0.2)',
                                                overflow: 'hidden'
                                            }}>
                                                <div style={{
                                                    height: '100%',
                                                    width: `${generationProgress}%`,
                                                    background: 'linear-gradient(90deg, #00d4ff, #00ff88)',
                                                    transition: 'width 0.3s'
                                                }} />
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* RETAKE TAB */}
                        {activeTab === 'retake' && (
                            <div style={styles.card}>
                                <h2 style={{ marginBottom: '1rem' }}>🔄 Variaciones</h2>
                                <p style={{ color: 'rgba(255,255,255,0.7)', marginBottom: '1.5rem' }}>
                                    Genera variaciones de tu última canción con diferentes niveles de creatividad.
                                </p>

                                {generatedAudio ? (
                                    <div>
                                        <p>Última generación: <strong>{generatedAudio.job_id}</strong></p>
                                        <button
                                            onClick={handleRetake}
                                            disabled={isGenerating}
                                            style={{ ...styles.primaryButton, marginTop: '1rem', maxWidth: '300px' }}
                                        >
                                            🔄 Generar Variación
                                        </button>
                                    </div>
                                ) : (
                                    <p style={{ color: 'rgba(255,255,255,0.5)' }}>
                                        Primero genera una canción en la pestaña "Crear"
                                    </p>
                                )}
                            </div>
                        )}

                        {/* REPAINT TAB */}
                        {activeTab === 'repaint' && (
                            <div style={styles.card}>
                                <h2 style={{ marginBottom: '1rem' }}>🎨 Repintar Sección</h2>
                                <p style={{ color: 'rgba(255,255,255,0.7)', marginBottom: '1.5rem' }}>
                                    Re-genera una sección específica de tu canción manteniendo el resto intacto.
                                </p>
                                <p style={{ color: 'rgba(255,255,255,0.5)', fontStyle: 'italic' }}>
                                    🔜 Próximamente disponible
                                </p>
                            </div>
                        )}

                        {/* EDIT TAB */}
                        {activeTab === 'edit' && (
                            <div style={styles.card}>
                                <h2 style={{ marginBottom: '1rem' }}>✏️ Editar Letras</h2>
                                <p style={{ color: 'rgba(255,255,255,0.7)', marginBottom: '1.5rem' }}>
                                    Modifica las letras de tu canción manteniendo la melodía y el acompañamiento.
                                </p>
                                <p style={{ color: 'rgba(255,255,255,0.5)', fontStyle: 'italic' }}>
                                    🔜 Próximamente disponible
                                </p>
                            </div>
                        )}

                        {/* EXTEND TAB */}
                        {activeTab === 'extend' && (
                            <div style={styles.card}>
                                <h2 style={{ marginBottom: '1rem' }}>➕ Extender</h2>
                                <p style={{ color: 'rgba(255,255,255,0.7)', marginBottom: '1.5rem' }}>
                                    Añade música al principio o al final de tu canción existente.
                                </p>
                                <p style={{ color: 'rgba(255,255,255,0.5)', fontStyle: 'italic' }}>
                                    🔜 Próximamente disponible
                                </p>
                            </div>
                        )}
                    </div>
                </main>
            </div>

            {/* Audio Player */}
            {generatedAudio && (
                <footer style={styles.player}>
                    <button onClick={togglePlayback} style={styles.playButton}>
                        {isPlaying ? '⏸️' : '▶️'}
                    </button>

                    <div style={{ minWidth: '60px', fontSize: '0.9rem' }}>
                        {formatTime(currentTime)}
                    </div>

                    <div style={styles.progressBar}>
                        <div style={{
                            position: 'absolute',
                            left: 0,
                            top: 0,
                            height: '100%',
                            width: `${totalDuration ? (currentTime / totalDuration) * 100 : 0}%`,
                            background: 'linear-gradient(90deg, #00d4ff, #00ff88)',
                            borderRadius: '3px'
                        }} />
                    </div>

                    <div style={{ minWidth: '60px', fontSize: '0.9rem', textAlign: 'right' }}>
                        {formatTime(totalDuration)}
                    </div>

                    <div style={{ marginLeft: '1rem', color: 'rgba(255,255,255,0.7)', fontSize: '0.85rem' }}>
                        🎵 {generatedAudio.job_id}
                    </div>

                    <audio
                        ref={audioRef}
                        src={`${API_BASE}/audio/${generatedAudio.job_id}.wav`}
                        onTimeUpdate={handleTimeUpdate}
                        onEnded={() => setIsPlaying(false)}
                        onLoadedMetadata={handleTimeUpdate}
                    />
                </footer>
            )}
        </div>
    );
}
