"""
DGB AUDIO - ACE-Step Service
==============================
Connects to ACE-Step 1.5 API server for local music generation.
Implements the Antigravity Engine for creative control.
"""

import os
import asyncio
import aiohttp
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json
import secrets

# ACE-Step API Configuration
ACESTEP_HOST = os.getenv("ACESTEP_HOST", "http://localhost")
ACESTEP_PORT = int(os.getenv("ACESTEP_PORT", "8001"))
ACESTEP_BASE_URL = f"{ACESTEP_HOST}:{ACESTEP_PORT}"

# Output directory for generated audio
OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated_audio"
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================================
# ANTIGRAVITY ENGINE
# ============================================================================

def calculate_antigravity_params(antigravity_level: int) -> Dict[str, float]:
    """
    Convert Antigravity slider (0-100) to ACE-Step generation parameters.
    
    The Antigravity Engine controls how "experimental" the generation becomes:
    - 0-20: Safe/Traditional - Stays close to genre conventions
    - 20-50: Balanced - Some creative freedom
    - 50-80: Creative - More unexpected elements
    - 80-100: Experimental/Wild - Maximum creative chaos
    """
    # Clamp value
    level = max(0, min(100, antigravity_level))
    
    # Map to guidance_scale (3.0 to 15.0)
    # Higher guidance = more adherence to prompt (less creative)
    # Lower guidance = more creative/unpredictable
    # INVERTED: Higher antigravity = LOWER guidance for more creativity
    if level < 20:
        guidance_scale = 3.0 + (level / 20) * 1.0  # 3.0 - 4.0
    elif level < 50:
        guidance_scale = 4.0 + ((level - 20) / 30) * 2.0  # 4.0 - 6.0
    elif level < 80:
        guidance_scale = 6.0 + ((level - 50) / 30) * 2.0  # 6.0 - 8.0
    else:
        guidance_scale = 8.0 + ((level - 80) / 20) * 7.0  # 8.0 - 15.0
    
    # Map to temperature (0.7 to 1.0)
    # Higher temperature = more randomness/creativity
    temperature = 0.7 + (level / 100) * 0.3
    
    # Map to cfg_rescale (0.0 to 0.75)
    cfg_rescale = (level / 100) * 0.75
    
    # Map to infer_steps (more steps for higher quality at high antigravity)
    infer_steps = int(60 + (level / 100) * 40)  # 60-100 steps
    
    return {
        "guidance_scale": round(guidance_scale, 2),
        "temperature": round(temperature, 2),
        "cfg_rescale": round(cfg_rescale, 2),
        "infer_steps": infer_steps,
        "antigravity_level": level,
        "mode": get_antigravity_mode_name(level)
    }


def get_antigravity_mode_name(level: int) -> str:
    """Get human-readable name for antigravity level"""
    if level < 20:
        return "Tradicional"
    elif level < 50:
        return "Balanceado"
    elif level < 80:
        return "Creativo"
    else:
        return "Experimental"


# ============================================================================
# ACE-STEP API CLIENT
# ============================================================================

