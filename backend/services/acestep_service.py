"""
DGB AUDIO - ACE-Step Service (Gradio Client Integration)
=========================================================
Connects to ACE-Step Gradio server for music generation.
Uses the Gradio Client to call the Text2Music functions.

Architecture:
    Next.js (3000) → FastAPI (8000) → ACE-Step/Gradio (7870)
"""

import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import secrets
import random
import shutil

# Gradio Client for API calls
from gradio_client import Client, handle_file

# ACE-Step Gradio Configuration
ACESTEP_URL = os.getenv("ACESTEP_URL", "http://localhost:7870")

# Output directory for generated audio
OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated_audio"
OUTPUT_DIR.mkdir(exist_ok=True)

# Gradio client singleton
_client = None


def get_gradio_client() -> Client:
    """Get or create Gradio client connection"""
    global _client
    if _client is None:
        _client = Client(ACESTEP_URL)
    return _client


# ============================================================================
# ANTIGRAVITY ENGINE (Maps 0-100 slider to ACE-Step parameters)
# ============================================================================

def calculate_antigravity_params(antigravity_level: int) -> Dict[str, Any]:
    """
    Convert Antigravity slider (0-100) to ACE-Step generation parameters.
    
    - 0-20: Tradicional - Sonido auténtico y fiel al género
    - 20-50: Balanceado - Equilibrio entre tradición e innovación
    - 50-80: Creativo - Explorando nuevos territorios
    - 80-100: Experimental - ¡Rompiendo todas las reglas!
    """
    level = max(0, min(100, antigravity_level))
    
    # Map to ACE-Step parameters
    if level < 20:
        guidance_scale = 7.0
        infer_step = 27  # Fast, consistent
        omega_scale = 5.0
    elif level < 50:
        guidance_scale = 5.0 + (level - 20) / 30 * 3.0
        infer_step = 40
        omega_scale = 7.0
    elif level < 80:
        guidance_scale = 8.0 + (level - 50) / 30 * 4.0
        infer_step = 60
        omega_scale = 10.0
    else:
        guidance_scale = 12.0 + (level - 80) / 20 * 3.0
        infer_step = 100
        omega_scale = 13.0
    
    return {
        "guidance_scale": round(guidance_scale, 2),
        "infer_step": int(infer_step),
        "omega_scale": round(omega_scale, 2),
        "scheduler_type": "euler",
        "cfg_type": "apg",
        "antigravity_level": level,
        "mode": get_antigravity_mode_name(level)
    }


def get_antigravity_mode_name(level: int) -> str:
    if level < 20:
        return "Tradicional"
    elif level < 50:
        return "Balanceado"
    elif level < 80:
        return "Creativo"
    else:
        return "Experimental"


# ============================================================================
# HEALTH CHECK
# ============================================================================

def check_acestep_health() -> Dict:
    """Check if ACE-Step Gradio server is running"""
    try:
        client = get_gradio_client()
        # Try to get API info
        return {
            "connected": True,
            "status": "healthy",
            "url": ACESTEP_URL,
            "message": "ACE-Step Gradio server connected"
        }
    except Exception as e:
        return {
            "connected": False,
            "status": "offline",
            "url": ACESTEP_URL,
            "error": str(e),
            "message": "Run: acestep --bf16 false --port 7870"
        }


# ============================================================================
# MUSIC GENERATION
# ============================================================================

def generate_music(
    prompt: str,
    lyrics: str = "",
    duration: float = 60.0,
    antigravity: int = 50,
    seed: int = -1
) -> Dict:
    """
    Generate music using ACE-Step via Gradio Client.
    
    Args:
        prompt: Style tags (e.g., "bachata, romantic, guitar, bongos")
        lyrics: Lyrics with [Verse], [Chorus] tags
        duration: Duration in seconds (max 240)
        antigravity: Creativity level (0-100)
        seed: Random seed (-1 for random)
    
    Returns:
        Dict with audio path and generation details
    """
    # Calculate Antigravity parameters
    params = calculate_antigravity_params(antigravity)
    
    # Create job ID
    job_id = f"dgb_{secrets.token_hex(8)}"
    
    # Generate seed if random
    actual_seed = seed if seed > 0 else random.randint(1, 999999)
    
    try:
        client = get_gradio_client()
        
        # Call ACE-Step Text2Music endpoint
        # Based on Gradio interface: (tags, lyrics, duration, ..., guidance_scale, infer_step, ...)
        result = client.predict(
            # Basic inputs
            prompt,                          # Tags/prompt
            lyrics if lyrics else "[instrumental]",  # Lyrics
            duration,                        # Audio duration
            # Generation parameters
            params["infer_step"],           # Inference steps
            params["guidance_scale"],       # Guidance scale
            params["scheduler_type"],       # Scheduler type
            params["cfg_type"],             # CFG type
            params["omega_scale"],          # Omega scale
            str(actual_seed),               # Manual seeds
            0.5,                            # guidance_interval
            0.0,                            # guidance_interval_decay
            3.0,                            # min_guidance_scale
            True,                           # use_erg_tag
            True,                           # use_erg_lyric
            True,                           # use_erg_diffusion
            "60, 80",                       # oss_steps
            0.0,                            # guidance_scale_text
            0.0,                            # guidance_scale_lyric
            fn_index=0                      # Text2Music function
        )
        
        # Result is typically a tuple with (audio_path, ...)
        audio_path = result if isinstance(result, str) else result[0]
        
        # Copy to our output directory
        if audio_path and os.path.exists(audio_path):
            output_path = OUTPUT_DIR / f"{job_id}.wav"
            shutil.copy(audio_path, output_path)
            audio_path = str(output_path)
        
        return {
            "success": True,
            "job_id": job_id,
            "status": "completed",
            "audio_path": audio_path,
            "audio_url": f"/api/audio/{job_id}.wav",
            "antigravity_params": params,
            "prompt_used": prompt,
            "duration": duration,
            "seed": actual_seed
        }
        
    except Exception as e:
        return {
            "success": False,
            "job_id": job_id,
            "status": "error",
            "error": str(e),
            "message": "Check if ACE-Step is running on port 7870"
        }


