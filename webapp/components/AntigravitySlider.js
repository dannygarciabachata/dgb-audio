'use client';

import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api';

/**
 * AntigravitySlider - Creative control for DGB music generation
 * 
 * Props:
 *   - value: current antigravity level (0-100)
 *   - onChange: callback when value changes
 *   - showParams: whether to show technical parameters
 */
export default function AntigravitySlider({ value = 50, onChange, showParams = false }) {
    const [params, setParams] = useState(null);
    const [hovering, setHovering] = useState(false);

    useEffect(() => {
        loadParams(value);
    }, [value]);

    const loadParams = async (level) => {
        try {
            const res = await fetch(`${API_BASE}/acestep/antigravity/${level}`);
            const data = await res.json();
            setParams(data);
        } catch (err) {
            console.error('Error loading antigravity params:', err);
        }
    };

    const getModeColor = (mode) => {
        switch (mode) {
            case 'Tradicional': return '#00ff88';
            case 'Balanceado': return '#00d4ff';
            case 'Creativo': return '#ff9500';
            case 'Experimental': return '#ff3366';
            default: return '#00d4ff';
        }
    };

    const getModeIcon = (mode) => {
        switch (mode) {
            case 'Tradicional': return '🎸';
            case 'Balanceado': return '🎹';
            case 'Creativo': return '🚀';
            case 'Experimental': return '🌀';
            default: return '🎵';
        }
    };

    const getModeDescription = (mode) => {
        switch (mode) {
            case 'Tradicional': return 'Sonido auténtico y fiel al género';
            case 'Balanceado': return 'Equilibrio entre tradición e innovación';
            case 'Creativo': return 'Explorando nuevos territorios sonoros';
            case 'Experimental': return '¡Rompiendo todas las reglas!';
            default: return '';
        }
    };

    const gradientStyle = {
        background: `linear-gradient(90deg, 
            #00ff88 0%, 
            #00d4ff 33%, 
            #ff9500 66%, 
            #ff3366 100%)`
    };

    const containerStyles = {
        container: {
            background: 'linear-gradient(135deg, rgba(0,0,0,0.4), rgba(20,20,40,0.6))',
            borderRadius: '20px',
            padding: '25px',
            border: '1px solid rgba(255,255,255,0.1)',
            position: 'relative',
            overflow: 'hidden'
        },
        glow: {
            position: 'absolute',
            top: '-50%',
            left: '-50%',
            width: '200%',
            height: '200%',
            background: `radial-gradient(circle at 50% 50%, ${getModeColor(params?.mode)}20, transparent 50%)`,
            pointerEvents: 'none',
            transition: 'all 0.5s ease'
        },
        header: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            position: 'relative',
            zIndex: 1
        },
        title: {
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
        },
        titleText: {
            fontSize: '1.2rem',
            fontWeight: 'bold',
            background: 'linear-gradient(90deg, #00d4ff, #ff3366)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
        },
        badge: {
            background: getModeColor(params?.mode),
            color: '#000',
            padding: '5px 15px',
            borderRadius: '20px',
            fontSize: '0.85rem',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
        },
        sliderContainer: {
            position: 'relative',
            zIndex: 1,
            marginBottom: '15px'
        },
        sliderTrack: {
            width: '100%',
            height: '12px',
            borderRadius: '6px',
            ...gradientStyle,
            position: 'relative'
        },
        slider: {
            width: '100%',
            height: '12px',
            WebkitAppearance: 'none',
            appearance: 'none',
            background: 'transparent',
            cursor: 'pointer',
            position: 'absolute',
            top: 0,
            left: 0
        },
        labels: {
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: '10px',
            fontSize: '0.75rem',
            color: 'rgba(255,255,255,0.5)'
        },
        valueDisplay: {
            textAlign: 'center',
            marginTop: '15px',
            position: 'relative',
            zIndex: 1
        },
        valueNumber: {
            fontSize: '3rem',
            fontWeight: 'bold',
            color: getModeColor(params?.mode),
            textShadow: `0 0 30px ${getModeColor(params?.mode)}80`
        },
        modeDescription: {
            color: 'rgba(255,255,255,0.7)',
            marginTop: '5px',
            fontSize: '0.9rem'
        },
        paramsBox: {
            marginTop: '20px',
            background: 'rgba(0,0,0,0.3)',
            borderRadius: '12px',
            padding: '15px',
            position: 'relative',
            zIndex: 1
        },
        paramsTitle: {
            fontSize: '0.8rem',
            color: 'rgba(255,255,255,0.5)',
            marginBottom: '10px',
            textTransform: 'uppercase',
            letterSpacing: '1px'
        },
        paramsGrid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '10px'
        },
        paramItem: {
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '8px',
            padding: '10px'
        },
        paramLabel: {
            fontSize: '0.7rem',
            color: 'rgba(255,255,255,0.5)',
            marginBottom: '4px'
        },
        paramValue: {
            fontSize: '1rem',
            fontWeight: 'bold',
            color: '#fff'
        }
    };

    // Custom slider CSS
    const sliderCSS = `
        .antigravity-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: white;
            cursor: pointer;
            border: 3px solid ${getModeColor(params?.mode)};
            box-shadow: 0 0 20px ${getModeColor(params?.mode)}80, 0 2px 10px rgba(0,0,0,0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .antigravity-slider::-webkit-slider-thumb:hover {
            transform: scale(1.1);
            box-shadow: 0 0 30px ${getModeColor(params?.mode)}, 0 2px 15px rgba(0,0,0,0.4);
        }
        .antigravity-slider::-moz-range-thumb {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: white;
            cursor: pointer;
            border: 3px solid ${getModeColor(params?.mode)};
            box-shadow: 0 0 20px ${getModeColor(params?.mode)}80;
        }
    `;

    return (
        <div
            style={containerStyles.container}
            onMouseEnter={() => setHovering(true)}
            onMouseLeave={() => setHovering(false)}
        >
            <style>{sliderCSS}</style>

            {/* Background glow */}
            <div style={containerStyles.glow} />

            {/* Header */}
            <div style={containerStyles.header}>
                <div style={containerStyles.title}>
                    <span style={{ fontSize: '1.5rem' }}>🌀</span>
                    <span style={containerStyles.titleText}>Antigravity Engine</span>
                </div>
                {params && (
                    <div style={containerStyles.badge}>
                        {getModeIcon(params.mode)} {params.mode}
                    </div>
                )}
            </div>

            {/* Slider */}
            <div style={containerStyles.sliderContainer}>
                <div style={containerStyles.sliderTrack}>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value={value}
                        onChange={(e) => onChange && onChange(parseInt(e.target.value))}
                        className="antigravity-slider"
                        style={containerStyles.slider}
                    />
                </div>
                <div style={containerStyles.labels}>
                    <span>🎸 Tradicional</span>
                    <span>🎹 Balanceado</span>
                    <span>🚀 Creativo</span>
                    <span>🌀 Experimental</span>
                </div>
            </div>

            {/* Value Display */}
            <div style={containerStyles.valueDisplay}>
                <div style={containerStyles.valueNumber}>{value}</div>
                <div style={containerStyles.modeDescription}>
                    {getModeDescription(params?.mode)}
                </div>
            </div>

            {/* Technical Parameters (optional) */}
            {showParams && params && (
                <div style={containerStyles.paramsBox}>
                    <div style={containerStyles.paramsTitle}>
                        Parámetros de Generación
                    </div>
                    <div style={containerStyles.paramsGrid}>
                        <div style={containerStyles.paramItem}>
                            <div style={containerStyles.paramLabel}>Guidance Scale</div>
                            <div style={containerStyles.paramValue}>{params.guidance_scale}</div>
                        </div>
                        <div style={containerStyles.paramItem}>
                            <div style={containerStyles.paramLabel}>Temperature</div>
                            <div style={containerStyles.paramValue}>{params.temperature}</div>
                        </div>
                        <div style={containerStyles.paramItem}>
                            <div style={containerStyles.paramLabel}>CFG Rescale</div>
                            <div style={containerStyles.paramValue}>{params.cfg_rescale}</div>
                        </div>
                        <div style={containerStyles.paramItem}>
                            <div style={containerStyles.paramLabel}>Infer Steps</div>
                            <div style={containerStyles.paramValue}>{params.infer_steps}</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}


/**
 * GenerateMusicPanel - Complete music generation interface with Antigravity
 */
export function GenerateMusicPanel({ token, onGenerated }) {
    const [prompt, setPrompt] = useState('');
    const [lyrics, setLyrics] = useState('');
    const [genre, setGenre] = useState('bachata');
    const [bpm, setBpm] = useState(120);
    const [key, setKey] = useState('Am');
    const [duration, setDuration] = useState(120);
    const [antigravity, setAntigravity] = useState(50);
    const [generating, setGenerating] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [acestepStatus, setAcestepStatus] = useState(null);

    // Check ACE-Step status on mount
    useEffect(() => {
        checkAcestepHealth();
    }, []);

    const checkAcestepHealth = async () => {
        try {
            const res = await fetch(`${API_BASE}/acestep/health`);
            const data = await res.json();
            setAcestepStatus(data);
        } catch (err) {
            setAcestepStatus({ connected: false, error: 'Cannot connect to API' });
        }
    };

    const handleGenerate = async () => {
        if (!prompt.trim()) {
            setError('Por favor, describe la música que quieres crear');
            return;
        }

        setGenerating(true);
        setError(null);
        setResult(null);

        try {
            const res = await fetch(`${API_BASE}/generate/music?token=${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt,
                    lyrics,
                    genre,
                    bpm,
                    key,
                    duration,
                    antigravity
                })
            });

            const data = await res.json();

            if (data.success) {
                setResult(data);
                if (onGenerated) onGenerated(data);
            } else {
                setError(data.error || 'Error en la generación');
            }
        } catch (err) {
            setError('Error de conexión: ' + err.message);
        } finally {
            setGenerating(false);
        }
    };

    const genres = [
        { id: 'bachata', name: 'Bachata', icon: '💃' },
        { id: 'bolero', name: 'Bolero', icon: '🌹' },
        { id: 'merengue', name: 'Merengue', icon: '🎺' },
        { id: 'salsa', name: 'Salsa', icon: '🔥' },
        { id: 'cumbia', name: 'Cumbia', icon: '🎭' },
        { id: 'reggaeton', name: 'Reggaeton', icon: '🎤' }
    ];

    const keys = ['C', 'Cm', 'D', 'Dm', 'E', 'Em', 'F', 'Fm', 'G', 'Gm', 'A', 'Am', 'B', 'Bm'];

    const panelStyles = {
        container: {
            background: 'linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%)',
            borderRadius: '24px',
            padding: '30px',
            maxWidth: '800px',
            margin: '0 auto'
        },
        header: {
            textAlign: 'center',
            marginBottom: '30px'
        },
        title: {
            fontSize: '2rem',
            fontWeight: 'bold',
            background: 'linear-gradient(90deg, #00d4ff, #ff3366)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '10px'
        },
        subtitle: {
            color: 'rgba(255,255,255,0.6)',
            fontSize: '1rem'
        },
        statusBadge: (connected) => ({
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: connected ? 'rgba(0,255,136,0.1)' : 'rgba(255,68,68,0.1)',
            border: `1px solid ${connected ? '#00ff88' : '#ff4444'}`,
            color: connected ? '#00ff88' : '#ff4444',
            padding: '6px 14px',
            borderRadius: '20px',
            fontSize: '0.85rem',
            marginTop: '10px'
        }),
        section: {
            marginBottom: '25px'
        },
        label: {
            display: 'block',
            color: 'rgba(255,255,255,0.7)',
            marginBottom: '8px',
            fontSize: '0.9rem'
        },
        textarea: {
            width: '100%',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            padding: '15px',
            color: 'white',
            fontSize: '1rem',
            resize: 'vertical',
            minHeight: '80px'
        },
        genreGrid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '10px'
        },
        genreBtn: (isSelected) => ({
            background: isSelected ? 'linear-gradient(135deg, #00d4ff30, #ff336630)' : 'rgba(255,255,255,0.05)',
            border: isSelected ? '2px solid #00d4ff' : '2px solid transparent',
            borderRadius: '12px',
            padding: '12px',
            cursor: 'pointer',
            textAlign: 'center',
            transition: 'all 0.2s'
        }),
        row: {
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '15px'
        },
        input: {
            width: '100%',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '10px',
            padding: '12px',
            color: 'white',
            fontSize: '1rem'
        },
        select: {
            width: '100%',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '10px',
            padding: '12px',
            color: 'white',
            fontSize: '1rem'
        },
        generateBtn: {
            width: '100%',
            background: 'linear-gradient(135deg, #00d4ff 0%, #ff3366 100%)',
            border: 'none',
            borderRadius: '15px',
            padding: '18px',
            color: 'white',
            fontSize: '1.2rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            marginTop: '20px',
            transition: 'transform 0.2s, box-shadow 0.2s'
        },
        resultBox: {
            background: 'rgba(0,255,136,0.1)',
            border: '1px solid rgba(0,255,136,0.3)',
            borderRadius: '16px',
            padding: '20px',
            marginTop: '20px',
            textAlign: 'center'
        },
        errorBox: {
            background: 'rgba(255,68,68,0.1)',
            border: '1px solid rgba(255,68,68,0.3)',
            borderRadius: '12px',
            padding: '15px',
            color: '#ff6b6b',
            marginTop: '15px'
        }
    };

    return (
        <div style={panelStyles.container}>
            {/* Header */}
            <div style={panelStyles.header}>
                <h1 style={panelStyles.title}>🎵 Crear Música con IA</h1>
                <p style={panelStyles.subtitle}>
                    Describe tu canción y deja que el Antigravity Engine haga la magia
                </p>
                <div style={panelStyles.statusBadge(acestepStatus?.connected)}>
                    {acestepStatus?.connected ? '🟢 ACE-Step Conectado' : '🔴 ACE-Step Desconectado'}
                </div>
            </div>

            {/* Prompt */}
            <div style={panelStyles.section}>
                <label style={panelStyles.label}>✨ Describe tu canción</label>
                <textarea
                    style={panelStyles.textarea}
                    placeholder="Una bachata romántica con guitarra suave y bongos tropicales, perfecta para bailar bajo las estrellas..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                />
            </div>

            {/* Lyrics (optional) */}
            <div style={panelStyles.section}>
                <label style={panelStyles.label}>📝 Letra (opcional)</label>
                <textarea
                    style={{ ...panelStyles.textarea, minHeight: '100px' }}
                    placeholder="[Verse 1]&#10;Bajo la luna llena...&#10;&#10;[Chorus]&#10;Baila conmigo..."
                    value={lyrics}
                    onChange={(e) => setLyrics(e.target.value)}
                />
            </div>

            {/* Genre Selection */}
            <div style={panelStyles.section}>
                <label style={panelStyles.label}>🎭 Género</label>
                <div style={panelStyles.genreGrid}>
                    {genres.map(g => (
                        <div
                            key={g.id}
                            style={panelStyles.genreBtn(genre === g.id)}
                            onClick={() => setGenre(g.id)}
                        >
                            <div style={{ fontSize: '1.5rem' }}>{g.icon}</div>
                            <div style={{ color: 'white', marginTop: '5px' }}>{g.name}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* BPM, Key, Duration */}
            <div style={panelStyles.section}>
                <div style={panelStyles.row}>
                    <div>
                        <label style={panelStyles.label}>🥁 BPM</label>
                        <input
                            type="number"
                            style={panelStyles.input}
                            value={bpm}
                            onChange={(e) => setBpm(parseInt(e.target.value) || 120)}
                            min="60"
                            max="200"
                        />
                    </div>
                    <div>
                        <label style={panelStyles.label}>🎹 Tonalidad</label>
                        <select
                            style={panelStyles.select}
                            value={key}
                            onChange={(e) => setKey(e.target.value)}
                        >
                            {keys.map(k => (
                                <option key={k} value={k}>{k}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label style={panelStyles.label}>⏱️ Duración (seg)</label>
                        <input
                            type="number"
                            style={panelStyles.input}
                            value={duration}
                            onChange={(e) => setDuration(parseInt(e.target.value) || 120)}
                            min="30"
                            max="300"
                        />
                    </div>
                </div>
            </div>

            {/* Antigravity Slider */}
            <div style={panelStyles.section}>
                <AntigravitySlider
                    value={antigravity}
                    onChange={setAntigravity}
                    showParams={true}
                />
            </div>

            {/* Error */}
            {error && (
                <div style={panelStyles.errorBox}>
                    ❌ {error}
                </div>
            )}

            {/* Result */}
            {result && (
                <div style={panelStyles.resultBox}>
                    <div style={{ fontSize: '3rem', marginBottom: '15px' }}>✅</div>
                    <h3 style={{ color: '#00ff88', marginBottom: '10px' }}>
                        ¡Música Generada!
                    </h3>
                    <p style={{ color: 'rgba(255,255,255,0.8)' }}>
                        Modo: <strong>{result.antigravity_params?.mode}</strong>
                    </p>
                    {result.audio_path && (
                        <audio controls style={{ marginTop: '15px', width: '100%' }}>
                            <source src={result.audio_path} type="audio/wav" />
                        </audio>
                    )}
                </div>
            )}

            {/* Generate Button */}
            <button
                style={{
                    ...panelStyles.generateBtn,
                    opacity: generating || !acestepStatus?.connected ? 0.6 : 1,
                    cursor: generating || !acestepStatus?.connected ? 'not-allowed' : 'pointer'
                }}
                onClick={handleGenerate}
                disabled={generating || !acestepStatus?.connected}
            >
                {generating ? '🎵 Generando...' : '🚀 Crear Música'}
            </button>
        </div>
    );
}
