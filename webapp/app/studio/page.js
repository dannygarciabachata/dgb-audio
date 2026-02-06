'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import '../globals.css';

const API_BASE = 'http://localhost:8000/api';

export default function StudioPage() {
    const [user, setUser] = useState(null);
    const [tracks, setTracks] = useState([
        { id: 1, name: 'Track 1', type: 'vocal', muted: false, solo: false, volume: 80, pan: 0 },
        { id: 2, name: 'Guitarra', type: 'instrument', muted: false, solo: false, volume: 70, pan: -20 },
        { id: 3, name: 'Bajo', type: 'instrument', muted: false, solo: false, volume: 75, pan: 0 },
        { id: 4, name: 'Bongos', type: 'drums', muted: false, solo: false, volume: 65, pan: 10 }
    ]);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [bpm, setBpm] = useState(120);
    const [projectName, setProjectName] = useState('Mi Bachata Romántica');
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('dgb_token');
        if (!token) {
            router.push('/auth');
            return;
        }
        const storedUser = localStorage.getItem('dgb_user');
        if (storedUser) setUser(JSON.parse(storedUser));
    }, [router]);

    const toggleMute = (id) => {
        setTracks(prev => prev.map(t =>
            t.id === id ? { ...t, muted: !t.muted } : t
        ));
    };

    const toggleSolo = (id) => {
        setTracks(prev => prev.map(t =>
            t.id === id ? { ...t, solo: !t.solo } : t
        ));
    };

    const setVolume = (id, volume) => {
        setTracks(prev => prev.map(t =>
            t.id === id ? { ...t, volume } : t
        ));
    };

    const setPan = (id, pan) => {
        setTracks(prev => prev.map(t =>
            t.id === id ? { ...t, pan } : t
        ));
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div style={{
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            background: 'linear-gradient(180deg, #1a1a2e 0%, #0a0a0f 100%)',
            color: 'white',
            overflow: 'hidden'
        }}>
            {/* Top Toolbar */}
            <div style={{
                padding: '0.75rem 1.5rem',
                borderBottom: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'rgba(0,0,0,0.3)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <button
                        onClick={() => router.push('/create')}
                        style={{ background: 'none', border: 'none', color: 'white', fontSize: '1.25rem', cursor: 'pointer' }}
                    >
                        ←
                    </button>
                    <input
                        type="text"
                        value={projectName}
                        onChange={(e) => setProjectName(e.target.value)}
                        style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'white',
                            fontSize: '1.1rem',
                            fontWeight: 600,
                            width: '250px'
                        }}
                    />
                </div>

                {/* Transport Controls */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <button style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        background: 'rgba(255,255,255,0.1)',
                        border: 'none',
                        color: 'white',
                        cursor: 'pointer',
                        fontSize: '1rem'
                    }}>
                        ⏮
                    </button>
                    <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        style={{
                            width: '50px',
                            height: '50px',
                            borderRadius: '50%',
                            background: 'var(--gold)',
                            border: 'none',
                            color: 'black',
                            cursor: 'pointer',
                            fontSize: '1.25rem',
                            fontWeight: 700
                        }}
                    >
                        {isPlaying ? '⏸' : '▶'}
                    </button>
                    <button style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        background: 'rgba(255,255,255,0.1)',
                        border: 'none',
                        color: 'white',
                        cursor: 'pointer',
                        fontSize: '1rem'
                    }}>
                        ⏭
                    </button>
                    <button style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        background: 'rgba(255,68,68,0.3)',
                        border: '2px solid #ff4444',
                        color: '#ff4444',
                        cursor: 'pointer',
                        fontSize: '0.9rem'
                    }}>
                        ⏺
                    </button>
                </div>

                {/* Time & BPM */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <div style={{
                        fontFamily: 'monospace',
                        fontSize: '1.5rem',
                        background: 'rgba(0,0,0,0.5)',
                        padding: '0.5rem 1rem',
                        borderRadius: '8px'
                    }}>
                        {formatTime(currentTime)}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ color: 'var(--text-gray)' }}>BPM:</span>
                        <input
                            type="number"
                            value={bpm}
                            onChange={(e) => setBpm(Number(e.target.value))}
                            style={{
                                width: '60px',
                                background: 'rgba(0,0,0,0.5)',
                                border: '1px solid rgba(255,255,255,0.2)',
                                borderRadius: '4px',
                                color: 'var(--gold)',
                                padding: '0.5rem',
                                textAlign: 'center',
                                fontWeight: 600
                            }}
                        />
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                {/* Track Controls */}
                <div style={{
                    width: '250px',
                    background: 'rgba(0,0,0,0.4)',
                    borderRight: '1px solid rgba(255,255,255,0.1)',
                    display: 'flex',
                    flexDirection: 'column'
                }}>
                    {/* Add Track Button */}
                    <button style={{
                        margin: '1rem',
                        padding: '0.75rem',
                        background: 'rgba(255,255,255,0.1)',
                        border: '1px dashed rgba(255,255,255,0.3)',
                        borderRadius: '8px',
                        color: 'white',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '0.5rem'
                    }}>
                        ➕ Añadir Track
                    </button>

                    {/* Track List */}
                    {tracks.map(track => (
                        <div
                            key={track.id}
                            style={{
                                padding: '0.75rem 1rem',
                                borderBottom: '1px solid rgba(255,255,255,0.1)',
                                background: 'rgba(255,255,255,0.02)'
                            }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                <span style={{ fontWeight: 500 }}>{track.name}</span>
                                <div style={{ display: 'flex', gap: '0.25rem' }}>
                                    <button
                                        onClick={() => toggleMute(track.id)}
                                        style={{
                                            width: '24px',
                                            height: '24px',
                                            borderRadius: '4px',
                                            background: track.muted ? '#ff4444' : 'rgba(255,255,255,0.1)',
                                            border: 'none',
                                            color: 'white',
                                            fontSize: '0.7rem',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        M
                                    </button>
                                    <button
                                        onClick={() => toggleSolo(track.id)}
                                        style={{
                                            width: '24px',
                                            height: '24px',
                                            borderRadius: '4px',
                                            background: track.solo ? 'var(--gold)' : 'rgba(255,255,255,0.1)',
                                            border: 'none',
                                            color: track.solo ? 'black' : 'white',
                                            fontSize: '0.7rem',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        S
                                    </button>
                                </div>
                            </div>
                            {/* Volume Slider */}
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <span style={{ fontSize: '0.75rem', color: 'var(--text-gray)', width: '25px' }}>
                                    {track.volume}%
                                </span>
                                <input
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={track.volume}
                                    onChange={(e) => setVolume(track.id, Number(e.target.value))}
                                    style={{ flex: 1, height: '4px' }}
                                />
                            </div>
                            {/* Pan Slider */}
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
                                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>L</span>
                                <input
                                    type="range"
                                    min="-50"
                                    max="50"
                                    value={track.pan}
                                    onChange={(e) => setPan(track.id, Number(e.target.value))}
                                    style={{ flex: 1, height: '3px' }}
                                />
                                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>R</span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Timeline */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                    {/* Time Ruler */}
                    <div style={{
                        height: '30px',
                        background: 'rgba(0,0,0,0.3)',
                        borderBottom: '1px solid rgba(255,255,255,0.1)',
                        display: 'flex',
                        alignItems: 'flex-end',
                        paddingLeft: '10px'
                    }}>
                        {[1, 2, 3, 4, 5, 6, 7, 8].map(bar => (
                            <div
                                key={bar}
                                style={{
                                    width: '100px',
                                    borderLeft: '1px solid rgba(255,255,255,0.3)',
                                    paddingLeft: '4px',
                                    fontSize: '0.7rem',
                                    color: 'var(--text-gray)'
                                }}
                            >
                                {bar}
                            </div>
                        ))}
                    </div>

                    {/* Track Lanes */}
                    <div style={{ flex: 1, overflowY: 'auto' }}>
                        {tracks.map(track => (
                            <div
                                key={track.id}
                                style={{
                                    height: '80px',
                                    borderBottom: '1px solid rgba(255,255,255,0.1)',
                                    background: track.muted
                                        ? 'rgba(255,0,0,0.05)'
                                        : track.solo
                                            ? 'rgba(212, 175, 55, 0.1)'
                                            : 'transparent',
                                    display: 'flex',
                                    alignItems: 'center',
                                    padding: '0.5rem',
                                    position: 'relative'
                                }}
                            >
                                {/* Waveform placeholder */}
                                <div style={{
                                    height: '60px',
                                    width: '400px',
                                    marginLeft: '50px',
                                    background: `linear-gradient(90deg, 
                                        ${track.type === 'vocal' ? 'var(--electric-blue)' :
                                            track.type === 'drums' ? 'var(--gold)' : '#4caf50'} 0%, 
                                        transparent 100%)`,
                                    borderRadius: '4px',
                                    opacity: track.muted ? 0.3 : 0.8,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}>
                                    <div style={{
                                        width: '100%',
                                        height: '40px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-around'
                                    }}>
                                        {/* Fake waveform bars - using seeded values to avoid hydration mismatch */}
                                        {Array.from({ length: 50 }).map((_, i) => {
                                            // Seeded pseudo-random based on track id and bar index
                                            const seed = (track.id * 1000 + i * 7) % 100;
                                            return (
                                                <div
                                                    key={i}
                                                    style={{
                                                        width: '3px',
                                                        height: `${seed}%`,
                                                        background: 'rgba(255,255,255,0.5)',
                                                        borderRadius: '2px'
                                                    }}
                                                />
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Bottom Panel - Effects/Tools */}
            <div style={{
                height: '120px',
                borderTop: '1px solid rgba(255,255,255,0.1)',
                background: 'rgba(0,0,0,0.4)',
                padding: '1rem',
                display: 'flex',
                gap: '1rem'
            }}>
                <div style={{
                    padding: '1rem',
                    background: 'rgba(255,255,255,0.05)',
                    borderRadius: '8px',
                    minWidth: '150px',
                    textAlign: 'center'
                }}>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-gray)', marginBottom: '0.5rem' }}>Master</div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                        <div style={{
                            width: '8px',
                            height: '60px',
                            background: 'linear-gradient(to top, #4caf50, var(--gold), #ff4444)',
                            borderRadius: '4px',
                            position: 'relative'
                        }}>
                            <div style={{
                                position: 'absolute',
                                bottom: '70%',
                                left: '-4px',
                                width: '16px',
                                height: '4px',
                                background: 'white',
                                borderRadius: '2px'
                            }} />
                        </div>
                        <div style={{
                            width: '8px',
                            height: '60px',
                            background: 'linear-gradient(to top, #4caf50, var(--gold), #ff4444)',
                            borderRadius: '4px',
                            position: 'relative'
                        }}>
                            <div style={{
                                position: 'absolute',
                                bottom: '65%',
                                left: '-4px',
                                width: '16px',
                                height: '4px',
                                background: 'white',
                                borderRadius: '2px'
                            }} />
                        </div>
                    </div>
                </div>

                {/* Quick Effects */}
                {['EQ', 'Compressor', 'Reverb', 'Delay'].map(effect => (
                    <button
                        key={effect}
                        style={{
                            padding: '1rem',
                            background: 'rgba(255,255,255,0.05)',
                            border: '1px solid rgba(255,255,255,0.2)',
                            borderRadius: '8px',
                            color: 'var(--text-gray)',
                            cursor: 'pointer',
                            minWidth: '100px'
                        }}
                    >
                        {effect}
                    </button>
                ))}

                <div style={{ flex: 1 }} />

                {/* Export */}
                <button style={{
                    padding: '1rem 2rem',
                    background: 'var(--gold)',
                    border: 'none',
                    borderRadius: '8px',
                    color: 'black',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                }}>
                    ⬇️ Exportar
                </button>
            </div>
        </div>
    );
}
