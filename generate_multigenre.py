#!/usr/bin/env python3
"""
DGB AUDIO V2.0 - Multi-Genre MIDI Generator
============================================

Generates MIDI files for:
- Salsa (tumbao-based, clave 2-3/3-2)
- Merengue (tambora-led, galopante)  
- Bachata (requinto-driven, romántico)
- Generic Pop (standard 4/4)

Usage:
    python generate_multigenre.py --genre salsa --bars 16 --key C --bpm 180
    python generate_multigenre.py --genre merengue --bars 8 --bpm 170
    python generate_multigenre.py --genre bachata --bars 16 --key E --bpm 115
"""

import argparse
import os
from midiutil import MIDIFile
from dgb_engine import (
    DGBAudioEngine, Genre, IntelligenceMode, 
    GENRE_CONFIGS, INSTRUMENTS, RHYTHM_PATTERNS
)

OUTPUT_BASE = "/Users/odgmusic/DGB AUDIO V1.0/midi_output"


# ============================================================================
# SCALE & CHORD DEFINITIONS
# ============================================================================

def get_scale(root: str, scale_type: str = "major") -> dict:
    """Generate scale notes for any root"""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    root_idx = notes.index(root.upper().replace('b', '#'))  # Simplify flats
    
    # Intervals from root
    intervals = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
    }
    
    scale = {}
    for octave in range(2, 7):
        for i, interval in enumerate(intervals[scale_type]):
            note_idx = (root_idx + interval) % 12
            note_name = notes[note_idx]
            midi_num = 24 + (octave * 12) + note_idx
            scale[f"{note_name}{octave}"] = midi_num
            # Also store by degree
            scale[f"deg{i+1}_oct{octave}"] = midi_num
    
    return scale


def get_chord(root: str, chord_type: str, octave: int = 3) -> list:
    """Generate chord notes"""
    scale = get_scale(root, "major" if "m" not in chord_type else "minor")
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    root_idx = notes.index(root.upper())
    root_midi = 24 + (octave * 12) + root_idx
    
    if chord_type == "maj" or chord_type == "":
        return [root_midi, root_midi + 4, root_midi + 7]
    elif chord_type == "m" or chord_type == "min":
        return [root_midi, root_midi + 3, root_midi + 7]
    elif chord_type == "7":
        return [root_midi, root_midi + 4, root_midi + 7, root_midi + 10]
    elif chord_type == "m7":
        return [root_midi, root_midi + 3, root_midi + 7, root_midi + 10]
    elif chord_type == "maj7":
        return [root_midi, root_midi + 4, root_midi + 7, root_midi + 11]
    else:
        return [root_midi, root_midi + 4, root_midi + 7]


# ============================================================================
# SALSA GENERATOR
# ============================================================================

