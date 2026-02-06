#!/usr/bin/env python3
"""
DGB AUDIO V1.0 - Bolero-Bachata Intro Generator
8 bars, E Major, 115 BPM
Dominican Trío style arrangement
"""

from midiutil import MIDIFile
import os

# === CONFIGURATION ===
BPM = 115
KEY = "E"  # E Major
BARS = 8
BEATS_PER_BAR = 4
TOTAL_BEATS = BARS * BEATS_PER_BAR

# MIDI note numbers for E Major scale
# E3=52, F#3=54, G#3=56, A3=57, B3=59, C#4=61, D#4=63, E4=64
E_MAJOR = {
    'E2': 40, 'F#2': 42, 'G#2': 44, 'A2': 45, 'B2': 47, 'C#3': 49, 'D#3': 51,
    'E3': 52, 'F#3': 54, 'G#3': 56, 'A3': 57, 'B3': 59, 'C#4': 61, 'D#4': 63,
    'E4': 64, 'F#4': 66, 'G#4': 68, 'A4': 69, 'B4': 71, 'C#5': 73, 'D#5': 75,
    'E5': 76, 'F#5': 78, 'G#5': 80, 'A5': 81, 'B5': 83
}

# Chord voicings for E Major
CHORDS = {
    'E': [E_MAJOR['E3'], E_MAJOR['B3'], E_MAJOR['E4'], E_MAJOR['G#4']],
    'A': [E_MAJOR['A3'], E_MAJOR['E4'], E_MAJOR['A4']],
    'B7': [E_MAJOR['B2'], E_MAJOR['F#3'], E_MAJOR['A3'], E_MAJOR['D#4']],
    'C#m': [E_MAJOR['C#4'], E_MAJOR['E4'], E_MAJOR['G#4']],
    'F#m': [E_MAJOR['F#3'], E_MAJOR['A3'], E_MAJOR['C#4']]
}

OUTPUT_DIR = "/Users/odgmusic/DGB AUDIO V1.0/midi"


