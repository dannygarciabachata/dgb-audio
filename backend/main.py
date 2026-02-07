"""
DGB AUDIO - FastAPI Backend
===========================
Main server for admin dashboard, API management, and sample processing.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import os
import json
from pathlib import Path

# Initialize database on import
from database import init_db, get_db_stats, migrate_from_json

# Initialize app
app = FastAPI(
    title="DGB AUDIO API",
    description="Backend for DGB AUDIO - La Inteligencia de la Música Tropical",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
BASE_DIR = Path(__file__).parent.parent
SAMPLES_DIR = BASE_DIR / "samples"
CONFIG_DIR = BASE_DIR / "backend" / "config"

# Ensure directories exist
SAMPLES_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# Config file path
CONFIG_FILE = CONFIG_DIR / "settings.json"


# ============================================================================
# MODELS
# ============================================================================

class APIConfig(BaseModel):
    openai_api_key: Optional[str] = None
    default_genre: str = "bachata"
    default_bpm: int = 115
    sample_rate: int = 48000

class SampleMetadata(BaseModel):
    id: str
    filename: str
    instrument: str
    category: str
    duration: float
    sample_rate: int
    tags: List[str] = []

class ConversionRequest(BaseModel):
    sample_id: str
    output_format: str = "midi"  # midi, wav, both


# Auth models
class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    plan: str = "starter"

class UserLogin(BaseModel):
    email: str
    password: str

class UserAPIKey(BaseModel):
    api_key: str


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.post("/api/auth/register")
async def register(user: UserRegister):
    """Register a new user"""
    from services.auth_service import register_user
    result = register_user(user.email, user.password, user.name, user.plan)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/api/auth/login")
async def login(user: UserLogin):
    """Login and get auth token"""
    from services.auth_service import login_user
    result = login_user(user.email, user.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result


@app.get("/api/auth/me")
async def get_current_user(token: str):
    """Get current user info from token"""
    from services.auth_service import get_user_by_token
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"user": user}


@app.post("/api/auth/api-key")
async def set_api_key(token: str, data: UserAPIKey):
    """Set user's OpenAI API key (BYOK)"""
    from services.auth_service import get_user_by_token, set_user_api_key
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    result = set_user_api_key(user["email"], data.api_key)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/api/auth/usage")
async def get_usage(token: str):
    """Get user's API usage statistics"""
    from services.auth_service import get_user_by_token, get_user_usage
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    usage = get_user_usage(user["email"])
    return {"usage": usage, "plan": user.get("plan"), "limits": user.get("limits")}


# ============================================================================
# SUPERADMIN ENDPOINTS
# ============================================================================

@app.get("/api/admin/users")
async def list_all_users(token: str):
    """List all users (SuperAdmin only)"""
    from services.auth_service import get_user_by_token, get_all_users
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = get_all_users(user["email"])
    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result


class RoleUpdate(BaseModel):
    target_email: str
    new_role: str

@app.post("/api/admin/users/role")
async def update_role(token: str, data: RoleUpdate):
    """Update user role (SuperAdmin only)"""
    from services.auth_service import get_user_by_token, update_user_role
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = update_user_role(user["email"], data.target_email, data.new_role)
    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result


class PlanUpdate(BaseModel):
    target_email: str
    new_plan: str

@app.post("/api/admin/users/plan")
async def update_plan(token: str, data: PlanUpdate):
    """Update user plan (SuperAdmin only)"""
    from services.auth_service import get_user_by_token, update_user_plan
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = update_user_plan(user["email"], data.target_email, data.new_plan)
    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return result


# ============================================================================
# SUPPORT CHAT ENDPOINTS
# ============================================================================

@app.get("/api/chat/departments")
async def get_chat_departments():
    """Get available support departments"""
    from services.support_chat import get_departments, get_quick_responses
    departments = get_departments()
    for dept in departments:
        dept["quick_responses"] = get_quick_responses(dept["id"])
    return {"departments": departments}


class ChatMessage(BaseModel):
    message: str
    department: str = "general"
    history: List[dict] = []

