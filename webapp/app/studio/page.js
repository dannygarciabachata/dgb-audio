'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import '../globals.css';

const API_BASE = 'http://localhost:8000/api';

/**
 * DGB AUDIO STUDIO - Suno-Style Interface
 * ========================================
 * Features:
 * - Creation panel with real-time generation view
 * - Visual waveform/progress during generation
 * - Prominent audio player like Suno
 * - History sidebar with generated tracks
 */

export default function StudioPage() {
    const router = useRouter();
    const [user, setUser] = useState(null);
    const [aceStepConnected, setAceStepConnected] = useState(false);

    // Generation State
    const [isGenerating, setIsGenerating] = useState(false);
    const [generationProgress, setGenerationProgress] = useState(0);
    const [generationStage, setGenerationStage] = useState('');
    const [currentGeneration, setCurrentGeneration] = useState(null);
    const audioRef = useRef(null);

    // Input State
    const [prompt, setPrompt] = useState('');
    const [lyrics, setLyrics] = useState('');
    const [duration, setDuration] = useState(60);
    const [antigravity, setAntigravity] = useState(50);
    const [selectedPreset, setSelectedPreset] = useState(null);
    const [presets, setPresets] = useState([]);

    // Player State
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [totalDuration, setTotalDuration] = useState(0);

    // History
    const [generations, setGenerations] = useState([]);

    // Auth & Initial Load
    useEffect(() => {
        const token = localStorage.getItem('dgb_token');
        if (!token) {
            router.push('/auth');
            return;
        }
        const storedUser = localStorage.getItem('dgb_user');
        if (storedUser) setUser(JSON.parse(storedUser));

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

    // Generate Music
    const handleGenerate = async () => {
        const token = localStorage.getItem('dgb_token');
        if (!token || !aceStepConnected) return;

        setIsGenerating(true);
        setGenerationProgress(0);
        setGenerationStage('Preparando modelo...');
        setCurrentGeneration(null);

        // Simulate progress stages
        const stages = [
            { progress: 10, stage: 'Inicializando ACE-Step...' },
            { progress: 25, stage: 'Procesando prompt y letras...' },
            { progress: 40, stage: 'Generando composición...' },
            { progress: 60, stage: 'Creando melodía y ritmo...' },
            { progress: 80, stage: 'Renderizando audio...' },
            { progress: 95, stage: 'Finalizando...' }
        ];

        let stageIndex = 0;
        const progressInterval = setInterval(() => {
            if (stageIndex < stages.length) {
                setGenerationProgress(stages[stageIndex].progress);
                setGenerationStage(stages[stageIndex].stage);
                stageIndex++;
            }
        }, 3000);

        try {
            const fullPrompt = selectedPreset
                ? `${presets.find(p => p.id === selectedPreset)?.prompt || ''}, ${prompt}`
                : prompt || 'tropical, bachata, romantic';

            const res = await fetch(`${API_BASE}/generate/music?token=${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: fullPrompt,
                    lyrics: lyrics || '[instrumental]',
                    duration,
                    antigravity,
                    genre: selectedPreset || 'tropical',
                    bpm: 120,
                    key: 'Am'
                })
            });

            const data = await res.json();
            clearInterval(progressInterval);

            if (data.success) {
                setGenerationProgress(100);
                setGenerationStage('¡Completado!');
                setCurrentGeneration(data);
                setGenerations(prev => [data, ...prev.slice(0, 19)]);

                // Auto-play after short delay
                setTimeout(() => {
                    if (audioRef.current) {
                        audioRef.current.load();
                    }
                }, 500);
            } else {
                setGenerationStage(`Error: ${data.error || 'Generación fallida'}`);
            }
        } catch (e) {
            clearInterval(progressInterval);
            console.error('Generation error:', e);
            setGenerationStage('Error de conexión con el servidor');
        } finally {
            setTimeout(() => {
                setIsGenerating(false);
            }, 2000);
        }
    };

    // Audio Controls
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

    const handleSeek = (e) => {
        if (audioRef.current && totalDuration) {
            const rect = e.currentTarget.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            audioRef.current.currentTime = percent * totalDuration;
        }
    };

    const formatTime = (seconds) => {
        if (!seconds || isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // Antigravity Mode
    const getAntigravityMode = () => {
        if (antigravity < 20) return { name: 'Tradicional', color: '#10b981', emoji: '🎸' };
        if (antigravity < 50) return { name: 'Balanceado', color: '#3b82f6', emoji: '🎹' };
        if (antigravity < 80) return { name: 'Creativo', color: '#ec4899', emoji: '🚀' };
        return { name: 'Experimental', color: '#a855f7', emoji: '🌀' };
    };

    const mode = getAntigravityMode();

    // Select track from history
    const selectTrack = (gen) => {
        setCurrentGeneration(gen);
        setIsPlaying(false);
        setCurrentTime(0);
        if (audioRef.current) {
            audioRef.current.load();
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(180deg, #0a0a0f 0%, #111118 50%, #0a0a0f 100%)',
            color: 'white',
            display: 'flex',
            flexDirection: 'column'
        }}>
            {/* Header */}
            <header style={{
                padding: '1rem 2rem',
                borderBottom: '1px solid rgba(255,255,255,0.08)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'rgba(0,0,0,0.4)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <h1 style={{
                        fontSize: '1.5rem',
                        fontWeight: 'bold',
                        background: 'linear-gradient(135deg, #00d4ff, #00ff88)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent'
                    }}>
                        🎸 DGB STUDIO
                    </h1>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.4rem 0.8rem',
                        borderRadius: '20px',
                        background: aceStepConnected ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                        border: `1px solid ${aceStepConnected ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`
                    }}>
                        <div style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            background: aceStepConnected ? '#10b981' : '#ef4444',
                            animation: aceStepConnected ? 'pulse 2s infinite' : 'none'
                        }} />
                        <span style={{ fontSize: '0.85rem', color: aceStepConnected ? '#10b981' : '#ef4444' }}>
                            {aceStepConnected ? 'ACE-Step Conectado' : 'Offline'}
                        </span>
                    </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <span style={{ color: 'rgba(255,255,255,0.6)' }}>Hola, {user?.name || 'Usuario'}</span>
                    <button
                        onClick={() => router.push('/dashboard')}
                        style={{
                            padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            border: '1px solid rgba(255,255,255,0.2)',
                            background: 'transparent',
                            color: 'white',
                            cursor: 'pointer'
                        }}
                    >
                        Dashboard
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
                {/* Left Sidebar - Presets */}
                <aside style={{
                    width: '240px',
                    background: 'rgba(0,0,0,0.3)',
                    borderRight: '1px solid rgba(255,255,255,0.08)',
                    padding: '1.5rem',
                    overflowY: 'auto'
                }}>
                    <h3 style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'rgba(255,255,255,0.4)', marginBottom: '1rem' }}>
                        Estilos DGB
                    </h3>
                    {presets.map(preset => (
                        <button
                            key={preset.id}
                            onClick={() => setSelectedPreset(selectedPreset === preset.id ? null : preset.id)}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                marginBottom: '0.5rem',
                                borderRadius: '10px',
                                border: selectedPreset === preset.id ? '1px solid #00d4ff' : '1px solid rgba(255,255,255,0.1)',
                                background: selectedPreset === preset.id ? 'rgba(0,212,255,0.1)' : 'rgba(255,255,255,0.03)',
                                color: selectedPreset === preset.id ? '#00d4ff' : 'white',
                                textAlign: 'left',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}
                        >
                            <div style={{ fontWeight: '600', fontSize: '0.9rem', marginBottom: '0.25rem' }}>
                                {preset.id.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                            </div>
                            <div style={{ fontSize: '0.75rem', opacity: 0.6 }}>
                                {preset.bpm} BPM • {preset.key}
                            </div>
                        </button>
                    ))}
                </aside>

                {/* Center - Creation Area */}
                <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                    {/* Creation Panel */}
                    <div style={{ padding: '2rem', flex: 1, overflowY: 'auto' }}>
                        <div style={{ maxWidth: '900px', margin: '0 auto' }}>

                            {/* Generation Display / Preview */}
                            <div style={{
                                background: 'linear-gradient(135deg, rgba(0,212,255,0.05), rgba(0,255,136,0.05))',
                                borderRadius: '20px',
                                border: '1px solid rgba(255,255,255,0.1)',
                                padding: '2rem',
                                marginBottom: '2rem',
                                minHeight: '200px',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}>
                                {isGenerating ? (
                                    <>
                                        {/* Generation Animation */}
                                        <div style={{
                                            width: '120px',
                                            height: '120px',
                                            borderRadius: '50%',
                                            background: 'linear-gradient(135deg, #00d4ff, #00ff88)',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            marginBottom: '1.5rem',
                                            animation: 'pulse 1.5s infinite',
                                            boxShadow: '0 0 60px rgba(0,212,255,0.4)'
                                        }}>
                                            <span style={{ fontSize: '3rem' }}>🎵</span>
                                        </div>
                                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                                            Creando tu música...
                                        </div>
                                        <div style={{ color: 'rgba(255,255,255,0.6)', marginBottom: '1.5rem' }}>
                                            {generationStage}
                                        </div>
                                        {/* Progress Bar */}
                                        <div style={{
                                            width: '100%',
                                            maxWidth: '400px',
                                            height: '8px',
                                            background: 'rgba(255,255,255,0.1)',
                                            borderRadius: '4px',
                                            overflow: 'hidden'
                                        }}>
                                            <div style={{
                                                height: '100%',
                                                width: `${generationProgress}%`,
                                                background: 'linear-gradient(90deg, #00d4ff, #00ff88)',
                                                transition: 'width 0.5s ease-out',
                                                borderRadius: '4px'
                                            }} />
                                        </div>
                                        <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#00d4ff' }}>
                                            {generationProgress}%
                                        </div>
                                    </>
                                ) : currentGeneration ? (
                                    <>
                                        {/* Current Track Display */}
                                        <div style={{
                                            width: '100%',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '2rem'
                                        }}>
                                            {/* Album Art */}
                                            <div style={{
                                                width: '160px',
                                                height: '160px',
                                                borderRadius: '16px',
                                                background: 'linear-gradient(135deg, #1a1a2e, #2d2d44)',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                flexShrink: 0,
                                                boxShadow: '0 10px 40px rgba(0,0,0,0.4)'
                                            }}>
                                                <span style={{ fontSize: '4rem' }}>🎵</span>
                                            </div>

                                            {/* Track Info & Player */}
                                            <div style={{ flex: 1 }}>
                                                <div style={{ fontSize: '0.85rem', color: '#00d4ff', marginBottom: '0.5rem' }}>
                                                    {mode.emoji} {mode.name} • Antigravity {currentGeneration.antigravity_params?.antigravity_level || antigravity}
                                                </div>
                                                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                                                    {currentGeneration.prompt_used?.slice(0, 50) || 'Nueva Creación'}
                                                </h2>
                                                <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                                                    ID: {currentGeneration.job_id}
                                                </div>

                                                {/* Waveform/Progress */}
                                                <div
                                                    onClick={handleSeek}
                                                    style={{
                                                        width: '100%',
                                                        height: '60px',
                                                        background: 'rgba(255,255,255,0.05)',
                                                        borderRadius: '8px',
                                                        position: 'relative',
                                                        cursor: 'pointer',
                                                        marginBottom: '1rem',
                                                        overflow: 'hidden'
                                                    }}
                                                >
                                                    {/* Fake waveform visualization */}
                                                    <div style={{
                                                        position: 'absolute',
                                                        bottom: 0,
                                                        left: 0,
                                                        right: 0,
                                                        height: '100%',
                                                        display: 'flex',
                                                        alignItems: 'flex-end',
                                                        gap: '2px',
                                                        padding: '0 10px'
                                                    }}>
                                                        {[...Array(60)].map((_, i) => (
                                                            <div
                                                                key={i}
                                                                style={{
                                                                    flex: 1,
                                                                    height: `${20 + Math.random() * 35}px`,
                                                                    background: (i / 60) < (currentTime / totalDuration)
                                                                        ? 'linear-gradient(180deg, #00d4ff, #00ff88)'
                                                                        : 'rgba(255,255,255,0.2)',
                                                                    borderRadius: '2px',
                                                                    transition: 'background 0.1s'
                                                                }}
                                                            />
                                                        ))}
                                                    </div>
                                                </div>

                                                {/* Time & Controls */}
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                                    <button
                                                        onClick={togglePlayback}
                                                        style={{
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
                                                        }}
                                                    >
                                                        {isPlaying ? '⏸' : '▶'}
                                                    </button>
                                                    <span style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                                                        {formatTime(currentTime)} / {formatTime(totalDuration)}
                                                    </span>
                                                    <div style={{ flex: 1 }} />
                                                    <a
                                                        href={`${API_BASE}/audio/${currentGeneration.job_id}.wav`}
                                                        download
                                                        style={{
                                                            padding: '0.5rem 1rem',
                                                            borderRadius: '8px',
                                                            background: 'rgba(255,255,255,0.1)',
                                                            color: 'white',
                                                            textDecoration: 'none',
                                                            fontSize: '0.9rem'
                                                        }}
                                                    >
                                                        ⬇ Descargar
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                        <audio
                                            ref={audioRef}
                                            src={`${API_BASE}/audio/${currentGeneration.job_id}.wav`}
                                            onTimeUpdate={handleTimeUpdate}
                                            onEnded={() => setIsPlaying(false)}
                                            onLoadedMetadata={handleTimeUpdate}
                                        />
                                    </>
                                ) : (
                                    <>
                                        {/* Empty State */}
                                        <div style={{
                                            width: '100px',
                                            height: '100px',
                                            borderRadius: '50%',
                                            background: 'rgba(255,255,255,0.05)',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            marginBottom: '1rem'
                                        }}>
                                            <span style={{ fontSize: '2.5rem', opacity: 0.5 }}>🎵</span>
                                        </div>
                                        <div style={{ fontSize: '1.2rem', color: 'rgba(255,255,255,0.5)', marginBottom: '0.5rem' }}>
                                            Tu música aparecerá aquí
                                        </div>
                                        <div style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.3)' }}>
                                            Escribe un prompt y haz clic en Generar
                                        </div>
                                    </>
                                )}
                            </div>

                            {/* Input Controls */}
                            <div style={{
                                background: 'rgba(255,255,255,0.03)',
                                borderRadius: '16px',
                                border: '1px solid rgba(255,255,255,0.1)',
                                padding: '1.5rem'
                            }}>
                                {/* Prompt Input */}
                                <div style={{ marginBottom: '1rem' }}>
                                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                                        Describe tu música
                                    </label>
                                    <input
                                        type="text"
                                        value={prompt}
                                        onChange={(e) => setPrompt(e.target.value)}
                                        placeholder="ej: guitarra romántica, voces suaves, noche de verano..."
                                        style={{
                                            width: '100%',
                                            padding: '1rem',
                                            borderRadius: '12px',
                                            border: '1px solid rgba(255,255,255,0.15)',
                                            background: 'rgba(0,0,0,0.3)',
                                            color: 'white',
                                            fontSize: '1rem',
                                            outline: 'none'
                                        }}
                                    />
                                </div>

                                {/* Lyrics */}
                                <div style={{ marginBottom: '1.5rem' }}>
                                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                                        Letras (opcional)
                                    </label>
                                    <textarea
                                        value={lyrics}
                                        onChange={(e) => setLyrics(e.target.value)}
                                        placeholder="[Verse 1]&#10;Bajo la luna de Santo Domingo&#10;Tu mirada me tiene perdido...&#10;&#10;[Chorus]&#10;Bailando contigo..."
                                        rows={4}
                                        style={{
                                            width: '100%',
                                            padding: '1rem',
                                            borderRadius: '12px',
                                            border: '1px solid rgba(255,255,255,0.15)',
                                            background: 'rgba(0,0,0,0.3)',
                                            color: 'white',
                                            fontSize: '0.95rem',
                                            resize: 'vertical',
                                            outline: 'none',
                                            fontFamily: 'inherit'
                                        }}
                                    />
                                </div>

                                {/* Antigravity & Duration */}
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
                                    {/* Antigravity */}
                                    <div>
                                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                            <label style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                                                🌀 Antigravity
                                            </label>
                                            <span style={{
                                                padding: '0.25rem 0.75rem',
                                                borderRadius: '12px',
                                                background: `${mode.color}20`,
                                                color: mode.color,
                                                fontSize: '0.8rem'
                                            }}>
                                                {mode.emoji} {mode.name}
                                            </span>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="100"
                                            value={antigravity}
                                            onChange={(e) => setAntigravity(parseInt(e.target.value))}
                                            style={{
                                                width: '100%',
                                                height: '8px',
                                                borderRadius: '4px',
                                                appearance: 'none',
                                                background: 'linear-gradient(90deg, #10b981, #3b82f6, #ec4899, #a855f7)',
                                                cursor: 'pointer'
                                            }}
                                        />
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.25rem', fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)' }}>
                                            <span>Tradicional</span>
                                            <span>{antigravity}</span>
                                            <span>Experimental</span>
                                        </div>
                                    </div>

                                    {/* Duration */}
                                    <div>
                                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                                            ⏱ Duración: {duration}s
                                        </label>
                                        <input
                                            type="range"
                                            min="30"
                                            max="180"
                                            value={duration}
                                            onChange={(e) => setDuration(parseInt(e.target.value))}
                                            style={{
                                                width: '100%',
                                                height: '8px',
                                                borderRadius: '4px',
                                                appearance: 'none',
                                                background: 'rgba(255,255,255,0.2)',
                                                cursor: 'pointer'
                                            }}
                                        />
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.25rem', fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)' }}>
                                            <span>30s</span>
                                            <span>3 min</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Generate Button */}
                                <button
                                    onClick={handleGenerate}
                                    disabled={isGenerating || !aceStepConnected}
                                    style={{
                                        width: '100%',
                                        padding: '1.25rem',
                                        borderRadius: '16px',
                                        border: 'none',
                                        background: isGenerating
                                            ? 'rgba(255,255,255,0.1)'
                                            : 'linear-gradient(135deg, #00d4ff, #00ff88)',
                                        color: isGenerating ? 'rgba(255,255,255,0.5)' : '#000',
                                        fontSize: '1.1rem',
                                        fontWeight: 'bold',
                                        cursor: isGenerating || !aceStepConnected ? 'not-allowed' : 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: '0.75rem',
                                        transition: 'all 0.3s'
                                    }}
                                >
                                    {isGenerating ? (
                                        <>
                                            <span style={{ animation: 'spin 1s linear infinite' }}>⏳</span>
                                            Generando...
                                        </>
                                    ) : (
                                        <>
                                            ✨ Crear Música
                                        </>
                                    )}
                                </button>

                                {!aceStepConnected && (
                                    <p style={{ textAlign: 'center', marginTop: '0.75rem', color: '#ef4444', fontSize: '0.85rem' }}>
                                        ⚠️ ACE-Step no está conectado. Ejecuta: acestep --bf16 false --port 7870
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                </main>

                {/* Right Sidebar - History */}
                <aside style={{
                    width: '280px',
                    background: 'rgba(0,0,0,0.3)',
                    borderLeft: '1px solid rgba(255,255,255,0.08)',
                    padding: '1.5rem',
                    overflowY: 'auto'
                }}>
                    <h3 style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'rgba(255,255,255,0.4)', marginBottom: '1rem' }}>
                        Historial de Creaciones
                    </h3>
                    {generations.length === 0 ? (
                        <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.9rem' }}>
                            Tus creaciones aparecerán aquí
                        </p>
                    ) : (
                        generations.map((gen) => (
                            <div
                                key={gen.job_id}
                                onClick={() => selectTrack(gen)}
                                style={{
                                    padding: '1rem',
                                    borderRadius: '12px',
                                    background: currentGeneration?.job_id === gen.job_id
                                        ? 'rgba(0,212,255,0.15)'
                                        : 'rgba(255,255,255,0.03)',
                                    border: currentGeneration?.job_id === gen.job_id
                                        ? '1px solid rgba(0,212,255,0.3)'
                                        : '1px solid rgba(255,255,255,0.05)',
                                    marginBottom: '0.75rem',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                    <div style={{
                                        width: '45px',
                                        height: '45px',
                                        borderRadius: '8px',
                                        background: 'linear-gradient(135deg, #1a1a2e, #2d2d44)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        flexShrink: 0
                                    }}>
                                        <span>🎵</span>
                                    </div>
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{
                                            fontWeight: '500',
                                            fontSize: '0.9rem',
                                            whiteSpace: 'nowrap',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis'
                                        }}>
                                            {gen.prompt_used?.slice(0, 25) || 'Creación'}...
                                        </div>
                                        <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)' }}>
                                            {gen.antigravity_params?.mode || 'Balanceado'} • {gen.duration || 60}s
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </aside>
            </div>

            <style jsx global>{`
                @keyframes pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.8; transform: scale(1.05); }
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
}
