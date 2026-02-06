'use client';

import { useState, useEffect } from 'react';

// Navigation Component
function Navigation() {
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <nav className="nav" style={{
            background: scrolled ? 'rgba(13, 13, 13, 0.95)' : 'transparent',
            borderBottom: scrolled ? '1px solid rgba(212, 175, 55, 0.1)' : 'none'
        }}>
            <div className="nav-container">
                <a href="/" className="nav-logo">
                    DGB <span>AUDIO</span>
                </a>
                <ul className="nav-links">
                    <li><a href="#engine">El Motor</a></li>
                    <li><a href="#genres">Géneros</a></li>
                    <li><a href="#features">Funciones</a></li>
                    <li><a href="#vision">Visión</a></li>
                    <li><a href="#pricing">Precios</a></li>
                </ul>
                <div className="nav-cta">
                    <a href="/studio" className="btn btn-secondary" style={{ padding: '0.75rem 1.5rem' }}>
                        Iniciar Sesión
                    </a>
                    <a href="/studio" className="btn btn-primary" style={{ padding: '0.75rem 1.5rem' }}>
                        Empezar Gratis
                    </a>
                </div>
            </div>
        </nav>
    );
}

// Animated Waveform Component
function Waveform() {
    const bars = 60;

    return (
        <div className="waveform-container">
            <div className="waveform">
                {[...Array(bars)].map((_, i) => (
                    <div
                        key={i}
                        className="wave-bar"
                        style={{
                            animationDelay: `${i * 0.05}s`,
                            height: `${Math.random() * 60 + 20}%`
                        }}
                    />
                ))}
            </div>
        </div>
    );
}

// Hero Section
function Hero() {
    return (
        <section className="hero">
            <Waveform />
            <div className="hero-content">
                <span className="hero-badge">
                    🎸 Powered by AI + ADN Danny Garcia
                </span>
                <h1>
                    <span className="highlight">DGB AUDIO:</span><br />
                    La Inteligencia de la<br />
                    Música Tropical
                </h1>
                <p className="hero-subtitle">
                    Crea Bachata, Bolero, Salsa y más con el ADN del Maestro Danny Garcia.
                    Genera tracks separados con calidad de estudio profesional.
                </p>
                <div className="hero-buttons">
                    <a href="/studio" className="btn btn-primary">
                        🎵 Empezar a Crear
                    </a>
                    <a href="/download" className="btn btn-secondary">
                        ⬇️ Descargar Plugin
                    </a>
                </div>
            </div>
        </section>
    );
}

