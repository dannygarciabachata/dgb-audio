"""
DGB AUDIO - Audio Processor
===========================
Audio processing utilities for sample management and MIDI conversion.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json


def get_audio_info(file_path: str) -> Dict:
    """
    Get basic audio file information.
    Returns duration, sample rate, channels.
    """
    try:
        import librosa
        y, sr = librosa.load(file_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        
        return {
            "duration": round(duration, 3),
            "sample_rate": sr,
            "samples": len(y),
            "format": Path(file_path).suffix.lower()
        }
    except ImportError:
        # Fallback without librosa
        import wave
        try:
            with wave.open(file_path, 'r') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)
                return {
                    "duration": round(duration, 3),
                    "sample_rate": rate,
                    "samples": frames,
                    "format": ".wav"
                }
        except:
            return {"duration": 0, "sample_rate": 48000, "samples": 0, "format": "unknown"}


def analyze_audio(file_path: str) -> Dict:
    """
    Analyze audio for pitch, tempo, and other musical features.
    """
    try:
        import librosa
        import numpy as np
        
        # Load audio
        y, sr = librosa.load(file_path, sr=None)
        
        # Basic info
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Pitch detection (fundamental frequency)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        avg_pitch = np.mean(pitch_values) if pitch_values else 0
        
        # Convert frequency to note name
        if avg_pitch > 0:
            midi_note = librosa.hz_to_midi(avg_pitch)
            note_name = librosa.midi_to_note(int(midi_note))
        else:
            midi_note = 0
            note_name = "Unknown"
        
        # Tempo detection
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # Onset detection (note attacks)
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        
        # RMS energy (dynamics)
        rms = librosa.feature.rms(y=y)[0]
        avg_rms = float(np.mean(rms))
        max_rms = float(np.max(rms))
        
        return {
            "duration": round(duration, 3),
            "sample_rate": sr,
            "pitch": {
                "frequency_hz": round(avg_pitch, 2),
                "midi_note": int(midi_note) if midi_note > 0 else None,
                "note_name": note_name
            },
            "tempo": {
                "bpm": round(float(tempo), 1),
                "beat_count": len(beats)
            },
            "onsets": {
                "count": len(onset_times),
                "times": [round(t, 3) for t in onset_times[:20]]  # First 20 onsets
            },
            "dynamics": {
                "average_rms": round(avg_rms, 4),
                "peak_rms": round(max_rms, 4)
            }
        }
    except ImportError:
        return {
            "error": "librosa not installed. Run: pip install librosa",
            "duration": 0
        }
    except Exception as e:
        return {
            "error": str(e),
            "duration": 0
        }


def audio_to_midi(file_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert an audio file to MIDI based on pitch detection.
    Returns path to generated MIDI file.
    """
    try:
        import librosa
        import numpy as np
        from midiutil import MIDIFile
        
        # Load audio
        y, sr = librosa.load(file_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Detect pitches frame by frame
        hop_length = 512
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=hop_length)
        
        # Get onsets for note segmentation
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length)
        
        if len(onset_frames) == 0:
            # No onsets detected, create single note
            onset_frames = [0]
        
        # Add end frame
        end_frame = pitches.shape[1]
        onset_frames = list(onset_frames) + [end_frame]
        
        # Create MIDI file
        midi = MIDIFile(1)
        track = 0
        channel = 0
        tempo = 120  # Default tempo
        midi.addTempo(track, 0, tempo)
        midi.addProgramChange(track, channel, 0, 24)  # Nylon guitar
        
        # Estimate tempo from audio
        estimated_tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if estimated_tempo > 0:
            tempo = float(estimated_tempo)
            midi.addTempo(track, 0, tempo)
        
        # Convert frames to beats
        def frame_to_beat(frame):
            time_sec = librosa.frames_to_time(frame, sr=sr, hop_length=hop_length)
            return time_sec * (tempo / 60)
        
        # Extract notes from each onset segment
        notes_added = 0
        for i in range(len(onset_frames) - 1):
            start_frame = onset_frames[i]
            end_frame = onset_frames[i + 1]
            
            # Find dominant pitch in this segment
            segment_pitches = pitches[:, start_frame:end_frame]
            segment_mags = magnitudes[:, start_frame:end_frame]
            
            # Get average pitch weighted by magnitude
            pitch_list = []
            for t in range(segment_pitches.shape[1]):
                idx = segment_mags[:, t].argmax()
                p = segment_pitches[idx, t]
                if p > 0:
                    pitch_list.append(p)
            
            if pitch_list:
                avg_freq = np.median(pitch_list)
                if avg_freq > 20:  # Filter out very low frequencies
                    midi_note = int(librosa.hz_to_midi(avg_freq))
                    
                    # Clamp to valid MIDI range
                    midi_note = max(0, min(127, midi_note))
                    
                    # Calculate timing
                    start_beat = frame_to_beat(start_frame)
                    end_beat = frame_to_beat(end_frame)
                    duration_beats = max(0.1, end_beat - start_beat)
                    
                    # Calculate velocity from RMS
                    segment_audio = y[int(start_frame * hop_length):int(end_frame * hop_length)]
                    if len(segment_audio) > 0:
                        rms = np.sqrt(np.mean(segment_audio**2))
                        velocity = int(min(127, max(30, rms * 1000)))
                    else:
                        velocity = 80
                    
                    midi.addNote(track, channel, midi_note, start_beat, duration_beats, velocity)
                    notes_added += 1
        
        # Generate output path
        if output_path is None:
            input_path = Path(file_path)
            output_path = str(input_path.parent / f"{input_path.stem}_converted.mid")
        
        # Write MIDI file
        with open(output_path, 'wb') as f:
            midi.writeFile(f)
        
        print(f"✓ Converted {file_path} to MIDI: {notes_added} notes")
        return output_path
        
    except ImportError as e:
        raise Exception(f"Missing dependency: {e}. Run: pip install librosa midiutil numpy")
    except Exception as e:
        raise Exception(f"Conversion failed: {str(e)}")


