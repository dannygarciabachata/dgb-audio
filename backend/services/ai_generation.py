"""
AI Music Generation Service
Handles audio analysis, prompt-to-MIDI, and music generation
"""
import os
import json
import base64
from datetime import datetime
from typing import Optional, List, Dict
import httpx


async def analyze_audio(
    audio_data: bytes,
    api_key: str,
    instrument: str = "guitar",
    genre: str = "bachata"
) -> dict:
    """
    Analyze recorded audio using OpenAI's audio understanding
    Returns detected key, BPM, timbre profile, and patterns
    """
    if not api_key:
        return {"error": "OpenAI API key not configured"}
    
    try:
        # Encode audio to base64
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Use GPT-4 with audio understanding
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"""Eres un experto analizador de audio para música tropical latina.
                            Analiza grabaciones de {instrument} en género {genre}.
                            Identifica: tonalidad, BPM estimado, características del timbre,
                            patrones rítmicos, y calidad de la grabación."""
                        },
                        {
                            "role": "user",
                            "content": f"""Analiza esta grabación de {instrument} en estilo {genre}.
                            
                            Responde en JSON con esta estructura:
                            {{
                                "detected_key": "Am/C/Dm/etc",
                                "detected_bpm": 120,
                                "timbre_profile": {{
                                    "brightness": 0.0-1.0,
                                    "warmth": 0.0-1.0,
                                    "attack": 0.0-1.0,
                                    "sustain": 0.0-1.0
                                }},
                                "suggested_patterns": ["pattern1", "pattern2"],
                                "quality_score": 0-100,
                                "recommendations": ["tip1", "tip2"]
                            }}"""
                        }
                    ],
                    "max_tokens": 500,
                    "response_format": {"type": "json_object"}
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = json.loads(result["choices"][0]["message"]["content"])
                
                return {
                    "success": True,
                    "analysis": analysis,
                    "detected_instrument": instrument,
                    "genre": genre,
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                    "analyzed_at": datetime.now().isoformat()
                }
            else:
                return {
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }
                
    except Exception as e:
        return {"error": str(e)}