// Genre Cards Section
function GenresSection() {
    const genres = [
        { icon: '🎸', name: 'Bachata', desc: 'Requinto auténtico con mordentes y vibrato del Maestro' },
        { icon: '🎻', name: 'Bolero', desc: 'Romanticismo profundo con armonías de Trío' },
        { icon: '💃', name: 'Salsa', desc: 'Montunos de piano y tumbao en clave 2-3' },
        { icon: '🥁', name: 'Merengue', desc: 'Tambora galopante y güira dominicana' },
    ];

    return (
        <section id="genres" className="section genres">
            <div className="container">
                <h2 style={{ textAlign: 'center' }}>Géneros con <span style={{ color: 'var(--gold)' }}>Alma Real</span></h2>
                <p style={{ textAlign: 'center', maxWidth: '600px', margin: '1rem auto 0' }}>
                    No es IA genérica. Es el ADN musical de un maestro real aplicado a cada nota.
                </p>
                <div className="genres-grid">
                    {genres.map((genre, i) => (
                        <div key={i} className="genre-card">
                            <div className="genre-icon">{genre.icon}</div>
                            <h3>{genre.name}</h3>
                            <p>{genre.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// Features Section
function FeaturesSection() {
    const features = [
        {
            icon: '🎚️',
            title: 'Tracks Separados',
            desc: 'Descarga Requinto, Segunda, Bongo, Güira y Bajo como pistas individuales. Mezcla en tu DAW.'
        },
        {
            icon: '📍',
            title: 'Control por Compás',
            desc: 'Edita compás por compás. ¿No te gusta el solo del bar 10? Regenera solo esa sección.'
        },
        {
            icon: '🔌',
            title: 'Plugin Pro Tools',
            desc: 'DGB Maestro VST3/AAX se sincroniza con tu DAW. Arrastra audio directo a la línea de tiempo.'
        },
        {
            icon: '☁️',
            title: 'Cloud Sync',
            desc: 'Crea en tu móvil, edita en la web, mezcla en el estudio. Todo sincronizado.'
        },
        {
            icon: '🎤',
            title: 'Hum-to-Instrument',
            desc: 'Tararea tu melodía. La IA la convierte en un solo de requinto con el estilo del Maestro.'
        },
        {
            icon: '✨',
            title: 'Botón "DGB Touch"',
            desc: 'Aplica el sello único de Danny Garcia a cualquier ritmo con un solo click.'
        },
    ];

    return (
        <section id="features" className="section features">
            <div className="container">
                <h2 style={{ textAlign: 'center' }}>Funciones <span style={{ color: 'var(--electric-blue)' }}>Profesionales</span></h2>
                <p style={{ textAlign: 'center', maxWidth: '600px', margin: '1rem auto 0' }}>
                    Diseñado para productores que exigen calidad de estudio, no demos de baja fidelidad.
                </p>
                <div className="features-grid">
                    {features.map((feature, i) => (
                        <div key={i} className="feature-card">
                            <div className="feature-icon">{feature.icon}</div>
                            <h3>{feature.title}</h3>
                            <p>{feature.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// Vision Section
function VisionSection() {
    return (
        <section id="vision" className="section vision">
            <div className="container">
                <div className="vision-content">
                    <div className="vision-text-container">
                        <p className="vision-quote">
                            "La música no es solo matemáticas; es sentimiento, es historia y es cultura."
                        </p>
                        <p className="vision-text">
                            Como artista, productor y compositor, siempre he creído que la tecnología debe ser un puente,
                            no un muro. Tras años de trayectoria en la Bachata y el Bolero, identifiqué una necesidad
                            en la industria: herramientas que respeten nuestra esencia.
                        </p>
                        <p className="vision-text">
                            La mayoría de las inteligencias artificiales son genéricas. Entienden el ritmo, pero no
                            el swing de una güira dominicana; conocen la armonía, pero no el mordente de un requinto
                            sentido. Por eso nació <strong style={{ color: 'var(--gold)' }}>DGB AUDIO</strong>.
                        </p>
                        <a href="/about" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                            Únete a la Revolución
                        </a>
                    </div>
                    <div className="vision-image">
                        {/* Image placeholder - would be replaced with actual photo */}
                    </div>
                </div>
            </div>
        </section>
    );
}

// Pricing Section
function PricingSection() {
    const plans = [
        {
            tier: 'Free',
            name: 'Básico',
            price: '$0',
            period: '/siempre',
            features: [
                'Generación de 30 segundos',
                'Calidad estándar',
                'Solo mezcla estéreo',
                'Acceso web únicamente',
                'Con marca de agua'
            ],
            cta: 'Empezar Gratis',
            featured: false
        },
        {
            tier: 'Pro',
            name: 'DGB Artist',
            price: '$19',
            period: '/mes',
            features: [
                'Generación ilimitada',
                'Descarga de Stems separados',
                'App Móvil incluida',
                'Sin marca de agua',
                'Procesamiento prioritario',
                'Cloud Library 50GB'
            ],
            cta: 'Comenzar Pro',
            featured: true
        },
        {
            tier: 'Studio',
            name: 'Maestro',
            price: '$49',
            period: '/mes',
            features: [
                'Todo lo de Pro',
                'Plugin DGB Maestro (VST3/AAX)',
                'Licencia comercial',
                'Calidad 48kHz/24-bit',
                'Exportación MIDI',
                'Cloud Library 500GB',
                'Soporte prioritario'
            ],
            cta: 'Ir a Studio',
            featured: false
        },
    ];

    return (
        <section id="pricing" className="section pricing">
            <div className="container">
                <h2 style={{ textAlign: 'center' }}>Planes y <span style={{ color: 'var(--gold)' }}>Precios</span></h2>
                <p style={{ textAlign: 'center', maxWidth: '600px', margin: '1rem auto 0' }}>
                    Desde creadores de contenido hasta estudios profesionales. Hay un plan para ti.
                </p>
                <div className="pricing-grid">
                    {plans.map((plan, i) => (
                        <div key={i} className={`pricing-card ${plan.featured ? 'featured' : ''}`}>
                            <p className="pricing-tier">{plan.tier}</p>
                            <h3>{plan.name}</h3>
                            <p className="pricing-price">
                                {plan.price}<span>{plan.period}</span>
                            </p>
                            <ul className="pricing-features">
                                {plan.features.map((feature, j) => (
                                    <li key={j}>{feature}</li>
                                ))}
                            </ul>
                            <a href="/signup" className={`btn ${plan.featured ? 'btn-primary' : 'btn-secondary'}`} style={{ width: '100%' }}>
                                {plan.cta}
                            </a>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// Footer
function Footer() {
    return (
        <footer className="footer">
            <div className="container">
                <div className="footer-content">
                    <div className="footer-brand">
                        <h3>DGB <span>AUDIO</span></h3>
                        <p style={{ color: 'var(--text-gray)', maxWidth: '300px' }}>
                            La Inteligencia de la Música Tropical.
                            Creado con ❤️ en República Dominicana.
                        </p>
                    </div>
                    <div className="footer-links">
                        <h4>Producto</h4>
                        <ul>
                            <li><a href="/studio">The Studio</a></li>
                            <li><a href="/download">Plugin</a></li>
                            <li><a href="/pricing">Precios</a></li>
                            <li><a href="/api">API</a></li>
                        </ul>
                    </div>
                    <div className="footer-links">
                        <h4>Recursos</h4>
                        <ul>
                            <li><a href="/docs">Documentación</a></li>
                            <li><a href="/tutorials">Tutoriales</a></li>
                            <li><a href="/presets">Presets</a></li>
                            <li><a href="/blog">Blog</a></li>
                        </ul>
                    </div>
                    <div className="footer-links">
                        <h4>Compañía</h4>
                        <ul>
                            <li><a href="/about">Sobre Nosotros</a></li>
                            <li><a href="/contact">Contacto</a></li>
                            <li><a href="/terms">Términos</a></li>
                            <li><a href="/privacy">Privacidad</a></li>
                        </ul>
                    </div>
                </div>
                <div className="footer-bottom">
                    <p>© 2026 DGB AUDIO - Odalis J. García. Todos los derechos reservados.</p>
                    <div>
                        <a href="#" style={{ marginRight: '1rem' }}>🐦 Twitter</a>
                        <a href="#" style={{ marginRight: '1rem' }}>📸 Instagram</a>
                        <a href="#">🎵 YouTube</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}

// Main Page Component
export default function Home() {
    return (
        <>
            <Navigation />
            <main>
                <Hero />
                <GenresSection />
                <FeaturesSection />
                <VisionSection />
                <PricingSection />
            </main>
            <Footer />
        </>
    );
}