def generate_salsa(bars: int, key: str, bpm: int, clave: str = "2-3") -> dict:
    """Generate Salsa multitrack MIDI"""
    
    output_dir = os.path.join(OUTPUT_BASE, "salsa")
    os.makedirs(output_dir, exist_ok=True)
    
    scale = get_scale(key, "minor")  # Salsa often in minor
    
    # Chord progression (typical son montuno)
    # i - IV - V - i
    progressions = {
        "C": ["Cm", "F", "G7", "Cm"],
        "D": ["Dm", "G", "A7", "Dm"],
        "E": ["Em", "A", "B7", "Em"],
        "A": ["Am", "D", "E7", "Am"],
    }
    chords = progressions.get(key, progressions["C"])
    
    tracks = {}
    
    # === PIANO MONTUNO ===
    piano = MIDIFile(1)
    piano.addTempo(0, 0, bpm)
    piano.addProgramChange(0, 0, 0, 0)  # Acoustic Piano
    
    for bar in range(bars):
        bar_start = bar * 4
        chord_name = chords[bar % len(chords)]
        chord_root = chord_name.replace("m", "").replace("7", "")
        chord_type = "m" if "m" in chord_name else ("7" if "7" in chord_name else "")
        chord_notes = get_chord(chord_root, chord_type, 4)
        
        # Montuno pattern (syncopated)
        montuno_pattern = [
            (0, 80), (0.5, 90), (1, 75), (1.5, 85),
            (2, 90), (2.5, 80), (3, 85), (3.5, 90)
        ]
        
        for offset, vel in montuno_pattern:
            for note in chord_notes[:3]:  # Use top 3 notes
                piano.addNote(0, 0, note, bar_start + offset, 0.3, vel)
    
    tracks["piano_montuno"] = piano
    
    # === BASS TUMBAO ===
    bass = MIDIFile(1)
    bass.addTempo(0, 0, bpm)
    bass.addProgramChange(0, 0, 0, 32)  # Acoustic Bass
    
    for bar in range(bars):
        bar_start = bar * 4
        chord_name = chords[bar % len(chords)]
        root = chord_name.replace("m", "").replace("7", "")
        root_note = get_chord(root, "", 2)[0]  # Bass octave
        fifth = root_note + 7
        
        # Classic tumbao with anticipated bass
        bass.addNote(0, 0, root_note, bar_start + 0.5, 0.4, 95)  # & of 1
        bass.addNote(0, 0, fifth, bar_start + 2, 0.4, 85)        # 3
        bass.addNote(0, 0, root_note, bar_start + 3.5, 0.4, 95)  # & of 4
    
    tracks["bass_tumbao"] = bass
    
    # === CONGAS ===
    congas = MIDIFile(1)
    congas.addTempo(0, 0, bpm)
    
    CONGA_LOW = 63   # Low conga
    CONGA_HI = 62    # High conga
    CONGA_SLAP = 64  # Slap
    
    for bar in range(bars):
        bar_start = bar * 4
        intensity = 70 + ((bar / bars) * 25)
        
        # Standard tumbao pattern
        pattern = [
            (CONGA_HI, 0, 0.3, 0),
            (CONGA_LOW, 0.5, 0.3, -10),
            (CONGA_SLAP, 1, 0.2, 10),
            (CONGA_LOW, 1.5, 0.3, -5),
            (CONGA_HI, 2, 0.3, 0),
            (CONGA_LOW, 2.5, 0.3, -10),
            (CONGA_LOW, 3, 0.3, 5),
            (CONGA_SLAP, 3.5, 0.2, 10),
        ]
        
        for note, offset, dur, vel_mod in pattern:
            congas.addNote(0, 9, note, bar_start + offset, dur, int(intensity + vel_mod))
    
    tracks["congas"] = congas
    
    # === CLAVE ===
    clave_midi = MIDIFile(1)
    clave_midi.addTempo(0, 0, bpm)
    
    CLAVE = 75  # Claves
    
    # 2-3 or 3-2 clave pattern (2 bar pattern)
    if clave == "2-3":
        clave_pattern = [
            (0, 0), (1, 0),           # Bar 1: 2 hits
            (0, 1), (0.75, 1), (1.5, 1)  # Bar 2: 3 hits
        ]
    else:  # 3-2
        clave_pattern = [
            (0, 0), (0.75, 0), (1.5, 0),  # Bar 1: 3 hits
            (0, 1), (1, 1)                 # Bar 2: 2 hits
        ]
    
    for bar in range(0, bars, 2):
        for offset, bar_offset in clave_pattern:
            if bar + bar_offset < bars:
                clave_midi.addNote(0, 9, CLAVE, (bar + bar_offset) * 4 + offset * 2, 0.2, 90)
    
    tracks["clave"] = clave_midi
    
    # === TIMBALES ===
    timbales = MIDIFile(1)
    timbales.addTempo(0, 0, bpm)
    
    TIMBAL_HI = 65  # High timbale
    TIMBAL_LO = 66  # Low timbale
    COWBELL = 56    # Cowbell (campana)
    
    for bar in range(bars):
        bar_start = bar * 4
        
        # Cascara pattern on shell
        for beat in range(8):
            t = bar_start + (beat * 0.5)
            vel = 80 if beat % 2 == 0 else 70
            timbales.addNote(0, 9, COWBELL, t, 0.2, vel)
    
    tracks["timbales"] = timbales
    
    # Save all tracks
    for name, midi in tracks.items():
        filepath = os.path.join(output_dir, f"{name}.mid")
        with open(filepath, 'wb') as f:
            midi.writeFile(f)
        print(f"  ✓ {name}.mid")
    
    return {"output_dir": output_dir, "tracks": list(tracks.keys())}


# ============================================================================
# MERENGUE GENERATOR
# ============================================================================

