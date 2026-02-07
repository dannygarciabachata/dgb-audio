"""
DGB AUDIO - Database Module
============================
SQLite database management for all platform data.
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
import json

# Database path
DB_PATH = Path(__file__).parent / "data" / "dgb_audio.db"


def get_db_path() -> str:
    """Get the database file path"""
    return str(DB_PATH)


@contextmanager
def get_connection():
    """Context manager for database connections"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_db():
    """Initialize the database with all required tables"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # ====================================================================
        # USERS TABLE
        # ====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            plan TEXT DEFAULT 'starter',
            role TEXT DEFAULT 'user',
            permissions TEXT DEFAULT '[]',
            limits TEXT DEFAULT '{}',
            storage_used_bytes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # ====================================================================
        # SESSIONS TABLE
        # ====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # ====================================================================
        # API KEYS TABLE
        # ====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            encrypted_key TEXT NOT NULL,
            provider TEXT DEFAULT 'openai',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # ====================================================================
        # API USAGE TABLE
        # ====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            tokens_used INTEGER NOT NULL,
            cost_estimate REAL NOT NULL,
            endpoint TEXT,
            model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # ====================================================================
        # PROJECTS TABLE
        # ====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            genre TEXT,
            bpm INTEGER DEFAULT 120,
            key TEXT DEFAULT 'Am',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # ====================================================================
        # SAMPLES TABLE
        # ====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS samples (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            project_id TEXT,
            filename TEXT NOT NULL,
            original_name TEXT,
            genre TEXT,
            instrument TEXT,
            category TEXT,
            duration_seconds REAL,
            file_size_bytes INTEGER,
            file_path TEXT NOT NULL,
            is_public INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
        )
        """)
        
        # ====================================================================
        # COMPOSITIONS TABLE
        # ====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS compositions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            project_id TEXT,
            title TEXT,
            genre TEXT,
            bpm INTEGER,
            key TEXT,
            prompt TEXT,
            lyrics TEXT,
            instruments TEXT,
            midi_path TEXT,
            audio_path TEXT,
            duration_seconds REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
        )
        """)
        
        # ====================================================================
        # SUBSCRIPTIONS TABLE
        # ====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            plan TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            current_period_start TIMESTAMP,
            current_period_end TIMESTAMP,
            canceled_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # ====================================================================
        # SUPPORT MESSAGES TABLE
        # ====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            department TEXT DEFAULT 'general',
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # ====================================================================
        # RECORDINGS TABLE
        # ====================================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recordings (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            project_id TEXT,
            filename TEXT NOT NULL,
            instrument TEXT,
            genre TEXT,
            duration_seconds REAL,
            file_size_bytes INTEGER,
            file_path TEXT NOT NULL,
            analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
        )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_usage_user ON api_usage(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_samples_user ON samples(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_samples_genre ON samples(genre)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_compositions_user ON compositions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recordings_user ON recordings(user_id)")
        
        print("✅ Database initialized successfully!")
        return True


def migrate_from_json():
    """Migrate existing data from JSON files to SQLite"""
    users_file = Path(__file__).parent / "data" / "users.json"
    
    if not users_file.exists():
        print("No existing users.json to migrate")
        return
    
    try:
        with open(users_file, 'r') as f:
            users_data = json.load(f)
        
        with get_connection() as conn:
            cursor = conn.cursor()
            
            for email, user in users_data.items():
                try:
                    # Insert user
                    cursor.execute("""
                    INSERT OR IGNORE INTO users 
                    (id, email, password_hash, name, plan, role, permissions, limits, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user.get('id', f"usr_{email[:8]}"),
                        email,
                        user.get('password_hash', ''),
                        user.get('name', 'User'),
                        user.get('plan', 'starter'),
                        user.get('role', 'user'),
                        json.dumps(user.get('permissions', [])),
                        json.dumps(user.get('limits', {})),
                        user.get('created_at', datetime.now().isoformat())
                    ))
                    
                    # Migrate API key if exists
                    if user.get('openai_api_key'):
                        cursor.execute("""
                        INSERT OR IGNORE INTO api_keys (user_id, encrypted_key)
                        VALUES (?, ?)
                        """, (user.get('id'), user.get('openai_api_key')))
                    
                    # Migrate active token if exists
                    if user.get('token'):
                        cursor.execute("""
                        INSERT OR IGNORE INTO sessions (user_id, token, expires_at)
                        VALUES (?, ?, ?)
                        """, (
                            user.get('id'),
                            user.get('token'),
                            (datetime.now() + timedelta(hours=24)).isoformat()
                        ))
                    
                    # Migrate API usage if exists
                    if user.get('api_usage'):
                        usage = user['api_usage']
                        cursor.execute("""
                        INSERT INTO api_usage (user_id, tokens_used, cost_estimate, endpoint)
                        VALUES (?, ?, ?, ?)
                        """, (
                            user.get('id'),
                            usage.get('total_tokens', 0),
                            usage.get('total_cost', 0),
                            'migration'
                        ))
                    
                except Exception as e:
                    print(f"Error migrating user {email}: {e}")
                    continue
            
            print(f"✅ Migrated {len(users_data)} users from JSON to SQLite")
            
            # Backup and rename old file
            backup_path = users_file.with_suffix('.json.bak')
            users_file.rename(backup_path)
            print(f"📁 Original users.json backed up to {backup_path}")
            
    except Exception as e:
        print(f"Migration error: {e}")


