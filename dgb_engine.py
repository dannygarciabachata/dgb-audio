#!/usr/bin/env python3
"""
DGB AUDIO ENGINE V2.0 - Multi-Genre Production System
======================================================

A virtuoso multi-instrumentalist producer system capable of:
- Salsa (tumbao-based, clave 2-3/3-2)
- Merengue (tambora-led, galopante)
- Bachata (requinto-driven, romántico)
- Generic Pop (standard 4/4)

CORE: High-fidelity multitrack production with phase-coherent separation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import json

# ============================================================================
# GENRE DEFINITIONS
# ============================================================================

class Genre(Enum):
    BACHATA = "bachata"
    SALSA = "salsa"
    MERENGUE = "merengue"
    GENERIC = "generic"


class IntelligenceMode(Enum):
    MAESTRO_DGB = "maestro"      # Optimized for DGB guitars and bachata
    VERSATIL = "versatil"       # Tropical: Salsa, Merengue
    GLOBAL = "global"           # Pop, Rock, Ballads, synthetic


@dataclass
class InstrumentProfile:
    """Defines an instrument's sonic characteristics"""
    name: str
    midi_program: int           # General MIDI program number
    midi_channel: int           # 0-8, 10-15 (9 reserved for drums)
    frequency_focus: Tuple[int, int]  # Hz range to emphasize
    velocity_range: Tuple[int, int]   # Min/max velocity
    articulations: List[str]    # Available playing techniques
    

@dataclass
class RhythmPattern:
    """Defines a rhythmic pattern for an instrument"""
    name: str
    beats_per_bar: int
    subdivision: int            # 8 = 8th notes, 16 = 16th notes
    pattern: List[Tuple[float, float, int]]  # (beat_offset, duration, velocity_offset)
    swing_amount: float = 0.0   # 0.0 = straight, 0.5 = full swing


@dataclass 
class GenreConfig:
    """Complete configuration for a music genre"""
    name: str
    display_name: str
    default_bpm_range: Tuple[int, int]
    time_signature: Tuple[int, int]  # (numerator, denominator)
    swing_type: str             # "straight", "syncopated", "galopante"
    clave_pattern: Optional[str]  # "2-3", "3-2", None
    instruments: Dict[str, InstrumentProfile]
    rhythm_patterns: Dict[str, RhythmPattern]
    frequency_profile: Dict[str, Tuple[int, int]]  # EQ recommendations
    negative_prompts: List[str]  # What to avoid


# ============================================================================
# INSTRUMENT LIBRARY
# ============================================================================