def generate_merengue(bars: int, key: str, bpm: int) -> dict:
    """Generate Merengue multitrack MIDI"""
    
    output_dir = os.path.join(OUTPUT_BASE, "merengue")
    os.makedirs(output_dir, exist_ok=True)
    
    scale = get_scale(key, "major")
    
    # Merengue chord progression
    progressions = {
        "C": ["C", "G", "Am", "F"],
        "D": ["D", "A", "Bm", "G"],
        "E": ["E", "B", "C#m", "A"],
        "G": ["G", "D", "Em", "C"],
    }
    chords = progressions.get(key, progressions["C"])
    
    tracks = {}
    
    # === TAMBORA ===
    tambora = MIDIFile(1)
    tambora.addTempo(0, 0, bpm)
    
    TAMBORA_OPEN = 41   # Low floor tom (approximation)
    TAMBORA_MUTED = 43  # High floor tom
    TAMBORA_RIM = 37    # Side stick
    
    for bar in range(bars):
        bar_start = bar * 4
        intensity = 85 + ((bar / bars) * 20)
        
        # Galloping merengue pattern (fast 8ths)
        for beat in range(8):
            t = bar_start + (beat * 0.5)
            if beat % 2 == 0:
                # Open hit on downbeats
                tambora.addNote(0, 9, TAMBORA_OPEN, t, 0.2, int(intensity + 10))
            else:
                # Muted/rim on upbeats
                tambora.addNote(0, 9, TAMBORA_MUTED, t, 0.2, int(intensity - 10))
            
            # Add rim accents
            if beat == 4:
                tambora.addNote(0, 9, TAMBORA_RIM, t, 0.1, int(intensity + 5))
    
    tracks["tambora"] = tambora
    
    # === GÜIRA (Fast Scrape) ===
    guira = MIDIFile(1)
    guira.addTempo(0, 0, bpm)
    
    GUIRA_DOWN = 69  # Cabasa
    GUIRA_UP = 70    # Maracas
    
    for bar in range(bars):
        bar_start = bar * 4
        intensity = 90
        
        # Continuous 16th note scrape
        for beat in range(16):
            t = bar_start + (beat * 0.25)
            note = GUIRA_DOWN if beat % 2 == 0 else GUIRA_UP
            vel = intensity + (5 if beat % 4 == 0 else -5)
            guira.addNote(0, 9, note, t, 0.18, vel)
    
    tracks["guira"] = guira
    
    # === SAXOPHONE SECTION ===
    saxos = MIDIFile(1)
    saxos.addTempo(0, 0, bpm)
    saxos.addProgramChange(0, 0, 0, 65)  # Alto Sax
    
    for bar in range(bars):
        bar_start = bar * 4
        chord_name = chords[bar % len(chords)]
        chord_root = chord_name.replace("m", "")
        chord_type = "m" if "m" in chord_name else ""
        chord_notes = get_chord(chord_root, chord_type, 4)
        
        # Mambo-style horn hits
        if bar % 2 == 0:
            # Rhythmic stabs
            saxos.addNote(0, 0, chord_notes[0] + 12, bar_start, 0.3, 95)
            saxos.addNote(0, 0, chord_notes[1] + 12, bar_start, 0.3, 90)
            saxos.addNote(0, 0, chord_notes[0] + 12, bar_start + 1.5, 0.3, 90)
            saxos.addNote(0, 0, chord_notes[2] + 12, bar_start + 1.5, 0.3, 85)
            saxos.addNote(0, 0, chord_notes[0] + 12, bar_start + 3, 0.3, 95)
        else:
            # Melodic fill
            for i, offset in enumerate([0, 0.5, 1, 1.5]):
                note = chord_notes[(i % 3)] + 12
                saxos.addNote(0, 0, note, bar_start + offset, 0.4, 85 + (i * 3))
    
    tracks["saxos"] = saxos
    
    # === PIANO ===
    piano = MIDIFile(1)
    piano.addTempo(0, 0, bpm)
    piano.addProgramChange(0, 0, 0, 0)
    
    for bar in range(bars):
        bar_start = bar * 4
        chord_name = chords[bar % len(chords)]
        chord_root = chord_name.replace("m", "")
        chord_type = "m" if "m" in chord_name else ""
        chord_notes = get_chord(chord_root, chord_type, 4)
        
        # Fast guajeo pattern
        for beat in range(8):
            t = bar_start + (beat * 0.5)
            for note in chord_notes:
                piano.addNote(0, 0, note, t, 0.3, 80 if beat % 2 == 0 else 70)
    
    tracks["piano"] = piano
    
    # === BASS ===
    bass = MIDIFile(1)
    bass.addTempo(0, 0, bpm)
    bass.addProgramChange(0, 0, 0, 33)  # Electric bass
    
    for bar in range(bars):
        bar_start = bar * 4
        chord_name = chords[bar % len(chords)]
        root = chord_name.replace("m", "")
        root_note = get_chord(root, "", 2)[0]
        
        # Driving bass line
        bass.addNote(0, 0, root_note, bar_start, 0.4, 95)
        bass.addNote(0, 0, root_note, bar_start + 1, 0.4, 90)
        bass.addNote(0, 0, root_note + 5, bar_start + 2, 0.4, 85)  # 4th
        bass.addNote(0, 0, root_note + 7, bar_start + 3, 0.4, 90)  # 5th
    
    tracks["bass"] = bass
    
    # Save all tracks
    for name, midi in tracks.items():
        filepath = os.path.join(output_dir, f"{name}.mid")
        with open(filepath, 'wb') as f:
            midi.writeFile(f)
        print(f"  ✓ {name}.mid")
    
    return {"output_dir": output_dir, "tracks": list(tracks.keys())}