# Need to import timedelta for migration
from datetime import timedelta


def get_db_stats() -> dict:
    """Get database statistics"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        stats = {}
        tables = ['users', 'sessions', 'api_keys', 'api_usage', 'projects', 
                  'samples', 'compositions', 'subscriptions', 'recordings']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
        
        # Get database file size
        if DB_PATH.exists():
            stats['db_size_bytes'] = DB_PATH.stat().st_size
            stats['db_size_mb'] = round(stats['db_size_bytes'] / (1024 * 1024), 2)
        
        return stats


# ============================================================================
# CRUD HELPERS
# ============================================================================

def dict_from_row(row) -> dict:
    """Convert sqlite3.Row to dict"""
    if row is None:
        return None
    return dict(row)


def get_user_by_email(email: str) -> dict:
    """Get user by email"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            user = dict_from_row(row)
            # Parse JSON fields
            user['permissions'] = json.loads(user.get('permissions', '[]'))
            user['limits'] = json.loads(user.get('limits', '{}'))
            return user
        return None


def get_user_by_id(user_id: str) -> dict:
    """Get user by ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            user = dict_from_row(row)
            user['permissions'] = json.loads(user.get('permissions', '[]'))
            user['limits'] = json.loads(user.get('limits', '{}'))
            return user
        return None


def get_user_by_token(token: str) -> dict:
    """Get user by session token"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT u.* FROM users u
        JOIN sessions s ON u.id = s.user_id
        WHERE s.token = ? AND s.expires_at > datetime('now')
        """, (token,))
        row = cursor.fetchone()
        if row:
            user = dict_from_row(row)
            user['permissions'] = json.loads(user.get('permissions', '[]'))
            user['limits'] = json.loads(user.get('limits', '{}'))
            return user
        return None


def create_user(user_id: str, email: str, password_hash: str, name: str, 
                plan: str = 'starter', role: str = 'user', 
                permissions: list = None, limits: dict = None) -> bool:
    """Create a new user"""
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO users (id, email, password_hash, name, plan, role, permissions, limits)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, email, password_hash, name, plan, role,
                json.dumps(permissions or []),
                json.dumps(limits or {})
            ))
            return True
        except sqlite3.IntegrityError:
            return False


def create_session(user_id: str, token: str, expires_at: str) -> bool:
    """Create a new session"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO sessions (user_id, token, expires_at)
        VALUES (?, ?, ?)
        """, (user_id, token, expires_at))
        return True


def delete_session(token: str) -> bool:
    """Delete a session (logout)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        return cursor.rowcount > 0


def save_api_key(user_id: str, encrypted_key: str) -> bool:
    """Save or update user's API key"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO api_keys (user_id, encrypted_key)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET 
            encrypted_key = excluded.encrypted_key,
            updated_at = CURRENT_TIMESTAMP
        """, (user_id, encrypted_key))
        return True


def get_api_key(user_id: str) -> str:
    """Get user's encrypted API key"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT encrypted_key FROM api_keys WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else None


def track_api_usage(user_id: str, tokens: int, cost: float, endpoint: str = None, model: str = None) -> bool:
    """Track API usage"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO api_usage (user_id, tokens_used, cost_estimate, endpoint, model)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, tokens, cost, endpoint, model))
        return True


