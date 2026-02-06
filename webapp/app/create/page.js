'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import '../globals.css';

const API_BASE = 'http://localhost:8000/api';

// Tropical genres and styles
const GENRES = [
    { id: 'bachata', name: 'Bachata', icon: '💃', color: '#e91e63' },
    { id: 'bolero', name: 'Bolero', icon: '🌹', color: '#9c27b0' },
    { id: 'merengue', name: 'Merengue', icon: '🎺', color: '#ff9800' },
    { id: 'salsa', name: 'Salsa', icon: '🔥', color: '#f44336' },
    { id: 'vallenato', name: 'Vallenato', icon: '🪗', color: '#4caf50' },
    { id: 'cumbia', name: 'Cumbia', icon: '🥁', color: '#2196f3' },
    { id: 'reggaeton', name: 'Reggaeton', icon: '🎤', color: '#673ab7' },
    { id: 'son', name: 'Son Cubano', icon: '🎸', color: '#795548' }
];

const INSTRUMENTS = [
    'Guitarra', 'Bongos', 'Güira', 'Bajo', 'Piano', 'Acordeón',
    'Trompeta', 'Saxofón', 'Congas', 'Timbales', 'Maracas', 'Cuatro'
];

const STYLE_TAGS = [
    'romántico', 'bailable', 'nostálgico', 'alegre', 'melancólico',
    'sensual', 'tradicional', 'moderno', 'lento', 'rápido',
    'acústico', 'con cuerdas', 'con vientos', 'percusivo', 'suave'
];

