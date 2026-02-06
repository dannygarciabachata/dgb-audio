'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import '../globals.css';

const API_BASE = 'http://localhost:8000/api';

export default function PricingPage() {
    const [plans, setPlans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [processingPlan, setProcessingPlan] = useState(null);
    const [user, setUser] = useState(null);
    const [currentPlan, setCurrentPlan] = useState('starter');
    const router = useRouter();

    useEffect(() => {
        fetchPlans();

        const token = localStorage.getItem('dgb_token');
        if (token) {
            const storedUser = localStorage.getItem('dgb_user');
            if (storedUser) {
                const u = JSON.parse(storedUser);
                setUser(u);
                setCurrentPlan(u.plan || 'starter');
            }
        }
    }, []);

    const fetchPlans = async () => {
        try {
            const res = await fetch(`${API_BASE}/plans`);
            const data = await res.json();
            setPlans(data.plans || []);
        } catch (err) {
            console.error('Error loading plans:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSubscribe = async (planId) => {
        const token = localStorage.getItem('dgb_token');

        if (!token) {
            router.push('/auth');
            return;
        }

        if (planId === 'starter') {
            router.push('/dashboard');
            return;
        }

        setProcessingPlan(planId);

        try {
            const res = await fetch(`${API_BASE}/payments/checkout?token=${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ plan: planId })
            });

            const data = await res.json();

            if (data.checkout_url) {
                window.location.href = data.checkout_url;
            } else if (data.demo_mode) {
                alert('⚠️ Stripe no configurado. En modo demo, ve al Dashboard.');
                router.push('/dashboard');
            } else {
                alert(data.detail || 'Error al crear checkout');
            }
        } catch (err) {
            console.error(err);
            alert('Error de conexión');
        } finally {
            setProcessingPlan(null);
        }
    };

    const planColors = {
        starter: 'rgba(255,255,255,0.1)',
        creator: 'rgba(212, 175, 55, 0.2)',
        pro: 'rgba(0, 212, 255, 0.2)',
        studio: 'linear-gradient(135deg, rgba(212, 175, 55, 0.3), rgba(0, 212, 255, 0.3))'
    };

    const planBorders = {
        starter: 'rgba(255,255,255,0.2)',
        creator: 'var(--gold)',
        pro: 'var(--electric-blue)',
        studio: 'var(--gold)'
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
                <p>Cargando planes...</p>
            </div>
        );
    }

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, var(--carbon) 0%, #1a1a2e 100%)',
            color: 'white',
            padding: '2rem'
        }}>
            {/* Header */}
            <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
                <h1 style={{
                    background: 'linear-gradient(135deg, var(--gold), #fff, var(--gold))',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    fontSize: '3rem',
                    marginBottom: '1rem'
                }}>
                    DGB AUDIO
                </h1>
                <h2 style={{ color: 'var(--text-gray)', fontWeight: 400 }}>
                    Elige tu Plan
                </h2>
                <p style={{ color: 'var(--text-muted)', maxWidth: '600px', margin: '1rem auto' }}>
                    Cada plan usa tu propia API Key de OpenAI (BYOK).
                    DGB AUDIO = infraestructura, tú controlas tu consumo de AI.
                </p>
            </header>

            {/* Plans Grid */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '1.5rem',
                maxWidth: '1200px',
                margin: '0 auto'
            }}>
                {plans.map(plan => (
                    <div
                        key={plan.id}
                        style={{
                            background: planColors[plan.id],
                            borderRadius: '16px',
                            padding: '2rem',
                            border: `2px solid ${planBorders[plan.id]}`,
                            display: 'flex',
                            flexDirection: 'column',
                            position: 'relative',
                            transform: plan.id === 'pro' ? 'scale(1.05)' : 'none'
                        }}
                    >
                        {plan.id === 'pro' && (
                            <div style={{
                                position: 'absolute',
                                top: '-12px',
                                left: '50%',
                                transform: 'translateX(-50%)',
                                background: 'var(--electric-blue)',
                                padding: '0.5rem 1rem',
                                borderRadius: '20px',
                                fontSize: '0.8rem',
                                fontWeight: 600
                            }}>
                                🔥 MÁS POPULAR
                            </div>
                        )}

                        <h3 style={{
                            fontSize: '1.5rem',
                            marginBottom: '0.5rem',
                            color: plan.id === 'studio' ? 'var(--gold)' : 'white'
                        }}>
                            {plan.name}
                        </h3>

                        <div style={{ marginBottom: '1.5rem' }}>
                            <span style={{ fontSize: '3rem', fontWeight: 700 }}>
                                ${plan.price_monthly}
                            </span>
                            <span style={{ color: 'var(--text-gray)' }}>/mes</span>
                        </div>

                        <ul style={{
                            listStyle: 'none',
                            padding: 0,
                            margin: 0,
                            flex: 1,
                            marginBottom: '1.5rem'
                        }}>
                            {plan.features?.map((feature, i) => (
                                <li key={i} style={{
                                    padding: '0.5rem 0',
                                    borderBottom: '1px solid rgba(255,255,255,0.1)',
                                    color: 'var(--text-gray)'
                                }}>
                                    ✓ {feature}
                                </li>
                            ))}
                        </ul>

                        <button
                            onClick={() => handleSubscribe(plan.id)}
                            disabled={processingPlan === plan.id || plan.id === currentPlan}
                            style={{
                                padding: '1rem',
                                borderRadius: '8px',
                                border: 'none',
                                background: plan.id === currentPlan
                                    ? 'rgba(255,255,255,0.1)'
                                    : plan.id === 'starter'
                                        ? 'rgba(255,255,255,0.2)'
                                        : plan.id === 'studio'
                                            ? 'linear-gradient(135deg, var(--gold), #c9a227)'
                                            : 'var(--electric-blue)',
                                color: plan.id === 'studio' ? 'black' : 'white',
                                fontWeight: 600,
                                cursor: plan.id === currentPlan ? 'not-allowed' : 'pointer',
                                opacity: processingPlan === plan.id ? 0.7 : 1
                            }}
                        >
                            {processingPlan === plan.id
                                ? 'Procesando...'
                                : plan.id === currentPlan
                                    ? '✓ Plan Actual'
                                    : plan.id === 'starter'
                                        ? 'Comenzar Gratis'
                                        : 'Suscribirse'}
                        </button>
                    </div>
                ))}
            </div>

            {/* FAQ */}
            <div style={{
                maxWidth: '800px',
                margin: '4rem auto 0',
                padding: '2rem',
                background: 'rgba(26, 26, 46, 0.8)',
                borderRadius: '12px'
            }}>
                <h3 style={{ marginBottom: '1.5rem' }}>❓ Preguntas Frecuentes</h3>

                <div style={{ marginBottom: '1.5rem' }}>
                    <h4 style={{ color: 'var(--gold)', marginBottom: '0.5rem' }}>
                        ¿Qué significa BYOK?
                    </h4>
                    <p style={{ color: 'var(--text-gray)' }}>
                        Bring Your Own Key. Usas tu propia API Key de OpenAI.
                        Tú controlas tu consumo de tokens directamente con OpenAI.
                    </p>
                </div>

                <div style={{ marginBottom: '1.5rem' }}>
                    <h4 style={{ color: 'var(--gold)', marginBottom: '0.5rem' }}>
                        ¿Puedo cambiar de plan?
                    </h4>
                    <p style={{ color: 'var(--text-gray)' }}>
                        Sí, puedes upgrade o downgrade en cualquier momento.
                        Los cambios se aplican inmediatamente.
                    </p>
                </div>

                <div>
                    <h4 style={{ color: 'var(--gold)', marginBottom: '0.5rem' }}>
                        ¿Hay reembolsos?
                    </h4>
                    <p style={{ color: 'var(--text-gray)' }}>
                        Sí, reembolso proporcional si cancelas antes del fin del mes.
                    </p>
                </div>
            </div>

            {/* Back Button */}
            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                <button
                    onClick={() => user ? router.push('/dashboard') : router.push('/')}
                    style={{
                        background: 'none',
                        border: '1px solid rgba(255,255,255,0.2)',
                        color: 'white',
                        padding: '1rem 2rem',
                        borderRadius: '8px',
                        cursor: 'pointer'
                    }}
                >
                    ← Volver
                </button>
            </div>
        </div>
    );
}
