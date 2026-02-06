'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import '../globals.css';

const API_BASE = 'http://localhost:8000/api';

export default function RecordPage() {
    const [user, setUser] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [maxDuration, setMaxDuration] = useState(30);
    const [countdown, setCountdown] = useState(null);
    const [audioBlob, setAudioBlob] = useState(null);
    const [audioUrl, setAudioUrl] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);
    const [selectedInstrument, setSelectedInstrument] = useState('guitar');
    const [selectedGenre, setSelectedGenre] = useState('bachata');
    const [waveformData, setWaveformData] = useState([]);

    const mediaRecorderRef = useRef(null);
    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const chunksRef = useRef([]);
    const timerRef = useRef(null);
    const animationRef = useRef(null);
    const router = useRouter();

    const instruments = [
        { id: 'guitar', name: 'Guitarra', icon: '🎸' },
        { id: 'requinto', name: 'Requinto', icon: '🎵' },
        { id: 'bongo', name: 'Bongos', icon: '🥁' },
        { id: 'piano', name: 'Piano', icon: '🎹' },
        { id: 'bass', name: 'Bajo', icon: '🎸' },
        { id: 'voice', name: 'Voz', icon: '🎤' },
        { id: 'guira', name: 'Güira', icon: '🪘' },
        { id: 'accordion', name: 'Acordeón', icon: '🪗' }
    ];

    const genres = [
        { id: 'bachata', name: 'Bachata', bpm: 130 },
        { id: 'bolero', name: 'Bolero', bpm: 85 },
        { id: 'merengue', name: 'Merengue', bpm: 160 },
        { id: 'salsa', name: 'Salsa', bpm: 180 },
        { id: 'vallenato', name: 'Vallenato', bpm: 120 },
        { id: 'cumbia', name: 'Cumbia', bpm: 100 }
    ];

    const durations = [
        { value: 30, label: '30 segundos', description: 'Ideal para riffs cortos' },
        { value: 60, label: '60 segundos', description: 'Para frases completas' },
        { value: 0, label: '8 compases', description: 'Sincronizado con BPM' }
    ];

    useEffect(() => {
        const token = localStorage.getItem('dgb_token');
        if (!token) {
            router.push('/auth');
            return;
        }
        const storedUser = localStorage.getItem('dgb_user');
        if (storedUser) setUser(JSON.parse(storedUser));

        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
            if (animationRef.current) cancelAnimationFrame(animationRef.current);
            if (audioContextRef.current) audioContextRef.current.close();
        };
    }, [router]);

    const startCountdown = () => {
        setCountdown(3);
        const countdownInterval = setInterval(() => {
            setCountdown(prev => {
                if (prev <= 1) {
                    clearInterval(countdownInterval);
                    startRecording();
                    return null;
                }
                return prev - 1;
            });
        }, 1000);
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
            analyserRef.current = audioContextRef.current.createAnalyser();
            const source = audioContextRef.current.createMediaStreamSource(stream);
            source.connect(analyserRef.current);
            analyserRef.current.fftSize = 256;

            mediaRecorderRef.current = new MediaRecorder(stream);
            chunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunksRef.current.push(e.data);
                }
            };

            mediaRecorderRef.current.onstop = () => {
                const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
                setAudioBlob(blob);
                setAudioUrl(URL.createObjectURL(blob));
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorderRef.current.start(100);
            setIsRecording(true);
            setRecordingTime(0);

            timerRef.current = setInterval(() => {
                setRecordingTime(prev => {
                    const newTime = prev + 0.1;
                    if (maxDuration > 0 && newTime >= maxDuration) {
                        stopRecording();
                        return maxDuration;
                    }
                    return newTime;
                });
            }, 100);

            visualize();
        } catch (err) {
            console.error('Recording error:', err);
            alert('Error al acceder al micrófono. Asegúrate de dar permiso.');
        }
    };

    const visualize = () => {
        if (!analyserRef.current) return;

        const bufferLength = analyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
            if (!isRecording) return;
            animationRef.current = requestAnimationFrame(draw);
            analyserRef.current.getByteFrequencyData(dataArray);

            const normalized = Array.from(dataArray.slice(0, 32)).map(v => v / 255);
            setWaveformData(normalized);
        };

        draw();
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            if (timerRef.current) clearInterval(timerRef.current);
            if (animationRef.current) cancelAnimationFrame(animationRef.current);
        }
    };

    const analyzeAudio = async () => {
        if (!audioBlob) return;

        setIsAnalyzing(true);

        // Simulate AI analysis (in production, this would call the backend)
        setTimeout(() => {
            setAnalysisResult({
                detected_key: 'Am',
                detected_bpm: genres.find(g => g.id === selectedGenre)?.bpm || 120,
                detected_instrument: selectedInstrument,
                timbre_profile: {
                    brightness: 0.7,
                    warmth: 0.8,
                    attack: 0.6,
                    sustain: 0.75
                },
                suggested_patterns: [
                    'Bachata rhythm pattern detected',
                    'Syncopated strumming identified',
                    'Minor key progression'
                ],
                quality_score: 85
            });
            setIsAnalyzing(false);
        }, 2000);
    };

    const saveRecording = async () => {
        if (!audioBlob || !analysisResult) return;

        const formData = new FormData();
        formData.append('audio', audioBlob, `${selectedGenre}_${selectedInstrument}_recording.webm`);
        formData.append('analysis', JSON.stringify(analysisResult));
        formData.append('genre', selectedGenre);
        formData.append('instrument', selectedInstrument);

        // API call to save would go here
        alert('¡Grabación guardada exitosamente!');
        router.push('/library');
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        const ms = Math.floor((seconds % 1) * 10);
        return `${mins}:${secs.toString().padStart(2, '0')}.${ms}`;
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0f0f1a 100%)',
            color: 'white',
            padding: '2rem'
        }}>
            {/* Header */}
            <header style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '2rem'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <button
                        onClick={() => router.push('/create')}
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
                    <h1 style={{ margin: 0 }}>🎙️ Estudio de Grabación</h1>
                </div>
                <div style={{ color: 'var(--text-gray)' }}>
                    {user?.name || 'Usuario'}
                </div>
            </header>

            <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 400px',
                gap: '2rem',
                maxWidth: '1400px',
                margin: '0 auto'
            }}>
                {/* Main Recording Area */}
                <div>
                    {/* Recording Visualization */}
                    <div style={{
                        background: 'rgba(0,0,0,0.4)',
                        borderRadius: '20px',
                        padding: '2rem',
                        marginBottom: '2rem',
                        border: isRecording ? '2px solid #ff4444' : '1px solid rgba(255,255,255,0.1)'
                    }}>
                        {/* Countdown Overlay */}
                        {countdown !== null && (
                            <div style={{
                                position: 'absolute',
                                inset: 0,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                background: 'rgba(0,0,0,0.8)',
                                zIndex: 10,
                                borderRadius: '20px',
                                fontSize: '8rem',
                                fontWeight: 700,
                                color: 'var(--gold)',
                                animation: 'pulse 1s ease-in-out'
                            }}>
                                {countdown}
                            </div>
                        )}

                        {/* Waveform Display */}
                        <div style={{
                            height: '200px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '4px',
                            marginBottom: '2rem'
                        }}>
                            {isRecording ? (
                                waveformData.map((v, i) => (
                                    <div
                                        key={i}
                                        style={{
                                            width: '8px',
                                            height: `${Math.max(10, v * 180)}px`,
                                            background: `linear-gradient(to top, #ff4444, var(--gold))`,
                                            borderRadius: '4px',
                                            transition: 'height 0.1s ease'
                                        }}
                                    />
                                ))
                            ) : audioUrl ? (
                                <audio
                                    controls
                                    src={audioUrl}
                                    style={{ width: '100%' }}
                                />
                            ) : (
                                <div style={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    gap: '1rem',
                                    color: 'var(--text-gray)'
                                }}>
                                    <div style={{ fontSize: '4rem' }}>🎤</div>
                                    <p>Configura y presiona Grabar para comenzar</p>
                                </div>
                            )}
                        </div>

                        {/* Timer */}
                        <div style={{
                            textAlign: 'center',
                            marginBottom: '2rem'
                        }}>
                            <div style={{
                                fontFamily: 'monospace',
                                fontSize: '3rem',
                                fontWeight: 700,
                                color: isRecording ? '#ff4444' : 'var(--gold)'
                            }}>
                                {formatTime(recordingTime)}
                            </div>
                            <div style={{ color: 'var(--text-gray)' }}>
                                / {maxDuration > 0 ? formatTime(maxDuration) : '8 compases'}
                            </div>
                        </div>

                        {/* Controls */}
                        <div style={{
                            display: 'flex',
                            justifyContent: 'center',
                            gap: '1rem'
                        }}>
                            {!isRecording && !audioUrl && (
                                <button
                                    onClick={startCountdown}
                                    style={{
                                        width: '80px',
                                        height: '80px',
                                        borderRadius: '50%',
                                        background: 'linear-gradient(135deg, #ff4444, #cc0000)',
                                        border: 'none',
                                        color: 'white',
                                        fontSize: '2rem',
                                        cursor: 'pointer',
                                        boxShadow: '0 0 30px rgba(255,68,68,0.5)'
                                    }}
                                >
                                    ⏺
                                </button>
                            )}

                            {isRecording && (
                                <button
                                    onClick={stopRecording}
                                    style={{
                                        width: '80px',
                                        height: '80px',
                                        borderRadius: '50%',
                                        background: 'rgba(255,255,255,0.2)',
                                        border: '3px solid white',
                                        color: 'white',
                                        fontSize: '1.5rem',
                                        cursor: 'pointer'
                                    }}
                                >
                                    ⏹
                                </button>
                            )}

                            {audioUrl && !analysisResult && (
                                <>
                                    <button
                                        onClick={() => {
                                            setAudioUrl(null);
                                            setAudioBlob(null);
                                            setRecordingTime(0);
                                        }}
                                        style={{
                                            padding: '1rem 2rem',
                                            background: 'rgba(255,255,255,0.1)',
                                            border: '1px solid rgba(255,255,255,0.3)',
                                            borderRadius: '12px',
                                            color: 'white',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        🔄 Grabar de nuevo
                                    </button>
                                    <button
                                        onClick={analyzeAudio}
                                        disabled={isAnalyzing}
                                        style={{
                                            padding: '1rem 2rem',
                                            background: 'var(--gold)',
                                            border: 'none',
                                            borderRadius: '12px',
                                            color: 'black',
                                            fontWeight: 600,
                                            cursor: 'pointer'
                                        }}
                                    >
                                        {isAnalyzing ? '✨ Analizando...' : '🧠 Analizar con AI'}
                                    </button>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Analysis Results */}
                    {analysisResult && (
                        <div style={{
                            background: 'rgba(0,0,0,0.4)',
                            borderRadius: '16px',
                            padding: '1.5rem',
                            border: '1px solid rgba(212,175,55,0.3)'
                        }}>
                            <h3 style={{ marginTop: 0, color: 'var(--gold)' }}>
                                ✨ Análisis de AI
                            </h3>

                            <div style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(4, 1fr)',
                                gap: '1rem',
                                marginBottom: '1.5rem'
                            }}>
                                <div style={{
                                    padding: '1rem',
                                    background: 'rgba(255,255,255,0.05)',
                                    borderRadius: '8px',
                                    textAlign: 'center'
                                }}>
                                    <div style={{ fontSize: '1.5rem', color: 'var(--gold)' }}>
                                        {analysisResult.detected_key}
                                    </div>
                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-gray)' }}>
                                        Key Detectada
                                    </div>
                                </div>
                                <div style={{
                                    padding: '1rem',
                                    background: 'rgba(255,255,255,0.05)',
                                    borderRadius: '8px',
                                    textAlign: 'center'
                                }}>
                                    <div style={{ fontSize: '1.5rem', color: 'var(--electric-blue)' }}>
                                        {analysisResult.detected_bpm}
                                    </div>
                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-gray)' }}>
                                        BPM
                                    </div>
                                </div>
                                <div style={{
                                    padding: '1rem',
                                    background: 'rgba(255,255,255,0.05)',
                                    borderRadius: '8px',
                                    textAlign: 'center'
                                }}>
                                    <div style={{ fontSize: '1.5rem', color: '#4caf50' }}>
                                        {analysisResult.quality_score}%
                                    </div>
                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-gray)' }}>
                                        Calidad
                                    </div>
                                </div>
                                <div style={{
                                    padding: '1rem',
                                    background: 'rgba(255,255,255,0.05)',
                                    borderRadius: '8px',
                                    textAlign: 'center'
                                }}>
                                    <div style={{ fontSize: '1.5rem' }}>
                                        {instruments.find(i => i.id === analysisResult.detected_instrument)?.icon}
                                    </div>
                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-gray)' }}>
                                        Instrumento
                                    </div>
                                </div>
                            </div>

                            {/* Timbre Profile */}
                            <div style={{ marginBottom: '1.5rem' }}>
                                <h4 style={{ marginBottom: '0.75rem' }}>Perfil de Timbre</h4>
                                {Object.entries(analysisResult.timbre_profile).map(([key, value]) => (
                                    <div key={key} style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '1rem',
                                        marginBottom: '0.5rem'
                                    }}>
                                        <span style={{
                                            width: '80px',
                                            fontSize: '0.85rem',
                                            color: 'var(--text-gray)',
                                            textTransform: 'capitalize'
                                        }}>
                                            {key}
                                        </span>
                                        <div style={{
                                            flex: 1,
                                            height: '8px',
                                            background: 'rgba(255,255,255,0.1)',
                                            borderRadius: '4px',
                                            overflow: 'hidden'
                                        }}>
                                            <div style={{
                                                width: `${value * 100}%`,
                                                height: '100%',
                                                background: 'var(--gold)',
                                                borderRadius: '4px'
                                            }} />
                                        </div>
                                        <span style={{ width: '40px', textAlign: 'right' }}>
                                            {Math.round(value * 100)}%
                                        </span>
                                    </div>
                                ))}
                            </div>

                            {/* Suggested Patterns */}
                            <div style={{ marginBottom: '1.5rem' }}>
                                <h4 style={{ marginBottom: '0.5rem' }}>Patrones Detectados</h4>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                    {analysisResult.suggested_patterns.map((pattern, i) => (
                                        <span
                                            key={i}
                                            style={{
                                                padding: '0.5rem 1rem',
                                                background: 'rgba(100, 181, 246, 0.2)',
                                                border: '1px solid var(--electric-blue)',
                                                borderRadius: '20px',
                                                fontSize: '0.85rem'
                                            }}
                                        >
                                            {pattern}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <button
                                onClick={saveRecording}
                                style={{
                                    width: '100%',
                                    padding: '1rem',
                                    background: 'var(--gold)',
                                    border: 'none',
                                    borderRadius: '12px',
                                    color: 'black',
                                    fontWeight: 600,
                                    fontSize: '1rem',
                                    cursor: 'pointer'
                                }}
                            >
                                💾 Guardar en Librería
                            </button>
                        </div>
                    )}
                </div>

                {/* Sidebar Settings */}
                <div>
                    {/* Instrument Selection */}
                    <div style={{
                        background: 'rgba(0,0,0,0.4)',
                        borderRadius: '16px',
                        padding: '1.5rem',
                        marginBottom: '1rem'
                    }}>
                        <h3 style={{ marginTop: 0 }}>🎸 Instrumento</h3>
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(2, 1fr)',
                            gap: '0.5rem'
                        }}>
                            {instruments.map(inst => (
                                <button
                                    key={inst.id}
                                    onClick={() => setSelectedInstrument(inst.id)}
                                    style={{
                                        padding: '0.75rem',
                                        background: selectedInstrument === inst.id
                                            ? 'rgba(212,175,55,0.3)'
                                            : 'rgba(255,255,255,0.05)',
                                        border: selectedInstrument === inst.id
                                            ? '2px solid var(--gold)'
                                            : '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px',
                                        color: 'white',
                                        cursor: 'pointer',
                                        textAlign: 'left'
                                    }}
                                >
                                    <span style={{ marginRight: '0.5rem' }}>{inst.icon}</span>
                                    {inst.name}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Genre Selection */}
                    <div style={{
                        background: 'rgba(0,0,0,0.4)',
                        borderRadius: '16px',
                        padding: '1.5rem',
                        marginBottom: '1rem'
                    }}>
                        <h3 style={{ marginTop: 0 }}>🎵 Género</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            {genres.map(genre => (
                                <button
                                    key={genre.id}
                                    onClick={() => setSelectedGenre(genre.id)}
                                    style={{
                                        padding: '0.75rem 1rem',
                                        background: selectedGenre === genre.id
                                            ? 'rgba(212,175,55,0.3)'
                                            : 'rgba(255,255,255,0.05)',
                                        border: selectedGenre === genre.id
                                            ? '2px solid var(--gold)'
                                            : '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px',
                                        color: 'white',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        justifyContent: 'space-between'
                                    }}
                                >
                                    <span>{genre.name}</span>
                                    <span style={{ color: 'var(--text-gray)' }}>{genre.bpm} BPM</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Duration Selection */}
                    <div style={{
                        background: 'rgba(0,0,0,0.4)',
                        borderRadius: '16px',
                        padding: '1.5rem'
                    }}>
                        <h3 style={{ marginTop: 0 }}>⏱️ Duración</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            {durations.map(dur => (
                                <button
                                    key={dur.value}
                                    onClick={() => setMaxDuration(dur.value)}
                                    disabled={isRecording}
                                    style={{
                                        padding: '0.75rem 1rem',
                                        background: maxDuration === dur.value
                                            ? 'rgba(212,175,55,0.3)'
                                            : 'rgba(255,255,255,0.05)',
                                        border: maxDuration === dur.value
                                            ? '2px solid var(--gold)'
                                            : '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px',
                                        color: 'white',
                                        cursor: isRecording ? 'not-allowed' : 'pointer',
                                        textAlign: 'left',
                                        opacity: isRecording ? 0.5 : 1
                                    }}
                                >
                                    <div style={{ fontWeight: 500 }}>{dur.label}</div>
                                    <div style={{ fontSize: '0.8rem', color: 'var(--text-gray)' }}>
                                        {dur.description}
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Tips */}
                    <div style={{
                        marginTop: '1rem',
                        padding: '1rem',
                        background: 'rgba(100, 181, 246, 0.1)',
                        borderRadius: '12px',
                        border: '1px solid rgba(100, 181, 246, 0.3)'
                    }}>
                        <h4 style={{ margin: '0 0 0.5rem', color: 'var(--electric-blue)' }}>
                            💡 Tips
                        </h4>
                        <ul style={{
                            margin: 0,
                            paddingLeft: '1.25rem',
                            fontSize: '0.85rem',
                            color: 'var(--text-gray)'
                        }}>
                            <li>Graba en un ambiente silencioso</li>
                            <li>Mantén un tempo consistente</li>
                            <li>La AI detectará tu estilo único</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
