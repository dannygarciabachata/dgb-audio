"""
DGB AUDIO - Authentication Service
===================================
User registration, login, and JWT token management.
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
import json

# Configuration
SECRET_KEY = os.getenv("DGB_SECRET_KEY", secrets.token_hex(32))
TOKEN_EXPIRE_HOURS = 24

# Users file (will migrate to SQLite)
USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"


def _ensure_data_dir():
    """Ensure data directory exists"""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)


def _load_users() -> dict:
    """Load users from file"""
    _ensure_data_dir()
    with open(USERS_FILE, 'r') as f:
        return json.load(f)


def _save_users(users: dict):
    """Save users to file"""
    _ensure_data_dir()
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def hash_password(password: str) -> str:
    """Hash a password with salt"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{hash_obj.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    try:
        salt, hash_hex = hashed.split(':')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex() == hash_hex
    except:
        return False


def generate_token(user_id: str) -> str:
    """Generate a simple token (for demo - use JWT in production)"""
    timestamp = datetime.now().isoformat()
    token_data = f"{user_id}:{timestamp}:{secrets.token_hex(16)}"
    return hashlib.sha256(token_data.encode()).hexdigest()


def encrypt_api_key(api_key: str) -> str:
    """Simple encryption for API key (use proper encryption in production)"""
    # Base64 encode with a marker - in production use Fernet or similar
    import base64
    encoded = base64.b64encode(api_key.encode()).decode()
    return f"dgb:{encoded}"


def decrypt_api_key(encrypted: str) -> str:
    """Decrypt API key"""
    import base64
    if encrypted.startswith("dgb:"):
        encoded = encrypted[4:]
        return base64.b64decode(encoded).decode()
    return encrypted


# ============================================================================
# USER MANAGEMENT
# ============================================================================

