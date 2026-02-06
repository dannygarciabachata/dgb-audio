import './globals.css';

export const metadata = {
    title: 'DGB AUDIO - La Inteligencia de la Música Tropical',
    description: 'Crea Bachata, Bolero, Salsa y más con el ADN del Maestro Danny Garcia. IA generativa de música tropical con calidad de estudio profesional.',
    keywords: 'bachata, bolero, salsa, merengue, AI music, music production, tropical music, DGB Audio',
    authors: [{ name: 'Odalis J. García' }],
    openGraph: {
        title: 'DGB AUDIO - La Inteligencia de la Música Tropical',
        description: 'Crea Bachata, Bolero, Salsa y más con el ADN del Maestro Danny Garcia.',
        type: 'website',
    },
};

export default function RootLayout({ children }) {
    return (
        <html lang="es">
            <head>
                <link rel="icon" href="/favicon.ico" />
            </head>
            <body>
                {children}
            </body>
        </html>
    );
}
