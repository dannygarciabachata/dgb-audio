#!/usr/bin/env python3
"""
DGB AUDIO Engine V1.0
=====================
Generate a 16-bar multitrack arrangement
Structure: 4 bars bolero intro, 12 bars bachata verse
Focus: High-frequency transient response (güira), deep wood texture (bongo)

DGB AUDIO CORE: High-fidelity multitrack production, authentic Dominican 
Bachata & Bolero, real acoustic instruments, warm studio preamps, Neve console texture.
"""

from midiutil import MIDIFile
import os

# === DGB AUDIO CORE CONFIGURATION ===
BPM = 115
KEY = "E"  # E Major
BARS = 16
BEATS_PER_BAR = 4
TOTAL_BEATS = BARS * BEATS_PER_BAR

# Structure markers
BOLERO_END = 4      # Bars 1-4: Bolero intro
VERSE_START = 5     # Bars 5-16: Bachata verse
SOLO_START = 10     # Bars 10-14: Requinto solo
SOLO_END = 14

# MIDI note numbers for E Major scale
E_MAJOR = {
    'E2': 40, 'F#2': 42, 'G#2': 44, 'A2': 45, 'B2': 47, 'C#3': 49, 'D#3': 51,
    'E3': 52, 'F#3': 54, 'G#3': 56, 'A3': 57, 'B3': 59, 'C#4': 61, 'D#4': 63,
    'E4': 64, 'F#4': 66, 'G#4': 68, 'A4': 69, 'B4': 71, 'C#5': 73, 'D#5': 75,
    'E5': 76, 'F#5': 78, 'G#5': 80, 'A5': 81, 'B5': 83, 'C#6': 85, 'D#6': 87, 'E6': 88
}

# Chord voicings
CHORDS = {
    'E': [E_MAJOR['E3'], E_MAJOR['B3'], E_MAJOR['E4'], E_MAJOR['G#4']],
    'A': [E_MAJOR['A3'], E_MAJOR['E4'], E_MAJOR['A4']],
    'B7': [E_MAJOR['B2'], E_MAJOR['F#3'], E_MAJOR['A3'], E_MAJOR['D#4']],
    'C#m': [E_MAJOR['C#4'], E_MAJOR['E4'], E_MAJOR['G#4']],
    'F#m': [E_MAJOR['F#3'], E_MAJOR['A3'], E_MAJOR['C#4']]
}

OUTPUT_DIR = "/Users/odgmusic/DGB AUDIO V1.0/midi_16bar"