# ============================================================================
# GENERIC POP GENERATOR
# ============================================================================

def generate_generic(bars: int, key: str, bpm: int) -> dict:
    """Generate Generic Pop/Rock multitrack MIDI"""
    
    output_dir = os.path.join(OUTPUT_BASE, "generic")
    os.makedirs(output_dir, exist_ok=True)
    
    # Standard pop progression
    progressions = {
        "C": ["C", "G", "Am", "F"],
        "D": ["D", "A", "Bm", "G"],
        "E": ["E", "B", "C#m", "A"],
        "G": ["G", "D", "Em", "C"],
    }
    chords = progressions.get(key, progressions["C"])
    
    tracks = {}
    
    # === DRUMS ===
    drums = MIDIFile(1)
    drums.addTempo(0, 0, bpm)
    
    KICK = 36
    SNARE = 38
    HIHAT = 42
    HIHAT_OPEN = 46
    
    for bar in range(bars):
        bar_start = bar * 4
        
        # Standard rock beat
        for beat in range(4):
            t = bar_start + beat
            
            # Kick on 1 and 3
            if beat == 0 or beat == 2:
                drums.addNote(0, 9, KICK, t, 0.3, 100)
            
            # Snare on 2 and 4
            if beat == 1 or beat == 3:
                drums.addNote(0, 9, SNARE, t, 0.3, 95)
            
            # Hi-hat on 8ths
            drums.addNote(0, 9, HIHAT, t, 0.2, 75)
            drums.addNote(0, 9, HIHAT, t + 0.5, 0.2, 65)
        
        # Open hi-hat on beat 4&
        drums.addNote(0, 9, HIHAT_OPEN, bar_start + 3.5, 0.3, 80)
    
    tracks["drums"] = drums
    
    # === BASS ===
    bass = MIDIFile(1)
    bass.addTempo(0, 0, bpm)
    bass.addProgramChange(0, 0, 0, 33)
    
    for bar in range(bars):
        bar_start = bar * 4
        chord_name = chords[bar % len(chords)]
        root = chord_name.replace("m", "")
        root_note = get_chord(root, "", 2)[0]
        
        # Simple root-fifth pattern
        bass.addNote(0, 0, root_note, bar_start, 1, 90)
        bass.addNote(0, 0, root_note, bar_start + 1, 0.5, 85)
        bass.addNote(0, 0, root_note + 7, bar_start + 1.5, 0.5, 80)
        bass.addNote(0, 0, root_note, bar_start + 2, 1, 90)
        bass.addNote(0, 0, root_note + 7, bar_start + 3, 0.5, 85)
        bass.addNote(0, 0, root_note + 5, bar_start + 3.5, 0.5, 80)
    
    tracks["bass"] = bass
    
    # === GUITAR ===
    guitar = MIDIFile(1)
    guitar.addTempo(0, 0, bpm)
    guitar.addProgramChange(0, 0, 0, 27)  # Clean electric
    
    for bar in range(bars):
        bar_start = bar * 4
        chord_name = chords[bar % len(chords)]
        chord_root = chord_name.replace("m", "")
        chord_type = "m" if "m" in chord_name else ""
        chord_notes = get_chord(chord_root, chord_type, 3)
        
        # Strumming pattern
        for beat in range(4):
            for i, note in enumerate(chord_notes):
                guitar.addNote(0, 0, note, bar_start + beat + (i * 0.02), 0.8, 75)
    
    tracks["guitar"] = guitar
    
    # === KEYS ===
    keys = MIDIFile(1)
    keys.addTempo(0, 0, bpm)
    keys.addProgramChange(0, 0, 0, 4)  # Electric Piano
    
    for bar in range(bars):
        bar_start = bar * 4
        chord_name = chords[bar % len(chords)]
        chord_root = chord_name.replace("m", "")
        chord_type = "m" if "m" in chord_name else ""
        chord_notes = get_chord(chord_root, chord_type, 4)
        
        # Pad-style whole notes
        for note in chord_notes:
            keys.addNote(0, 0, note, bar_start, 4, 60)
    
    tracks["keys"] = keys
    
    # Save all tracks
    for name, midi in tracks.items():
        filepath = os.path.join(output_dir, f"{name}.mid")
        with open(filepath, 'wb') as f:
            midi.writeFile(f)
        print(f"  ✓ {name}.mid")
    
    return {"output_dir": output_dir, "tracks": list(tracks.keys())}