def create_requinto():
    """
    Requinto lead guitar - the soul of the Dominican Trío
    Bars 1-2: Long notes with deep vibrato feel (slow, emotional)
    Bars 3-4: Descending melodic phrase
    Bars 5-6: Picado technique (rapid short notes)
    Bars 7-8: Fast arpeggio resolving to E
    """
    midi = MIDIFile(1)
    track = 0
    channel = 0
    midi.addTempo(track, 0, BPM)
    midi.addProgramChange(track, channel, 0, 24)  # Nylon guitar
    
    # Velocity curve: 40% → 90% (51 → 115 in MIDI)
    def velocity(bar):
        return int(51 + (bar / 8) * 64)
    
    # === BARS 1-2: Long emotional notes (Bolero feel) ===
    # Slow, sustained notes with space for vibrato
    notes_1_2 = [
        (E_MAJOR['B4'], 0, 1.5, velocity(1)),      # B (5th) - longing
        (E_MAJOR['G#4'], 2, 1.5, velocity(1)),     # G# (3rd) - emotional
        (E_MAJOR['E4'], 4, 2, velocity(2)),        # E (root) - resolve
        (E_MAJOR['F#4'], 6.5, 1.5, velocity(2)),   # F# - tension
    ]
    
    for pitch, time, dur, vel in notes_1_2:
        midi.addNote(track, channel, pitch, time, dur, vel)
    
    # === BARS 3-4: Descending melodic phrase ===
    notes_3_4 = [
        (E_MAJOR['B4'], 8, 0.75, velocity(3)),
        (E_MAJOR['A4'], 8.75, 0.75, velocity(3)),
        (E_MAJOR['G#4'], 9.5, 1, velocity(3)),
        (E_MAJOR['F#4'], 10.5, 0.5, velocity(3)),
        (E_MAJOR['E4'], 11, 1.5, velocity(3)),
        # Bar 4
        (E_MAJOR['G#4'], 12.5, 0.75, velocity(4)),
        (E_MAJOR['F#4'], 13.25, 0.75, velocity(4)),
        (E_MAJOR['E4'], 14, 0.5, velocity(4)),
        (E_MAJOR['D#4'], 14.5, 0.5, velocity(4)),
        (E_MAJOR['C#4'], 15, 1, velocity(4)),
    ]
    
    for pitch, time, dur, vel in notes_3_4:
        midi.addNote(track, channel, pitch, time, dur, vel)
    
    # === BARS 5-6: Picado technique (rapid short notes) ===
    # 16th note runs, increasing velocity
    picado_start = 16
    picado_notes = [
        E_MAJOR['E4'], E_MAJOR['F#4'], E_MAJOR['G#4'], E_MAJOR['A4'],
        E_MAJOR['B4'], E_MAJOR['A4'], E_MAJOR['G#4'], E_MAJOR['F#4'],
        E_MAJOR['E4'], E_MAJOR['G#4'], E_MAJOR['B4'], E_MAJOR['E5'],
        E_MAJOR['D#5'], E_MAJOR['C#5'], E_MAJOR['B4'], E_MAJOR['A4'],
        # Bar 6
        E_MAJOR['G#4'], E_MAJOR['A4'], E_MAJOR['B4'], E_MAJOR['C#5'],
        E_MAJOR['D#5'], E_MAJOR['E5'], E_MAJOR['D#5'], E_MAJOR['C#5'],
        E_MAJOR['B4'], E_MAJOR['C#5'], E_MAJOR['D#5'], E_MAJOR['E5'],
        E_MAJOR['F#5'], E_MAJOR['E5'], E_MAJOR['D#5'], E_MAJOR['C#5'],
    ]
    
    for i, pitch in enumerate(picado_notes):
        time = picado_start + (i * 0.25)  # 16th notes
        vel = velocity(5) + int((i / len(picado_notes)) * 20)  # Building
        midi.addNote(track, channel, pitch, time, 0.2, min(vel, 115))
    
    # === BARS 7-8: Fast arpeggio → resolve to E (El Remate) ===
    # Rapid E Major arpeggios climbing to resolution
    arpeggio_notes = [
        # Bar 7 - ascending arpeggios
        (E_MAJOR['E4'], 24, 0.25, 100),
        (E_MAJOR['G#4'], 24.25, 0.25, 102),
        (E_MAJOR['B4'], 24.5, 0.25, 104),
        (E_MAJOR['E5'], 24.75, 0.25, 106),
        (E_MAJOR['G#5'], 25, 0.25, 108),
        (E_MAJOR['B5'], 25.25, 0.5, 110),
        # Descending
        (E_MAJOR['A5'], 25.75, 0.25, 108),
        (E_MAJOR['G#5'], 26, 0.25, 106),
        (E_MAJOR['F#5'], 26.25, 0.25, 108),
        (E_MAJOR['E5'], 26.5, 0.5, 110),
        (E_MAJOR['D#5'], 27, 0.25, 108),
        (E_MAJOR['C#5'], 27.25, 0.25, 110),
        (E_MAJOR['B4'], 27.5, 0.5, 112),
        # Bar 8 - final resolution
        (E_MAJOR['E5'], 28, 0.25, 112),
        (E_MAJOR['D#5'], 28.25, 0.25, 110),
        (E_MAJOR['C#5'], 28.5, 0.25, 112),
        (E_MAJOR['B4'], 28.75, 0.25, 114),
        (E_MAJOR['A4'], 29, 0.25, 112),
        (E_MAJOR['G#4'], 29.25, 0.25, 114),
        (E_MAJOR['F#4'], 29.5, 0.25, 112),
        (E_MAJOR['E4'], 29.75, 2.25, 115),  # Final resolve to tonic
    ]
    
    for pitch, time, dur, vel in arpeggio_notes:
        midi.addNote(track, channel, pitch, time, dur, vel)
    
    return midi