async def check_acestep_health() -> Dict:
    """Check if ACE-Step server is running and healthy"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ACESTEP_BASE_URL}/health", timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "connected": True,
                        "status": "healthy",
                        "url": ACESTEP_BASE_URL,
                        "version": data.get("version", "unknown")
                    }
    except Exception as e:
        pass
    
    return {
        "connected": False,
        "status": "offline",
        "url": ACESTEP_BASE_URL,
        "error": "ACE-Step server not responding"
    }


def check_acestep_health_sync() -> Dict:
    """Synchronous version of health check"""
    try:
        resp = requests.get(f"{ACESTEP_BASE_URL}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "connected": True,
                "status": "healthy",
                "url": ACESTEP_BASE_URL,
                "version": data.get("version", "unknown")
            }
    except Exception as e:
        pass
    
    return {
        "connected": False,
        "status": "offline", 
        "url": ACESTEP_BASE_URL,
        "error": "ACE-Step server not responding. Run: uv run acestep-api --port 8001"
    }


async def generate_music(
    prompt: str,
    lyrics: str = "",
    genre: str = "bachata",
    bpm: int = 120,
    key: str = "Am",
    duration: int = 120,  # seconds
    antigravity: int = 50,
    user_id: str = None
) -> Dict:
    """
    Generate music using ACE-Step API with Antigravity Engine.
    
    Args:
        prompt: Text description of the music
        lyrics: Optional lyrics for the song
        genre: Music genre (bachata, bolero, merengue, salsa, etc.)
        bpm: Tempo in beats per minute
        key: Musical key (Am, C, G, etc.)
        duration: Duration in seconds
        antigravity: Creativity level (0-100)
        user_id: User ID for tracking
    
    Returns:
        Dict with job_id, status, and details
    """
    # Calculate Antigravity parameters
    params = calculate_antigravity_params(antigravity)
    
    # Build the enhanced prompt with DGB style
    enhanced_prompt = build_dgb_prompt(prompt, genre, bpm, key)
    
    # Create job ID
    job_id = f"dgb_{secrets.token_hex(12)}"
    
    # Prepare ACE-Step request
    acestep_payload = {
        "prompt": enhanced_prompt,
        "lyrics": lyrics if lyrics else "[instrumental]",
        "duration": duration,
        "guidance_scale": params["guidance_scale"],
        "temperature": params["temperature"],
        "cfg_rescale": params["cfg_rescale"],
        "infer_steps": params["infer_steps"],
        # ACE-Step specific params
        "num_segments": max(1, duration // 60),  # One segment per minute
        "seed": -1,  # Random seed
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{ACESTEP_BASE_URL}/generate",
                json=acestep_payload,
                timeout=aiohttp.ClientTimeout(total=600)  # 10 min timeout
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    # Save audio if returned directly
                    audio_path = None
                    if result.get("audio_data"):
                        audio_path = save_generated_audio(
                            result["audio_data"],
                            job_id,
                            genre
                        )
                    elif result.get("audio_url"):
                        audio_path = await download_audio_from_url(
                            result["audio_url"],
                            job_id,
                            genre
                        )
                    
                    return {
                        "success": True,
                        "job_id": job_id,
                        "status": "completed" if audio_path else "processing",
                        "audio_path": audio_path,
                        "antigravity_params": params,
                        "prompt_used": enhanced_prompt,
                        "acestep_response": result
                    }
                else:
                    error_text = await resp.text()
                    return {
                        "success": False,
                        "job_id": job_id,
                        "status": "failed",
                        "error": f"ACE-Step error: {error_text}"
                    }
                    
    except asyncio.TimeoutError:
        return {
            "success": False,
            "job_id": job_id,
            "status": "timeout",
            "error": "Generation took too long (>10 min)"
        }
    except Exception as e:
        return {
            "success": False,
            "job_id": job_id,
            "status": "error",
            "error": str(e)
        }


def generate_music_sync(
    prompt: str,
    lyrics: str = "",
    genre: str = "bachata",
    bpm: int = 120,
    key: str = "Am",
    duration: int = 120,
    antigravity: int = 50,
    user_id: str = None
) -> Dict:
    """Synchronous wrapper for generate_music"""
    return asyncio.run(generate_music(
        prompt=prompt,
        lyrics=lyrics,
        genre=genre,
        bpm=bpm,
        key=key,
        duration=duration,
        antigravity=antigravity,
        user_id=user_id
    ))


def build_dgb_prompt(prompt: str, genre: str, bpm: int, key: str) -> str:
    """
    Build an enhanced prompt with DGB tropical music style hints.
    """
    # Genre-specific style hints
    genre_hints = {
        "bachata": "smooth guitar arpeggios, romantic bongos, sensual bassline, Dominican style",
        "bolero": "slow romantic melody, expressive guitar, emotional strings, Cuban influence",
        "merengue": "fast accordion, energetic tambora, syncopated rhythms, Dominican party",
        "salsa": "bright brass section, clave rhythm, congas, Cuban son influence",
        "cumbia": "Colombian cumbia pattern, accordion, guacharaca, tropical feel",
        "reggaeton": "dembow rhythm, 808 bass, urban Latin style, perreo beat",
        "son": "Cuban son montuno, tres guitar, bongos, traditional roots"
    }
    
    style_hint = genre_hints.get(genre.lower(), "tropical Latin music, Caribbean influence")
    
    # Build the enhanced prompt
    enhanced = f"{prompt}. Style: {genre.title()}, {style_hint}. Tempo: {bpm} BPM, Key: {key}."
    
    return enhanced


def save_generated_audio(audio_data: bytes, job_id: str, genre: str) -> str:
    """Save generated audio to file"""
    filename = f"{genre}_{job_id}.wav"
    filepath = OUTPUT_DIR / filename
    
    with open(filepath, 'wb') as f:
        f.write(audio_data)
    
    return str(filepath)


async def download_audio_from_url(url: str, job_id: str, genre: str) -> str:
    """Download audio from ACE-Step server URL"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                audio_data = await resp.read()
                return save_generated_audio(audio_data, job_id, genre)
    return None


