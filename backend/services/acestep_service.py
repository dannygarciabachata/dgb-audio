"""
DGB AUDIO - ACE-Step Service
==============================
Connects to ACE-Step 1.5 API server for local music generation.
Implements the Antigravity Engine for creative control.

ACE-Step API Parameters (from official repo):
- audio_duration: float (seconds)
- prompt: str (genre/style description)
- lyrics: str (song lyrics with [Verse], [Chorus] tags)
- infer_step: int (number of inference steps)
- guidance_scale: float (adherence to prompt)
- scheduler_type: str ("euler" recommended)
- cfg_type: str ("apg" or "cfg")
- omega_scale: float (omega parameter)
- actual_seeds: List[int] (random seeds)
- guidance_interval: float
- guidance_interval_decay: float
- min_guidance_scale: float
- use_erg_tag: bool (ERG for tags)
- use_erg_lyric: bool (ERG for lyrics)
- use_erg_diffusion: bool (ERG for diffusion)
- oss_steps: List[int] (OSS optimization steps)
- guidance_scale_text: float
- guidance_scale_lyric: float
"""

import os
import asyncio
import aiohttp
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import secrets
import random

# ACE-Step API Configuration
ACESTEP_HOST = os.getenv("ACESTEP_HOST", "http://localhost")
ACESTEP_PORT = int(os.getenv("ACESTEP_PORT", "8001"))
ACESTEP_BASE_URL = f"{ACESTEP_HOST}:{ACESTEP_PORT}"

# Checkpoint path (user should configure this)
ACESTEP_CHECKPOINT = os.getenv("ACESTEP_CHECKPOINT", "ACE-Step/ACE-Step-v1-3.5B")

# Output directory for generated audio
OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated_audio"
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================================
# ANTIGRAVITY ENGINE (Maps 0-100 slider to ACE-Step parameters)
# ============================================================================