def get_user_usage_stats(user_id: str) -> dict:
    """Get user's total API usage stats"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT 
            COUNT(*) as total_requests,
            COALESCE(SUM(tokens_used), 0) as total_tokens,
            COALESCE(SUM(cost_estimate), 0) as total_cost
        FROM api_usage WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        return {
            'total_requests': row[0],
            'total_tokens': row[1],
            'total_cost': round(row[2], 4)
        }


def update_user(user_id: str, **kwargs) -> bool:
    """Update user fields"""
    if not kwargs:
        return False
    
    # Handle JSON fields
    if 'permissions' in kwargs and isinstance(kwargs['permissions'], list):
        kwargs['permissions'] = json.dumps(kwargs['permissions'])
    if 'limits' in kwargs and isinstance(kwargs['limits'], dict):
        kwargs['limits'] = json.dumps(kwargs['limits'])
    
    with get_connection() as conn:
        cursor = conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        cursor.execute(f"""
        UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """, values)
        return cursor.rowcount > 0


# ============================================================================
# PROJECT OPERATIONS
# ============================================================================

def create_project(project_id: str, user_id: str, name: str, **kwargs) -> bool:
    """Create a new project"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO projects (id, user_id, name, description, genre, bpm, key)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, user_id, name,
            kwargs.get('description'),
            kwargs.get('genre'),
            kwargs.get('bpm', 120),
            kwargs.get('key', 'Am')
        ))
        return True


def get_user_projects(user_id: str) -> list:
    """Get all projects for a user"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM projects WHERE user_id = ? ORDER BY updated_at DESC
        """, (user_id,))
        return [dict_from_row(row) for row in cursor.fetchall()]


# ============================================================================
# SAMPLE OPERATIONS
# ============================================================================

def create_sample(sample_id: str, filename: str, file_path: str, **kwargs) -> bool:
    """Create a new sample record"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO samples (id, user_id, project_id, filename, original_name, 
                            genre, instrument, category, duration_seconds, 
                            file_size_bytes, file_path, is_public)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sample_id,
            kwargs.get('user_id'),
            kwargs.get('project_id'),
            filename,
            kwargs.get('original_name'),
            kwargs.get('genre'),
            kwargs.get('instrument'),
            kwargs.get('category'),
            kwargs.get('duration_seconds'),
            kwargs.get('file_size_bytes'),
            file_path,
            kwargs.get('is_public', 0)
        ))
        return True


def get_samples(genre: str = None, instrument: str = None, limit: int = 50) -> list:
    """Get samples with optional filters"""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM samples WHERE 1=1"
        params = []
        
        if genre:
            query += " AND genre = ?"
            params.append(genre)
        if instrument:
            query += " AND instrument = ?"
            params.append(instrument)
        
        query += f" ORDER BY created_at DESC LIMIT {limit}"
        cursor.execute(query, params)
        return [dict_from_row(row) for row in cursor.fetchall()]


# ============================================================================
# COMPOSITION OPERATIONS
# ============================================================================

def create_composition(comp_id: str, user_id: str, **kwargs) -> bool:
    """Create a new composition"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO compositions (id, user_id, project_id, title, genre, bpm, key,
                                  prompt, lyrics, instruments, midi_path, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            comp_id, user_id,
            kwargs.get('project_id'),
            kwargs.get('title'),
            kwargs.get('genre'),
            kwargs.get('bpm'),
            kwargs.get('key'),
            kwargs.get('prompt'),
            kwargs.get('lyrics'),
            json.dumps(kwargs.get('instruments', [])),
            kwargs.get('midi_path'),
            kwargs.get('status', 'pending')
        ))
        return True


def get_user_compositions(user_id: str) -> list:
    """Get all compositions for a user"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM compositions WHERE user_id = ? ORDER BY created_at DESC
        """, (user_id,))
        return [dict_from_row(row) for row in cursor.fetchall()]


# Initialize database when module is imported
if __name__ == "__main__":
    init_db()
    print("\n📊 Database Stats:")
    stats = get_db_stats()
    for table, count in stats.items():
        print(f"  {table}: {count}")