def create_segunda_guitarra():
    """
    Segunda (rhythm) guitar - harmonic foundation
    Bars 1-2: Open strumming, sustained chords
    Bars 3-4: Harmonic support
    Bars 5-6: Bachata rhythm pattern emerging
    Bars 7-8: Full Bachata derecho strum
    """
    midi = MIDIFile(1)
    track = 0
    channel = 0
    midi.addTempo(track, 0, BPM)
    midi.addProgramChange(track, channel, 0, 24)  # Nylon guitar
    
    def add_chord(chord_name, start_time, duration, velocity, strum_delay=0.03):
        """Add chord with slight strum effect"""
        chord = CHORDS[chord_name]
        for i, note in enumerate(chord):
            midi.addNote(track, channel, note, start_time + (i * strum_delay), 
                        duration - (i * strum_delay), velocity)
    
    # === BARS 1-2: Bolero open strumming ===
    add_chord('E', 0, 2, 50)      # Bar 1, beat 1
    add_chord('E', 2, 2, 48)      # Bar 1, beat 3
    add_chord('A', 4, 2, 52)      # Bar 2, beat 1
    add_chord('B7', 6, 2, 50)     # Bar 2, beat 3
    
    # === BARS 3-4: Harmonic support ===
    add_chord('E', 8, 1.5, 55)
    add_chord('C#m', 9.5, 1.5, 53)
    add_chord('A', 11, 1, 55)
    add_chord('A', 12, 1.5, 58)
    add_chord('B7', 13.5, 1.5, 56)
    add_chord('E', 15, 1, 58)
    
    # === BARS 5-6: Bachata rhythm emerging ===
    # Bachata "derecho" pattern: bass-chord-chord-chord
    bachata_pattern = [
        ('E', 16, 0.5, 65), ('E', 16.75, 0.25, 60), ('E', 17.25, 0.25, 62), ('E', 17.75, 0.25, 64),
        ('A', 18, 0.5, 68), ('A', 18.75, 0.25, 63), ('A', 19.25, 0.25, 65), ('A', 19.75, 0.25, 67),
        ('B7', 20, 0.5, 70), ('B7', 20.75, 0.25, 65), ('B7', 21.25, 0.25, 68), ('B7', 21.75, 0.25, 70),
        ('E', 22, 0.5, 72), ('E', 22.75, 0.25, 67), ('E', 23.25, 0.25, 70), ('E', 23.75, 0.25, 72),
    ]
    
    for chord, time, dur, vel in bachata_pattern:
        add_chord(chord, time, dur, vel)
    
    # === BARS 7-8: Full Bachata derecho ===
    full_bachata = [
        ('E', 24, 0.5, 85), ('E', 24.5, 0.25, 75), ('E', 25, 0.25, 78), ('E', 25.5, 0.25, 80),
        ('A', 26, 0.5, 88), ('A', 26.5, 0.25, 78), ('A', 27, 0.25, 82), ('A', 27.5, 0.25, 85),
        ('B7', 28, 0.5, 90), ('B7', 28.5, 0.25, 80), ('B7', 29, 0.25, 85), ('B7', 29.5, 0.25, 88),
        ('E', 30, 2, 95),  # Final sustain
    ]
    
    for chord, time, dur, vel in full_bachata:
        add_chord(chord, time, dur, vel)
    
    return midi


def create_bongo():
    """
    Bongo - entering at bar 3, martillo pattern by bar 7
    Uses standard bongo mapping (high=60, low=61, slap=62)
    """
    midi = MIDIFile(1)
    track = 0
    channel = 9  # Drum channel
    midi.addTempo(track, 0, BPM)
    
    # Bongo sounds (General MIDI percussion)
    BONGO_HI = 60   # High bongo
    BONGO_LO = 61   # Low bongo
    
    # === BARS 3-4: Soft time-keeping ===
    soft_pattern = [
        # Bar 3
        (BONGO_LO, 8, 35), (BONGO_HI, 8.5, 30), 
        (BONGO_LO, 9, 38), (BONGO_HI, 9.5, 32),
        (BONGO_LO, 10, 35), (BONGO_HI, 10.5, 30),
        (BONGO_LO, 11, 40), (BONGO_HI, 11.5, 35),
        # Bar 4
        (BONGO_LO, 12, 38), (BONGO_HI, 12.5, 33),
        (BONGO_LO, 13, 40), (BONGO_HI, 13.5, 35),
        (BONGO_LO, 14, 42), (BONGO_HI, 14.5, 38),
        (BONGO_LO, 15, 45), (BONGO_HI, 15.5, 40),
    ]
    
    for note, time, vel in soft_pattern:
        midi.addNote(track, channel, note, time, 0.25, vel)
    
    # === BARS 5-6: Building intensity ===
    building_pattern = [
        # Bar 5 - more presence
        (BONGO_LO, 16, 55), (BONGO_HI, 16.5, 48), (BONGO_HI, 16.75, 45),
        (BONGO_LO, 17, 58), (BONGO_HI, 17.5, 50), (BONGO_HI, 17.75, 48),
        (BONGO_LO, 18, 60), (BONGO_HI, 18.5, 52), (BONGO_HI, 18.75, 50),
        (BONGO_LO, 19, 62), (BONGO_HI, 19.5, 55), (BONGO_HI, 19.75, 52),
        # Bar 6 - approaching martillo
        (BONGO_LO, 20, 65), (BONGO_HI, 20.5, 58), (BONGO_HI, 20.75, 55),
        (BONGO_LO, 21, 68), (BONGO_HI, 21.5, 60), (BONGO_HI, 21.75, 58),
        (BONGO_LO, 22, 70), (BONGO_HI, 22.5, 62), (BONGO_HI, 22.75, 60),
        (BONGO_LO, 23, 72), (BONGO_HI, 23.5, 65), (BONGO_HI, 23.75, 62),
    ]
    
    for note, time, vel in building_pattern:
        midi.addNote(track, channel, note, time, 0.2, vel)
    
    # === BARS 7-8: Full Martillo pattern ===
    # Classic bachata bongo martillo
    martillo = [
        # Bar 7
        (BONGO_LO, 24, 90), (BONGO_HI, 24.25, 70), (BONGO_HI, 24.5, 75), (BONGO_HI, 24.75, 72),
        (BONGO_LO, 25, 92), (BONGO_HI, 25.25, 72), (BONGO_HI, 25.5, 78), (BONGO_HI, 25.75, 75),
        (BONGO_LO, 26, 90), (BONGO_HI, 26.25, 70), (BONGO_HI, 26.5, 75), (BONGO_HI, 26.75, 72),
        (BONGO_LO, 27, 95), (BONGO_HI, 27.25, 75), (BONGO_HI, 27.5, 80), (BONGO_HI, 27.75, 78),
        # Bar 8
        (BONGO_LO, 28, 95), (BONGO_HI, 28.25, 75), (BONGO_HI, 28.5, 80), (BONGO_HI, 28.75, 78),
        (BONGO_LO, 29, 98), (BONGO_HI, 29.25, 78), (BONGO_HI, 29.5, 82), (BONGO_HI, 29.75, 80),
        (BONGO_LO, 30, 100), (BONGO_HI, 30.25, 80), (BONGO_HI, 30.5, 85), (BONGO_HI, 30.75, 82),
        (BONGO_LO, 31, 105), (BONGO_HI, 31.5, 85), (BONGO_LO, 31.75, 100),  # Final hit
    ]
    
    for note, time, vel in martillo:
        midi.addNote(track, channel, note, time, 0.15, vel)
    
    return midi