def create_requinto_16bar():
    """
    Requinto lead guitar - 16 bar arrangement
    Bars 1-4: Bolero intro (slow, emotional)
    Bars 5-9: Bachata verse accompaniment
    Bars 10-14: HIGH-ENERGY SOLO (replacing rhythm guitar feel)
    Bars 15-16: Resolution
    """
    midi = MIDIFile(1)
    track = 0
    channel = 0
    midi.addTempo(track, 0, BPM)
    midi.addProgramChange(track, channel, 0, 24)  # Nylon guitar
    
    def velocity(bar, base=50, peak=115):
        """Dynamic velocity curve"""
        if bar <= 4:
            return int(base + (bar / 4) * 20)  # Slow build
        elif bar <= 9:
            return int(70 + ((bar - 5) / 5) * 15)  # Moderate
        elif bar <= 14:
            return int(90 + ((bar - 10) / 5) * 25)  # Solo peak
        else:
            return int(peak)
    
    # === BARS 1-4: BOLERO INTRO ===
    # Deep emotional notes with space for vibrato
    bolero_notes = [
        # Bar 1
        (E_MAJOR['B4'], 0, 2, velocity(1)),
        (E_MAJOR['G#4'], 2.5, 1.5, velocity(1)),
        # Bar 2
        (E_MAJOR['E4'], 4, 2, velocity(2)),
        (E_MAJOR['F#4'], 6.5, 1.5, velocity(2)),
        # Bar 3
        (E_MAJOR['G#4'], 8, 1, velocity(3)),
        (E_MAJOR['A4'], 9, 1, velocity(3)),
        (E_MAJOR['B4'], 10, 2, velocity(3)),
        # Bar 4 - descending phrase
        (E_MAJOR['A4'], 12, 0.75, velocity(4)),
        (E_MAJOR['G#4'], 12.75, 0.75, velocity(4)),
        (E_MAJOR['F#4'], 13.5, 0.75, velocity(4)),
        (E_MAJOR['E4'], 14.25, 1.75, velocity(4)),
    ]
    
    for pitch, time, dur, vel in bolero_notes:
        midi.addNote(track, channel, pitch, time, dur, vel)
    
    # === BARS 5-9: BACHATA VERSE ACCOMPANIMENT ===
    # Melodic fills between vocal phrases
    verse_fills = [
        # Bar 5 - opening phrase
        (E_MAJOR['E4'], 16, 0.5, 72), (E_MAJOR['G#4'], 16.5, 0.5, 74),
        (E_MAJOR['B4'], 17, 1, 76),
        (E_MAJOR['A4'], 18.5, 0.5, 74), (E_MAJOR['G#4'], 19, 0.5, 72),
        # Bar 6
        (E_MAJOR['F#4'], 20, 0.5, 74), (E_MAJOR['E4'], 20.5, 1.5, 76),
        (E_MAJOR['G#4'], 22.5, 0.5, 74), (E_MAJOR['A4'], 23, 0.5, 76),
        # Bar 7
        (E_MAJOR['B4'], 24, 1, 78), (E_MAJOR['C#5'], 25, 0.5, 76),
        (E_MAJOR['B4'], 25.5, 0.5, 78), (E_MAJOR['A4'], 26, 0.5, 76),
        (E_MAJOR['G#4'], 26.5, 1.5, 80),
        # Bar 8
        (E_MAJOR['A4'], 28, 0.75, 78), (E_MAJOR['B4'], 28.75, 0.75, 80),
        (E_MAJOR['C#5'], 29.5, 0.5, 82), (E_MAJOR['D#5'], 30, 0.5, 84),
        (E_MAJOR['E5'], 30.5, 1.5, 86),
        # Bar 9 - building to solo
        (E_MAJOR['D#5'], 32, 0.5, 84), (E_MAJOR['E5'], 32.5, 0.5, 86),
        (E_MAJOR['F#5'], 33, 0.5, 88), (E_MAJOR['G#5'], 33.5, 0.5, 90),
        (E_MAJOR['A5'], 34, 0.5, 88), (E_MAJOR['G#5'], 34.5, 0.5, 86),
        (E_MAJOR['F#5'], 35, 0.5, 88), (E_MAJOR['E5'], 35.5, 0.5, 90),
    ]
    
    for pitch, time, dur, vel in verse_fills:
        midi.addNote(track, channel, pitch, time, dur, vel)
    
    # === BARS 10-14: HIGH-ENERGY REQUINTO SOLO ===
    # "Increasing BPM feel without changing global tempo"
    # Achieved through note density and syncopation
    
    solo_time = 36  # Bar 10 starts at beat 36
    
    # Bar 10 - Solo entrance (moderate tempo feel)
    bar10 = [
        (E_MAJOR['E5'], 0, 0.5, 95), (E_MAJOR['F#5'], 0.5, 0.25, 92),
        (E_MAJOR['G#5'], 0.75, 0.5, 98), (E_MAJOR['A5'], 1.25, 0.25, 95),
        (E_MAJOR['B5'], 1.5, 0.75, 100), (E_MAJOR['A5'], 2.25, 0.25, 95),
        (E_MAJOR['G#5'], 2.5, 0.25, 98), (E_MAJOR['F#5'], 2.75, 0.25, 95),
        (E_MAJOR['E5'], 3, 0.5, 100), (E_MAJOR['D#5'], 3.5, 0.5, 95),
    ]
    
    # Bar 11 - Accelerating feel (more 16ths)
    bar11 = [
        (E_MAJOR['E5'], 0, 0.25, 98), (E_MAJOR['G#5'], 0.25, 0.25, 100),
        (E_MAJOR['B5'], 0.5, 0.25, 102), (E_MAJOR['E6'], 0.75, 0.5, 105),
        (E_MAJOR['D#6'], 1.25, 0.25, 102), (E_MAJOR['C#6'], 1.5, 0.25, 100),
        (E_MAJOR['B5'], 1.75, 0.25, 102), (E_MAJOR['A5'], 2, 0.25, 100),
        (E_MAJOR['G#5'], 2.25, 0.25, 102), (E_MAJOR['F#5'], 2.5, 0.25, 100),
        (E_MAJOR['E5'], 2.75, 0.25, 105), (E_MAJOR['F#5'], 3, 0.25, 102),
        (E_MAJOR['G#5'], 3.25, 0.25, 105), (E_MAJOR['A5'], 3.5, 0.25, 102),
        (E_MAJOR['B5'], 3.75, 0.25, 108),
    ]
    
    # Bar 12 - Full speed (continuous 16ths)
    bar12_scale = [
        E_MAJOR['B5'], E_MAJOR['C#6'], E_MAJOR['D#6'], E_MAJOR['E6'],
        E_MAJOR['D#6'], E_MAJOR['C#6'], E_MAJOR['B5'], E_MAJOR['A5'],
        E_MAJOR['G#5'], E_MAJOR['A5'], E_MAJOR['B5'], E_MAJOR['C#6'],
        E_MAJOR['D#6'], E_MAJOR['E6'], E_MAJOR['D#6'], E_MAJOR['C#6'],
    ]
    
    # Bar 13 - Peak intensity (virtuoso run)
    bar13_scale = [
        E_MAJOR['B5'], E_MAJOR['A5'], E_MAJOR['G#5'], E_MAJOR['F#5'],
        E_MAJOR['E5'], E_MAJOR['D#5'], E_MAJOR['C#5'], E_MAJOR['B4'],
        E_MAJOR['C#5'], E_MAJOR['D#5'], E_MAJOR['E5'], E_MAJOR['F#5'],
        E_MAJOR['G#5'], E_MAJOR['A5'], E_MAJOR['B5'], E_MAJOR['C#6'],
    ]
    
    # Bar 14 - Landing into resolution
    bar14 = [
        (E_MAJOR['D#6'], 0, 0.25, 110), (E_MAJOR['E6'], 0.25, 0.5, 112),
        (E_MAJOR['D#6'], 0.75, 0.25, 108), (E_MAJOR['C#6'], 1, 0.25, 110),
        (E_MAJOR['B5'], 1.25, 0.75, 108), (E_MAJOR['A5'], 2, 0.5, 105),
        (E_MAJOR['G#5'], 2.5, 0.5, 102), (E_MAJOR['E5'], 3, 1, 110),
    ]
    
    # Add Bar 10
    for pitch, t, dur, vel in bar10:
        midi.addNote(track, channel, pitch, solo_time + t, dur, vel)
    
    # Add Bar 11
    for pitch, t, dur, vel in bar11:
        midi.addNote(track, channel, pitch, solo_time + 4 + t, dur, vel)
    
    # Add Bar 12 (16th notes)
    for i, pitch in enumerate(bar12_scale):
        vel = 105 + int((i / len(bar12_scale)) * 10)
        midi.addNote(track, channel, pitch, solo_time + 8 + (i * 0.25), 0.22, vel)
    
    # Add Bar 13 (16th notes)
    for i, pitch in enumerate(bar13_scale):
        vel = 108 + int((i / len(bar13_scale)) * 7)
        midi.addNote(track, channel, pitch, solo_time + 12 + (i * 0.25), 0.22, vel)
    
    # Add Bar 14
    for pitch, t, dur, vel in bar14:
        midi.addNote(track, channel, pitch, solo_time + 16 + t, dur, vel)
    
    # === BARS 15-16: RESOLUTION ===
    resolution = [
        (E_MAJOR['B4'], 56, 0.5, 100), (E_MAJOR['G#4'], 56.5, 0.5, 98),
        (E_MAJOR['E4'], 57, 1.5, 102),
        (E_MAJOR['F#4'], 58.5, 0.5, 95), (E_MAJOR['G#4'], 59, 0.5, 98),
        (E_MAJOR['A4'], 59.5, 0.5, 100),
        # Bar 16 - final landing
        (E_MAJOR['B4'], 60, 0.5, 102), (E_MAJOR['A4'], 60.5, 0.5, 98),
        (E_MAJOR['G#4'], 61, 0.5, 100), (E_MAJOR['F#4'], 61.5, 0.5, 95),
        (E_MAJOR['E4'], 62, 2, 105),  # Final tonic
    ]
    
    for pitch, time, dur, vel in resolution:
        midi.addNote(track, channel, pitch, time, dur, vel)
    
    return midi


