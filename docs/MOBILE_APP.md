# DGB CREATOR - Mobile App Design

## Visual Identity
- **Theme**: Dark Mode native (saves battery, studio-friendly)
- **Processing Animation**: 3D guitar string vibrating → transforms to code
- **UI Sounds**: Small E Major requinto chord on confirmations (Danny's signature)

---

## Screen 1: Dashboard (Home)

### Layout
```
┌─────────────────────────────────────┐
│         Logo: DGB AUDIO             │
├─────────────────────────────────────┤
│                                     │
│   "Hola, Maestro.                   │
│    ¿Qué vamos a crear hoy?"         │
│                                     │
├─────────────────────────────────────┤
│                                     │
│         ┌─────────────┐             │
│         │             │             │
│         │  🎤 MIC     │  ← Big      │
│         │  BUTTON     │    central  │
│         │             │    button   │
│         └─────────────┘             │
│                                     │
│   "Toca para tararear tu idea"      │
│                                     │
├─────────────────────────────────────┤
│   RECIENTES                         │
│   ┌────┐ ┌────┐ ┌────┐             │
│   │ 🎵 │ │ 🎵 │ │ 🎵 │  Horizontal │
│   │Proj│ │Proj│ │Proj│  scroll     │
│   └────┘ └────┘ └────┘             │
└─────────────────────────────────────┘
```

---

## Screen 2: Generator (Modo Estudio)

### Genre Selector (Horizontal Scroll)
```
  [🎸 Bachata] [💃 Salsa] [🥁 Merengue] [🎻 Bolero] [🎹 Pop]
```

### Prompt Box
```
┌─────────────────────────────────────┐
│ "Hazme un mambo de bachatarengue    │
│  con un solo de requinto agresivo"  │
└─────────────────────────────────────┘
```

### Session Controls
```
BPM:        ○────────●──────○  [120]
            80              180

Key:        [Circle of Fifths visual picker]
            Currently: E Major
```

### Action Buttons
- [Generate] - Primary gold button
- [Load Voice] - Upload audio reference

---

## Screen 3: Mixer (Multitrack View)

### Track Visualization
```
┌─────────────────────────────────────┐
│ 🎸 Requinto                    S M  │
│ ═══════▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄════════  │
├─────────────────────────────────────┤
│ 🎸 Segunda                     S M  │
│ ═══▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄═════  │
├─────────────────────────────────────┤
│ 🥁 Percusión                   S M  │
│ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄  │
├─────────────────────────────────────┤
│ 🎻 Bass                        S M  │
│ ═══▄▄▄▄═══▄▄▄▄═══▄▄▄▄═══▄▄▄▄════  │
└─────────────────────────────────────┘

S = Solo button
M = Mute button

[Swipe left on track] → [🔄 Regenerar]
```

### Transport Controls
```
    ◀◀     ▶/⏸     ⏹     ▶▶
```

---

## Screen 4: Cloud & Sync

### DAW Connection
```
┌─────────────────────────────────────┐
│  ☁️  CLOUD SYNC                     │
├─────────────────────────────────────┤
│                                     │
│  Pro Tools Connection: ● Connected  │
│  Last sync: 2 minutes ago           │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   📤 SEND TO PRO TOOLS      │   │
│  └─────────────────────────────┘   │
│                                     │
├─────────────────────────────────────┤
│  EXPORT OPTIONS                     │
│                                     │
│  [WAV 48kHz]  [MP3 320k]  [MIDI]    │
│                                     │
└─────────────────────────────────────┘
```

---

## Exclusive Features: "Modo Maestro"

### 1. Hum-to-Instrument
- User hums melody
- Select target instrument: [Requinto] [Segunda] [Piano] [Sax]
- AI translates voice → instrument with Danny's articulations

### 2. DGB Radio
- Community feed of best creations
- Inspiration mode
- Like/save favorites

### 3. AI Lyric Assistant
- Genre-aware lyric generation
- Styles:
  - Bachata Cortavenas (heartbreak)
  - Bolero Romántico (love)
  - Salsa Callejera (party)
  - Merengue Festivo (celebration)

---

## Technical Notes

### Platform
- Flutter or React Native
- iOS & Android support

### Offline Mode
- Cache last 3 projects
- Queue generation for when online

### Push Notifications
- "Your track is ready!"
- "New preset from Danny Garcia"
- "Sync complete with Pro Tools"