async def generate_music_async(
    prompt: str,
    lyrics: str = "",
    duration: float = 60.0,
    antigravity: int = 50,
    seed: int = -1
) -> Dict:
    """Async wrapper for generate_music"""
    return await asyncio.to_thread(
        generate_music,
        prompt=prompt,
        lyrics=lyrics,
        duration=duration,
        antigravity=antigravity,
        seed=seed
    )


# ============================================================================
# DGB TROPICAL MUSIC PRESETS
# ============================================================================

DGB_PRESETS = {
    "bachata_romantica": {
        "prompt": "bachata, romantic, smooth guitar, bongos, güira, Dominican style, sensual",
        "bpm": 130,
        "key": "Am",
        "antigravity": 30,
        "description": "Bachata romántica tradicional para enamorar"
    },
    "bachata_moderna": {
        "prompt": "bachata, modern, urban influences, catchy melody, guitar, drums",
        "bpm": 140,
        "key": "Em",
        "antigravity": 60,
        "description": "Bachata moderna con toques urbanos"
    },
    "bolero_clasico": {
        "prompt": "bolero, slow romantic ballad, expressive guitar, emotional strings, Cuban",
        "bpm": 80,
        "key": "Dm",
        "antigravity": 20,
        "description": "Bolero clásico para noches de luna"
    },
    "merengue_fiesta": {
        "prompt": "Dominican merengue, fast accordion, tambora drum, party atmosphere",
        "bpm": 160,
        "key": "C",
        "antigravity": 50,
        "description": "Merengue para bailar hasta el amanecer"
    },
    "salsa_dura": {
        "prompt": "Cuban salsa, son, bright brass, clave rhythm, congas, piano montuno",
        "bpm": 180,
        "key": "G",
        "antigravity": 45,
        "description": "Salsa brava con descarga"
    },
    "cumbia_colombiana": {
        "prompt": "Colombian cumbia, accordion melody, guacharaca, tropical, festive",
        "bpm": 95,
        "key": "D",
        "antigravity": 35,
        "description": "Cumbia colombiana tradicional"
    },
    "reggaeton_caliente": {
        "prompt": "reggaeton, dembow rhythm, 808 bass, urban Latin, perreo beat",
        "bpm": 92,
        "key": "Fm",
        "antigravity": 55,
        "description": "Reggaeton urbano para el perreo"
    },
    "tropical_fusion": {
        "prompt": "tropical fusion, experimental, Latin electronic, Caribbean, innovative",
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
        "presets": [{"id": k, **v} for k, v in DGB_PRESETS.items()],
        "count": len(DGB_PRESETS)
    }


def generate_from_preset(
    preset_name: str,
    lyrics: str = "",
    duration: float = 60.0,
    custom_prompt: str = ""
) -> Dict:
    """Generate music using a DGB preset"""
    preset = get_preset(preset_name)
    
    # Combine preset prompt with custom
    full_prompt = preset["prompt"]
    if custom_prompt:
        full_prompt = f"{custom_prompt}, {full_prompt}"
    
    return generate_music(
        prompt=full_prompt,
        lyrics=lyrics,
        duration=duration,
        antigravity=preset["antigravity"]
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_lyrics(lyrics: str) -> str:
    """Format lyrics for ACE-Step"""
    if not lyrics or lyrics.strip() == "":
        return "[instrumental]"
    
    if "[" in lyrics and "]" in lyrics:
        return lyrics
    
    # Wrap in verse structure
    lines = lyrics.strip().split("\n")
    formatted = "[Verse 1]\n" + "\n".join(lines)
    return formatted


def get_generated_audio(job_id: str) -> Optional[str]:
    """Get path to generated audio file"""
    audio_path = OUTPUT_DIR / f"{job_id}.wav"
    if audio_path.exists():
        return str(audio_path)
    return None


def list_generated_audio(limit: int = 20) -> List[Dict]:
    """List recent generated audio files"""
    audio_files = []
    for f in sorted(OUTPUT_DIR.glob("*.wav"), key=os.path.getmtime, reverse=True)[:limit]:
        audio_files.append({
            "job_id": f.stem,
            "path": str(f),
            "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
            "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })
    return audio_files