# ============================================================================
# BACHATA GENERATOR (Enhanced from original)
# ============================================================================

def generate_bachata(bars: int, key: str, bpm: int) -> dict:
    """Generate Bachata multitrack MIDI (DGB AUDIO specialty)"""
    
    output_dir = os.path.join(OUTPUT_BASE, "bachata")
    os.makedirs(output_dir, exist_ok=True)
    
    scale = get_scale(key, "major")
    
    # Bachata romantic progression
    progressions = {
        "C": ["C", "Am", "F", "G"],
        "D": ["D", "Bm", "G", "A"],
        "E": ["E", "C#m", "A", "B7"],
        "G": ["G", "Em", "C", "D"],
    }
    chords = progressions.get(key, progressions["E"])
    
    tracks = {}
    
    # Import the enhanced generators from generate_16bar
    # For now, create simplified versions that follow DGB standard
    
    # === REQUINTO ===
    requinto = MIDIFile(1)
    requinto.addTempo(0, 0, bpm)
    requinto.addProgramChange(0, 0, 0, 24)  # Nylon guitar
    
    notes_list = list(scale.items())
    
    for bar in range(bars):
        bar_start = bar * 4
        chord_idx = bar % len(chords)
        
        # Build velocity over time
        vel = int(50 + (bar / bars) * 55)
        
        # Melodic fills
        if bar % 4 < 2:
            # Long romantic notes
            root_note = get_chord(chords[chord_idx].replace("m", "").replace("7", ""), "", 4)[0]
            requinto.addNote(0, 0, root_note + 12, bar_start, 2, vel)
            requinto.addNote(0, 0, root_note + 7, bar_start + 2.5, 1.5, vel - 5)
        else:
            # Faster fills
            root_note = get_chord(chords[chord_idx].replace("m", "").replace("7", ""), "", 4)[0]
            for i, offset in enumerate([0, 0.5, 1, 1.5, 2, 2.5]):
                note = root_note + [0, 4, 7, 12, 7, 4][i]
                requinto.addNote(0, 0, note, bar_start + offset, 0.4, vel + (i * 2))
    
    tracks["requinto"] = requinto
    
    # === SEGUNDA GUITARRA ===
    segunda = MIDIFile(1)
    segunda.addTempo(0, 0, bpm)
    segunda.addProgramChange(0, 0, 0, 24)
    
    for bar in range(bars):
        bar_start = bar * 4
        chord_name = chords[bar % len(chords)]
        chord_root = chord_name.replace("m", "").replace("7", "")
        chord_type = "m" if "m" in chord_name else ("7" if "7" in chord_name else "")
        chord_notes = get_chord(chord_root, chord_type, 3)
        
        vel = int(55 + (bar / bars) * 35)
        
        # Bachata derecho pattern
        for beat in range(4):
            t = bar_start + beat
            for i, note in enumerate(chord_notes):
                segunda.addNote(0, 0, note, t + (i * 0.02), 0.4, vel)
            # Off-beat ghost notes
            for i, note in enumerate(chord_notes):
                segunda.addNote(0, 0, note, t + 0.5 + (i * 0.02), 0.2, vel - 15)
    
    tracks["segunda_guitarra"] = segunda
    
    # === BONGO ===
    bongo = MIDIFile(1)
    bongo.addTempo(0, 0, bpm)
    
    BONGO_HI = 60
    BONGO_LO = 61
    
    for bar in range(bars):
        if bar < 2:  # Soft entry
            continue
            
        bar_start = bar * 4
        vel = int(50 + (bar / bars) * 55)
        
        # Martillo pattern
        for beat in range(4):
            t = bar_start + beat
            bongo.addNote(0, 9, BONGO_LO, t, 0.2, vel + 10)
            bongo.addNote(0, 9, BONGO_HI, t + 0.25, 0.15, vel - 10)
            bongo.addNote(0, 9, BONGO_HI, t + 0.5, 0.15, vel - 5)
            bongo.addNote(0, 9, BONGO_HI, t + 0.75, 0.15, vel - 8)
    
    tracks["bongo"] = bongo
    
    # === GÜIRA ===
    guira = MIDIFile(1)
    guira.addTempo(0, 0, bpm)
    
    GUIRA_DOWN = 69
    GUIRA_UP = 70
    
    for bar in range(bars):
        if bar < 4:  # Enter later
            continue
            
        bar_start = bar * 4
        vel = int(60 + (bar / bars) * 35)
        
        # 16th note scrape
        for beat in range(16):
            t = bar_start + (beat * 0.25)
            note = GUIRA_DOWN if beat % 2 == 0 else GUIRA_UP
            guira.addNote(0, 9, note, t, 0.18, vel + (5 if beat % 4 == 0 else -5))
    
    tracks["guira"] = guira
    
    # === BASS ===
    bass = MIDIFile(1)
    bass.addTempo(0, 0, bpm)
    bass.addProgramChange(0, 0, 0, 32)  # Acoustic bass
    
    for bar in range(bars):
        bar_start = bar * 4
        chord_name = chords[bar % len(chords)]
        root = chord_name.replace("m", "").replace("7", "")
        root_note = get_chord(root, "", 2)[0]
        
        # Simple bachata bass
        bass.addNote(0, 0, root_note, bar_start, 0.8, 85)
        bass.addNote(0, 0, root_note, bar_start + 2, 0.8, 80)
    
    tracks["bass"] = bass
    
    # Save all tracks
    for name, midi in tracks.items():
        filepath = os.path.join(output_dir, f"{name}.mid")
        with open(filepath, 'wb') as f:
            midi.writeFile(f)
        print(f"  ✓ {name}.mid")
    
    return {"output_dir": output_dir, "tracks": list(tracks.keys())}


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="DGB AUDIO V2.0 - Multi-Genre MIDI Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python generate_multigenre.py --genre salsa --bars 16 --key C --bpm 180
    python generate_multigenre.py --genre merengue --bars 8 --key D --bpm 170
    python generate_multigenre.py --genre bachata --bars 16 --key E --bpm 115
    python generate_multigenre.py --genre generic --bars 8 --key G --bpm 120
        """
    )
    
    parser.add_argument("--genre", "-g", 
                       choices=["salsa", "merengue", "bachata", "generic"],
                       default="bachata",
                       help="Music genre to generate")
    parser.add_argument("--bars", "-b", type=int, default=16,
                       help="Number of bars to generate")
    parser.add_argument("--key", "-k", default="E",
                       help="Musical key (C, D, E, F, G, A, B)")
    parser.add_argument("--bpm", type=int, default=115,
                       help="Tempo in BPM")
    parser.add_argument("--clave", choices=["2-3", "3-2"], default="2-3",
                       help="Clave pattern for Salsa")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🎸 DGB AUDIO ENGINE V2.0 - Multi-Genre Generator")
    print("=" * 60)
    print(f"Genre: {args.genre.upper()}")
    print(f"Key: {args.key} | BPM: {args.bpm} | Bars: {args.bars}")
    print("-" * 60)
    
    # Generate based on genre
    if args.genre == "salsa":
        result = generate_salsa(args.bars, args.key, args.bpm, args.clave)
    elif args.genre == "merengue":
        result = generate_merengue(args.bars, args.key, args.bpm)
    elif args.genre == "bachata":
        result = generate_bachata(args.bars, args.key, args.bpm)
    else:
        result = generate_generic(args.bars, args.key, args.bpm)
    
    print("-" * 60)
    print(f"✅ Generated {len(result['tracks'])} tracks")
    print(f"📁 Location: {result['output_dir']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