def create_segunda_guitarra_16bar():
    """
    Segunda (rhythm) guitar - 16 bar arrangement
    Bars 1-4: Bolero strumming
    Bars 5-9: Bachata derecho pattern
    Bars 10-14: DROPS OUT during solo (or very light)
    Bars 15-16: Returns for resolution
    """
    midi = MIDIFile(1)
    track = 0
    channel = 0
    midi.addTempo(track, 0, BPM)
    midi.addProgramChange(track, channel, 0, 24)
    
    def add_chord(chord_name, start_time, duration, velocity, strum_delay=0.03):
        chord = CHORDS[chord_name]
        for i, note in enumerate(chord):
            midi.addNote(track, channel, note, start_time + (i * strum_delay), 
                        duration - (i * strum_delay), velocity)
    
    # === BARS 1-4: BOLERO INTRO ===
    bolero_chords = [
        ('E', 0, 2, 50), ('E', 2.5, 1.5, 48),
        ('A', 4, 2, 52), ('B7', 6.5, 1.5, 50),
        ('E', 8, 1.5, 55), ('C#m', 10, 1.5, 53),
        ('A', 12, 1.5, 55), ('B7', 14, 2, 58),
    ]
    
    for chord, time, dur, vel in bolero_chords:
        add_chord(chord, time, dur, vel)
    
    # === BARS 5-9: BACHATA VERSE ===
    # Full derecho pattern
    for bar in range(5, 10):
        bar_start = (bar - 1) * 4
        intensity = 65 + ((bar - 5) * 5)
        
        progression = ['E', 'A', 'B7', 'E'] if bar % 2 == 1 else ['A', 'B7', 'C#m', 'E']
        
        for beat, chord in enumerate(progression):
            add_chord(chord, bar_start + beat, 0.5, intensity)
            # Bachata upbeat hits
            add_chord(chord, bar_start + beat + 0.5, 0.25, intensity - 15)
            add_chord(chord, bar_start + beat + 0.75, 0.25, intensity - 10)
    
    # === BARS 10-14: LIGHT DURING SOLO ===
    # Very sparse - just bass notes to support
    solo_support = [
        (E_MAJOR['E2'], 36, 4, 45),   # Bar 10
        (E_MAJOR['A2'], 40, 4, 42),   # Bar 11
        (E_MAJOR['B2'], 44, 2, 45),   # Bar 12
        (E_MAJOR['E2'], 46, 2, 48),
        (E_MAJOR['A2'], 48, 2, 45),   # Bar 13
        (E_MAJOR['B2'], 50, 2, 48),
        (E_MAJOR['E2'], 52, 4, 50),   # Bar 14
    ]
    
    for note, time, dur, vel in solo_support:
        midi.addNote(track, channel, note, time, dur, vel)
    
    # === BARS 15-16: RESOLUTION ===
    for bar in range(15, 17):
        bar_start = (bar - 1) * 4
        intensity = 85
        
        for beat, chord in enumerate(['E', 'A', 'B7', 'E']):
            add_chord(chord, bar_start + beat, 0.5, intensity)
            add_chord(chord, bar_start + beat + 0.5, 0.25, intensity - 10)
            add_chord(chord, bar_start + beat + 0.75, 0.25, intensity - 5)
    
    # Final chord
    add_chord('E', 62, 2, 95)
    
    return midi