INSTRUMENTS = {
    # === BACHATA INSTRUMENTS ===
    "requinto": InstrumentProfile(
        name="Requinto Guitar",
        midi_program=24,  # Nylon guitar
        midi_channel=0,
        frequency_focus=(2000, 5000),
        velocity_range=(40, 115),
        articulations=["vibrato", "picado", "mordente", "arpeggio", "tremolo"]
    ),
    "segunda_guitarra": InstrumentProfile(
        name="Segunda Guitar",
        midi_program=24,
        midi_channel=1,
        frequency_focus=(200, 2000),
        velocity_range=(45, 100),
        articulations=["rasgueado", "derecho", "arpegio", "staccato"]
    ),
    "bongo": InstrumentProfile(
        name="Bongo",
        midi_program=0,  # Drum channel
        midi_channel=9,
        frequency_focus=(200, 2000),
        velocity_range=(35, 110),
        articulations=["martillo", "abierto", "cerrado", "slap"]
    ),
    "guira_bachata": InstrumentProfile(
        name="Güira (Bachata)",
        midi_program=0,
        midi_channel=9,
        frequency_focus=(5000, 12000),
        velocity_range=(50, 100),
        articulations=["scrape", "accent", "roll"]
    ),
    "bajo_bachata": InstrumentProfile(
        name="Bass (Bachata)",
        midi_program=32,  # Acoustic bass
        midi_channel=2,
        frequency_focus=(60, 250),
        velocity_range=(60, 100),
        articulations=["fingered", "muted", "slide"]
    ),
    
    # === SALSA INSTRUMENTS ===
    "piano_montuno": InstrumentProfile(
        name="Piano (Montuno)",
        midi_program=0,  # Acoustic Grand Piano
        midi_channel=0,
        frequency_focus=(250, 4000),
        velocity_range=(60, 120),
        articulations=["montuno", "guajeo", "tumbao", "block_chords"]
    ),
    "bajo_tumbao": InstrumentProfile(
        name="Bass (Tumbao)",
        midi_program=32,
        midi_channel=1,
        frequency_focus=(40, 200),
        velocity_range=(70, 110),
        articulations=["tumbao", "anticipated", "syncopated"]
    ),
    "congas": InstrumentProfile(
        name="Congas",
        midi_program=0,
        midi_channel=9,
        frequency_focus=(150, 3000),
        velocity_range=(50, 120),
        articulations=["tumbao", "open", "slap", "muted", "heel_toe"]
    ),
    "timbal": InstrumentProfile(
        name="Timbales",
        midi_program=0,
        midi_channel=9,
        frequency_focus=(500, 8000),
        velocity_range=(60, 127),
        articulations=["cascara", "campana", "paila", "abanico"]
    ),
    "trombone_section": InstrumentProfile(
        name="Trombone Section",
        midi_program=57,  # Trombone
        midi_channel=3,
        frequency_focus=(80, 3000),
        velocity_range=(50, 115),
        articulations=["legato", "staccato", "sforzando", "mambo"]
    ),
    "clave": InstrumentProfile(
        name="Claves",
        midi_program=0,
        midi_channel=9,
        frequency_focus=(1000, 4000),
        velocity_range=(70, 100),
        articulations=["2-3", "3-2"]
    ),
    
    # === MERENGUE INSTRUMENTS ===
    "tambora": InstrumentProfile(
        name="Tambora",
        midi_program=0,
        midi_channel=9,
        frequency_focus=(60, 500),
        velocity_range=(70, 127),
        articulations=["open", "muted", "rim", "gallop"]
    ),
    "guira_merengue": InstrumentProfile(
        name="Güira (Merengue)",
        midi_program=0,
        midi_channel=9,
        frequency_focus=(6000, 15000),
        velocity_range=(70, 115),
        articulations=["fast_scrape", "accent", "roll", "syncopated"]
    ),
    "saxo_section": InstrumentProfile(
        name="Saxophone Section",
        midi_program=65,  # Alto Sax
        midi_channel=4,
        frequency_focus=(200, 6000),
        velocity_range=(55, 120),
        articulations=["mambo", "legato", "staccato", "growl"]
    ),
    "piano_merengue": InstrumentProfile(
        name="Piano (Merengue)",
        midi_program=0,
        midi_channel=0,
        frequency_focus=(300, 4000),
        velocity_range=(70, 120),
        articulations=["guajeo", "block_chords", "octaves"]
    ),
    
    # === GENERIC POP INSTRUMENTS ===
    "drums": InstrumentProfile(
        name="Drum Kit",
        midi_program=0,
        midi_channel=9,
        frequency_focus=(40, 12000),
        velocity_range=(50, 127),
        articulations=["straight", "shuffle", "half_time", "fills"]
    ),
    "electric_bass": InstrumentProfile(
        name="Electric Bass",
        midi_program=33,  # Electric Bass (finger)
        midi_channel=1,
        frequency_focus=(40, 400),
        velocity_range=(60, 110),
        articulations=["fingered", "picked", "slap", "muted"]
    ),
    "keyboards": InstrumentProfile(
        name="Keyboards/Synth",
        midi_program=4,  # Electric Piano
        midi_channel=0,
        frequency_focus=(100, 8000),
        velocity_range=(50, 110),
        articulations=["pad", "stab", "arpeggio", "lead"]
    ),
    "electric_guitar": InstrumentProfile(
        name="Electric Guitar",
        midi_program=27,  # Clean Electric
        midi_channel=2,
        frequency_focus=(200, 6000),
        velocity_range=(45, 115),
        articulations=["clean", "palm_mute", "power_chord", "arpeggio"]
    ),
}


