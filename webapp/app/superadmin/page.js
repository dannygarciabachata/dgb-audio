'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import '../globals.css';

const API_BASE = 'http://localhost:8000/api';

export default function SuperAdminPage() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);
    const [stats, setStats] = useState({});
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('dgb_token');
        if (!token) {
            router.push('/auth');
            return;
        }

        const storedUser = localStorage.getItem('dgb_user');
        if (storedUser) {
            const u = JSON.parse(storedUser);
            setUser(u);
            if (u.role !== 'superadmin') {
                alert('⛔ Acceso denegado - Solo SuperAdmin');
                router.push('/dashboard');
                return;
            }
        }

        fetchUsers(token);
    }, [router]);

    const fetchUsers = async (token) => {
        try {
            const res = await fetch(`${API_BASE}/admin/users?token=${token}`);
            if (res.ok) {
                const data = await res.json();
                setUsers(data.users || []);

                // Calculate stats
                const plans = {};
                let totalTokens = 0;
                let totalCost = 0;

                data.users?.forEach(u => {
                    plans[u.plan] = (plans[u.plan] || 0) + 1;
                    totalTokens += u.usage?.tokens_used || 0;
                    totalCost += u.usage?.estimated_cost_usd || 0;
                });

                setStats({
                    totalUsers: data.users?.length || 0,
                    planDistribution: plans,
                    totalTokens,
                    totalCost
                });
            } else {
                alert('Error al cargar usuarios');
                router.push('/dashboard');
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const updateRole = async (email, newRole) => {
        const token = localStorage.getItem('dgb_token');
        try {
            const res = await fetch(`${API_BASE}/admin/users/role?token=${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_email: email, new_role: newRole })
            });
            if (res.ok) {
                fetchUsers(token);
            }
        } catch (err) {
            console.error(err);
        }
    };

    const updatePlan = async (email, newPlan) => {
        const token = localStorage.getItem('dgb_token');
        try {
            const res = await fetch(`${API_BASE}/admin/users/plan?token=${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_email: email, new_plan: newPlan })
            });
            if (res.ok) {
                fetchUsers(token);
            }
        } catch (err) {
            console.error(err);
        }
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
                <p>Cargando panel de SuperAdmin...</p>
            </div>
        );
    }

    const roleColors = {
        superadmin: '#ff4444',
        admin: 'var(--gold)',
        user: 'var(--electric-blue)'
    };

    const planIcons = {
        starter: '🆓',
        creator: '✨',
        pro: '🚀',
        studio: '🎵'
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #1a0a0a 0%, #2d1515 100%)',
            color: 'white'
        }}>
            {/* Header */}
            <header style={{
                padding: '1rem 2rem',
                borderBottom: '1px solid rgba(255,68,68,0.3)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                background: 'rgba(255,68,68,0.1)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <button
                        onClick={() => router.push('/dashboard')}
                        style={{ background: 'none', border: 'none', color: 'white', fontSize: '1.5rem', cursor: 'pointer' }}
                    >
                        ←
                    </button>
                    <h1 style={{ color: '#ff4444' }}>👑 SuperAdmin Panel</h1>
                </div>
                <span style={{ color: 'var(--text-gray)' }}>{user?.email}</span>
            </header>

            <main style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
                {/* Stats */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '1rem',
                    marginBottom: '2rem'
                }}>
                    <div style={{
                        background: 'rgba(255,68,68,0.2)',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        border: '1px solid rgba(255,68,68,0.3)'
                    }}>
                        <h3 style={{ color: 'var(--text-gray)', marginBottom: '0.5rem' }}>Total Usuarios</h3>
                        <div style={{ fontSize: '2rem', color: '#ff4444' }}>{stats.totalUsers}</div>
                    </div>
                    <div style={{
                        background: 'rgba(212, 175, 55, 0.2)',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        border: '1px solid var(--gold)'
                    }}>
                        <h3 style={{ color: 'var(--text-gray)', marginBottom: '0.5rem' }}>Tokens Totales</h3>
                        <div style={{ fontSize: '2rem', color: 'var(--gold)' }}>{stats.totalTokens?.toLocaleString()}</div>
                    </div>
                    <div style={{
                        background: 'rgba(0, 212, 255, 0.2)',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        border: '1px solid var(--electric-blue)'
                    }}>
                        <h3 style={{ color: 'var(--text-gray)', marginBottom: '0.5rem' }}>Costo Total</h3>
                        <div style={{ fontSize: '2rem', color: 'var(--electric-blue)' }}>${stats.totalCost?.toFixed(2)}</div>
                    </div>
                </div>

                {/* Users Table */}
                <div style={{
                    background: 'rgba(26, 26, 46, 0.8)',
                    borderRadius: '12px',
                    border: '1px solid rgba(255,255,255,0.1)',
                    overflow: 'hidden'
                }}>
                    <h2 style={{ padding: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                        👥 Gestión de Usuarios
                    </h2>
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ background: 'rgba(0,0,0,0.3)' }}>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>Usuario</th>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>Rol</th>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>Plan</th>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>Tokens</th>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>Costo</th>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>API Key</th>
                                    <th style={{ padding: '1rem', textAlign: 'left' }}>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(u => (
                                    <tr key={u.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                        <td style={{ padding: '1rem' }}>
                                            <div>{u.name}</div>
                                            <div style={{ fontSize: '0.8rem', color: 'var(--text-gray)' }}>{u.email}</div>
                                        </td>
                                        <td style={{ padding: '1rem' }}>
                                            <select
                                                value={u.role}
                                                onChange={(e) => updateRole(u.email, e.target.value)}
                                                style={{
                                                    padding: '0.5rem',
                                                    background: 'rgba(0,0,0,0.3)',
                                                    border: `1px solid ${roleColors[u.role]}`,
                                                    borderRadius: '4px',
                                                    color: roleColors[u.role]
                                                }}
                                            >
                                                <option value="user">User</option>
                                                <option value="admin">Admin</option>
                                                <option value="superadmin">SuperAdmin</option>
                                            </select>
                                        </td>
                                        <td style={{ padding: '1rem' }}>
                                            <select
                                                value={u.plan}
                                                onChange={(e) => updatePlan(u.email, e.target.value)}
                                                style={{
                                                    padding: '0.5rem',
                                                    background: 'rgba(0,0,0,0.3)',
                                                    border: '1px solid var(--gold)',
                                                    borderRadius: '4px',
                                                    color: 'var(--gold)'
                                                }}
                                            >
                                                <option value="starter">🆓 Starter</option>
                                                <option value="creator">✨ Creator</option>
                                                <option value="pro">🚀 Pro</option>
                                                <option value="studio">🎵 Studio</option>
                                            </select>
                                        </td>
                                        <td style={{ padding: '1rem' }}>{u.usage?.tokens_used?.toLocaleString() || 0}</td>
                                        <td style={{ padding: '1rem' }}>${u.usage?.estimated_cost_usd?.toFixed(2) || '0.00'}</td>
                                        <td style={{ padding: '1rem' }}>
                                            {u.openai_key_encrypted ? (
                                                <span style={{ color: 'var(--electric-blue)' }}>✅ Configurada</span>
                                            ) : (
                                                <span style={{ color: 'var(--text-muted)' }}>❌ Sin key</span>
                                            )}
                                        </td>
                                        <td style={{ padding: '1rem' }}>
                                            <button style={{
                                                padding: '0.5rem 1rem',
                                                background: 'rgba(255,255,255,0.1)',
                                                border: 'none',
                                                borderRadius: '4px',
                                                color: 'white',
                                                cursor: 'pointer',
                                                fontSize: '0.8rem'
                                            }}>
                                                Ver detalles
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    );
}