def create_bongo_16bar():
    """
    Bongo - DEEP WOOD TEXTURE focus
    Bars 1-2: Silent
    Bars 3-4: Very soft entering
    Bars 5-16: Full patterns with wood texture emphasis
    """
    midi = MIDIFile(1)
    track = 0
    channel = 9
    midi.addTempo(track, 0, BPM)
    
    BONGO_HI = 60
    BONGO_LO = 61
    BONGO_SLAP = 62  # Open slap for accent
    
    # === BARS 3-4: SOFT ENTRY ===
    for beat in range(8, 16):
        vel = 35 + ((beat - 8) * 3)
        midi.addNote(track, channel, BONGO_LO, beat, 0.4, vel)
        midi.addNote(track, channel, BONGO_HI, beat + 0.5, 0.3, vel - 8)
    
    # === BARS 5-9: BACHATA PATTERN ===
    for bar in range(5, 10):
        bar_start = (bar - 1) * 4
        base_vel = 60 + ((bar - 5) * 6)
        
        for beat in range(4):
            t = bar_start + beat
            # Full martillo pattern
            midi.addNote(track, channel, BONGO_LO, t, 0.2, base_vel + 5)
            midi.addNote(track, channel, BONGO_HI, t + 0.25, 0.15, base_vel - 10)
            midi.addNote(track, channel, BONGO_HI, t + 0.5, 0.15, base_vel - 5)
            midi.addNote(track, channel, BONGO_HI, t + 0.75, 0.15, base_vel - 8)
    
    # === BARS 10-14: SOLO SUPPORT (driving rhythm) ===
    for bar in range(10, 15):
        bar_start = (bar - 1) * 4
        intensity = 90 + ((bar - 10) * 3)
        
        for beat in range(4):
            t = bar_start + beat
            # Heavier martillo with slaps for accent
            midi.addNote(track, channel, BONGO_LO, t, 0.18, intensity)
            midi.addNote(track, channel, BONGO_HI, t + 0.25, 0.12, intensity - 15)
            midi.addNote(track, channel, BONGO_SLAP if beat == 2 else BONGO_HI, 
                        t + 0.5, 0.15, intensity - 5)
            midi.addNote(track, channel, BONGO_HI, t + 0.75, 0.12, intensity - 12)
    
    # === BARS 15-16: RESOLUTION ===
    for bar in range(15, 17):
        bar_start = (bar - 1) * 4
        for beat in range(4):
            t = bar_start + beat
            midi.addNote(track, channel, BONGO_LO, t, 0.2, 95)
            midi.addNote(track, channel, BONGO_HI, t + 0.25, 0.15, 80)
            midi.addNote(track, channel, BONGO_HI, t + 0.5, 0.15, 85)
            midi.addNote(track, channel, BONGO_HI, t + 0.75, 0.15, 82)
    
    return midi


