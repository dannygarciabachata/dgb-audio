'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import '../globals.css';

const API_BASE = 'http://localhost:8000/api';

export default function AuthPage() {
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const router = useRouter();

    const [form, setForm] = useState({
        email: '',
        password: '',
        name: '',
        plan: 'starter'
    });

    // Check if already logged in
    useEffect(() => {
        const token = localStorage.getItem('dgb_token');
        if (token) {
            router.push('/dashboard');
        }
    }, [router]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const endpoint = isLogin ? '/auth/login' : '/auth/register';
            const body = isLogin
                ? { email: form.email, password: form.password }
                : form;

            const res = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || 'Error en autenticación');
            }

            if (data.token) {
                localStorage.setItem('dgb_token', data.token);
                localStorage.setItem('dgb_user', JSON.stringify(data.user));
                router.push('/dashboard');
            } else if (data.success && !isLogin) {
                // Registered successfully, now login
                setIsLogin(true);
                setError('');
                alert('¡Cuenta creada! Ahora inicia sesión.');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, var(--carbon) 0%, #1a1a2e 50%, var(--carbon) 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem'
        }}>
            <div style={{
                background: 'rgba(26, 26, 46, 0.9)',
                borderRadius: '16px',
                padding: '3rem',
                width: '100%',
                maxWidth: '450px',
                border: '1px solid var(--gold)',
                boxShadow: '0 20px 60px rgba(0,0,0,0.5)'
            }}>
                {/* Logo */}
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <h1 style={{
                        background: 'linear-gradient(135deg, var(--gold), #fff, var(--gold))',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        fontSize: '2.5rem',
                        marginBottom: '0.5rem'
                    }}>
                        DGB AUDIO
                    </h1>
                    <p style={{ color: 'var(--text-gray)' }}>
                        La Inteligencia de la Música Tropical
                    </p>
                </div>

                {/* Tabs */}
                <div style={{ display: 'flex', marginBottom: '2rem', gap: '1rem' }}>
                    <button
                        onClick={() => setIsLogin(true)}
                        style={{
                            flex: 1,
                            padding: '1rem',
                            background: isLogin ? 'var(--gold)' : 'transparent',
                            border: `1px solid ${isLogin ? 'var(--gold)' : 'rgba(255,255,255,0.2)'}`,
                            borderRadius: '8px',
                            color: isLogin ? 'black' : 'white',
                            fontWeight: 600,
                            cursor: 'pointer'
                        }}
                    >
                        Iniciar Sesión
                    </button>
                    <button
                        onClick={() => setIsLogin(false)}
                        style={{
                            flex: 1,
                            padding: '1rem',
                            background: !isLogin ? 'var(--gold)' : 'transparent',
                            border: `1px solid ${!isLogin ? 'var(--gold)' : 'rgba(255,255,255,0.2)'}`,
                            borderRadius: '8px',
                            color: !isLogin ? 'black' : 'white',
                            fontWeight: 600,
                            cursor: 'pointer'
                        }}
                    >
                        Registrarse
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit}>
                    {!isLogin && (
                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>
                                Nombre
                            </label>
                            <input
                                type="text"
                                value={form.name}
                                onChange={(e) => setForm({ ...form, name: e.target.value })}
                                placeholder="Tu nombre"
                                required={!isLogin}
                                style={{
                                    width: '100%',
                                    padding: '1rem',
                                    background: 'rgba(0,0,0,0.3)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px',
                                    color: 'white',
                                    fontSize: '1rem'
                                }}
                            />
                        </div>
                    )}

                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>
                            Email
                        </label>
                        <input
                            type="email"
                            value={form.email}
                            onChange={(e) => setForm({ ...form, email: e.target.value })}
                            placeholder="tu@email.com"
                            required
                            style={{
                                width: '100%',
                                padding: '1rem',
                                background: 'rgba(0,0,0,0.3)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '8px',
                                color: 'white',
                                fontSize: '1rem'
                            }}
                        />
                    </div>

                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>
                            Contraseña
                        </label>
                        <input
                            type="password"
                            value={form.password}
                            onChange={(e) => setForm({ ...form, password: e.target.value })}
                            placeholder="••••••••"
                            required
                            style={{
                                width: '100%',
                                padding: '1rem',
                                background: 'rgba(0,0,0,0.3)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '8px',
                                color: 'white',
                                fontSize: '1rem'
                            }}
                        />
                    </div>

                    {!isLogin && (
                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-gray)' }}>
                                Plan
                            </label>
                            <select
                                value={form.plan}
                                onChange={(e) => setForm({ ...form, plan: e.target.value })}
                                style={{
                                    width: '100%',
                                    padding: '1rem',
                                    background: 'rgba(0,0,0,0.3)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px',
                                    color: 'white',
                                    fontSize: '1rem'
                                }}
                            >
                                <option value="starter">🆓 Starter (Gratis) - 1GB</option>
                                <option value="creator">✨ Creator ($19/mes) - 10GB</option>
                                <option value="pro">🚀 Pro ($49/mes) - 50GB</option>
                                <option value="studio">🎵 Studio ($149/mes) - 200GB</option>
                            </select>
                        </div>
                    )}

                    {error && (
                        <div style={{
                            background: 'rgba(255, 68, 68, 0.2)',
                            border: '1px solid #ff4444',
                            padding: '1rem',
                            borderRadius: '8px',
                            marginBottom: '1.5rem',
                            color: '#ff4444'
                        }}>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            width: '100%',
                            padding: '1rem',
                            background: 'linear-gradient(135deg, var(--gold), #c9a227)',
                            border: 'none',
                            borderRadius: '8px',
                            color: 'black',
                            fontWeight: 700,
                            fontSize: '1.1rem',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            opacity: loading ? 0.7 : 1
                        }}
                    >
                        {loading ? 'Procesando...' : (isLogin ? 'Iniciar Sesión' : 'Crear Cuenta')}
                    </button>
                </form>

                {/* BYOK Notice */}
                <div style={{
                    marginTop: '2rem',
                    padding: '1rem',
                    background: 'rgba(0, 212, 255, 0.1)',
                    borderRadius: '8px',
                    border: '1px solid rgba(0, 212, 255, 0.3)'
                }}>
                    <p style={{ color: 'var(--electric-blue)', fontSize: '0.9rem', margin: 0 }}>
                        🔑 <strong>BYOK</strong>: Usa tu propia API Key de OpenAI.
                        DGB AUDIO no almacena ni cobra por tus tokens.
                    </p>
                </div>
            </div>
        </div>
    );
}