def register_user(email: str, password: str, name: str, plan: str = "starter", role: str = "user") -> dict:
    """Register a new user"""
    users = _load_users()
    
    # Check if email exists
    if email in users:
        return {"error": "Email already registered"}
    
    user_id = f"usr_{secrets.token_hex(8)}"
    
    # Plan limits
    plan_config = {
        "starter": {"storage_gb": 1, "recording_seconds": 30, "max_projects": 2},
        "creator": {"storage_gb": 10, "recording_seconds": 60, "max_projects": 20},
        "pro": {"storage_gb": 50, "recording_seconds": -1, "max_projects": -1},
        "studio": {"storage_gb": 200, "recording_seconds": -1, "max_projects": -1}
    }
    
    # Role permissions
    role_permissions = {
        "superadmin": ["all", "manage_users", "manage_plans", "view_analytics", "manage_roles", "system_config"],
        "admin": ["manage_own_users", "view_own_analytics", "manage_samples"],
        "user": ["create_music", "upload_samples", "use_chat"]
    }
    
    user = {
        "id": user_id,
        "email": email,
        "name": name,
        "password_hash": hash_password(password),
        "plan": plan,
        "role": role,
        "permissions": role_permissions.get(role, role_permissions["user"]),
        "limits": plan_config.get(plan, plan_config["starter"]),
        "openai_key_encrypted": None,
        "usage": {
            "tokens_used": 0,
            "estimated_cost_usd": 0.0,
            "storage_used_bytes": 0,
            "requests_count": 0
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    users[email] = user
    _save_users(users)
    
    # Return user without password
    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    return {"success": True, "user": safe_user}


# ============================================================================
# ROLE MANAGEMENT (SuperAdmin only)
# ============================================================================

def get_all_users(requester_email: str) -> dict:
    """Get all users (SuperAdmin only)"""
    users = _load_users()
    
    requester = users.get(requester_email)
    if not requester or requester.get("role") != "superadmin":
        return {"error": "Unauthorized - SuperAdmin only"}
    
    # Return users without passwords
    safe_users = []
    for user in users.values():
        safe_user = {k: v for k, v in user.items() if k != "password_hash"}
        safe_users.append(safe_user)
    
    return {"users": safe_users, "total": len(safe_users)}


def update_user_role(requester_email: str, target_email: str, new_role: str) -> dict:
    """Update a user's role (SuperAdmin only)"""
    users = _load_users()
    
    requester = users.get(requester_email)
    if not requester or requester.get("role") != "superadmin":
        return {"error": "Unauthorized - SuperAdmin only"}
    
    if target_email not in users:
        return {"error": "User not found"}
    
    role_permissions = {
        "superadmin": ["all", "manage_users", "manage_plans", "view_analytics", "manage_roles", "system_config"],
        "admin": ["manage_own_users", "view_own_analytics", "manage_samples"],
        "user": ["create_music", "upload_samples", "use_chat"]
    }
    
    users[target_email]["role"] = new_role
    users[target_email]["permissions"] = role_permissions.get(new_role, role_permissions["user"])
    users[target_email]["updated_at"] = datetime.now().isoformat()
    _save_users(users)
    
    return {"success": True, "message": f"Role updated to {new_role}"}


def update_user_plan(requester_email: str, target_email: str, new_plan: str) -> dict:
    """Update a user's plan (SuperAdmin only)"""
    users = _load_users()
    
    requester = users.get(requester_email)
    if not requester or requester.get("role") != "superadmin":
        return {"error": "Unauthorized - SuperAdmin only"}
    
    if target_email not in users:
        return {"error": "User not found"}
    
    plan_config = {
        "starter": {"storage_gb": 1, "recording_seconds": 30, "max_projects": 2},
        "creator": {"storage_gb": 10, "recording_seconds": 60, "max_projects": 20},
        "pro": {"storage_gb": 50, "recording_seconds": -1, "max_projects": -1},
        "studio": {"storage_gb": 200, "recording_seconds": -1, "max_projects": -1}
    }
    
    users[target_email]["plan"] = new_plan
    users[target_email]["limits"] = plan_config.get(new_plan, plan_config["starter"])
    users[target_email]["updated_at"] = datetime.now().isoformat()
    _save_users(users)
    
    return {"success": True, "message": f"Plan updated to {new_plan}"}


def login_user(email: str, password: str) -> dict:
    """Login a user"""
    users = _load_users()
    
    if email not in users:
        return {"error": "Invalid email or password"}
    
    user = users[email]
    
    if not verify_password(password, user["password_hash"]):
        return {"error": "Invalid email or password"}
    
    # Generate token
    token = generate_token(user["id"])
    
    # Store active token
    user["active_token"] = token
    user["token_expires"] = (datetime.now() + timedelta(hours=TOKEN_EXPIRE_HOURS)).isoformat()
    users[email] = user
    _save_users(users)
    
    safe_user = {k: v for k, v in user.items() if k not in ["password_hash", "active_token"]}
    return {"success": True, "token": token, "user": safe_user}


def get_user_by_token(token: str) -> Optional[dict]:
    """Get user by authentication token"""
    users = _load_users()
    
    for user in users.values():
        if user.get("active_token") == token:
            # Check expiration
            expires = user.get("token_expires")
            if expires and datetime.fromisoformat(expires) > datetime.now():
                safe_user = {k: v for k, v in user.items() if k not in ["password_hash", "active_token"]}
                return safe_user
    
    return None


def set_user_api_key(email: str, api_key: str) -> dict:
    """Set user's OpenAI API key"""
    users = _load_users()
    
    if email not in users:
        return {"error": "User not found"}
    
    users[email]["openai_key_encrypted"] = encrypt_api_key(api_key)
    users[email]["updated_at"] = datetime.now().isoformat()
    _save_users(users)
    
    return {"success": True, "message": "API key saved"}


def get_user_api_key(email: str) -> Optional[str]:
    """Get user's decrypted OpenAI API key"""
    users = _load_users()
    
    if email not in users:
        return None
    
    encrypted = users[email].get("openai_key_encrypted")
    if encrypted:
        return decrypt_api_key(encrypted)
    return None


def track_api_usage(email: str, tokens: int, cost: float):
    """Track API usage for a user"""
    users = _load_users()
    
    if email not in users:
        return
    
    users[email]["usage"]["tokens_used"] += tokens
    users[email]["usage"]["estimated_cost_usd"] += cost
    users[email]["usage"]["requests_count"] += 1
    users[email]["updated_at"] = datetime.now().isoformat()
    _save_users(users)


def get_user_usage(email: str) -> dict:
    """Get user's usage statistics"""
    users = _load_users()
    
    if email not in users:
        return {"error": "User not found"}
    
    return users[email].get("usage", {})