def create_guira_16bar():
    """
    Güira - HIGH-FREQUENCY TRANSIENT RESPONSE focus
    Bars 1-4: Silent
    Bars 5-16: Building to full groove with crisp high-end
    """
    midi = MIDIFile(1)
    track = 0
    channel = 9
    midi.addTempo(track, 0, BPM)
    
    # Using higher velocity and open sounds for transient response
    GUIRA_DOWN = 69   # Cabasa (accented strike)
    GUIRA_UP = 70     # Maracas (lighter)
    GUIRA_ACCENT = 82 # Shaker for extra brightness
    
    # === BARS 5-9: BUILDING GROOVE ===
    for bar in range(5, 10):
        bar_start = (bar - 1) * 4
        intensity = 55 + ((bar - 5) * 8)
        
        for beat in range(4):
            t = bar_start + beat
            # 8th note pattern with accents
            midi.addNote(track, channel, GUIRA_DOWN, t, 0.35, intensity)
            midi.addNote(track, channel, GUIRA_UP, t + 0.5, 0.35, intensity - 12)
    
    # === BARS 10-14: FULL CRISP GROOVE (supporting solo) ===
    for bar in range(10, 15):
        bar_start = (bar - 1) * 4
        intensity = 95
        
        for beat in range(4):
            t = bar_start + beat
            # 16th note pattern for maximum energy
            midi.addNote(track, channel, GUIRA_DOWN, t, 0.18, intensity + 8)
            midi.addNote(track, channel, GUIRA_UP, t + 0.25, 0.18, intensity - 5)
            midi.addNote(track, channel, GUIRA_DOWN, t + 0.5, 0.18, intensity + 3)
            midi.addNote(track, channel, GUIRA_UP, t + 0.75, 0.18, intensity - 5)
            
            # Add accent layer for bar accents
            if beat == 0:
                midi.addNote(track, channel, GUIRA_ACCENT, t, 0.1, intensity + 10)
    
    # === BARS 15-16: RESOLUTION ===
    for bar in range(15, 17):
        bar_start = (bar - 1) * 4
        for beat in range(4):
            t = bar_start + beat
            midi.addNote(track, channel, GUIRA_DOWN, t, 0.2, 90)
            midi.addNote(track, channel, GUIRA_UP, t + 0.25, 0.2, 80)
            midi.addNote(track, channel, GUIRA_DOWN, t + 0.5, 0.2, 85)
            midi.addNote(track, channel, GUIRA_UP, t + 0.75, 0.2, 78)
    
    return midi


