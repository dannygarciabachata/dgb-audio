# DGB AUDIO - Platform Requirements
## Version 1.0 | Colores del Amor Launch

---

## 🎯 Product Vision

DGB AUDIO is a multi-platform music production ecosystem combining AI-powered generation with authentic Dominican musical styles (Bachata, Salsa, Merengue) and versatile global genres.

---

## 🌐 1. WEB PORTAL: DGB-AUDIO.COM

### Design System
- **Theme**: Dark, elegant (matte black + gold or neon blue accents)
- **Vibe**: "Expensive Recording Studio" meets "Cutting-Edge Technology"
- **Typography**: Modern Sans-Serif (tech aesthetic)

### Main Sections

#### 1.1 The Studio (Web App)
| Feature | Description |
|---------|-------------|
| Text Input | "Escribe tu idea musical" prompt box |
| Mode Selector | **Simple** (quick generation) / **Pro** (per-track control) |
| Visualizer | Real-time waveform generation |
| Genre Selector | Bachata (DGB), Salsa, Merengue, Generic |

#### 1.2 The Library
- Cloud storage for all user creations
- Project history and versioning
- Share/collaborate features

#### 1.3 Download Center
- Plugin installers (VST3, AAX, AU)
- Compatible DAWs: Pro Tools, Logic Pro, Ableton, FL Studio

---

## 🎛️ 2. DAW PLUGIN: DGB Maestro VST/AAX

### Core Features
- **DAW Sync**: Locks to host BPM and timeline
- **Multi-Output Routing**:
  ```
  Out 1: Requinto (Audio)
  Out 2: Segunda (Audio)
  Out 3: Percussion (MIDI/Audio)
  Out 4: Bass (Audio)
  ```
- **In-Fill Mode**: Select timeline region → AI fills with musical content

### Intelligence Modes
| Mode | Optimization |
|------|--------------|
| **Maestro (DGB)** | Maximum quality for guitars and bachata |
| **Versátil** | Tropical: Salsa, Merengue |
| **Global** | Pop, Rock, Ballads, Synth |

### Special Buttons
- **"Sabor"**: Add micro-timing variations for human feel
- **"Trío"**: Auto-generate 3-part harmonies (guitars/vocals)

---

## 📱 3. MOBILE APP: DGB Creator

### Core Features
- **Hum-to-Song**: Sing/hum melody → full arrangement returned
- **Cloud Sync**: Creations appear in Pro Tools automatically
- **Quick Ideas**: Capture inspiration on-the-go

### Platforms
- iOS (iPhone/iPad)
- Android

---

## 🏗️ 4. TECH STACK

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend Web** | React.js / Next.js | Fast, modern interface |
| **Backend / AI** | Python (FastAPI) + Antigravity API | Audio processing brain |
| **Mobile App** | Flutter / React Native | Cross-platform iOS/Android |
| **DAW Plugin** | C++ / JUCE Framework | Pro Tools, Logic compatibility |
| **Database** | PostgreSQL + Redis | User data, session cache |
| **Cloud Storage** | AWS S3 / CloudFront | Audio file delivery |
| **Auth** | Auth0 / Firebase Auth | User accounts |

---

## 💰 5. PRICING TIERS

### Free Tier
- [ ] Generate up to 30 seconds per creation
- [ ] Maximum 5 creations per day
- [ ] Stereo mixdown only (no stems)
- [ ] Watermarked audio
- [ ] Web app only

### Pro Tier ($XX/month)
- [ ] Unlimited generation length
- [ ] Unlimited creations
- [ ] **Download separated stems/tracks**
- [ ] **DAW Plugin access (DGB Maestro)**
- [ ] Priority generation queue
- [ ] Cloud library (50GB)
- [ ] Mobile app access

### Studio Tier ($XX/month)
- [ ] Everything in Pro
- [ ] **Commercial usage rights**
- [ ] **MIDI export**
- [ ] API access for custom integrations
- [ ] Cloud library (500GB)
- [ ] Priority support

---

## 🎨 6. BRANDING ASSETS NEEDED

### Logo Concept
- Sound wave combined with stylized requinto guitar silhouette
- Works in dark and light modes
- Scalable (favicon to billboard)

### Mockups Required
- [ ] Plugin inside Pro Tools session (colorful tracks)
- [ ] Web app "Studio" interface
- [ ] Mobile app screens
- [ ] Marketing hero images

### Color Palette
```
Primary:    #0D0D0D (Matte Black)
Secondary:  #D4AF37 (Gold) or #00D4FF (Neon Blue)
Accent:     #1A1A2E (Deep Blue-Black)
Text:       #FFFFFF (White), #B0B0B0 (Gray)
Success:    #00FF88 (Neon Green)
```

---

## 📅 7. LAUNCH ROADMAP

### Phase 1: "Colores del Amor" Launch (Feb 14)
- [x] MIDI generation engine (multi-genre)
- [ ] Basic web interface prototype
- [ ] Marketing materials

### Phase 2: Beta Web App (Q2)
- [ ] Full web app with user accounts
- [ ] Cloud storage integration
- [ ] Basic Pro tier

### Phase 3: Plugin Release (Q3)
- [ ] DGB Maestro VST3/AAX
- [ ] Pro tier with plugin access
- [ ] Studio tier launch

### Phase 4: Mobile App (Q4)
- [ ] DGB Creator iOS/Android
- [ ] Hum-to-Song feature
- [ ] Full ecosystem sync

---

## 📋 IMMEDIATE NEXT STEPS

1. [ ] **Week 1**: Record "Stems Maestros" (guitars and percussion solo)
2. [ ] **Week 2**: Upload recordings to Antigravity as "Audio Reference"
3. [ ] **Week 3**: Generate individual tracks for "Colores del Amor"
4. [ ] **Week 4**: Mix AI tracks with real vocals in Pro Tools
5. [ ] **Define pricing**: Finalize Free/Pro/Studio tier limits

---

*Document created: 2026-02-05*
*DGB AUDIO V1.0 → V2.0 Multi-Genre Engine Complete*
