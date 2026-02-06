"""
DGB AUDIO - Database Models
============================
SQLite models for users, projects, and samples.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import json

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "dgb_audio.db"


def get_db():
    """Get database connection"""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            plan TEXT DEFAULT 'free',
            storage_limit_gb REAL DEFAULT 1.0,
            storage_used_bytes INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # Projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            genre TEXT DEFAULT 'bolero',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Samples table (migrating from JSON)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS samples (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            project_id TEXT,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            genre TEXT NOT NULL,
            instrument TEXT NOT NULL,
            category TEXT NOT NULL,
            path TEXT NOT NULL,
            duration REAL DEFAULT 0,
            sample_rate INTEGER DEFAULT 48000,
            file_size_bytes INTEGER DEFAULT 0,
            tags TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    
    # Project collaborators
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_collaborators (
            project_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            created_at TEXT NOT NULL,
            PRIMARY KEY (project_id, user_id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()


# Storage plans configuration
STORAGE_PLANS = {
    "free": {
        "name": "Free",
        "storage_gb": 1,
        "max_projects": 2,
        "price_usd": 0
    },
    "creator": {
        "name": "Creator",
        "storage_gb": 5,
        "max_projects": 10,
        "price_usd": 9
    },
    "pro": {
        "name": "Pro",
        "storage_gb": 20,
        "max_projects": -1,  # Unlimited
        "price_usd": 29
    },
    "studio": {
        "name": "Studio",
        "storage_gb": 50,
        "max_projects": -1,
        "price_usd": 79,
        "api_access": True
    }
}


# ============================================================================
# USER FUNCTIONS
# ============================================================================

def create_user(user_id: str, email: str, name: str, plan: str = "free") -> dict:
    """Create a new user"""
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    storage_limit = STORAGE_PLANS.get(plan, STORAGE_PLANS["free"])["storage_gb"]
    
    cursor.execute("""
        INSERT INTO users (id, email, name, plan, storage_limit_gb, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, email, name, plan, storage_limit, now, now))
    
    conn.commit()
    conn.close()
    
    return {
        "id": user_id,
        "email": email,
        "name": name,
        "plan": plan,
        "storage_limit_gb": storage_limit
    }


def get_user(user_id: str) -> Optional[dict]:
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_user_storage_info(user_id: str) -> dict:
    """Get user storage usage info"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user info
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        return {"error": "User not found"}
    
    user = dict(user)
    
    # Calculate total used
    cursor.execute("""
        SELECT COALESCE(SUM(file_size_bytes), 0) as total_bytes
        FROM samples WHERE user_id = ?
    """, (user_id,))
    
    result = cursor.fetchone()
    used_bytes = result["total_bytes"] if result else 0
    
    conn.close()
    
    limit_bytes = user["storage_limit_gb"] * 1024 * 1024 * 1024
    
    return {
        "user_id": user_id,
        "plan": user["plan"],
        "storage_limit_gb": user["storage_limit_gb"],
        "storage_used_bytes": used_bytes,
        "storage_used_gb": round(used_bytes / (1024 * 1024 * 1024), 3),
        "storage_percent": round((used_bytes / limit_bytes) * 100, 1) if limit_bytes > 0 else 0,
        "storage_available_bytes": max(0, limit_bytes - used_bytes)
    }


# ============================================================================
# PROJECT FUNCTIONS
# ============================================================================

def create_project(project_id: str, user_id: str, name: str, 
                   description: str = "", genre: str = "bolero") -> dict:
    """Create a new project"""
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO projects (id, user_id, name, description, genre, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (project_id, user_id, name, description, genre, now, now))
    
    conn.commit()
    conn.close()
    
    return {
        "id": project_id,
        "user_id": user_id,
        "name": name,
        "description": description,
        "genre": genre
    }


def get_user_projects(user_id: str) -> List[dict]:
    """Get all projects for a user"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM projects WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return projects


# Initialize database on import
init_db()