def normalize_sample(file_path: str, target_sr: int = 48000) -> str:
    """
    Normalize an audio sample to target sample rate and level.
    """
    try:
        import librosa
        import soundfile as sf
        import numpy as np
        
        # Load audio
        y, sr = librosa.load(file_path, sr=target_sr)
        
        # Normalize amplitude
        max_val = np.max(np.abs(y))
        if max_val > 0:
            y = y / max_val * 0.9  # Normalize to 90% to avoid clipping
        
        # Trim silence
        y, _ = librosa.effects.trim(y, top_db=30)
        
        # Generate output path
        input_path = Path(file_path)
        output_path = str(input_path.parent / f"{input_path.stem}_normalized.wav")
        
        # Save
        sf.write(output_path, y, target_sr)
        
        return output_path
    except ImportError:
        raise Exception("Missing dependencies. Run: pip install librosa soundfile numpy")


def slice_sample(
    file_path: str, 
    output_dir: str,
    min_duration: float = 0.1,
    max_duration: float = 2.0
) -> List[str]:
    """
    Slice an audio file into individual notes based on onset detection.
    Useful for creating sample libraries from full recordings.
    """
    try:
        import librosa
        import soundfile as sf
        import numpy as np
        
        # Load audio
        y, sr = librosa.load(file_path, sr=None)
        
        # Detect onsets
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_samples = librosa.frames_to_samples(onset_frames)
        
        # Add start and end
        onset_samples = np.concatenate([[0], onset_samples, [len(y)]])
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Slice and save
        output_files = []
        input_name = Path(file_path).stem
        
        for i in range(len(onset_samples) - 1):
            start = onset_samples[i]
            end = onset_samples[i + 1]
            
            # Get slice
            slice_audio = y[start:end]
            duration = len(slice_audio) / sr
            
            # Filter by duration
            if min_duration <= duration <= max_duration:
                output_path = str(Path(output_dir) / f"{input_name}_slice_{i:03d}.wav")
                sf.write(output_path, slice_audio, sr)
                output_files.append(output_path)
        
        return output_files
    except ImportError:
        raise Exception("Missing dependencies. Run: pip install librosa soundfile numpy")


# Initialization - create empty __init__.py for package
init_file = Path(__file__).parent / "__init__.py"
if not init_file.exists():
    init_file.touch()