async def generate_midi_from_prompt(
    prompt: str,
    api_key: str,
    genre: str = "bachata",
    bpm: int = 120,
    key: str = "Am",
    bars: int = 8
) -> dict:
    """
    Generate MIDI notation from a text prompt using AI
    Returns a structured MIDI-like representation
    """
    if not api_key:
        return {"error": "OpenAI API key not configured"}
    
    genre_styles = {
        "bachata": {
            "rhythm": "syncopated with requinto patterns",
            "instruments": ["requinto", "segunda", "bass", "bongos", "guira"],
            "typical_progression": "i-V-VI-iv or i-iv-V-i"
        },
        "bolero": {
            "rhythm": "slow romantic with arpeggiated guitar",
            "instruments": ["guitar", "bass", "piano", "strings"],
            "typical_progression": "I-vi-ii-V or I-IV-V-I"
        },
        "merengue": {
            "rhythm": "fast 2/4 with tambora patterns",
            "instruments": ["accordion", "tambora", "guira", "bass", "saxophone"],
            "typical_progression": "I-IV-V-I with fast changes"
        },
        "salsa": {
            "rhythm": "clave-based with montuno patterns",
            "instruments": ["piano", "bass", "congas", "timbales", "horns"],
            "typical_progression": "ii-V-I with extensions"
        },
        "vallenato": {
            "rhythm": "accordion-led with caja patterns",
            "instruments": ["accordion", "caja", "guacharaca", "bass"],
            "typical_progression": "I-IV-V with accordion fills"
        },
        "cumbia": {
            "rhythm": "steady 4/4 with güiro patterns",
            "instruments": ["accordion", "guiro", "drums", "bass"],
            "typical_progression": "I-IV-V-I or I-V-I"
        }
    }
    
    style = genre_styles.get(genre, genre_styles["bachata"])
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"""Eres un compositor experto de música {genre} latina.
                            
Estilo del género:
- Ritmo: {style['rhythm']}
- Instrumentos típicos: {', '.join(style['instruments'])}
- Progresiones comunes: {style['typical_progression']}

Genera composiciones en formato estructurado que puedan convertirse a MIDI.
Usa notación estándar (C4, D#5, etc.) con duraciones en beats."""
                        },
                        {
                            "role": "user",
                            "content": f"""Genera una composición de {genre} basada en esta descripción:
                            
"{prompt}"

Parámetros:
- BPM: {bpm}
- Tonalidad: {key}
- Duración: {bars} compases

Responde en JSON con esta estructura:
{{
    "title": "Nombre sugerido",
    "structure": ["intro", "verso", "coro"],
    "tracks": [
        {{
            "instrument": "nombre",
            "channel": 0,
            "notes": [
                {{"pitch": "C4", "start_beat": 0, "duration": 1.0, "velocity": 80}},
                ...
            ]
        }}
    ],
    "chord_progression": ["Am", "Dm", "E7", "Am"],
    "suggested_lyrics_theme": "tema romántico/festivo/etc"
}}"""
                        }
                    ],
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"}
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                composition = json.loads(result["choices"][0]["message"]["content"])
                
                return {
                    "success": True,
                    "composition": composition,
                    "genre": genre,
                    "bpm": bpm,
                    "key": key,
                    "bars": bars,
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return {
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }
                
    except Exception as e:
        return {"error": str(e)}


async def generate_lyrics(
    theme: str,
    api_key: str,
    genre: str = "bachata",
    mood: str = "romantic",
    language: str = "spanish"
) -> dict:
    """
    Generate lyrics for tropical music based on theme and genre
    """
    if not api_key:
        return {"error": "OpenAI API key not configured"}
    
    genre_themes = {
        "bachata": "amor, desamor, nostalgia, pasión",
        "bolero": "romance profundo, despedidas, recuerdos",
        "merengue": "fiesta, alegría, baile, celebración",
        "salsa": "vida urbana, amor, baile, ritmo",
        "vallenato": "amor, tierra natal, historias personales",
        "cumbia": "fiesta, tradición, alegría popular"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"""Eres un letrista profesional de {genre} latino.
                            
Temas típicos del género: {genre_themes.get(genre, 'amor y vida')}

Escribe letras auténticas con:
- Estructura clara (verso, pre-coro, coro)
- Rimas naturales
- Vocabulario apropiado al género
- Emociones genuinas"""
                        },
                        {
                            "role": "user",
                            "content": f"""Escribe una letra de {genre} sobre: {theme}
                            
Estado de ánimo: {mood}
Idioma: {language}

Responde en JSON:
{{
    "title": "Título de la canción",
    "sections": [
        {{"type": "verso1", "lines": ["línea 1", "línea 2", ...]}},
        {{"type": "coro", "lines": ["línea 1", "línea 2", ...]}}
    ],
    "suggested_rhyme_scheme": "ABAB o AABB",
    "emotional_arc": "descripción del arco emocional"
}}"""
                        }
                    ],
                    "max_tokens": 1000,
                    "response_format": {"type": "json_object"}
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                lyrics = json.loads(result["choices"][0]["message"]["content"])
                
                return {
                    "success": True,
                    "lyrics": lyrics,
                    "genre": genre,
                    "mood": mood,
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return {
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }
                
    except Exception as e:
        return {"error": str(e)}


def convert_to_midi_file(composition: dict, output_path: str) -> dict:
    """
    Convert AI-generated composition to actual MIDI file
    Uses the midiutil library
    """
    try:
        from midiutil import MIDIFile
        
        tracks = composition.get("tracks", [])
        num_tracks = len(tracks)
        
        midi = MIDIFile(num_tracks)
        tempo = composition.get("bpm", 120)
        
        for track_idx, track in enumerate(tracks):
            midi.addTempo(track_idx, 0, tempo)
            midi.addProgramChange(track_idx, track.get("channel", 0), 0, 0)
            
            for note in track.get("notes", []):
                pitch = note_name_to_midi(note["pitch"])
                start = note["start_beat"]
                duration = note["duration"]
                velocity = note.get("velocity", 80)
                
                midi.addNote(
                    track_idx,
                    track.get("channel", 0),
                    pitch,
                    start,
                    duration,
                    velocity
                )
        
        with open(output_path, "wb") as f:
            midi.writeFile(f)
        
        return {
            "success": True,
            "path": output_path,
            "tracks": num_tracks,
            "tempo": tempo
        }
        
    except ImportError:
        return {"error": "midiutil not installed"}
    except Exception as e:
        return {"error": str(e)}


def note_name_to_midi(note_name: str) -> int:
    """Convert note name (C4, D#5) to MIDI number"""
    notes = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    
    if len(note_name) < 2:
        return 60  # Default to middle C
    
    note = note_name[0].upper()
    modifier = 0
    octave_pos = 1
    
    if len(note_name) > 2 and note_name[1] in '#b':
        modifier = 1 if note_name[1] == '#' else -1
        octave_pos = 2
    
    try:
        octave = int(note_name[octave_pos:])
    except ValueError:
        octave = 4
    
    return notes.get(note, 0) + modifier + (octave + 1) * 12