# ============================================================================
# RHYTHM PATTERNS LIBRARY
# ============================================================================

RHYTHM_PATTERNS = {
    # === BACHATA PATTERNS ===
    "bachata_derecho": RhythmPattern(
        name="Bachata Derecho",
        beats_per_bar=4,
        subdivision=16,
        pattern=[
            (0, 0.5, 10),      # Beat 1 - accent
            (0.5, 0.25, -10),  # & 
            (0.75, 0.25, -5),  # a
            (1, 0.5, 5),       # Beat 2
            (1.5, 0.25, -10),
            (1.75, 0.25, -5),
            (2, 0.5, 10),      # Beat 3 - accent
            (2.5, 0.25, -10),
            (2.75, 0.25, -5),
            (3, 0.5, 5),       # Beat 4
            (3.5, 0.25, -10),
            (3.75, 0.25, -5),
        ],
        swing_amount=0.0
    ),
    "bongo_martillo": RhythmPattern(
        name="Bongo Martillo",
        beats_per_bar=4,
        subdivision=16,
        pattern=[
            (0, 0.2, 15),      # Low bongo
            (0.25, 0.15, -15), # High (ghost)
            (0.5, 0.15, -5),   # High
            (0.75, 0.15, -10), # High (ghost)
            (1, 0.2, 15),
            (1.25, 0.15, -15),
            (1.5, 0.15, -5),
            (1.75, 0.15, -10),
            (2, 0.2, 15),
            (2.25, 0.15, -15),
            (2.5, 0.15, -5),
            (2.75, 0.15, -10),
            (3, 0.2, 15),
            (3.25, 0.15, -15),
            (3.5, 0.15, -5),
            (3.75, 0.15, -10),
        ],
        swing_amount=0.0
    ),
    
    # === SALSA PATTERNS ===
    "clave_3_2": RhythmPattern(
        name="Clave 3-2",
        beats_per_bar=4,
        subdivision=8,
        pattern=[
            (0, 0.25, 10),     # 1
            (0.75, 0.25, 5),   # 1&
            (1.5, 0.25, 10),   # 2&
            # Bar 2
            (2, 0.25, 10),     # 3
            (3, 0.25, 10),     # 4
        ],
        swing_amount=0.1
    ),
    "clave_2_3": RhythmPattern(
        name="Clave 2-3",
        beats_per_bar=4,
        subdivision=8,
        pattern=[
            (0, 0.25, 10),     # 1
            (1, 0.25, 10),     # 2
            # Bar 2
            (2, 0.25, 10),     # 3
            (2.75, 0.25, 5),   # 3&
            (3.5, 0.25, 10),   # 4&
        ],
        swing_amount=0.1
    ),
    "tumbao_bass": RhythmPattern(
        name="Tumbao Bass",
        beats_per_bar=4,
        subdivision=8,
        pattern=[
            (0.5, 0.5, 10),    # & of 1 (anticipated)
            (2, 0.5, 5),       # 3
            (3.5, 0.5, 10),    # & of 4 (anticipated)
        ],
        swing_amount=0.15
    ),
    "montuno_piano": RhythmPattern(
        name="Piano Montuno",
        beats_per_bar=4,
        subdivision=8,
        pattern=[
            (0, 0.25, 5),
            (0.5, 0.25, 10),   # & accent
            (1, 0.25, 0),
            (1.5, 0.25, 5),
            (2, 0.25, 10),     # 3 accent
            (2.5, 0.25, 0),
            (3, 0.25, 5),
            (3.5, 0.25, 10),   # & accent
        ],
        swing_amount=0.1
    ),
    
    # === MERENGUE PATTERNS ===
    "tambora_gallop": RhythmPattern(
        name="Tambora Gallop",
        beats_per_bar=4,
        subdivision=8,
        pattern=[
            (0, 0.25, 15),     # Open
            (0.5, 0.25, -5),   # Muted
            (1, 0.25, 10),     # Rim
            (1.5, 0.25, -5),   # Muted
            (2, 0.25, 15),     # Open
            (2.5, 0.25, -5),   # Muted
            (3, 0.25, 10),     # Rim
            (3.5, 0.25, -5),   # Muted
        ],
        swing_amount=0.0  # Straight gallop
    ),
    "guira_merengue_fast": RhythmPattern(
        name="Güira Merengue Fast",
        beats_per_bar=4,
        subdivision=16,
        pattern=[(i * 0.25, 0.2, 5 if i % 2 == 0 else -5) for i in range(16)],
        swing_amount=0.0
    ),
    
    # === GENERIC PATTERNS ===
    "rock_beat": RhythmPattern(
        name="Rock Beat",
        beats_per_bar=4,
        subdivision=8,
        pattern=[
            (0, 0.5, 15),      # Kick + HiHat
            (0.5, 0.25, -10),  # HiHat
            (1, 0.5, 20),      # Snare + HiHat
            (1.5, 0.25, -10),  # HiHat
            (2, 0.5, 15),      # Kick + HiHat
            (2.5, 0.25, -10),  # HiHat
            (3, 0.5, 20),      # Snare + HiHat
            (3.5, 0.25, -10),  # HiHat
        ],
        swing_amount=0.0
    ),
}


