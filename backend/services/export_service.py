"""
DGB AUDIO - Export Service
===========================
Professional export system with DAW compatibility.
Supports MIDI, WAV, AIFF, MP3 with format recommendations per DAW.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import zipfile
import secrets

# Try to import audio processing libraries
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# Export directory
EXPORT_DIR = Path(__file__).parent.parent.parent / "exports"
EXPORT_DIR.mkdir(exist_ok=True)


# ============================================================================
# DAW CONFIGURATION
# ============================================================================

DAW_CONFIGS = {
    "protools": {
        "name": "Pro Tools",
        "icon": "🎚️",
        "audio_format": "wav",
        "sample_rate": 48000,
        "bit_depth": 24,
        "midi": True,
        "description": "Estándar de la industria para grabación y mezcla profesional",
        "import_instructions": """
1. Abre Pro Tools y crea una nueva sesión a 48kHz/24bit
2. File → Import → Session Data (para importar toda la sesión)
   O arrastra los archivos WAV/MIDI directamente a las pistas
3. Los archivos MIDI se importan en pistas de instrumento
4. Los archivos WAV van a pistas de audio
5. Ajusta el tempo de la sesión al BPM indicado en project_info.json
        """,
        "extensions": [".wav", ".mid", ".ptx"]
    },
    "logic": {
        "name": "Logic Pro",
        "icon": "🍎",
        "audio_format": "aiff",
        "sample_rate": 48000,
        "bit_depth": 24,
        "midi": True,
        "description": "DAW profesional de Apple para macOS",
        "import_instructions": """
1. Abre Logic Pro y crea un nuevo proyecto
2. File → Import → Audio File (para WAV/AIFF)
3. File → Import → MIDI File (para archivos MIDI)
4. O simplemente arrastra todos los archivos al área de pistas
5. Logic detectará el tempo automáticamente
        """,
        "extensions": [".aiff", ".mid", ".logicx"]
    },
    "ableton": {
        "name": "Ableton Live",
        "icon": "🔶",
        "audio_format": "wav",
        "sample_rate": 44100,
        "bit_depth": 24,
        "midi": True,
        "description": "Perfecto para producción electrónica y performance en vivo",
        "import_instructions": """
1. Abre Ableton Live y crea un nuevo proyecto
2. Arrastra los archivos WAV al área de clips o al Arrangement
3. Los archivos MIDI se arrastran a pistas MIDI con instrumentos
4. Ajusta el tempo del proyecto en la esquina superior izquierda
5. Activa Warp para sincronización automática
        """,
        "extensions": [".wav", ".mid", ".als"]
    },
    "flstudio": {
        "name": "FL Studio",
        "icon": "🍊",
        "audio_format": "wav",
        "sample_rate": 44100,
        "bit_depth": 32,
        "midi": True,
        "description": "Popular para hip-hop, trap y música electrónica",
        "import_instructions": """
1. Abre FL Studio y crea un nuevo proyecto
2. Arrastra los archivos WAV al Playlist
3. Para MIDI: File → Import → MIDI File
4. Los MIDI se cargan en el Channel Rack
5. Ajusta el tempo en el panel de transporte
        """,
        "extensions": [".wav", ".mid", ".flp"]
    },
    "cubase": {
        "name": "Cubase",
        "icon": "🎹",
        "audio_format": "wav",
        "sample_rate": 48000,
        "bit_depth": 24,
        "midi": True,
        "description": "DAW versátil de Steinberg para composición y producción",
        "import_instructions": """
1. Abre Cubase y crea un nuevo proyecto a 48kHz
2. File → Import → Audio File para importar WAV
3. File → Import → MIDI File para MIDI
4. Los archivos se colocan en pistas nuevas
5. Project → Tempo Track para ajustar el tempo
        """,
        "extensions": [".wav", ".mid"]
    },
    "garageband": {
        "name": "GarageBand",
        "icon": "🎸",
        "audio_format": "aiff",
        "sample_rate": 44100,
        "bit_depth": 16,
        "midi": True,
        "description": "DAW gratuito de Apple, ideal para principiantes",
        "import_instructions": """
1. Abre GarageBand y crea un nuevo proyecto
2. Arrastra los archivos de audio a las pistas
3. Los archivos MIDI se pueden arrastrar a pistas de instrumento
4. GarageBand ajustará automáticamente al tempo del proyecto
        """,
        "extensions": [".aiff", ".mid"]
    },
    "reaper": {
        "name": "Reaper",
        "icon": "🎧",
        "audio_format": "wav",
        "sample_rate": 48000,
        "bit_depth": 24,
        "midi": True,
        "description": "DAW económico y potente para cualquier género",
        "import_instructions": """
