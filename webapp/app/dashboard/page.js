'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import '../globals.css';

const API_BASE = 'http://localhost:8000/api';

export default function DashboardPage() {
    const [user, setUser] = useState(null);
    const [usage, setUsage] = useState(null);
    const [loading, setLoading] = useState(true);
    const [apiKey, setApiKey] = useState('');
    const [savingKey, setSavingKey] = useState(false);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('dgb_token');
        if (!token) {
            router.push('/auth');
            return;
        }

        // Load user data
        const storedUser = localStorage.getItem('dgb_user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }

        // Fetch fresh data
        fetchUserData(token);
    }, [router]);

    const fetchUserData = async (token) => {
        try {
            // Get user info
            const userRes = await fetch(`${API_BASE}/auth/me?token=${token}`);
            if (!userRes.ok) {
                localStorage.removeItem('dgb_token');
                localStorage.removeItem('dgb_user');
                router.push('/auth');
                return;
            }
            const userData = await userRes.json();
            setUser(userData.user);

            // Get usage
            const usageRes = await fetch(`${API_BASE}/auth/usage?token=${token}`);
            if (usageRes.ok) {
                const usageData = await usageRes.json();
                setUsage(usageData);
            }
        } catch (err) {
            console.error('Error fetching data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSaveApiKey = async () => {
        const token = localStorage.getItem('dgb_token');
        if (!apiKey.trim()) return;

        setSavingKey(true);
        try {
            const res = await fetch(`${API_BASE}/auth/api-key?token=${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey })
            });

            if (res.ok) {
                alert('✅ API Key guardada exitosamente');
                setApiKey('');
                fetchUserData(token);
            } else {
                alert('Error al guardar la API Key');
            }
        } catch (err) {
            alert('Error de conexión');
        } finally {
            setSavingKey(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('dgb_token');
        localStorage.removeItem('dgb_user');
        router.push('/auth');
    };

    if (loading) {
        return (
            <div style={{
                minHeight: '100vh',
                background: 'var(--carbon)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white'
            }}>
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎵</div>
                    <p>Cargando...</p>
                </div>
            </div>
        );
    }

    const planIcons = {
        starter: '🆓',
        creator: '✨',
        pro: '🚀',
        studio: '🎵'
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, var(--carbon) 0%, #1a1a2e 100%)',
            color: 'white'
        }}>
            {/* Header */}
            <header style={{
                padding: '1rem 2rem',
                borderBottom: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <h1 style={{
                    background: 'linear-gradient(135deg, var(--gold), #fff)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    fontSize: '1.5rem'
                }}>
                    DGB AUDIO
                </h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <span style={{ color: 'var(--text-gray)' }}>
                        {planIcons[user?.plan]} {user?.name}
                    </span>
                    <button
                        onClick={() => router.push('/admin')}
                        style={{
                            background: 'rgba(212, 175, 55, 0.2)',
                            border: '1px solid var(--gold)',
                            color: 'var(--gold)',
                            padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            cursor: 'pointer'
                        }}
                    >
                        ⚙️ Admin
                    </button>
                    <button
                        onClick={handleLogout}
                        style={{
                            background: 'rgba(255,255,255,0.1)',
                            border: 'none',
                            color: 'white',
                            padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            cursor: 'pointer'
                        }}
                    >
                        Salir
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
                <h2 style={{ marginBottom: '2rem' }}>Bienvenido, {user?.name} 👋</h2>

                {/* Stats Grid */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: '1.5rem',
                    marginBottom: '2rem'
                }}>
                    {/* Plan Card */}
                    <div style={{
                        background: 'rgba(26, 26, 46, 0.8)',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        border: '1px solid var(--gold)'
                    }}>
                        <h3 style={{ color: 'var(--text-gray)', marginBottom: '1rem' }}>Plan Actual</h3>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
                            {planIcons[user?.plan]} {user?.plan?.charAt(0).toUpperCase() + user?.plan?.slice(1)}
                        </div>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                            {usage?.limits?.storage_gb || 1}GB de almacenamiento
                        </p>
                    </div>

                    {/* API Usage Card */}
                    <div style={{
                        background: 'rgba(26, 26, 46, 0.8)',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        border: '1px solid var(--electric-blue)'
                    }}>
                        <h3 style={{ color: 'var(--text-gray)', marginBottom: '1rem' }}>Uso de API (OpenAI)</h3>
                        <div style={{ fontSize: '2rem', color: 'var(--electric-blue)', marginBottom: '0.5rem' }}>
                            {usage?.usage?.tokens_used?.toLocaleString() || 0}
                        </div>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                            tokens usados • ~${usage?.usage?.estimated_cost_usd?.toFixed(2) || '0.00'} USD
                        </p>
                    </div>

                    {/* Requests Card */}
                    <div style={{
                        background: 'rgba(26, 26, 46, 0.8)',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        border: '1px solid rgba(255,255,255,0.1)'
                    }}>
                        <h3 style={{ color: 'var(--text-gray)', marginBottom: '1rem' }}>Solicitudes</h3>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
                            {usage?.usage?.requests_count || 0}
                        </div>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                            requests totales
                        </p>
                    </div>
                </div>

                {/* API Key Configuration */}
                <div style={{
                    background: 'rgba(26, 26, 46, 0.8)',
                    borderRadius: '12px',
                    padding: '2rem',
                    border: '1px solid rgba(255,255,255,0.1)',
                    marginBottom: '2rem'
                }}>
                    <h3 style={{ marginBottom: '1rem' }}>🔑 Configurar tu OpenAI API Key (BYOK)</h3>
                    <p style={{ color: 'var(--text-gray)', marginBottom: '1.5rem' }}>
                        DGB AUDIO usa tu propia API Key de OpenAI. Tus tokens, tu control, tu privacidad.
                    </p>

                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <input
                            type="password"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            placeholder="sk-..."
                            style={{
                                flex: 1,
                                padding: '1rem',
                                background: 'rgba(0,0,0,0.3)',
                                border: '1px solid rgba(255,255,255,0.2)',
                                borderRadius: '8px',
                                color: 'white'
                            }}
                        />
                        <button
                            onClick={handleSaveApiKey}
                            disabled={savingKey || !apiKey}
                            style={{
                                padding: '1rem 2rem',
                                background: 'var(--gold)',
                                border: 'none',
                                borderRadius: '8px',
                                color: 'black',
                                fontWeight: 600,
                                cursor: savingKey || !apiKey ? 'not-allowed' : 'pointer',
                                opacity: savingKey || !apiKey ? 0.7 : 1
                            }}
                        >
                            {savingKey ? 'Guardando...' : '💾 Guardar'}
                        </button>
                    </div>

                    {user?.openai_key_encrypted && (
                        <p style={{ color: 'var(--electric-blue)', marginTop: '1rem', fontSize: '0.9rem' }}>
                            ✅ API Key configurada
                        </p>
                    )}
                </div>

                {/* Quick Actions */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '1rem'
                }}>
                    <button
                        onClick={() => router.push('/admin')}
                        style={{
                            padding: '1.5rem',
                            background: 'linear-gradient(135deg, var(--gold), #c9a227)',
                            border: 'none',
                            borderRadius: '12px',
                            color: 'black',
                            fontWeight: 600,
                            fontSize: '1.1rem',
                            cursor: 'pointer'
                        }}
                    >
                        📚 Sample Library
                    </button>
                    <button
                        onClick={() => alert('🎙️ Próximamente: Grabación en tiempo real')}
                        style={{
                            padding: '1.5rem',
                            background: 'rgba(0, 212, 255, 0.2)',
                            border: '1px solid var(--electric-blue)',
                            borderRadius: '12px',
                            color: 'var(--electric-blue)',
                            fontWeight: 600,
                            fontSize: '1.1rem',
                            cursor: 'pointer'
                        }}
                    >
                        🎙️ Grabar Instrumento
                    </button>
                    <button
                        onClick={() => alert('✍️ Próximamente: Generación por prompts')}
                        style={{
                            padding: '1.5rem',
                            background: 'rgba(255,255,255,0.1)',
                            border: '1px solid rgba(255,255,255,0.2)',
                            borderRadius: '12px',
                            color: 'white',
                            fontWeight: 600,
                            fontSize: '1.1rem',
                            cursor: 'pointer'
                        }}
                    >
                        ✍️ Crear con Prompts
                    </button>
                </div>
            </main>
        </div>
    );
}