def create_guira():
    """
    Güira (metal scraper) - entering at bar 5, full groove by bar 7
    Uses shaker/cabasa sounds as approximation
    """
    midi = MIDIFile(1)
    track = 0
    channel = 9  # Drum channel
    midi.addTempo(track, 0, BPM)
    
    # Güira approximation (using cabasa)
    GUIRA_DOWN = 69  # Cabasa
    GUIRA_UP = 70    # Maracas (for upstroke feel)
    
    # === BARS 5-6: Soft constant scrape ===
    for beat in range(16, 24):  # Bars 5-6
        velocity_base = 45 + ((beat - 16) * 3)  # Building from 45 to 69
        # Constant 8th note scrape pattern
        midi.addNote(track, channel, GUIRA_DOWN, beat, 0.4, velocity_base)
        midi.addNote(track, channel, GUIRA_UP, beat + 0.5, 0.4, velocity_base - 10)
    
    # === BARS 7-8: Full Bachata güira groove ===
    # Crisp 16th note pattern with accents
    for beat in range(24, 32):  # Bars 7-8
        base_vel = 85
        # 16th note pattern: DOWN-up-DOWN-up
        midi.addNote(track, channel, GUIRA_DOWN, beat, 0.2, base_vel + 10)      # 1
        midi.addNote(track, channel, GUIRA_UP, beat + 0.25, 0.2, base_vel - 5)  # e
        midi.addNote(track, channel, GUIRA_DOWN, beat + 0.5, 0.2, base_vel + 5) # &
        midi.addNote(track, channel, GUIRA_UP, beat + 0.75, 0.2, base_vel - 5)  # a
    
    return midi


def main():
    """Generate all MIDI files"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("🎸 DGB AUDIO V1.0 - Bolero-Bachata Intro Generator")
    print("=" * 50)
    print(f"Key: E Major | BPM: {BPM} | Bars: {BARS}")
    print("=" * 50)
    
    # Generate each instrument
    instruments = [
        ("requinto", create_requinto(), "Lead requinto guitar with vibrato → picado → arpeggio"),
        ("segunda_guitarra", create_segunda_guitarra(), "Rhythm guitar with Bachata derecho pattern"),
        ("bongo", create_bongo(), "Bongo with martillo pattern"),
        ("guira", create_guira(), "Güira metallic scraper groove"),
    ]
    
    for name, midi, description in instruments:
        filepath = os.path.join(OUTPUT_DIR, f"{name}.mid")
        with open(filepath, 'wb') as f:
            midi.writeFile(f)
        print(f"✓ Created: {name}.mid")
        print(f"  └─ {description}")
    
    print("\n" + "=" * 50)
    print("✅ All MIDI files generated successfully!")
    print(f"📁 Location: {OUTPUT_DIR}")
    print("\n🎧 Import these into your DAW and use high-quality")
    print("   nylon guitar VSTs for authentic Dominican Trío sound.")


if __name__ == "__main__":
    main()