1. Abre Reaper y crea un nuevo proyecto
2. Insert → Media File para importar audio
3. Insert → New MIDI item y pega contenido MIDI
4. O arrastra archivos directamente a la timeline
        """,
        "extensions": [".wav", ".mid"]
    },
    "studio_one": {
        "name": "Studio One",
        "icon": "🔷",
        "audio_format": "wav",
        "sample_rate": 48000,
        "bit_depth": 24,
        "midi": True,
        "description": "DAW moderno de PreSonus con workflow intuitivo",
        "import_instructions": """
1. Abre Studio One y crea una nueva canción
2. Arrastra archivos de audio al área de pistas
3. Los MIDI se importan con Song → Import MIDI File
4. Tempo se ajusta en la barra de transporte
        """,
        "extensions": [".wav", ".mid"]
    }
}

# Audio format specifications
AUDIO_FORMATS = {
    "wav": {
        "name": "WAV",
        "extension": ".wav",
        "description": "Sin compresión, máxima calidad",
        "use_case": "Producción profesional, mezcla, mastering"
    },
    "aiff": {
        "name": "AIFF",
        "extension": ".aiff",
        "description": "Sin compresión, estándar Apple",
        "use_case": "Logic Pro, GarageBand, sistemas Mac"
    },
    "mp3": {
        "name": "MP3",
        "extension": ".mp3",
        "description": "Comprimido, archivo pequeño",
        "use_case": "Escucha, compartir, demos"
    },
    "flac": {
        "name": "FLAC",
        "extension": ".flac",
        "description": "Compresión sin pérdida",
        "use_case": "Archivado, distribución de alta calidad"
    }
}


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def get_daw_recommendations() -> Dict:
    """Get all DAW configurations with recommendations"""
    return {
        "daws": DAW_CONFIGS,
        "formats": AUDIO_FORMATS,
        "recommended": "protools"  # Default recommendation
    }


def get_export_settings_for_daw(daw_id: str) -> Dict:
    """Get recommended export settings for a specific DAW"""
    if daw_id not in DAW_CONFIGS:
        daw_id = "protools"  # Default fallback
    
    config = DAW_CONFIGS[daw_id]
    return {
        "daw": daw_id,
        "name": config["name"],
        "audio_format": config["audio_format"],
        "sample_rate": config["sample_rate"],
        "bit_depth": config["bit_depth"],
        "extensions": config["extensions"],
        "instructions": config["import_instructions"]
    }


def create_export_package(
    project_id: str,
    project_name: str,
    tracks: List[Dict],
    daw_id: str = "protools",
    include_midi: bool = True,
    include_audio: bool = True,
    include_stems: bool = False,
    bpm: int = 120,
    key: str = "Am",
    genre: str = "bachata"
) -> Dict:
    """
    Create a complete export package for a project
    Returns path to the ZIP file
    """
    # Get DAW settings
    settings = get_export_settings_for_daw(daw_id)
    
    # Create unique export folder
    export_id = f"exp_{secrets.token_hex(8)}"
    export_folder = EXPORT_DIR / export_id
    export_folder.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    if include_midi:
        (export_folder / "midi").mkdir(exist_ok=True)
    if include_audio:
        (export_folder / "audio").mkdir(exist_ok=True)
    if include_stems:
        (export_folder / "stems").mkdir(exist_ok=True)
    
    # Project info
    project_info = {
        "project_name": project_name,
        "project_id": project_id,
        "export_date": datetime.now().isoformat(),
        "genre": genre,
        "bpm": bpm,
        "key": key,
        "time_signature": "4/4",
        "target_daw": settings["name"],
        "audio_format": settings["audio_format"],
        "sample_rate": settings["sample_rate"],
        "bit_depth": settings["bit_depth"],
        "tracks": []
    }
    
    exported_files = []
    
    # Process each track
    for track in tracks:
        track_info = {
            "name": track.get("name", "Track"),
            "instrument": track.get("instrument", "unknown"),
            "files": []
        }
        
        # Export MIDI if available
        if include_midi and track.get("midi_path"):
            midi_src = Path(track["midi_path"])
            if midi_src.exists():
                midi_dest = export_folder / "midi" / f"{track['name']}.mid"
                shutil.copy(midi_src, midi_dest)
                track_info["files"].append(f"midi/{track['name']}.mid")
                exported_files.append(str(midi_dest))
        
        # Export audio if available
        if include_audio and track.get("audio_path"):
            audio_src = Path(track["audio_path"])
            if audio_src.exists():
                # Convert to target format if needed
                audio_dest = export_folder / "audio" / f"{track['name']}.{settings['audio_format']}"
                
                if PYDUB_AVAILABLE and audio_src.suffix != f".{settings['audio_format']}":
                    # Convert audio format
                    audio = AudioSegment.from_file(str(audio_src))
                    audio.export(
                        str(audio_dest),
                        format=settings["audio_format"],
                        parameters=["-ar", str(settings["sample_rate"])]
                    )
                else:
                    shutil.copy(audio_src, audio_dest)
                
                track_info["files"].append(f"audio/{track['name']}.{settings['audio_format']}")
                exported_files.append(str(audio_dest))
        
        project_info["tracks"].append(track_info)
    
    # Save project info
    with open(export_folder / "project_info.json", 'w') as f:
        json.dump(project_info, f, indent=2)
    
    # Create README with import instructions
    readme_content = f"""
