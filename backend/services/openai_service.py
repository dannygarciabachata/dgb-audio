"""
DGB AUDIO - OpenAI Service
==========================
Integration with OpenAI APIs for audio analysis and processing.
"""

import os
from typing import Optional, List, Dict


def test_connection(api_key: str) -> List[str]:
    """Test connection to OpenAI API and return available models"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # List available models
        models = client.models.list()
        audio_models = [m.id for m in models.data if 'whisper' in m.id.lower() or 'audio' in m.id.lower()]
        
        return audio_models if audio_models else ["gpt-4", "gpt-3.5-turbo"]
    except ImportError:
        raise Exception("OpenAI library not installed. Run: pip install openai")
    except Exception as e:
        raise Exception(f"Failed to connect to OpenAI: {str(e)}")


def transcribe_audio(api_key: str, audio_path: str) -> Dict:
    """
    Transcribe audio using OpenAI Whisper.
    Useful for analyzing vocal samples or getting timing information.
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment", "word"]
            )
        
        return {
            "text": transcript.text,
            "duration": transcript.duration,
            "segments": transcript.segments if hasattr(transcript, 'segments') else [],
            "words": transcript.words if hasattr(transcript, 'words') else []
        }
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")


def analyze_music_description(api_key: str, description: str) -> Dict:
    """
    Analyze a music description and extract parameters using GPT.
    Example: "bachata romántica con solo de requinto en Mi mayor a 120 BPM"
    Returns structured data: genre, key, bpm, instruments, mood
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        system_prompt = """You are a music analysis assistant for DGB AUDIO, specializing in Latin music.
        Analyze the user's music description and extract:
        - genre: bachata, salsa, merengue, bolero, or generic
        - key: musical key (e.g., "E major", "C minor")
        - bpm: tempo in BPM (default 120 if not specified)
        - instruments: list of instruments mentioned
        - mood: emotional tone (romantic, energetic, melancholic, etc.)
        - special_instructions: any specific requests
        
        Return as JSON only, no additional text."""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": description}
            ],
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Analysis failed: {str(e)}")


def generate_arrangement_prompt(api_key: str, params: Dict) -> str:
    """
    Generate a detailed arrangement prompt based on parameters.
    Used to create specific instructions for the music generation engine.
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        system_prompt = """You are a professional Latin music arranger for DGB AUDIO.
        Based on the given parameters, create a detailed bar-by-bar arrangement description
        that can be used to generate MIDI tracks.
        
        Include:
        - Structure (intro, verse, chorus, etc.)
        - Instrument entries and exits
        - Dynamic changes
        - Key moments and transitions
        
        Be specific about timing (bar numbers) and techniques (picado, mordentes, etc.)."""
        
        user_prompt = f"""Create an arrangement for:
        Genre: {params.get('genre', 'bachata')}
        Key: {params.get('key', 'E major')}
        BPM: {params.get('bpm', 120)}
        Length: {params.get('bars', 16)} bars
        Mood: {params.get('mood', 'romantic')}
        Special: {params.get('special_instructions', 'none')}"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Arrangement generation failed: {str(e)}")


class OpenAIService:
    """Main service class for OpenAI integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    def transcribe(self, audio_path: str) -> Dict:
        """Transcribe audio file"""
        return transcribe_audio(self.api_key, audio_path)
    
    def analyze_description(self, text: str) -> Dict:
        """Parse music description into parameters"""
        return analyze_music_description(self.api_key, text)
    
    def generate_arrangement(self, params: Dict) -> str:
        """Create detailed arrangement from parameters"""
        return generate_arrangement_prompt(self.api_key, params)
    
    def test(self) -> List[str]:
        """Test API connection"""
        return test_connection(self.api_key)
