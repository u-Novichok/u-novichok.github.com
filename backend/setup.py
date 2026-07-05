from database import get_db

def create_tables():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            category TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            media_type TEXT DEFAULT 'image',
            cloudinary_public_id TEXT,
            cloudinary_url TEXT,
            uploaded_at TEXT DEFAULT (datetime('now')),
            download_count INTEGER DEFAULT 0
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