================================================================================
DGB AUDIO - {project_name}
================================================================================

Género: {genre.title()}
Tempo: {bpm} BPM
Tonalidad: {key}
Exportado para: {settings['name']}

--------------------------------------------------------------------------------
INSTRUCCIONES DE IMPORTACIÓN - {settings['name'].upper()}
--------------------------------------------------------------------------------
{settings['instructions']}

--------------------------------------------------------------------------------
CONTENIDO DEL PAQUETE
--------------------------------------------------------------------------------
"""
    
    if include_midi:
        readme_content += "\n📁 midi/\n   Archivos MIDI para cada instrumento\n"
    if include_audio:
        readme_content += f"\n📁 audio/\n   Archivos de audio en formato {settings['audio_format'].upper()}\n"
    if include_stems:
        readme_content += "\n📁 stems/\n   Stems mezclados (melodía, percusión, etc.)\n"
    
    readme_content += f"""
--------------------------------------------------------------------------------
INFORMACIÓN TÉCNICA
--------------------------------------------------------------------------------
Sample Rate: {settings['sample_rate']} Hz
Bit Depth: {settings['bit_depth']}-bit
Formato: {settings['audio_format'].upper()}

--------------------------------------------------------------------------------
© DGB AUDIO - La Inteligencia de la Música Tropical
www.dgbaudio.com
================================================================================
"""
    
    with open(export_folder / "README.txt", 'w') as f:
        f.write(readme_content)
    
    # Create ZIP file
    zip_filename = f"DGB_{project_name.replace(' ', '_')}_{daw_id}.zip"
    zip_path = EXPORT_DIR / zip_filename
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(export_folder):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(export_folder)
                zipf.write(file_path, arcname)
    
    # Clean up folder (keep only ZIP)
    shutil.rmtree(export_folder)
    
    return {
        "success": True,
        "export_id": export_id,
        "filename": zip_filename,
        "path": str(zip_path),
        "size_bytes": zip_path.stat().st_size,
        "size_mb": round(zip_path.stat().st_size / (1024 * 1024), 2),
        "daw": settings["name"],
        "format": settings["audio_format"],
        "tracks_exported": len(tracks),
        "files_exported": len(exported_files)
    }


def export_single_track(
    track_path: str,
    track_name: str,
    daw_id: str = "protools",
    output_format: Optional[str] = None
) -> Dict:
    """Export a single track in the specified format"""
    settings = get_export_settings_for_daw(daw_id)
    target_format = output_format or settings["audio_format"]
    
    src_path = Path(track_path)
    if not src_path.exists():
        return {"error": f"Source file not found: {track_path}"}
    
    # Create output path
    output_filename = f"{track_name}.{target_format}"
    output_path = EXPORT_DIR / output_filename
    
    # Convert if needed
    if PYDUB_AVAILABLE and src_path.suffix[1:] != target_format:
        audio = AudioSegment.from_file(str(src_path))
        audio.export(
            str(output_path),
            format=target_format,
            parameters=["-ar", str(settings["sample_rate"])]
        )
    else:
        shutil.copy(src_path, output_path)
    
    return {
        "success": True,
        "filename": output_filename,
        "path": str(output_path),
        "format": target_format,
        "size_bytes": output_path.stat().st_size
    }


def get_export_history(limit: int = 20) -> List[Dict]:
    """Get list of recent exports"""
    exports = []
    
    if EXPORT_DIR.exists():
        for f in sorted(EXPORT_DIR.glob("*.zip"), key=os.path.getmtime, reverse=True)[:limit]:
            exports.append({
                "filename": f.name,
                "path": str(f),
                "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
    
    return exports


def cleanup_old_exports(max_age_days: int = 7):
    """Remove exports older than specified days"""
    if not EXPORT_DIR.exists():
        return 0
    
    removed = 0
    cutoff = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
    
    for f in EXPORT_DIR.glob("*.zip"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
            removed += 1
    
    return removed