# ============================================================================
# GENRE CONFIGURATIONS
# ============================================================================

GENRE_CONFIGS: Dict[Genre, GenreConfig] = {
    Genre.BACHATA: GenreConfig(
        name="bachata",
        display_name="Bachata Romántica",
        default_bpm_range=(115, 140),
        time_signature=(4, 4),
        swing_type="straight",
        clave_pattern=None,
        instruments={
            "lead": INSTRUMENTS["requinto"],
            "rhythm": INSTRUMENTS["segunda_guitarra"],
            "percussion1": INSTRUMENTS["bongo"],
            "percussion2": INSTRUMENTS["guira_bachata"],
            "bass": INSTRUMENTS["bajo_bachata"],
        },
        rhythm_patterns={
            "main": RHYTHM_PATTERNS["bachata_derecho"],
            "bongo": RHYTHM_PATTERNS["bongo_martillo"],
        },
        frequency_profile={
            "requinto": (2000, 5000),
            "segunda": (200, 400),
            "bongo": (200, 800),
            "guira": (5000, 10000),
            "bass": (60, 250),
        },
        negative_prompts=[
            "drums", "electronic beats", "distorted guitar", "synthesizer",
            "piano", "heavy reverb", "muddy low end", "fast merengue", "trap"
        ]
    ),
    
    Genre.SALSA: GenreConfig(
        name="salsa",
        display_name="Salsa Dura",
        default_bpm_range=(160, 220),
        time_signature=(4, 4),
        swing_type="syncopated",
        clave_pattern="2-3",  # or "3-2"
        instruments={
            "lead": INSTRUMENTS["piano_montuno"],
            "bass": INSTRUMENTS["bajo_tumbao"],
            "percussion1": INSTRUMENTS["congas"],
            "percussion2": INSTRUMENTS["timbal"],
            "brass": INSTRUMENTS["trombone_section"],
            "clave": INSTRUMENTS["clave"],
        },
        rhythm_patterns={
            "clave": RHYTHM_PATTERNS["clave_2_3"],
            "bass": RHYTHM_PATTERNS["tumbao_bass"],
            "piano": RHYTHM_PATTERNS["montuno_piano"],
        },
        frequency_profile={
            "piano": (250, 4000),
            "bass": (40, 200),
            "congas": (150, 3000),
            "timbales": (500, 8000),
            "trombones": (80, 3000),
        },
        negative_prompts=[
            "rock drums", "electric guitar", "synthesizer pads",
            "straight rhythms", "reverb wash", "auto-tune"
        ]
    ),
    
    Genre.MERENGUE: GenreConfig(
        name="merengue",
        display_name="Merengue Típico",
        default_bpm_range=(140, 180),
        time_signature=(2, 4),
        swing_type="galopante",
        clave_pattern=None,
        instruments={
            "lead": INSTRUMENTS["saxo_section"],
            "keys": INSTRUMENTS["piano_merengue"],
            "percussion1": INSTRUMENTS["tambora"],
            "percussion2": INSTRUMENTS["guira_merengue"],
            "bass": INSTRUMENTS["bajo_bachata"],
        },
        rhythm_patterns={
            "tambora": RHYTHM_PATTERNS["tambora_gallop"],
            "guira": RHYTHM_PATTERNS["guira_merengue_fast"],
        },
        frequency_profile={
            "tambora": (60, 500),
            "guira": (6000, 15000),
            "saxos": (200, 6000),
            "piano": (300, 4000),
            "bass": (40, 200),
        },
        negative_prompts=[
            "slow tempo", "ballad feel", "heavy reverb",
            "rock drums", "distorted guitar"
        ]
    ),
    
    Genre.GENERIC: GenreConfig(
        name="generic",
        display_name="Pop/Rock Standard",
        default_bpm_range=(90, 140),
        time_signature=(4, 4),
        swing_type="straight",
        clave_pattern=None,
        instruments={
            "drums": INSTRUMENTS["drums"],
            "bass": INSTRUMENTS["electric_bass"],
            "keys": INSTRUMENTS["keyboards"],
            "guitar": INSTRUMENTS["electric_guitar"],
        },
        rhythm_patterns={
            "drums": RHYTHM_PATTERNS["rock_beat"],
        },
        frequency_profile={
            "drums": (40, 12000),
            "bass": (40, 400),
            "keys": (100, 8000),
            "guitar": (200, 6000),
        },
        negative_prompts=[
            "lo-fi", "amateur recording", "thin sound", "harsh frequencies"
        ]
    ),
}