export default function CreateStudioPage() {
    const [user, setUser] = useState(null);
    const [mode, setMode] = useState('simple'); // simple or custom
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    // Creation state
    const [prompt, setPrompt] = useState('');
    const [lyrics, setLyrics] = useState('');
    const [selectedGenre, setSelectedGenre] = useState('bachata');
    const [selectedInstruments, setSelectedInstruments] = useState([]);
    const [selectedStyles, setSelectedStyles] = useState([]);
    const [isInstrumental, setIsInstrumental] = useState(false);
    const [bpm, setBpm] = useState(120);

    // Workspace
    const [workspaces, setWorkspaces] = useState([
        { id: 1, name: 'Mi Proyecto', songs: 12, lastEdited: 'Hace 2h' },
        { id: 2, name: 'Album Romántico', songs: 8, lastEdited: 'Ayer' }
    ]);
    const [selectedWorkspace, setSelectedWorkspace] = useState(1);

    // Tracks/Library
    const [tracks, setTracks] = useState([]);
    const [currentTrack, setCurrentTrack] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);

    // Generation
    const [generating, setGenerating] = useState(false);
    const [credits, setCredits] = useState(50);

    // Sections
    const [lyricsExpanded, setLyricsExpanded] = useState(true);
    const [stylesExpanded, setStylesExpanded] = useState(true);

    const router = useRouter();
    const audioRef = useRef(null);

    useEffect(() => {
        const token = localStorage.getItem('dgb_token');
        if (!token) {
            router.push('/auth');
            return;
        }
        const storedUser = localStorage.getItem('dgb_user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
        fetchTracks();
    }, [router]);

    const fetchTracks = async () => {
        try {
            const res = await fetch(`${API_BASE}/samples`);
            const data = await res.json();
            setTracks(data.samples?.slice(0, 10) || []);
        } catch (err) {
            console.error(err);
        }
    };

    const handleGenerate = async () => {
        if (credits <= 0) {
            alert('No tienes créditos. Actualiza tu plan.');
            return;
        }

        setGenerating(true);

        // Simulate generation (would call AI API)
        setTimeout(() => {
            const newTrack = {
                id: Date.now(),
                name: prompt || `${GENRES.find(g => g.id === selectedGenre)?.name} - Nueva Pista`,
                genre: selectedGenre,
                duration: '3:24',
                created: new Date().toISOString(),
                status: 'completed'
            };
            setTracks(prev => [newTrack, ...prev]);
            setCredits(prev => prev - 10);
            setGenerating(false);
        }, 3000);
    };

    const toggleInstrument = (inst) => {
        setSelectedInstruments(prev =>
            prev.includes(inst)
                ? prev.filter(i => i !== inst)
                : [...prev, inst]
        );
    };

    const toggleStyle = (style) => {
        setSelectedStyles(prev =>
            prev.includes(style)
                ? prev.filter(s => s !== style)
                : [...prev, style]
        );
    };

    return (
        <div style={{
            height: '100vh',
            display: 'flex',
            background: 'var(--carbon)',
            color: 'white',
            overflow: 'hidden'
        }}>
            {/* Sidebar */}
            <aside style={{
                width: sidebarCollapsed ? '60px' : '200px',
                background: 'rgba(0,0,0,0.3)',
                borderRight: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                flexDirection: 'column',
                transition: 'width 0.2s'
            }}>
                {/* Logo */}
                <div style={{ padding: '1.5rem 1rem', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                    <div style={{
                        background: 'linear-gradient(135deg, var(--gold), #fff)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        fontWeight: 700,
                        fontSize: sidebarCollapsed ? '1rem' : '1.25rem'
                    }}>
                        {sidebarCollapsed ? 'DGB' : 'DGB AUDIO'}
                    </div>
                </div>

                {/* Profile */}
                <div style={{
                    padding: '1rem',
                    borderBottom: '1px solid rgba(255,255,255,0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem'
                }}>
                    <div style={{
                        width: '36px',
                        height: '36px',
                        borderRadius: '50%',
                        background: 'var(--gold)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        {user?.name?.[0] || '?'}
                    </div>
                    {!sidebarCollapsed && (
                        <div>
                            <div style={{ fontSize: '0.9rem' }}>{user?.name || 'Usuario'}</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--electric-blue)' }}>
                                {credits} créditos
                            </div>
                        </div>
                    )}
                </div>

                {/* Navigation */}
                <nav style={{ padding: '0.5rem', flex: 1 }}>
                    {[
                        { icon: '🏠', label: 'Home', path: '/' },
                        { icon: '✨', label: 'Crear', path: '/create', active: true },
                        { icon: '🎙️', label: 'Grabar', path: '/record' },
                        { icon: '🎛️', label: 'Studio', path: '/studio' },
                        { icon: '📚', label: 'Library', path: '/library' },
                        { icon: '🎵', label: 'Samples', path: '/admin' },
                        { icon: '🔔', label: 'Alertas', path: '/notifications' }
                    ].map(item => (
                        <button
                            key={item.label}
                            onClick={() => !item.active && router.push(item.path)}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.75rem',
                                background: item.active ? 'rgba(212, 175, 55, 0.2)' : 'transparent',
                                border: 'none',
                                borderRadius: '8px',
                                color: item.active ? 'var(--gold)' : 'var(--text-gray)',
                                cursor: 'pointer',
                                marginBottom: '0.25rem'
                            }}
                        >
                            <span style={{ fontSize: '1.1rem' }}>{item.icon}</span>
                            {!sidebarCollapsed && <span>{item.label}</span>}
                        </button>
                    ))}
                </nav>

                {/* Bottom Links */}
                <div style={{ padding: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                    {[
                        { icon: '💬', label: 'Soporte', path: '/support' },
                        { icon: '💳', label: 'Planes', path: '/pricing' },
                        { icon: '⚙️', label: 'Config', path: '/dashboard' }
                    ].map(item => (
                        <button
                            key={item.label}
                            onClick={() => router.push(item.path)}
                            style={{
                                width: '100%',
                                padding: '0.5rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--text-muted)',
                                cursor: 'pointer',
                                fontSize: '0.85rem'
                            }}
                        >
                            <span>{item.icon}</span>
                            {!sidebarCollapsed && <span>{item.label}</span>}
                        </button>
                    ))}
                </div>

                {/* Collapse Button */}
                <button
                    onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                    style={{
                        position: 'absolute',
                        top: '2rem',
                        right: '-12px',
                        width: '24px',
                        height: '24px',
                        borderRadius: '50%',
                        background: 'var(--carbon)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        color: 'white',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.75rem'
                    }}
                >
                    {sidebarCollapsed ? '→' : '←'}
                </button>
            </aside>

            {/* Workspace Panel */}
            <div style={{
                width: '240px',
                background: 'rgba(26, 26, 46, 0.5)',
                borderRight: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                flexDirection: 'column'
            }}>
                <div style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                    <input
                        type="text"
                        placeholder="🔍 Buscar workspaces..."
                        style={{
                            width: '100%',
                            padding: '0.5rem',
                            background: 'rgba(0,0,0,0.3)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                            color: 'white',
                            fontSize: '0.85rem'
                        }}
                    />
                </div>

                <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem' }}>
                    {/* New Workspace */}
                    <button style={{
                        width: '100%',
                        padding: '1rem',
                        background: 'rgba(255,255,255,0.05)',
                        border: '1px dashed rgba(255,255,255,0.2)',
                        borderRadius: '12px',
                        color: 'var(--text-gray)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '0.5rem',
                        marginBottom: '0.5rem'
                    }}>
                        ➕ Nuevo Workspace
                    </button>

                    {/* Workspaces */}
                    {workspaces.map(ws => (
                        <div
                            key={ws.id}
                            onClick={() => setSelectedWorkspace(ws.id)}
                            style={{
                                padding: '0.75rem',
                                background: selectedWorkspace === ws.id
                                    ? 'rgba(212, 175, 55, 0.15)'
                                    : 'rgba(255,255,255,0.05)',
                                border: selectedWorkspace === ws.id
                                    ? '1px solid var(--gold)'
                                    : '1px solid transparent',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                marginBottom: '0.5rem'
                            }}
                        >
                            <div style={{ fontWeight: 500, marginBottom: '0.25rem' }}>{ws.name}</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                {ws.songs} canciones · {ws.lastEdited}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Create Panel */}
            <div style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden'
            }}>
                {/* Header */}
                <header style={{
                    padding: '1rem 1.5rem',
                    borderBottom: '1px solid rgba(255,255,255,0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                }}>
                    {/* Credits */}
                    <button style={{
                        padding: '0.5rem 1rem',
                        background: credits > 0 ? 'var(--electric-blue)' : '#e53935',
                        border: 'none',
                        borderRadius: '20px',
                        color: 'white',
                        fontWeight: 600,
                        fontSize: '0.85rem'
                    }}>
                        🎵 {credits} créditos
                    </button>

                    {/* Mode Toggle */}
                    <div style={{
                        display: 'flex',
                        background: 'rgba(255,255,255,0.1)',
                        borderRadius: '20px',
                        padding: '3px'
                    }}>
                        {['simple', 'custom'].map(m => (
                            <button
                                key={m}
                                onClick={() => setMode(m)}
                                style={{
                                    padding: '0.5rem 1.5rem',
                                    background: mode === m ? 'var(--gold)' : 'transparent',
                                    border: 'none',
                                    borderRadius: '20px',
                                    color: mode === m ? 'black' : 'var(--text-gray)',
                                    fontWeight: 500,
                                    cursor: 'pointer',
                                    textTransform: 'capitalize'
                                }}
                            >
                                {m === 'simple' ? 'Simple' : 'Custom'}
                            </button>
                        ))}
                    </div>

                    {/* Model/Version */}
                    <button style={{
                        padding: '0.5rem 1rem',
                        background: 'transparent',
                        border: '1px solid rgba(255,255,255,0.2)',
                        borderRadius: '20px',
                        color: 'white',
                        fontSize: '0.85rem',
                        cursor: 'pointer'
                    }}>
                        v2.0-tropical ▾
                    </button>
                </header>

                {/* Create Form */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem' }}>
                    {/* Genre Selector */}
                    <div style={{ marginBottom: '1.5rem' }}>
                        <h3 style={{ marginBottom: '0.75rem', fontWeight: 500 }}>🎵 Género</h3>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                            {GENRES.map(genre => (
                                <button
                                    key={genre.id}
                                    onClick={() => setSelectedGenre(genre.id)}
                                    style={{
                                        padding: '0.5rem 1rem',
                                        background: selectedGenre === genre.id
                                            ? genre.color
                                            : 'rgba(255,255,255,0.1)',
                                        border: 'none',
                                        borderRadius: '20px',
                                        color: 'white',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.5rem'
                                    }}
                                >
                                    <span>{genre.icon}</span> {genre.name}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Prompt Input */}
                    <div style={{ marginBottom: '1.5rem' }}>
                        <h3 style={{ marginBottom: '0.75rem', fontWeight: 500 }}>
                            ✍️ Descripción de la canción
                        </h3>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="Describe tu canción... ej: Una bachata romántica sobre el amor perdido, con guitarra suave y coros emotivos"
                            style={{
                                width: '100%',
                                minHeight: '80px',
                                padding: '1rem',
                                background: 'rgba(0,0,0,0.3)',
                                border: '1px solid rgba(255,255,255,0.2)',
                                borderRadius: '12px',
                                color: 'white',
                                fontSize: '0.95rem',
                                resize: 'vertical'
                            }}
                        />
                    </div>

                    {/* Lyrics Section */}
                    <div style={{
                        marginBottom: '1.5rem',
                        background: 'rgba(255,255,255,0.05)',
                        borderRadius: '12px',
                        border: '1px solid rgba(255,255,255,0.1)'
                    }}>
                        <button
                            onClick={() => setLyricsExpanded(!lyricsExpanded)}
                            style={{
                                width: '100%',
                                padding: '1rem',
                                background: 'transparent',
                                border: 'none',
                                color: 'white',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                cursor: 'pointer'
                            }}
                        >
                            <span style={{ fontWeight: 500 }}>📝 Letra</span>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <label style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.25rem',
                                    fontSize: '0.85rem',
                                    color: 'var(--text-gray)'
                                }}>
                                    <input
                                        type="checkbox"
                                        checked={isInstrumental}
                                        onChange={(e) => setIsInstrumental(e.target.checked)}
                                        onClick={(e) => e.stopPropagation()}
                                    />
                                    Instrumental
                                </label>
                                <span>{lyricsExpanded ? '▲' : '▼'}</span>
                            </div>
                        </button>

                        {lyricsExpanded && !isInstrumental && (
                            <div style={{ padding: '0 1rem 1rem' }}>
                                <textarea
                                    value={lyrics}
                                    onChange={(e) => setLyrics(e.target.value)}
                                    placeholder="[Verso 1]
Tu amor me tiene loco
No puedo más sin ti...

[Coro]
Bailando bachata contigo..."
                                    style={{
                                        width: '100%',
                                        minHeight: '120px',
                                        padding: '1rem',
                                        background: 'rgba(0,0,0,0.2)',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px',
                                        color: 'white',
                                        fontSize: '0.9rem',
                                        fontFamily: 'monospace',
                                        resize: 'vertical'
                                    }}
                                />
                                <div style={{
                                    display: 'flex',
                                    gap: '0.5rem',
                                    marginTop: '0.75rem'
                                }}>
                                    <button style={{
                                        padding: '0.5rem 1rem',
                                        background: 'var(--electric-blue)',
                                        border: 'none',
                                        borderRadius: '8px',
                                        color: 'white',
                                        fontSize: '0.85rem',
                                        cursor: 'pointer'
                                    }}>
                                        ✨ Generar letra con AI
                                    </button>
                                    <button style={{
                                        padding: '0.5rem 1rem',
                                        background: 'rgba(255,255,255,0.1)',
                                        border: 'none',
                                        borderRadius: '8px',
                                        color: 'white',
                                        fontSize: '0.85rem',
                                        cursor: 'pointer'
                                    }}>
                                        📂 Cargar letra
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Styles Section */}
                    {mode === 'custom' && (
                        <div style={{
                            marginBottom: '1.5rem',
                            background: 'rgba(255,255,255,0.05)',
                            borderRadius: '12px',
                            border: '1px solid rgba(255,255,255,0.1)'
                        }}>
                            <button
                                onClick={() => setStylesExpanded(!stylesExpanded)}
                                style={{
                                    width: '100%',
                                    padding: '1rem',
                                    background: 'transparent',
                                    border: 'none',
                                    color: 'white',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    cursor: 'pointer'
                                }}
                            >
                                <span style={{ fontWeight: 500 }}>🎨 Estilos y Tags</span>
                                <span>{stylesExpanded ? '▲' : '▼'}</span>
                            </button>

                            {stylesExpanded && (
                                <div style={{ padding: '0 1rem 1rem' }}>
                                    {/* Instruments */}
                                    <div style={{ marginBottom: '1rem' }}>
                                        <p style={{ fontSize: '0.85rem', color: 'var(--text-gray)', marginBottom: '0.5rem' }}>
                                            Instrumentos:
                                        </p>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                            {INSTRUMENTS.map(inst => (
                                                <button
                                                    key={inst}
                                                    onClick={() => toggleInstrument(inst)}
                                                    style={{
                                                        padding: '0.4rem 0.75rem',
                                                        background: selectedInstruments.includes(inst)
                                                            ? 'var(--gold)'
                                                            : 'rgba(255,255,255,0.1)',
                                                        border: 'none',
                                                        borderRadius: '20px',
                                                        color: selectedInstruments.includes(inst) ? 'black' : 'white',
                                                        fontSize: '0.8rem',
                                                        cursor: 'pointer'
                                                    }}
                                                >
                                                    {inst}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Style Tags */}
                                    <div style={{ marginBottom: '1rem' }}>
                                        <p style={{ fontSize: '0.85rem', color: 'var(--text-gray)', marginBottom: '0.5rem' }}>
                                            Estilo:
                                        </p>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                            {STYLE_TAGS.map(tag => (
                                                <button
                                                    key={tag}
                                                    onClick={() => toggleStyle(tag)}
                                                    style={{
                                                        padding: '0.4rem 0.75rem',
                                                        background: selectedStyles.includes(tag)
                                                            ? 'var(--electric-blue)'
                                                            : 'rgba(255,255,255,0.1)',
                                                        border: 'none',
                                                        borderRadius: '20px',
                                                        color: 'white',
                                                        fontSize: '0.8rem',
                                                        cursor: 'pointer'
                                                    }}
                                                >
                                                    + {tag}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* BPM */}
                                    <div>
                                        <p style={{ fontSize: '0.85rem', color: 'var(--text-gray)', marginBottom: '0.5rem' }}>
                                            BPM: {bpm}
                                        </p>
                                        <input
                                            type="range"
                                            min="60"
                                            max="180"
                                            value={bpm}
                                            onChange={(e) => setBpm(Number(e.target.value))}
                                            style={{ width: '100%' }}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Generate Button */}
                    <button
                        onClick={handleGenerate}
                        disabled={generating}
                        style={{
                            width: '100%',
                            padding: '1rem',
                            background: generating
                                ? 'rgba(255,255,255,0.2)'
                                : 'linear-gradient(135deg, var(--gold), #c9a227)',
                            border: 'none',
                            borderRadius: '12px',
                            color: generating ? 'var(--text-gray)' : 'black',
                            fontWeight: 700,
                            fontSize: '1.1rem',
                            cursor: generating ? 'not-allowed' : 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.75rem'
                        }}
                    >
                        {generating ? (
                            <>⏳ Generando música...</>
                        ) : (
                            <>🎵 Crear Música ({Math.floor(credits / 10)} canciones disponibles)</>
                        )}
                    </button>
                </div>
            </div>

            {/* Right Panel - Track Player & Library */}
            <div style={{
                width: '350px',
                background: 'rgba(26, 26, 46, 0.8)',
                borderLeft: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                flexDirection: 'column'
            }}>
                {/* Now Playing */}
                {currentTrack && (
                    <div style={{
                        padding: '1.5rem',
                        borderBottom: '1px solid rgba(255,255,255,0.1)',
                        background: 'rgba(0,0,0,0.3)'
                    }}>
                        <div style={{
                            width: '100%',
                            height: '60px',
                            background: 'linear-gradient(90deg, var(--gold) 30%, transparent)',
                            borderRadius: '8px',
                            marginBottom: '1rem'
                        }} />
                        <h4 style={{ margin: '0 0 0.25rem' }}>{currentTrack.name}</h4>
                        <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-gray)' }}>
                            {currentTrack.genre} · {currentTrack.duration}
                        </p>
                        <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                            <button style={{
                                flex: 1,
                                padding: '0.75rem',
                                background: 'var(--gold)',
                                border: 'none',
                                borderRadius: '8px',
                                color: 'black',
                                fontWeight: 600,
                                cursor: 'pointer'
                            }}>
                                {isPlaying ? '⏸️ Pausar' : '▶️ Reproducir'}
                            </button>
                            <button style={{
                                padding: '0.75rem',
                                background: 'rgba(255,255,255,0.1)',
                                border: 'none',
                                borderRadius: '8px',
                                color: 'white',
                                cursor: 'pointer'
                            }}>
                                ⬇️
                            </button>
                        </div>
                    </div>
                )}

                {/* Track List */}
                <div style={{ flex: 1, overflowY: 'auto' }}>
                    <div style={{
                        padding: '1rem',
                        borderBottom: '1px solid rgba(255,255,255,0.1)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <h3 style={{ margin: 0, fontWeight: 500 }}>📚 Tus Tracks</h3>
                        <span style={{ fontSize: '0.85rem', color: 'var(--text-gray)' }}>
                            {tracks.length} pistas
                        </span>
                    </div>

                    {tracks.map(track => (
                        <div
                            key={track.id}
                            onClick={() => setCurrentTrack(track)}
                            style={{
                                padding: '1rem',
                                borderBottom: '1px solid rgba(255,255,255,0.05)',
                                cursor: 'pointer',
                                background: currentTrack?.id === track.id
                                    ? 'rgba(212, 175, 55, 0.1)'
                                    : 'transparent',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.75rem'
                            }}
                        >
                            <div style={{
                                width: '40px',
                                height: '40px',
                                borderRadius: '8px',
                                background: GENRES.find(g => g.id === track.genre)?.color || 'var(--gold)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '1.25rem'
                            }}>
                                {GENRES.find(g => g.id === track.genre)?.icon || '🎵'}
                            </div>
                            <div style={{ flex: 1, minWidth: 0 }}>
                                <div style={{
                                    fontWeight: 500,
                                    whiteSpace: 'nowrap',
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis'
                                }}>
                                    {track.name}
                                </div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-gray)' }}>
                                    {track.duration || '0:00'}
                                </div>
                            </div>
                            <button style={{
                                background: 'none',
                                border: 'none',
                                color: 'var(--text-gray)',
                                cursor: 'pointer',
                                fontSize: '1.25rem'
                            }}>
                                ⋮
                            </button>
                        </div>
                    ))}

                    {tracks.length === 0 && (
                        <div style={{
                            padding: '3rem 1rem',
                            textAlign: 'center',
                            color: 'var(--text-muted)'
                        }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎵</div>
                            <p>Aún no tienes tracks</p>
                            <p style={{ fontSize: '0.85rem' }}>Crea tu primera canción</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Audio Element */}
            <audio ref={audioRef} />
        </div>
    );
}