def calculate_antigravity_params(antigravity_level: int) -> Dict[str, Any]:
    """
    Convert Antigravity slider (0-100) to ACE-Step generation parameters.
    
    The Antigravity Engine controls how "experimental" the generation becomes:
    - 0-20: Safe/Traditional - Stays close to genre conventions
    - 20-50: Balanced - Some creative freedom
    - 50-80: Creative - More unexpected elements
    - 80-100: Experimental/Wild - Maximum creative chaos
    
    Mapped ACE-Step parameters:
    - guidance_scale: 3.0-15.0 (higher = more adherence to prompt)
    - infer_step: 60-150 (more steps = higher quality)
    - omega_scale: 5.0-15.0 (affects generation variance)
    - cfg_type: "apg" (default) or "cfg" for experimental
    """
    level = max(0, min(100, antigravity_level))
    
    # Guidance scale mapping (inverted for creativity)
    # Low antigravity = high guidance (safe), High antigravity = varied guidance
    if level < 20:
        guidance_scale = 7.0  # Very stable
        omega_scale = 5.0
        infer_step = 60
        cfg_type = "apg"
    elif level < 50:
        guidance_scale = 5.0 + (level - 20) / 30 * 3.0  # 5.0 - 8.0
        omega_scale = 5.0 + (level - 20) / 30 * 5.0  # 5.0 - 10.0
        infer_step = 80
        cfg_type = "apg"
    elif level < 80:
        guidance_scale = 8.0 + (level - 50) / 30 * 4.0  # 8.0 - 12.0
        omega_scale = 10.0 + (level - 50) / 30 * 3.0  # 10.0 - 13.0
        infer_step = 100
        cfg_type = "apg"
    else:
        guidance_scale = 12.0 + (level - 80) / 20 * 3.0  # 12.0 - 15.0
        omega_scale = 13.0 + (level - 80) / 20 * 2.0  # 13.0 - 15.0
        infer_step = 150  # Maximum quality for experimental
        cfg_type = "cfg" if level > 90 else "apg"  # CFG for ultra-experimental
    
    # Guidance interval (affects temporal consistency)
    guidance_interval = 0.5 - (level / 100) * 0.3  # 0.5 to 0.2
    guidance_interval_decay = 0.0
    min_guidance_scale = 3.0
    
    # ERG settings (Enhanced Representation Guidance)
    use_erg = level < 80  # Disable ERG for very experimental
    
    # OSS steps (Optimal Seed Search)
    oss_steps = [60, 80, 100] if level < 50 else []
    
    return {
        "guidance_scale": round(guidance_scale, 2),
        "infer_step": infer_step,
        "omega_scale": round(omega_scale, 2),
        "cfg_type": cfg_type,
        "scheduler_type": "euler",
        "guidance_interval": round(guidance_interval, 2),
        "guidance_interval_decay": guidance_interval_decay,
        "min_guidance_scale": min_guidance_scale,
        "use_erg_tag": use_erg,
        "use_erg_lyric": use_erg,
        "use_erg_diffusion": use_erg,
        "oss_steps": oss_steps,
        "guidance_scale_text": 0.0,
        "guidance_scale_lyric": 0.0,
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
            async with session.get(f"{ACESTEP_BASE_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "connected": True,
                        "status": data.get("status", "healthy"),
                        "url": ACESTEP_BASE_URL,
                        "checkpoint": ACESTEP_CHECKPOINT,
                        "version": "1.5"
                    }
    except Exception as e:
        pass
    
    return {
        "connected": False,
        "status": "offline",
        "url": ACESTEP_BASE_URL,
        "error": f"ACE-Step server not responding. Start with: python infer-api.py"
    }


def check_acestep_health_sync() -> Dict:
    """Synchronous version of health check"""
    try:
        resp = requests.get(f"{ACESTEP_BASE_URL}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "connected": True,
                "status": data.get("status", "healthy"),
                "url": ACESTEP_BASE_URL,
                "checkpoint": ACESTEP_CHECKPOINT
            }
    except Exception as e:
        pass
    
    return {
        "connected": False,
        "status": "offline", 
        "url": ACESTEP_BASE_URL,
        "error": "ACE-Step server not responding. Start with: python infer-api.py"
    }


async def generate_music(
    prompt: str,
    lyrics: str = "",
    genre: str = "bachata",
    bpm: int = 120,
    key: str = "Am",
    duration: int = 120,  # seconds
    antigravity: int = 50,
    user_id: str = None,
    seed: int = -1
) -> Dict:
    """
    Generate music using ACE-Step API with Antigravity Engine.
    
    Args:
        prompt: Text description of the music
        lyrics: Optional lyrics for the song (with [Verse], [Chorus] tags)
        genre: Music genre (bachata, bolero, merengue, salsa, etc.)
        bpm: Tempo in beats per minute
        key: Musical key (Am, C, G, etc.)
        duration: Duration in seconds (max 240 = 4 minutes)
        antigravity: Creativity level (0-100)
        user_id: User ID for tracking
        seed: Random seed (-1 for random)
    
    Returns:
        Dict with job_id, status, audio_path, and generation details
    """
    # Calculate Antigravity parameters
    params = calculate_antigravity_params(antigravity)
    
    # Build the enhanced prompt with DGB style
    enhanced_prompt = build_dgb_prompt(prompt, genre, bpm, key)
    
    # Format lyrics with proper structure
    formatted_lyrics = format_lyrics(lyrics) if lyrics else "[instrumental]"
    
    # Create job ID
    job_id = f"dgb_{secrets.token_hex(12)}"
    
    # Generate seed if random
    actual_seed = seed if seed > 0 else random.randint(1, 999999)
    
    # Prepare ACE-Step API request (matching infer-api.py schema)
    acestep_payload = {
        "checkpoint_path": ACESTEP_CHECKPOINT,
        "bf16": True,
        "torch_compile": False,
        "device_id": 0,
        "output_path": str(OUTPUT_DIR / f"{job_id}.wav"),
        "audio_duration": float(min(duration, 240)),  # Max 4 minutes
        "prompt": enhanced_prompt,
        "lyrics": formatted_lyrics,
        "infer_step": params["infer_step"],
        "guidance_scale": params["guidance_scale"],
        "scheduler_type": params["scheduler_type"],
        "cfg_type": params["cfg_type"],
        "omega_scale": params["omega_scale"],
        "actual_seeds": [actual_seed],
        "guidance_interval": params["guidance_interval"],
        "guidance_interval_decay": params["guidance_interval_decay"],
        "min_guidance_scale": params["min_guidance_scale"],
        "use_erg_tag": params["use_erg_tag"],
        "use_erg_lyric": params["use_erg_lyric"],
        "use_erg_diffusion": params["use_erg_diffusion"],
        "oss_steps": params["oss_steps"],
        "guidance_scale_text": params["guidance_scale_text"],
        "guidance_scale_lyric": params["guidance_scale_lyric"]
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
                    
                    audio_path = result.get("output_path")
                    
                    return {
                        "success": True,
                        "job_id": job_id,
                        "status": "completed",
                        "audio_path": audio_path,
                        "audio_url": f"/audio/{job_id}.wav",
                        "antigravity_params": params,
                        "prompt_used": enhanced_prompt,
                        "lyrics_used": formatted_lyrics,
                        "duration": duration,
                        "seed": actual_seed,
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
    except aiohttp.ClientConnectorError:
        return {
            "success": False,
            "job_id": job_id,
            "status": "connection_error",
            "error": f"Cannot connect to ACE-Step at {ACESTEP_BASE_URL}. Is the server running?"
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
    ACE-Step works best with detailed style descriptions.
    """
    # Genre-specific style hints (matching ACE-Step's training data)
    genre_hints = {
        "bachata": "latin bachata, romantic guitar arpeggios, bongos, güira, sensual bassline, Dominican style, smooth male/female vocals",
        "bolero": "latin bolero, slow romantic ballad, expressive acoustic guitar, emotional strings, Cuban influence, passionate vocals",
        "merengue": "Dominican merengue, fast accordion, energetic tambora drum, syncopated rhythms, party atmosphere, 160-180 bpm",
        "salsa": "Cuban salsa, bright brass section, clave rhythm, congas, piano montuno, son influence, energetic horns",
        "cumbia": "Colombian cumbia, accordion melody, guacharaca percussion, tropical feel, danceable groove",
        "reggaeton": "reggaeton, dembow rhythm, 808 bass, urban Latin style, perreo beat, modern production",
        "son": "Cuban son montuno, tres guitar, bongos, traditional Caribbean roots, Afro-Cuban rhythms",
        "tropical": "tropical Latin music, Caribbean influence, warm production, danceable rhythms"
    }
    
    style_hint = genre_hints.get(genre.lower(), genre_hints["tropical"])
    
    # Build the enhanced prompt matching ACE-Step format
    enhanced = f"{style_hint}, {bpm} bpm, key of {key}"
    
    # Add user's custom description
    if prompt:
        enhanced = f"{prompt}, {enhanced}"
    
    return enhanced


def format_lyrics(lyrics: str) -> str:
    """
    Format lyrics for ACE-Step.
    ACE-Step expects lyrics with structure tags like [Verse], [Chorus], [Bridge]
    """
    if not lyrics or lyrics.strip() == "":
        return "[instrumental]"
    
    # If lyrics already have structure tags, return as-is
    if "[" in lyrics and "]" in lyrics:
        return lyrics
    
    # Otherwise, wrap in a generic verse structure
    lines = lyrics.strip().split("\n")
    formatted = "[Verse 1]\n"
    
    verse_count = 1
    line_count = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        formatted += line + "\n"
        line_count += 1
        
        # Add new verse tag every 4 lines
        if line_count >= 4 and line != lines[-1].strip():
            verse_count += 1
            if verse_count % 2 == 0:
                formatted += "\n[Chorus]\n"
            else:
                formatted += f"\n[Verse {(verse_count + 1) // 2}]\n"
            line_count = 0
    
    return formatted.strip()


async def get_generation_status(job_id: str) -> Dict:
    """Check status of generation by looking for output file"""
    audio_path = OUTPUT_DIR / f"{job_id}.wav"
    
    if audio_path.exists():
        return {
            "job_id": job_id,
            "status": "completed",
            "audio_path": str(audio_path),
            "audio_url": f"/audio/{job_id}.wav"
        }
    
    return {
        "job_id": job_id,
        "status": "processing"
    }


# ============================================================================
# ADVANCED FEATURES (Variations, Repaint, Edit)
# ============================================================================

async def generate_variations(
    prompt: str,
    genre: str,
    count: int = 3,
    antigravity_levels: List[int] = None,
    base_seed: int = -1
) -> List[Dict]:
    """
    Generate multiple variations of a song with different antigravity levels.
    Great for A/B testing different creative intensities.
    """
    if antigravity_levels is None:
        antigravity_levels = [25, 50, 75]  # Traditional, Balanced, Creative
    
    results = []
    base_seed = base_seed if base_seed > 0 else random.randint(1, 999999)
    
    for i, level in enumerate(antigravity_levels[:count]):
        result = await generate_music(
            prompt=prompt,
            genre=genre,
            antigravity=level,
            seed=base_seed + i  # Related but different seeds
        )
        result["variation"] = i + 1
        result["variation_seed"] = base_seed + i
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
        "description": "Bachata romántica tradicional para enamorar",
        "prompt_hint": "romantic slow bachata, heartfelt lyrics, smooth guitar"
    },
    "bachata_moderna": {
        "genre": "bachata",
        "bpm": 140,
        "key": "Em",
        "antigravity": 60,
        "description": "Bachata moderna con toques urbanos",
        "prompt_hint": "modern bachata, urban influences, catchy melody"
    },
    "bolero_clasico": {
        "genre": "bolero",
        "bpm": 80,
        "key": "Dm",
        "antigravity": 20,
        "description": "Bolero clásico para noches de luna",
        "prompt_hint": "classic Cuban bolero, romantic, expressive vocals"
    },
    "merengue_fiesta": {
        "genre": "merengue",
        "bpm": 160,
        "key": "C",
        "antigravity": 50,
        "description": "Merengue para bailar hasta el amanecer",
        "prompt_hint": "energetic merengue, party atmosphere, fast tempo"
    },
    "salsa_dura": {
        "genre": "salsa",
        "bpm": 180,
        "key": "G",
        "antigravity": 45,
        "description": "Salsa brava con descarga",
        "prompt_hint": "hard salsa, brass section, Cuban son influences"
    },
    "tropical_fusion": {
        "genre": "tropical",
        "bpm": 125,
        "key": "Gm",
        "antigravity": 85,
        "description": "Fusión experimental tropical",
        "prompt_hint": "experimental fusion, mixing tropical with electronic"
    },
    "cumbia_colombiana": {
        "genre": "cumbia",
        "bpm": 95,
        "key": "D",
        "antigravity": 35,
        "description": "Cumbia colombiana tradicional",
        "prompt_hint": "Colombian cumbia, accordion, guacharaca, festive"
    },
    "reggaeton_caliente": {
        "genre": "reggaeton",
        "bpm": 92,
        "key": "Fm",
        "antigravity": 55,
        "description": "Reggaeton urbano para el perreo",
        "prompt_hint": "reggaeton, dembow beat, 808 bass, urban latin"
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
        ],
        "count": len(DGB_PRESETS)
    }


def get_supported_genres() -> List[str]:
    """Get list of supported genres based on ACE-Step training data"""
    return [
        "bachata", "bolero", "merengue", "salsa", "cumbia",
        "reggaeton", "son", "tropical", "latin pop", "latin rock",
        "flamenco", "tango", "bossa nova", "samba"
    ]
