"""
DGB AUDIO - Authentication Service
===================================
User registration, login, and JWT token management.
Now uses SQLite database instead of JSON files.
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for database import
sys.path.insert(0, str(Path(__file__).parent.parent))
from database import (
    get_user_by_email, get_user_by_id, get_user_by_token as db_get_user_by_token,
    create_user as db_create_user, create_session, delete_session,
    save_api_key, get_api_key, track_api_usage as db_track_api_usage,
    get_user_usage_stats, update_user, get_connection
)

# Configuration
SECRET_KEY = os.getenv("DGB_SECRET_KEY", secrets.token_hex(32))
TOKEN_EXPIRE_HOURS = 24


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


# Plan configuration
PLAN_CONFIG = {
    "starter": {"storage_gb": 1, "recording_seconds": 30, "max_projects": 2},
    "creator": {"storage_gb": 10, "recording_seconds": 60, "max_projects": 20},
    "pro": {"storage_gb": 50, "recording_seconds": -1, "max_projects": -1},
    "studio": {"storage_gb": 200, "recording_seconds": -1, "max_projects": -1}
}

# Role permissions
ROLE_PERMISSIONS = {
    "superadmin": ["all", "manage_users", "manage_plans", "view_analytics", "manage_roles", "system_config"],
    "admin": ["manage_own_users", "view_own_analytics", "manage_samples"],
    "user": ["create_music", "upload_samples", "use_chat"]
}


# ============================================================================
# USER MANAGEMENT
# ============================================================================

def register_user(email: str, password: str, name: str, plan: str = "starter", role: str = "user") -> dict:
    """Register a new user"""
    # Check if email exists
    existing = get_user_by_email(email)
    if existing:
        return {"error": "Email already registered"}
    
    user_id = f"usr_{secrets.token_hex(8)}"
    password_hash = hash_password(password)
    permissions = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["user"])
    limits = PLAN_CONFIG.get(plan, PLAN_CONFIG["starter"])
    
    success = db_create_user(
        user_id=user_id,
        email=email,
        password_hash=password_hash,
        name=name,
        plan=plan,
        role=role,
        permissions=permissions,
        limits=limits
    )
    
    if success:
        user = get_user_by_email(email)
        safe_user = {k: v for k, v in user.items() if k != "password_hash"}
        return {"success": True, "user": safe_user}
    
    return {"error": "Failed to create user"}


def login_user(email: str, password: str) -> dict:
    """Login a user"""
    user = get_user_by_email(email)
    
    if not user:
        return {"error": "Invalid email or password"}
    
    if not verify_password(password, user["password_hash"]):
        return {"error": "Invalid email or password"}
    
    # Generate and store token
    token = generate_token(user["id"])
    expires_at = (datetime.now() + timedelta(hours=TOKEN_EXPIRE_HOURS)).isoformat()
    
    create_session(user["id"], token, expires_at)
    
    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    return {"success": True, "token": token, "user": safe_user}


def logout_user(token: str) -> dict:
    """Logout a user by deleting their session"""
    if delete_session(token):
        return {"success": True, "message": "Logged out successfully"}
    return {"error": "Session not found"}


def get_user_by_token(token: str) -> Optional[dict]:
    """Get user by authentication token"""
    user = db_get_user_by_token(token)
    if user:
        safe_user = {k: v for k, v in user.items() if k != "password_hash"}
        return safe_user
    return None


# ============================================================================
# ROLE MANAGEMENT (SuperAdmin only)
# ============================================================================

def get_all_users(requester_email: str) -> dict:
    """Get all users (SuperAdmin only)"""
    requester = get_user_by_email(requester_email)
    
    if not requester or requester.get("role") != "superadmin":
        return {"error": "Unauthorized - SuperAdmin only"}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = []
        for row in cursor.fetchall():
            user = dict(row)
            # Remove password, parse JSON fields
            user.pop("password_hash", None)
            import json
            user['permissions'] = json.loads(user.get('permissions', '[]'))
            user['limits'] = json.loads(user.get('limits', '{}'))
            users.append(user)
    
    return {"users": users, "total": len(users)}


def update_user_role(requester_email: str, target_email: str, new_role: str) -> dict:
    """Update a user's role (SuperAdmin only)"""
    requester = get_user_by_email(requester_email)
    
    if not requester or requester.get("role") != "superadmin":
        return {"error": "Unauthorized - SuperAdmin only"}
    
    target = get_user_by_email(target_email)
    if not target:
        return {"error": "User not found"}
    
    permissions = ROLE_PERMISSIONS.get(new_role, ROLE_PERMISSIONS["user"])
    
    success = update_user(target["id"], role=new_role, permissions=permissions)
    
    if success:
        return {"success": True, "message": f"Role updated to {new_role}"}
    return {"error": "Failed to update role"}


def update_user_plan(requester_email: str, target_email: str, new_plan: str) -> dict:
    """Update a user's plan (SuperAdmin only)"""
    requester = get_user_by_email(requester_email)
    
    if not requester or requester.get("role") != "superadmin":
        return {"error": "Unauthorized - SuperAdmin only"}
    
    target = get_user_by_email(target_email)
    if not target:
        return {"error": "User not found"}
    
    limits = PLAN_CONFIG.get(new_plan, PLAN_CONFIG["starter"])
    
    success = update_user(target["id"], plan=new_plan, limits=limits)
    
    if success:
        return {"success": True, "message": f"Plan updated to {new_plan}"}
    return {"error": "Failed to update plan"}


# ============================================================================
# API KEY MANAGEMENT
# ============================================================================

def set_user_api_key(email: str, api_key: str) -> dict:
    """Set user's OpenAI API key"""
    user = get_user_by_email(email)
    
    if not user:
        return {"error": "User not found"}
    
    encrypted = encrypt_api_key(api_key)
    save_api_key(user["id"], encrypted)
    
    return {"success": True, "message": "API key saved"}


def get_user_api_key(email: str) -> Optional[str]:
    """Get user's decrypted OpenAI API key"""
    user = get_user_by_email(email)
    
    if not user:
        return None
    
    encrypted = get_api_key(user["id"])
    if encrypted:
        return decrypt_api_key(encrypted)
    return None


# ============================================================================
# USAGE TRACKING
# ============================================================================

def track_api_usage(email: str, tokens: int, cost: float, endpoint: str = None):
    """Track API usage for a user"""
    user = get_user_by_email(email)
    
    if not user:
        return
    
    db_track_api_usage(user["id"], tokens, cost, endpoint)


def get_user_usage(email: str) -> dict:
    """Get user's usage statistics"""
    user = get_user_by_email(email)
    
    if not user:
        return {"error": "User not found"}
    
    return get_user_usage_stats(user["id"])


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_user_by_id_safe(user_id: str) -> Optional[dict]:
    """Get user by ID without password"""
    user = get_user_by_id(user_id)
    if user:
        return {k: v for k, v in user.items() if k != "password_hash"}
    return None