async def get_generation_status(job_id: str) -> Dict:
    """Check status of an ongoing generation"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ACESTEP_BASE_URL}/status/{job_id}") as resp:
                if resp.status == 200:
                    return await resp.json()
    except:
        pass
    
    return {"job_id": job_id, "status": "unknown"}


# ============================================================================
# BATCH GENERATION
# ============================================================================

async def generate_variations(
    prompt: str,
    genre: str,
    count: int = 3,
    antigravity_levels: list = None
) -> list:
    """
    Generate multiple variations of a song with different antigravity levels.
    Great for A/B testing different creative intensities.
    """
    if antigravity_levels is None:
        antigravity_levels = [25, 50, 75]  # Traditional, Balanced, Creative
    
    results = []
    for i, level in enumerate(antigravity_levels[:count]):
        result = await generate_music(
            prompt=prompt,
            genre=genre,
            antigravity=level
        )
        result["variation"] = i + 1
        results.append(result)
    
    return results


# ============================================================================
# DGB PRESETS
# ============================================================================

DGB_PRESETS = {
    "bachata_romantica": {
        "genre": "bachata",
        "bpm": 130,
        "key": "Am",
        "antigravity": 30,
        "description": "Bachata romántica tradicional para enamorar"
    },
    "bachata_moderna": {
        "genre": "bachata",
        "bpm": 140,
        "key": "Em",
        "antigravity": 60,
        "description": "Bachata moderna con toques urbanos"
    },
    "bolero_clasico": {
        "genre": "bolero",
        "bpm": 80,
        "key": "Dm",
        "antigravity": 20,
        "description": "Bolero clásico para noches de luna"
    },
    "merengue_fiesta": {
        "genre": "merengue",
        "bpm": 160,
        "key": "C",
        "antigravity": 50,
        "description": "Merengue para bailar hasta el amanecer"
    },
    "salsa_dura": {
        "genre": "salsa",
        "bpm": 180,
        "key": "G",
        "antigravity": 45,
        "description": "Salsa brava con descarga"
    },
    "tropical_fusion": {
        "genre": "bachata",
        "bpm": 125,
        "key": "Gm",
        "antigravity": 85,
        "description": "Fusión experimental tropical"
    }
}


def get_preset(preset_name: str) -> Dict:
    """Get a DGB preset configuration"""
    return DGB_PRESETS.get(preset_name, DGB_PRESETS["bachata_romantica"])


def list_presets() -> Dict:
    """List all available DGB presets"""
    return {
        "presets": [
            {"id": k, **v} for k, v in DGB_PRESETS.items()
        ]
    }