def main():
    """Generate all 16-bar MIDI files"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 60)
    print("🎸 DGB AUDIO ENGINE V1.0")
    print("=" * 60)
    print("CORE: High-fidelity multitrack, authentic Dominican Bachata")
    print(f"      Key: {KEY} Major | BPM: {BPM} | Bars: {BARS}")
    print("-" * 60)
    print("STRUCTURE:")
    print("  [Bars 1-4]   Bolero Intro")
    print("  [Bars 5-9]   Bachata Verse")
    print("  [Bars 10-14] Requinto Solo (high-energy)")
    print("  [Bars 15-16] Resolution")
    print("=" * 60)
    
    instruments = [
        ("requinto_16bar", create_requinto_16bar(), 
         "Lead requinto with virtuoso solo Bars 10-14"),
        ("segunda_guitarra_16bar", create_segunda_guitarra_16bar(), 
         "Rhythm guitar (drops out during solo)"),
        ("bongo_16bar", create_bongo_16bar(), 
         "Bongo - deep wood texture, martillo pattern"),
        ("guira_16bar", create_guira_16bar(), 
         "Güira - high-frequency transient response"),
    ]
    
    for name, midi, description in instruments:
        filepath = os.path.join(OUTPUT_DIR, f"{name}.mid")
        with open(filepath, 'wb') as f:
            midi.writeFile(f)
        print(f"✓ Created: {name}.mid")
        print(f"  └─ {description}")
    
    print("\n" + "=" * 60)
    print("✅ 16-bar arrangement generated successfully!")
    print(f"📁 Location: {OUTPUT_DIR}")
    print("\n📝 PRODUCTION NOTES:")
    print("  • Güira: Boost 5-10kHz for transient crispness")
    print("  • Bongo: Emphasize 200-800Hz for wood texture")
    print("  • Solo: Requinto velocity increases bars 10→14")
    print("=" * 60)


if __name__ == "__main__":
    main()
