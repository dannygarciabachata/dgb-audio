'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import '../globals.css';

const API_BASE = 'http://localhost:8000/api';

export default function SupportChatPage() {
    const [departments, setDepartments] = useState([]);
    const [selectedDept, setSelectedDept] = useState('general');
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [user, setUser] = useState(null);
    const messagesEndRef = useRef(null);
    const router = useRouter();

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

        fetchDepartments();
    }, [router]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const fetchDepartments = async () => {
        try {
            const res = await fetch(`${API_BASE}/chat/departments`);
            const data = await res.json();
            setDepartments(data.departments);
        } catch (err) {
            console.error('Error loading departments:', err);
        }
    };

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const token = localStorage.getItem('dgb_token');
        const userMessage = { role: 'user', content: input };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/chat/send?token=${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    department: selectedDept,
                    history: messages.map(m => ({ role: m.role, content: m.content }))
                })
            });

            const data = await res.json();

            if (data.success) {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: data.message,
                    department: data.department_name,
                    tokens: data.tokens_used,
                    cost: data.cost_estimate
                }]);
            } else {
                setMessages(prev => [...prev, {
                    role: 'error',
                    content: data.detail || data.message || 'Error al enviar mensaje'
                }]);
            }
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'error',
                content: 'Error de conexión'
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleQuickResponse = (text) => {
        setInput(text);
    };

    const currentDept = departments.find(d => d.id === selectedDept) || {};

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, var(--carbon) 0%, #1a1a2e 100%)',
            display: 'flex',
            flexDirection: 'column'
        }}>
            {/* Header */}
            <header style={{
                padding: '1rem 2rem',
                borderBottom: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <button
                        onClick={() => router.push('/dashboard')}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: 'white',
                            fontSize: '1.5rem',
                            cursor: 'pointer'
                        }}
                    >
                        ←
                    </button>
                    <h1 style={{ color: 'white' }}>💬 Soporte en Vivo</h1>
                </div>
                <span style={{ color: 'var(--text-gray)' }}>{user?.name}</span>
            </header>

            {/* Department Selector */}
            <div style={{
                padding: '1rem 2rem',
                borderBottom: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                gap: '1rem',
                overflowX: 'auto'
            }}>
                {departments.map(dept => (
                    <button
                        key={dept.id}
                        onClick={() => {
                            setSelectedDept(dept.id);
                            setMessages([]);
                        }}
                        style={{
                            padding: '0.75rem 1.5rem',
                            borderRadius: '20px',
                            border: selectedDept === dept.id ? '2px solid var(--gold)' : '1px solid rgba(255,255,255,0.2)',
                            background: selectedDept === dept.id ? 'rgba(212, 175, 55, 0.2)' : 'transparent',
                            color: selectedDept === dept.id ? 'var(--gold)' : 'white',
                            cursor: 'pointer',
                            whiteSpace: 'nowrap',
                            fontWeight: selectedDept === dept.id ? 600 : 400
                        }}
                    >
                        {dept.icon} {dept.name}
                    </button>
                ))}
            </div>

            {/* Chat Area */}
            <div style={{
                flex: 1,
                padding: '2rem',
                overflowY: 'auto',
                maxHeight: 'calc(100vh - 280px)'
            }}>
                {messages.length === 0 && (
                    <div style={{ textAlign: 'center', color: 'var(--text-gray)' }}>
                        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>{currentDept.icon}</div>
                        <h2 style={{ color: 'white', marginBottom: '1rem' }}>{currentDept.name}</h2>
                        <p style={{ marginBottom: '2rem' }}>¿En qué podemos ayudarte hoy?</p>

                        {/* Quick Responses */}
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', justifyContent: 'center' }}>
                            {currentDept.quick_responses?.map((text, i) => (
                                <button
                                    key={i}
                                    onClick={() => handleQuickResponse(text)}
                                    style={{
                                        padding: '0.75rem 1rem',
                                        borderRadius: '20px',
                                        border: '1px solid var(--electric-blue)',
                                        background: 'rgba(0, 212, 255, 0.1)',
                                        color: 'var(--electric-blue)',
                                        cursor: 'pointer',
                                        fontSize: '0.9rem'
                                    }}
                                >
                                    {text}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((msg, i) => (
                    <div
                        key={i}
                        style={{
                            display: 'flex',
                            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                            marginBottom: '1rem'
                        }}
                    >
                        <div style={{
                            maxWidth: '70%',
                            padding: '1rem',
                            borderRadius: '12px',
                            background: msg.role === 'user'
                                ? 'var(--gold)'
                                : msg.role === 'error'
                                    ? 'rgba(255, 68, 68, 0.2)'
                                    : 'rgba(255,255,255,0.1)',
                            color: msg.role === 'user' ? 'black' : msg.role === 'error' ? '#ff4444' : 'white'
                        }}>
                            <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{msg.content}</p>
                            {msg.tokens && (
                                <p style={{
                                    margin: '0.5rem 0 0',
                                    fontSize: '0.7rem',
                                    color: 'var(--text-muted)'
                                }}>
                                    {msg.tokens} tokens • ~${msg.cost?.toFixed(4)}
                                </p>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '1rem' }}>
                        <div style={{
                            padding: '1rem',
                            borderRadius: '12px',
                            background: 'rgba(255,255,255,0.1)',
                            color: 'var(--text-gray)'
                        }}>
                            ⏳ Escribiendo...
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div style={{
                padding: '1rem 2rem',
                borderTop: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                gap: '1rem'
            }}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Escribe tu mensaje..."
                    style={{
                        flex: 1,
                        padding: '1rem',
                        background: 'rgba(0,0,0,0.3)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        borderRadius: '8px',
                        color: 'white',
                        fontSize: '1rem'
                    }}
                />
                <button
                    onClick={handleSend}
                    disabled={loading || !input.trim()}
                    style={{
                        padding: '1rem 2rem',
                        background: 'var(--gold)',
                        border: 'none',
                        borderRadius: '8px',
                        color: 'black',
                        fontWeight: 600,
                        cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
                        opacity: loading || !input.trim() ? 0.7 : 1
                    }}
                >
                    Enviar
                </button>
            </div>
        </div>
    );
}