# ============================================================================
# DGB AUDIO ENGINE CLASS
# ============================================================================

class DGBAudioEngine:
    """
    Main engine for multi-genre music production.
    
    Modes:
    - MAESTRO_DGB: Optimized for DGB guitars and bachata
    - VERSATIL: Tropical (Salsa, Merengue)
    - GLOBAL: Pop, Rock, Ballads
    """
    
    VERSION = "2.0"
    CORE_PROMPT = (
        "DGB AUDIO System: You are a virtuoso multi-instrumentalist producer. "
        "Recognize and synthesize full arrangements for: Salsa (tumbao-based), "
        "Merengue (tambora-led), Bachata (requinto-driven), and General Pop. "
        "Distinguish between acoustic and synthetic textures. "
        "Maintain phase-coherent multitrack separation for every instrument generated."
    )
    
    def __init__(self, mode: IntelligenceMode = IntelligenceMode.MAESTRO_DGB):
        self.mode = mode
        self.current_genre: Optional[Genre] = None
        self.bpm = 120
        self.key = "C"
        self.time_signature = (4, 4)
        
    def set_mode(self, mode: IntelligenceMode):
        """Switch intelligence mode"""
        self.mode = mode
        print(f"🎛️  Mode switched to: {mode.value}")
    
    def set_genre(self, genre: Genre):
        """Configure engine for specific genre"""
        self.current_genre = genre
        config = GENRE_CONFIGS[genre]
        
        # Set defaults from genre config
        bpm_range = config.default_bpm_range
        self.bpm = (bpm_range[0] + bpm_range[1]) // 2
        self.time_signature = config.time_signature
        
        print(f"🎵 Genre set: {config.display_name}")
        print(f"   BPM: {self.bpm} | Time: {self.time_signature[0]}/{self.time_signature[1]}")
        print(f"   Swing: {config.swing_type}")
        if config.clave_pattern:
            print(f"   Clave: {config.clave_pattern}")
    
    def get_instruments(self) -> Dict[str, InstrumentProfile]:
        """Get instruments for current genre"""
        if self.current_genre is None:
            raise ValueError("Genre not set. Call set_genre() first.")
        return GENRE_CONFIGS[self.current_genre].instruments
    
    def get_rhythm_patterns(self) -> Dict[str, RhythmPattern]:
        """Get rhythm patterns for current genre"""
        if self.current_genre is None:
            raise ValueError("Genre not set. Call set_genre() first.")
        return GENRE_CONFIGS[self.current_genre].rhythm_patterns
    
    def get_negative_prompts(self) -> List[str]:
        """Get list of things to avoid for current genre"""
        if self.current_genre is None:
            return []
        return GENRE_CONFIGS[self.current_genre].negative_prompts
    
    def generate_prompt(self, bars: int, structure: str, special_instructions: str = "") -> str:
        """Generate a production prompt for the current configuration"""
        if self.current_genre is None:
            raise ValueError("Genre not set. Call set_genre() first.")
            
        config = GENRE_CONFIGS[self.current_genre]
        instruments = ", ".join([i.name for i in config.instruments.values()])
        
        prompt = (
            f"DGB AUDIO Engine: Generate a {bars}-bar multitrack arrangement. "
            f"Genre: {config.display_name}. Key: {self.key}. BPM: {self.bpm}. "
            f"Time signature: {self.time_signature[0]}/{self.time_signature[1]}. "
            f"Structure: {structure}. "
            f"Instruments: {instruments}. "
        )
        
        if config.clave_pattern:
            prompt += f"Clave: {config.clave_pattern}. "
        
        if special_instructions:
            prompt += f"Special: {special_instructions}. "
        
        prompt += f"Avoid: {', '.join(config.negative_prompts)}."
        
        return prompt
    
    def print_status(self):
        """Display current engine status"""
        print("\n" + "=" * 60)
        print("🎸 DGB AUDIO ENGINE V2.0")
        print("=" * 60)
        print(f"Mode: {self.mode.value}")
        if self.current_genre:
            config = GENRE_CONFIGS[self.current_genre]
            print(f"Genre: {config.display_name}")
            print(f"BPM: {self.bpm}")
            print(f"Key: {self.key}")
            print(f"Time: {self.time_signature[0]}/{self.time_signature[1]}")
            print("\nInstruments loaded:")
            for role, inst in config.instruments.items():
                print(f"  • {role}: {inst.name}")
        else:
            print("Genre: Not set")
        print("=" * 60 + "\n")


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def main():
    """Demo the DGB Audio Engine"""
    print("\n" + "=" * 60)
    print("🎸 DGB AUDIO ENGINE V2.0 - Multi-Genre System")
    print("=" * 60)
    print(DGBAudioEngine.CORE_PROMPT)
    print("=" * 60)
    
    # Demo each genre configuration
    engine = DGBAudioEngine()
    
    for genre in Genre:
        print(f"\n{'─' * 60}")
        engine.set_genre(genre)
        config = GENRE_CONFIGS[genre]
        
        print(f"\n📋 Instruments for {config.display_name}:")
        for role, inst in config.instruments.items():
            print(f"   {role:12} → {inst.name}")
            print(f"                Freq: {inst.frequency_focus[0]}-{inst.frequency_focus[1]}Hz")
            print(f"                Arts: {', '.join(inst.articulations[:3])}...")
        
        print(f"\n🎵 Rhythm Patterns:")
        for name, pattern in config.rhythm_patterns.items():
            print(f"   {name}: subdivision={pattern.subdivision}, swing={pattern.swing_amount}")
        
        print(f"\n🚫 Avoid: {', '.join(config.negative_prompts[:4])}...")
    
    # Generate sample prompt
    print("\n" + "=" * 60)
    print("📝 SAMPLE PROMPT GENERATION")
    print("=" * 60)
    
    engine.set_genre(Genre.BACHATA)
    engine.key = "E"
    engine.bpm = 115
    
    prompt = engine.generate_prompt(
        bars=16,
        structure="4 bars bolero intro, 12 bars bachata verse",
        special_instructions="requinto solo bars 10-14 with increasing intensity"
    )
    print(f"\n{prompt}")
    
    print("\n✅ Engine configuration complete!")
    print("   Ready for MIDI generation with any genre.\n")


if __name__ == "__main__":
    main()
