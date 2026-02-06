'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import '../globals.css';

const API_BASE = 'http://localhost:8000/api';

export default function LibraryPage() {
    const [user, setUser] = useState(null);
    const [samples, setSamples] = useState([]);
    const [filter, setFilter] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState('recent');
    const [viewMode, setViewMode] = useState('grid');
    const [selectedSamples, setSelectedSamples] = useState([]);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('dgb_token');
        if (!token) {
            router.push('/auth');
            return;
        }
        const storedUser = localStorage.getItem('dgb_user');
        if (storedUser) setUser(JSON.parse(storedUser));
        fetchSamples();
    }, [router]);

    const fetchSamples = async () => {
        try {
            const res = await fetch(`${API_BASE}/samples`);
            const data = await res.json();
            setSamples(data.samples || []);
        } catch (err) {
            console.error(err);
        }
    };

    const filteredSamples = samples.filter(s => {
        if (filter !== 'all' && s.genre !== filter) return false;
        if (searchQuery && !s.name?.toLowerCase().includes(searchQuery.toLowerCase())) return false;
        return true;
    });

    const toggleSelect = (id) => {
        setSelectedSamples(prev =>
            prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
        );
    };

    const genreColors = {
        bachata: '#e91e63',
        bolero: '#9c27b0',
        merengue: '#ff9800',
        salsa: '#f44336',
        vallenato: '#4caf50',
        cumbia: '#2196f3'
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, var(--carbon) 0%, #1a1a2e 100%)',
            color: 'white'
        }}>
            {/* Header */}
            <header style={{
                padding: '1.5rem 2rem',
                borderBottom: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <button
                        onClick={() => router.push('/create')}
                        style={{ background: 'none', border: 'none', color: 'white', fontSize: '1.5rem', cursor: 'pointer' }}
                    >
                        ←
                    </button>
                    <h1 style={{ margin: 0 }}>📚 Mi Librería</h1>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button
                        onClick={() => router.push('/admin')}
                        style={{
                            padding: '0.75rem 1.5rem',
                            background: 'var(--gold)',
                            border: 'none',
                            borderRadius: '8px',
                            color: 'black',
                            fontWeight: 600,
                            cursor: 'pointer'
                        }}
                    >
                        + Subir Samples
                    </button>
                </div>
            </header>

            {/* Filters Bar */}
            <div style={{
                padding: '1rem 2rem',
                borderBottom: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                gap: '1rem',
                alignItems: 'center',
                flexWrap: 'wrap'
            }}>
                {/* Search */}
                <div style={{ flex: 1, minWidth: '200px' }}>
                    <input
                        type="text"
                        placeholder="🔍 Buscar samples..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '0.75rem 1rem',
                            background: 'rgba(0,0,0,0.3)',
                            border: '1px solid rgba(255,255,255,0.2)',
                            borderRadius: '8px',
                            color: 'white'
                        }}
                    />
                </div>

                {/* Genre Filter */}
                <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    style={{
                        padding: '0.75rem 1rem',
                        background: 'rgba(0,0,0,0.3)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        borderRadius: '8px',
                        color: 'white'
                    }}
                >
                    <option value="all">Todos los géneros</option>
                    <option value="bachata">💃 Bachata</option>
                    <option value="bolero">🌹 Bolero</option>
                    <option value="merengue">🎺 Merengue</option>
                    <option value="salsa">🔥 Salsa</option>
                    <option value="vallenato">🪗 Vallenato</option>
                    <option value="cumbia">🥁 Cumbia</option>
                </select>

                {/* Sort */}
                <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    style={{
                        padding: '0.75rem 1rem',
                        background: 'rgba(0,0,0,0.3)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        borderRadius: '8px',
                        color: 'white'
                    }}
                >
                    <option value="recent">Más recientes</option>
                    <option value="name">Por nombre</option>
                    <option value="genre">Por género</option>
                </select>

                {/* View Mode */}
                <div style={{ display: 'flex', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
                    <button
                        onClick={() => setViewMode('grid')}
                        style={{
                            padding: '0.75rem',
                            background: viewMode === 'grid' ? 'var(--gold)' : 'transparent',
                            border: 'none',
                            borderRadius: '8px 0 0 8px',
                            color: viewMode === 'grid' ? 'black' : 'white',
                            cursor: 'pointer'
                        }}
                    >
                        ▦
                    </button>
                    <button
                        onClick={() => setViewMode('list')}
                        style={{
                            padding: '0.75rem',
                            background: viewMode === 'list' ? 'var(--gold)' : 'transparent',
                            border: 'none',
                            borderRadius: '0 8px 8px 0',
                            color: viewMode === 'list' ? 'black' : 'white',
                            cursor: 'pointer'
                        }}
                    >
                        ☰
                    </button>
                </div>
            </div>

            {/* Selected Actions */}
            {selectedSamples.length > 0 && (
                <div style={{
                    padding: '1rem 2rem',
                    background: 'rgba(212, 175, 55, 0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem'
                }}>
                    <span>{selectedSamples.length} seleccionados</span>
                    <button style={{
                        padding: '0.5rem 1rem',
                        background: 'var(--electric-blue)',
                        border: 'none',
                        borderRadius: '8px',
                        color: 'white',
                        cursor: 'pointer'
                    }}>
                        📁 Mover a proyecto
                    </button>
                    <button style={{
                        padding: '0.5rem 1rem',
                        background: 'rgba(255,255,255,0.2)',
                        border: 'none',
                        borderRadius: '8px',
                        color: 'white',
                        cursor: 'pointer'
                    }}>
                        ⬇️ Descargar
                    </button>
                    <button
                        onClick={() => setSelectedSamples([])}
                        style={{
                            padding: '0.5rem 1rem',
                            background: 'transparent',
                            border: '1px solid rgba(255,255,255,0.3)',
                            borderRadius: '8px',
                            color: 'white',
                            cursor: 'pointer'
                        }}
                    >
                        ✕ Deseleccionar
                    </button>
                </div>
            )}

            {/* Content */}
            <div style={{ padding: '2rem' }}>
                {/* Stats */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                    gap: '1rem',
                    marginBottom: '2rem'
                }}>
                    <div style={{
                        padding: '1rem',
                        background: 'rgba(255,255,255,0.05)',
                        borderRadius: '12px',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '2rem', color: 'var(--gold)' }}>{samples.length}</div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-gray)' }}>Total Samples</div>
                    </div>
                    <div style={{
                        padding: '1rem',
                        background: 'rgba(255,255,255,0.05)',
                        borderRadius: '12px',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '2rem', color: 'var(--electric-blue)' }}>
                            {[...new Set(samples.map(s => s.genre))].length}
                        </div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-gray)' }}>Géneros</div>
                    </div>
                    <div style={{
                        padding: '1rem',
                        background: 'rgba(255,255,255,0.05)',
                        borderRadius: '12px',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '2rem', color: '#4caf50' }}>
                            {(samples.reduce((acc, s) => acc + (s.file_size || 0), 0) / 1024 / 1024).toFixed(1)}MB
                        </div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-gray)' }}>Almacenamiento</div>
                    </div>
                </div>

                {/* Samples Grid/List */}
                {viewMode === 'grid' ? (
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                        gap: '1rem'
                    }}>
                        {filteredSamples.map(sample => (
                            <div
                                key={sample.id}
                                onClick={() => toggleSelect(sample.id)}
                                style={{
                                    padding: '1rem',
                                    background: selectedSamples.includes(sample.id)
                                        ? 'rgba(212, 175, 55, 0.2)'
                                        : 'rgba(255,255,255,0.05)',
                                    border: selectedSamples.includes(sample.id)
                                        ? '2px solid var(--gold)'
                                        : '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '12px',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                <div style={{
                                    width: '100%',
                                    height: '100px',
                                    background: genreColors[sample.genre] || 'var(--gold)',
                                    borderRadius: '8px',
                                    marginBottom: '0.75rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '2rem'
                                }}>
                                    🎵
                                </div>
                                <h4 style={{ margin: '0 0 0.25rem', fontSize: '0.95rem' }}>
                                    {sample.name || 'Sin título'}
                                </h4>
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    fontSize: '0.8rem',
                                    color: 'var(--text-gray)'
                                }}>
                                    <span style={{
                                        padding: '0.2rem 0.5rem',
                                        background: genreColors[sample.genre] || 'var(--gold)',
                                        borderRadius: '4px',
                                        fontSize: '0.7rem'
                                    }}>
                                        {sample.genre}
                                    </span>
                                    <span>{sample.duration || '0:00'}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{
                        background: 'rgba(255,255,255,0.05)',
                        borderRadius: '12px',
                        overflow: 'hidden'
                    }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ background: 'rgba(0,0,0,0.3)' }}>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>Nombre</th>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>Género</th>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>Instrumento</th>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>Duración</th>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredSamples.map(sample => (
                                    <tr
                                        key={sample.id}
                                        onClick={() => toggleSelect(sample.id)}
                                        style={{
                                            borderBottom: '1px solid rgba(255,255,255,0.05)',
                                            background: selectedSamples.includes(sample.id)
                                                ? 'rgba(212, 175, 55, 0.1)'
                                                : 'transparent',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        <td style={{ padding: '1rem' }}>{sample.name}</td>
                                        <td style={{ padding: '1rem' }}>
                                            <span style={{
                                                padding: '0.25rem 0.5rem',
                                                background: genreColors[sample.genre] || 'var(--gold)',
                                                borderRadius: '4px',
                                                fontSize: '0.8rem'
                                            }}>
                                                {sample.genre}
                                            </span>
                                        </td>
                                        <td style={{ padding: '1rem', color: 'var(--text-gray)' }}>
                                            {sample.instrument}
                                        </td>
                                        <td style={{ padding: '1rem', color: 'var(--text-gray)' }}>
                                            {sample.duration || '0:00'}
                                        </td>
                                        <td style={{ padding: '1rem' }}>
                                            <button style={{
                                                padding: '0.5rem',
                                                background: 'var(--electric-blue)',
                                                border: 'none',
                                                borderRadius: '4px',
                                                color: 'white',
                                                cursor: 'pointer',
                                                marginRight: '0.5rem'
                                            }}>
                                                ▶
                                            </button>
                                            <button style={{
                                                padding: '0.5rem',
                                                background: 'rgba(255,255,255,0.1)',
                                                border: 'none',
                                                borderRadius: '4px',
                                                color: 'white',
                                                cursor: 'pointer'
                                            }}>
                                                ⬇
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {filteredSamples.length === 0 && (
                    <div style={{
                        textAlign: 'center',
                        padding: '4rem',
                        color: 'var(--text-muted)'
                    }}>
                        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📁</div>
                        <h3>No hay samples</h3>
                        <p>Sube tus primeros samples para comenzar</p>
                        <button
                            onClick={() => router.push('/admin')}
                            style={{
                                marginTop: '1rem',
                                padding: '1rem 2rem',
                                background: 'var(--gold)',
                                border: 'none',
                                borderRadius: '8px',
                                color: 'black',
                                fontWeight: 600,
                                cursor: 'pointer'
                            }}
                        >
                            + Subir Samples
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
