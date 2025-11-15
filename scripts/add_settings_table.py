"""
Add settings table to database
Run this to upgrade your database with settings support
"""

import sqlite3
from pathlib import Path


def add_settings_table():
    """Add settings table to existing database"""
    db_path = Path("data/immigration.db")

    if not db_path.exists():
        print("❌ Database not found. Run the app first to create it.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='settings'
        """)

        if cursor.fetchone():
            print("⚠️  Settings table already exists. Skipping...")
            return

        # Create settings table
        cursor.execute("""
            CREATE TABLE settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert default settings
        default_settings = [
            # LLM Settings
            ('llm.provider', 'openrouter', 'string', 'llm', 'LLM provider (openrouter or openai)'),
            ('llm.model', 'google/gemini-2.0-flash-001:free', 'string', 'llm', 'Model to use'),
            ('llm.temperature', '0.3', 'float', 'llm', 'LLM temperature (0.0-1.0)'),
            ('llm.max_tokens', '2000', 'integer', 'llm', 'Maximum tokens per request'),

            # Crawler Settings
            ('crawler.delay', '2.0', 'float', 'crawler', 'Delay between requests (seconds)'),
            ('crawler.max_pages', '50', 'integer', 'crawler', 'Maximum pages per country'),
            ('crawler.max_depth', '3', 'integer', 'crawler', 'Maximum crawl depth'),

            # Embeddings
            ('embeddings.model', 'all-MiniLM-L6-v2', 'string', 'embeddings', 'Embedding model name'),

            # Application
            ('app.log_level', 'INFO', 'string', 'app', 'Log level'),
            ('app.default_country', 'australia', 'string', 'app', 'Default country in UI'),
        ]

        cursor.executemany("""
            INSERT INTO settings (key, value, type, category, description)
            VALUES (?, ?, ?, ?, ?)
        """, default_settings)

        conn.commit()
        print("✅ Settings table created successfully!")
        print(f"   Added {len(default_settings)} default settings")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
    finally:
        conn.close()


if __name__ == "__main__":
    add_settings_table()