@app.post("/api/chat/send")
async def send_chat_message(token: str, data: ChatMessage):
    """Send message to AI support chat (uses user's API key)"""
    from services.auth_service import get_user_by_token, get_user_api_key, track_api_usage
    from services.support_chat import chat_with_support
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user's API key
    api_key = get_user_api_key(user["email"])
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    # Send to chat
    result = await chat_with_support(
        message=data.message,
        department=data.department,
        api_key=api_key,
        conversation_history=data.history
    )
    
    # Track usage if successful
    if result.get("success"):
        track_api_usage(
            user["email"],
            result.get("tokens_used", 0),
            result.get("cost_estimate", 0)
        )
    
    return result


# ============================================================================
# STRIPE PAYMENT ENDPOINTS
# ============================================================================

@app.get("/api/plans")
async def get_available_plans():
    """Get all available subscription plans"""
    from services.stripe_service import get_plans
    return {"plans": get_plans()}


class CheckoutRequest(BaseModel):
    plan: str

@app.post("/api/payments/checkout")
async def create_checkout(token: str, data: CheckoutRequest):
    """Create Stripe checkout session for subscription"""
    from services.auth_service import get_user_by_token
    from services.stripe_service import create_checkout_session
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await create_checkout_session(
        user_email=user["email"],
        user_id=user["id"],
        plan=data.plan
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.post("/api/payments/billing-portal")
async def create_portal(token: str):
    """Create Stripe billing portal session"""
    from services.auth_service import get_user_by_token
    from services.stripe_service import create_billing_portal_session
    from services.auth_service import _load_users
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    users = _load_users()
    full_user = users.get(user["email"], {})
    customer_id = full_user.get("stripe_customer_id")
    
    if not customer_id:
        raise HTTPException(status_code=400, detail="No active subscription")
    
    result = await create_billing_portal_session(customer_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.get("/api/payments/subscription")
async def get_subscription(token: str):
    """Get user's subscription status"""
    from services.auth_service import get_user_by_token
    from services.stripe_service import get_subscription_status
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return get_subscription_status(user["email"])


from fastapi import Request

@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    from services.stripe_service import handle_webhook
    
    payload = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    
    result = await handle_webhook(payload, signature)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


# ============================================================================
# CONFIG ENDPOINTS
# ============================================================================

def load_config() -> dict:
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "openai_api_key": "",
        "default_genre": "bachata",
        "default_bpm": 115,
        "sample_rate": 48000
    }

def save_config(config: dict):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


@app.get("/api/config")
async def get_config():
    """Get current configuration (masks API keys)"""
    config = load_config()
    # Mask the API key for security
    if config.get("openai_api_key"):
        key = config["openai_api_key"]
        config["openai_api_key_masked"] = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
        config["openai_api_key_set"] = True
    else:
        config["openai_api_key_masked"] = ""
        config["openai_api_key_set"] = False
    del config["openai_api_key"]
    return config


@app.post("/api/config")
async def update_config(config: APIConfig):
    """Update configuration"""
    current = load_config()
    
    if config.openai_api_key:
        current["openai_api_key"] = config.openai_api_key
    current["default_genre"] = config.default_genre
    current["default_bpm"] = config.default_bpm
    current["sample_rate"] = config.sample_rate
    
    save_config(current)
    return {"status": "success", "message": "Configuration updated"}


@app.get("/api/config/test-openai")
async def test_openai_connection():
    """Test OpenAI API connection"""
    config = load_config()
    api_key = config.get("openai_api_key")
    
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    try:
        from services.openai_service import test_connection
        result = test_connection(api_key)
        return {"status": "success", "message": "OpenAI connection successful", "models": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI connection failed: {str(e)}")


# ============================================================================
# SAMPLE LIBRARY ENDPOINTS
# ============================================================================

def get_samples_metadata() -> List[dict]:
    """Get all samples metadata"""
    metadata_file = SAMPLES_DIR / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return []

def save_samples_metadata(samples: List[dict]):
    """Save samples metadata"""
    metadata_file = SAMPLES_DIR / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(samples, f, indent=2)


@app.get("/api/samples")
async def list_samples(instrument: Optional[str] = None):
    """List all samples, optionally filtered by instrument"""
    samples = get_samples_metadata()
    if instrument:
        samples = [s for s in samples if s.get("instrument") == instrument]
    return {"samples": samples, "total": len(samples)}


@app.post("/api/samples/upload")
async def upload_sample(
    file: UploadFile = File(...),
    genre: str = "bolero",
    instrument: str = "full_mix",
    category: str = "stem",
    project: str = "default",
    tags: str = ""
):
    """Upload a new audio sample with auto-rename"""
    import uuid
    import re
    from datetime import datetime
    
    # Validate file type
    if not file.filename.lower().endswith(('.wav', '.mp3', '.aiff', '.flac')):
        raise HTTPException(status_code=400, detail="Unsupported audio format. Use WAV, MP3, AIFF, or FLAC.")
    
    # Create sample ID
    sample_id = str(uuid.uuid4())[:8]
    
    # Clean original filename for use in new name
    original_name = Path(file.filename).stem
    # Remove special characters, keep alphanumeric and spaces
    clean_name = re.sub(r'[^\w\s-]', '', original_name)
    clean_name = re.sub(r'\s+', '_', clean_name)[:30]  # Limit length
    
    # Auto-rename: {genre}_{instrument}_{original_name}_{id}.ext
    file_ext = Path(file.filename).suffix.lower()
    auto_filename = f"{genre}_{instrument}_{clean_name}_{sample_id}{file_ext}"
    
    # Create directory organized by project/genre/instrument/category
    sample_dir = SAMPLES_DIR / project / genre / instrument / category
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = sample_dir / auto_filename
    
    # Save file
    content = await file.read()
    file_size = len(content)
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Get audio info
    try:
        from services.audio_processor import get_audio_info
        audio_info = get_audio_info(str(file_path))
    except:
        audio_info = {"duration": 0, "sample_rate": 48000}
    
    # Create metadata
    metadata = {
        "id": sample_id,
        "filename": auto_filename,
        "original_filename": file.filename,
        "project": project,
        "genre": genre,
        "instrument": instrument,
        "category": category,
        "path": str(file_path.relative_to(SAMPLES_DIR)),
        "file_size_bytes": file_size,
        "duration": audio_info.get("duration", 0),
        "sample_rate": audio_info.get("sample_rate", 48000),
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "uploaded_at": datetime.now().isoformat()
    }
    
    # Add to samples list
    samples = get_samples_metadata()
    samples.append(metadata)
    save_samples_metadata(samples)
    
    return {"status": "success", "sample": metadata}


@app.delete("/api/samples/{sample_id}")
async def delete_sample(sample_id: str):
    """Delete a sample"""
    samples = get_samples_metadata()
    sample = next((s for s in samples if s["id"] == sample_id), None)
    
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    # Delete file
    file_path = SAMPLES_DIR / sample["path"]
    if file_path.exists():
        os.remove(file_path)
    
    # Remove from metadata
    samples = [s for s in samples if s["id"] != sample_id]
    save_samples_metadata(samples)
    
    return {"status": "success", "message": "Sample deleted"}


class SampleUpdate(BaseModel):
    genre: Optional[str] = None
    instrument: Optional[str] = None
    category: Optional[str] = None


@app.patch("/api/samples/{sample_id}")
async def update_sample(sample_id: str, update: SampleUpdate):
    """Update sample metadata (genre, instrument, category)"""
    samples = get_samples_metadata()
    sample_index = next((i for i, s in enumerate(samples) if s["id"] == sample_id), None)
    
    if sample_index is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    # Update fields if provided
    if update.genre:
        samples[sample_index]["genre"] = update.genre
    if update.instrument:
        samples[sample_index]["instrument"] = update.instrument
    if update.category:
        samples[sample_index]["category"] = update.category
    
    save_samples_metadata(samples)
    
    return {"status": "success", "sample": samples[sample_index]}


# ============================================================================
# AUDIO CONVERSION ENDPOINTS
# ============================================================================

@app.post("/api/convert/audio-to-midi")
async def convert_audio_to_midi(sample_id: str):
    """Convert an audio sample to MIDI"""
    samples = get_samples_metadata()
    sample = next((s for s in samples if s["id"] == sample_id), None)
    
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    try:
        from services.audio_processor import audio_to_midi
        file_path = SAMPLES_DIR / sample["path"]
        midi_path = audio_to_midi(str(file_path))
        
        return {
            "status": "success",
            "midi_path": midi_path,
            "sample_id": sample_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.get("/api/convert/analyze/{sample_id}")
async def analyze_sample(sample_id: str):
    """Analyze an audio sample (pitch, tempo, etc.)"""
    samples = get_samples_metadata()
    sample = next((s for s in samples if s["id"] == sample_id), None)
    
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    try:
        from services.audio_processor import analyze_audio
        file_path = SAMPLES_DIR / sample["path"]
        analysis = analyze_audio(str(file_path))
        
        return {
            "status": "success",
            "sample_id": sample_id,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ============================================================================
# TRAINING ENDPOINTS
# ============================================================================

@app.get("/api/training/status")
async def get_training_status():
    """Get current training status"""
    samples = get_samples_metadata()
    
    # Count samples by instrument
    by_instrument = {}
    for s in samples:
        inst = s.get("instrument", "unknown")
        by_instrument[inst] = by_instrument.get(inst, 0) + 1
    
    return {
        "total_samples": len(samples),
        "by_instrument": by_instrument,
        "training_ready": len(samples) >= 10,
        "last_training": None,
        "model_version": "1.0.0"
    }


@app.post("/api/training/prepare")
async def prepare_training_data():
    """Prepare samples for training"""
    samples = get_samples_metadata()
    
    if len(samples) < 10:
        raise HTTPException(
            status_code=400, 
            detail="Need at least 10 samples to prepare training data"
        )
    
    # Future: Actual training preparation
    return {
        "status": "success",
        "message": f"Prepared {len(samples)} samples for training",
        "samples_prepared": len(samples)
    }


# ============================================================================
# PROJECTS ENDPOINTS
# ============================================================================

@app.get("/api/projects")
async def list_projects():
    """List all projects with sample counts"""
    samples = get_samples_metadata()
    
    projects = {}
    for sample in samples:
        project = sample.get("project", "default")
        if project not in projects:
            projects[project] = {
                "name": project,
                "sample_count": 0,
                "genres": set(),
                "total_size_bytes": 0
            }
        projects[project]["sample_count"] += 1
        projects[project]["genres"].add(sample.get("genre", "unknown"))
        projects[project]["total_size_bytes"] += sample.get("file_size_bytes", 0)
    
    # Convert sets to lists for JSON
    for p in projects.values():
        p["genres"] = list(p["genres"])
        p["total_size_mb"] = round(p["total_size_bytes"] / (1024 * 1024), 2)
    
    return {"projects": list(projects.values())}


# ============================================================================
# AI GENERATION ENDPOINTS
# ============================================================================

class GenerateMIDIRequest(BaseModel):
    prompt: str
    genre: str = "bachata"
    bpm: int = 120
    key: str = "Am"
    bars: int = 8

class GenerateLyricsRequest(BaseModel):
    theme: str
    genre: str = "bachata"
    mood: str = "romantic"
    language: str = "spanish"

class AnalyzeAudioRequest(BaseModel):
    instrument: str = "guitar"
    genre: str = "bachata"

@app.post("/api/ai/generate-midi")
async def generate_midi(token: str, data: GenerateMIDIRequest):
    """Generate MIDI from text prompt using AI"""
    from services.auth_service import get_user_by_token, get_user_api_key, track_api_usage
    from services.ai_generation import generate_midi_from_prompt
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    api_key = get_user_api_key(user["email"])
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    result = await generate_midi_from_prompt(
        prompt=data.prompt,
        api_key=api_key,
        genre=data.genre,
        bpm=data.bpm,
        key=data.key,
        bars=data.bars
    )
    
    if result.get("success"):
        track_api_usage(
            user["email"],
            result.get("tokens_used", 0),
            result.get("tokens_used", 0) * 0.00003  # Approximate cost
        )
    
    return result


@app.post("/api/ai/generate-lyrics")
async def generate_lyrics(token: str, data: GenerateLyricsRequest):
    """Generate lyrics for tropical music"""
    from services.auth_service import get_user_by_token, get_user_api_key, track_api_usage
    from services.ai_generation import generate_lyrics as gen_lyrics
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    api_key = get_user_api_key(user["email"])
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    result = await gen_lyrics(
        theme=data.theme,
        api_key=api_key,
        genre=data.genre,
        mood=data.mood,
        language=data.language
    )
    
    if result.get("success"):
        track_api_usage(
            user["email"],
            result.get("tokens_used", 0),
            result.get("tokens_used", 0) * 0.00003
        )
    
    return result


@app.post("/api/ai/analyze-audio")
async def analyze_audio_endpoint(
    token: str,
    instrument: str = "guitar",
    genre: str = "bachata",
    audio: UploadFile = File(...)
):
    """Analyze recorded audio using AI"""
    from services.auth_service import get_user_by_token, get_user_api_key, track_api_usage
    from services.ai_generation import analyze_audio
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    api_key = get_user_api_key(user["email"])
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    audio_data = await audio.read()
    
    result = await analyze_audio(
        audio_data=audio_data,
        api_key=api_key,
        instrument=instrument,
        genre=genre
    )
    
    if result.get("success"):
        track_api_usage(
            user["email"],
            result.get("tokens_used", 0),
            result.get("tokens_used", 0) * 0.00003
        )
    
    return result


@app.post("/api/ai/save-composition")
async def save_composition(token: str, composition: dict):
    """Save AI-generated composition to MIDI file"""
    from services.auth_service import get_user_by_token
    from services.ai_generation import convert_to_midi_file
    from datetime import datetime
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Create output path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    genre = composition.get("genre", "bachata")
    title = composition.get("composition", {}).get("title", "untitled")
    filename = f"{genre}_{title}_{timestamp}.mid".replace(" ", "_").lower()
    output_path = SAMPLES_DIR / "generated" / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    result = convert_to_midi_file(
        composition.get("composition", {}),
        str(output_path)
    )
    
    return result


# ============================================================================
# ACE-STEP GENERATION ENDPOINTS (Antigravity Engine)
# ============================================================================

class GenerateMusicRequest(BaseModel):
    prompt: str
    lyrics: Optional[str] = ""
    genre: str = "bachata"
    bpm: int = 120
    key: str = "Am"
    duration: int = 120
    antigravity: int = 50  # 0-100 creativity level

class PresetRequest(BaseModel):
    preset: str
    prompt: str
    lyrics: Optional[str] = ""

@app.get("/api/acestep/health")
async def acestep_health():
    """Check ACE-Step server status"""
    from services.acestep_service import check_acestep_health_sync
    return check_acestep_health_sync()

@app.get("/api/acestep/presets")
async def get_presets():
    """Get all DGB music presets"""
    from services.acestep_service import list_presets
    return list_presets()

@app.get("/api/acestep/antigravity/{level}")
async def get_antigravity_params(level: int):
    """Preview Antigravity Engine parameters for a given level"""
    from services.acestep_service import calculate_antigravity_params
    return calculate_antigravity_params(level)

@app.post("/api/generate/music")
async def generate_music_endpoint(token: str, data: GenerateMusicRequest):
    """
    Generate music using ACE-Step with Antigravity Engine.
    
    The antigravity parameter (0-100) controls creativity:
    - 0-20: Traditional - Stays close to genre conventions
    - 20-50: Balanced - Some creative freedom
    - 50-80: Creative - More experimental
    - 80-100: Wild - Maximum creative chaos
    """
    from services.auth_service import get_user_by_token
    from services.acestep_service import generate_music, calculate_antigravity_params
    from database import create_composition, track_api_usage
    import secrets
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Generate music
    result = await generate_music(
        prompt=data.prompt,
        lyrics=data.lyrics,
        genre=data.genre,
        bpm=data.bpm,
        key=data.key,
        duration=data.duration,
        antigravity=data.antigravity,
        user_id=user["id"]
    )
    
    # Save to database if successful
    if result.get("success"):
        comp_id = f"comp_{secrets.token_hex(8)}"
        create_composition(
            comp_id=comp_id,
            user_id=user["id"],
            title=f"{data.genre.title()} - {data.prompt[:30]}",
            genre=data.genre,
            bpm=data.bpm,
            key=data.key,
            prompt=data.prompt,
            lyrics=data.lyrics,
            midi_path=None,
            audio_path=result.get("audio_path"),
            status="completed"
        )
        result["composition_id"] = comp_id
    
    return result

@app.post("/api/generate/preset")
async def generate_from_preset(token: str, data: PresetRequest):
    """Generate music using a DGB preset"""
    from services.auth_service import get_user_by_token
    from services.acestep_service import generate_music, get_preset
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get preset configuration
    preset = get_preset(data.preset)
    
    result = await generate_music(
        prompt=data.prompt,
        lyrics=data.lyrics,
        genre=preset["genre"],
        bpm=preset["bpm"],
        key=preset["key"],
        antigravity=preset["antigravity"],
        user_id=user["id"]
    )
    
    result["preset_used"] = data.preset
    return result

@app.get("/api/generate/status/{job_id}")
async def get_generation_status(job_id: str, token: str):
    """Get status of an ongoing music generation"""
    from services.auth_service import get_user_by_token
    from services.acestep_service import get_generation_status
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return await get_generation_status(job_id)


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

class ExportProjectRequest(BaseModel):
    project_id: str
    project_name: str
    daw: str = "protools"
    include_midi: bool = True
    include_audio: bool = True
    include_stems: bool = False
    bpm: int = 120
    key: str = "Am"
    genre: str = "bachata"

class ExportTrackRequest(BaseModel):
    track_path: str
    track_name: str
    daw: str = "protools"
    format: Optional[str] = None

@app.get("/api/export/daws")
async def get_daw_options():
    """Get all supported DAWs and their recommended settings"""
    from services.export_service import get_daw_recommendations
    return get_daw_recommendations()

@app.get("/api/export/settings/{daw_id}")
async def get_daw_settings(daw_id: str):
    """Get export settings for a specific DAW"""
    from services.export_service import get_export_settings_for_daw
    return get_export_settings_for_daw(daw_id)

@app.post("/api/export/project")
async def export_project(token: str, data: ExportProjectRequest):
    """Export entire project as ZIP with DAW-specific format"""
    from services.auth_service import get_user_by_token
    from services.export_service import create_export_package
    from database import get_connection
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get project tracks from database
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM compositions WHERE project_id = ? OR user_id = ?
        """, (data.project_id, user["id"]))
        compositions = cursor.fetchall()
    
    # Convert to track format
    tracks = []
    for comp in compositions:
        tracks.append({
            "name": comp["title"] or f"Track_{comp['id'][:8]}",
            "instrument": comp["genre"] or "mixed",
            "midi_path": comp["midi_path"],
            "audio_path": comp["audio_path"]
        })
    
    # If no compositions, create demo tracks
    if not tracks:
        tracks = [
            {"name": "Requinto", "instrument": "requinto", "midi_path": None, "audio_path": None},
            {"name": "Bongo", "instrument": "bongo", "midi_path": None, "audio_path": None},
            {"name": "Bass", "instrument": "bass", "midi_path": None, "audio_path": None}
        ]
    
    result = create_export_package(
        project_id=data.project_id,
        project_name=data.project_name,
        tracks=tracks,
        daw_id=data.daw,
        include_midi=data.include_midi,
        include_audio=data.include_audio,
        include_stems=data.include_stems,
        bpm=data.bpm,
        key=data.key,
        genre=data.genre
    )
    
    return result

@app.post("/api/export/track")
async def export_track(token: str, data: ExportTrackRequest):
    """Export a single track"""
    from services.auth_service import get_user_by_token
    from services.export_service import export_single_track
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return export_single_track(
        track_path=data.track_path,
        track_name=data.track_name,
        daw_id=data.daw,
        output_format=data.format
    )

@app.get("/api/export/history")
async def get_export_history(token: str, limit: int = 20):
    """Get recent exports"""
    from services.auth_service import get_user_by_token
    from services.export_service import get_export_history
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"exports": get_export_history(limit)}


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    migrate_from_json()  # Migrate any existing JSON data
    print("🚀 DGB AUDIO API started successfully!")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    config = load_config()
    
    # Get storage info
    samples = get_samples_metadata()
    total_size = sum(s.get("file_size_bytes", 0) for s in samples)
    
    # Get database stats
    db_stats = get_db_stats()
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "openai_configured": bool(config.get("openai_api_key")),
        "samples_dir": str(SAMPLES_DIR),
        "total_samples": len(samples),
        "total_storage_mb": round(total_size / (1024 * 1024), 2),
        "database": db_stats
    }


@app.get("/api/db/status")
async def database_status():
    """Get database status and statistics"""
    stats = get_db_stats()
    return {
        "connected": True,
        "tables": stats,
        "message": "Database connected and operational"
    }


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
