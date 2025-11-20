"""
Database Layer - SQLite with Versioning
Handles all data storage with version tracking
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from contextlib import contextmanager
from shared.models import Visa, CrawledPage, load_visas_from_rows, load_pages_from_rows


class Database:
    """SQLite database with versioning for visa data"""

    def __init__(self, db_path: str = "data/immigration.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Crawled pages with versioning
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crawled_pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    country TEXT NOT NULL,
                    title TEXT,
                    content TEXT,
                    metadata TEXT,
                    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    version INTEGER DEFAULT 1,
                    is_latest BOOLEAN DEFAULT 1,
                    UNIQUE(url, version)
                )
            """)

            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_crawled_url
                ON crawled_pages(url, is_latest)
            """)

            # Structured visas with versioning
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS visas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    visa_type TEXT NOT NULL,
                    country TEXT NOT NULL,
                    category TEXT,
                    requirements TEXT,
                    fees TEXT,
                    processing_time TEXT,
                    documents_required TEXT,
                    timeline_stages TEXT,
                    cost_breakdown TEXT,
                    source_urls TEXT,
                    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    valid_to TIMESTAMP,
                    version INTEGER DEFAULT 1,
                    is_latest BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(visa_type, country, version)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_visa_latest
                ON visas(country, is_latest)
            """)

            # Clients
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    nationality TEXT,
                    profile TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Eligibility checks (audit trail)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS eligibility_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    visa_id INTEGER,
                    visa_version INTEGER,
                    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    profile_snapshot TEXT,
                    requirements_snapshot TEXT,
                    score REAL,
                    eligible BOOLEAN,
                    gaps TEXT,
                    strengths TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients(id),
                    FOREIGN KEY (visa_id) REFERENCES visas(id)
                )
            """)

            # Documents
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    doc_type TEXT,
                    file_path TEXT,
                    parsed_data TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients(id)
                )
            """)

            # Process tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS process_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    visa_id INTEGER,
                    status TEXT,
                    notes TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients(id),
                    FOREIGN KEY (visa_id) REFERENCES visas(id)
                )
            """)

            # Embeddings (for semantic search)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    visa_id INTEGER NOT NULL,
                    embedding BLOB NOT NULL,
                    model_name TEXT NOT NULL,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (visa_id) REFERENCES visas(id),
                    UNIQUE(visa_id, model_name)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_embeddings_visa
                ON embeddings(visa_id)
            """)

            # Settings (centralized configuration)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Insert default settings if table is empty
            cursor.execute("SELECT COUNT(*) as count FROM settings")
            if cursor.fetchone()['count'] == 0:
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

    # ============ CRAWLED PAGES ============

    def save_crawled_page(self, url: str, country: str, title: str,
                         content: str, metadata: Dict) -> int:
        """Save crawled page with automatic versioning"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if URL exists
            cursor.execute("""
                SELECT MAX(version) as max_version
                FROM crawled_pages
                WHERE url = ?
            """, (url,))

            result = cursor.fetchone()
            new_version = (result['max_version'] or 0) + 1

            # Mark old versions as not latest
            if new_version > 1:
                cursor.execute("""
                    UPDATE crawled_pages
                    SET is_latest = 0
                    WHERE url = ?
                """, (url,))

            # Insert new version
            cursor.execute("""
                INSERT INTO crawled_pages
                (url, country, title, content, metadata, version, is_latest)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (url, country, title, content, json.dumps(metadata), new_version))

            return cursor.lastrowid

    def get_latest_pages(self, country: Optional[str] = None) -> List[Dict]:
        """Get latest version of all crawled pages"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if country:
                cursor.execute("""
                    SELECT * FROM crawled_pages
                    WHERE is_latest = 1 AND country = ?
                    ORDER BY crawled_at DESC
                """, (country,))
            else:
                cursor.execute("""
                    SELECT * FROM crawled_pages
                    WHERE is_latest = 1
                    ORDER BY crawled_at DESC
                """)

            return [dict(row) for row in cursor.fetchall()]

    def get_page_history(self, url: str) -> List[Dict]:
        """Get all versions of a specific URL"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM crawled_pages
                WHERE url = ?
                ORDER BY version DESC
            """, (url,))

            return [dict(row) for row in cursor.fetchall()]

    # ============ VISAS ============

    def save_visa(self, visa_type: str, country: str, category: str,
                  requirements: Dict, fees: Dict, processing_time: str,
                  documents_required: List = None, timeline_stages: Dict = None,
                  cost_breakdown: Dict = None, source_urls: List = None) -> int:
        """Save visa with automatic versioning"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if visa exists
            cursor.execute("""
                SELECT MAX(version) as max_version
                FROM visas
                WHERE visa_type = ? AND country = ?
            """, (visa_type, country))

            result = cursor.fetchone()
            new_version = (result['max_version'] or 0) + 1

            # Mark old versions as not latest
            if new_version > 1:
                cursor.execute("""
                    UPDATE visas
                    SET is_latest = 0, valid_to = CURRENT_TIMESTAMP
                    WHERE visa_type = ? AND country = ?
                """, (visa_type, country))

            # Insert new version
            cursor.execute("""
                INSERT INTO visas
                (visa_type, country, category, requirements, fees, processing_time,
                 documents_required, timeline_stages, cost_breakdown, source_urls,
                 version, is_latest)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                visa_type, country, category,
                json.dumps(requirements),
                json.dumps(fees),
                processing_time,
                json.dumps(documents_required or []),
                json.dumps(timeline_stages or {}),
                json.dumps(cost_breakdown or {}),
                json.dumps(source_urls or []),
                new_version
            ))

            return cursor.lastrowid

    def get_latest_visas(self, country: Optional[str] = None) -> List[Dict]:
        """Get latest version of all visas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if country:
                cursor.execute("""
                    SELECT * FROM visas
                    WHERE is_latest = 1 AND country = ?
                    ORDER BY created_at DESC
                """, (country,))
            else:
                cursor.execute("""
                    SELECT * FROM visas
                    WHERE is_latest = 1
                    ORDER BY created_at DESC
                """)

            rows = cursor.fetchall()
            visas = []
            for row in rows:
                visa = dict(row)
                # Parse JSON fields
                visa['requirements'] = json.loads(visa['requirements'])
                visa['fees'] = json.loads(visa['fees'])
                visa['documents_required'] = json.loads(visa['documents_required'])
                visa['timeline_stages'] = json.loads(visa['timeline_stages'])
                visa['cost_breakdown'] = json.loads(visa['cost_breakdown'])
                visa['source_urls'] = json.loads(visa['source_urls'])
                visas.append(visa)

            return visas

    def get_visas(self, country: Optional[str] = None) -> List[Visa]:
        """
        Get visas as Visa model objects.

        This is the preferred method - returns typed Visa objects
        that are easier to work with.

        Args:
            country: Optional country filter

        Returns:
            List of Visa objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if country:
                cursor.execute("""
                    SELECT * FROM visas
                    WHERE is_latest = 1 AND country = ?
                    ORDER BY created_at DESC
                """, (country,))
            else:
                cursor.execute("""
                    SELECT * FROM visas
                    WHERE is_latest = 1
                    ORDER BY created_at DESC
                """)

            rows = [dict(row) for row in cursor.fetchall()]
            return load_visas_from_rows(rows)

    def get_pages(self, country: Optional[str] = None) -> List[CrawledPage]:
        """
        Get crawled pages as CrawledPage model objects.

        Args:
            country: Optional country filter

        Returns:
            List of CrawledPage objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if country:
                cursor.execute("""
                    SELECT * FROM crawled_pages
                    WHERE is_latest = 1 AND country = ?
                    ORDER BY crawled_at DESC
                """, (country,))
            else:
                cursor.execute("""
                    SELECT * FROM crawled_pages
                    WHERE is_latest = 1
                    ORDER BY crawled_at DESC
                """)

            rows = [dict(row) for row in cursor.fetchall()]
            return load_pages_from_rows(rows)

    def get_unclassified_pages(self, country: Optional[str] = None) -> List[CrawledPage]:
        """
        Get crawled pages that haven't been classified yet.

        A page is considered "unclassified" if there's no visa in the visas table
        with a matching source URL.

        Args:
            country: Optional country filter

        Returns:
            List of CrawledPage objects that need classification
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Query to find pages without corresponding visas
            if country:
                cursor.execute("""
                    SELECT cp.* FROM crawled_pages cp
                    WHERE cp.is_latest = 1
                      AND cp.country = ?
                      AND NOT EXISTS (
                        SELECT 1 FROM visas v
                        WHERE v.is_latest = 1
                          AND json_extract(v.source_urls, '$[0]') = cp.url
                      )
                    ORDER BY cp.crawled_at DESC
                """, (country,))
            else:
                cursor.execute("""
                    SELECT cp.* FROM crawled_pages cp
                    WHERE cp.is_latest = 1
                      AND NOT EXISTS (
                        SELECT 1 FROM visas v
                        WHERE v.is_latest = 1
                          AND json_extract(v.source_urls, '$[0]') = cp.url
                      )
                    ORDER BY cp.crawled_at DESC
                """)

            rows = [dict(row) for row in cursor.fetchall()]
            return load_pages_from_rows(rows)

    def get_visa_history(self, visa_type: str, country: str) -> List[Dict]:
        """Get all versions of a specific visa"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM visas
                WHERE visa_type = ? AND country = ?
                ORDER BY version DESC
            """, (visa_type, country))

            return [dict(row) for row in cursor.fetchall()]

    # ============ CLIENTS ============

    def save_client(self, name: str, email: str, nationality: str,
                   profile: Dict) -> int:
        """Save client profile"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clients (name, email, nationality, profile)
                VALUES (?, ?, ?, ?)
            """, (name, email, nationality, json.dumps(profile)))

            return cursor.lastrowid

    def get_client(self, client_id: int) -> Optional[Dict]:
        """Get client by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            row = cursor.fetchone()

            if row:
                client = dict(row)
                client['profile'] = json.loads(client['profile'])
                return client
            return None

    # ============ ELIGIBILITY CHECKS ============

    def save_eligibility_check(self, client_id: int, visa_id: int,
                              visa_version: int, profile_snapshot: Dict,
                              requirements_snapshot: Dict, score: float,
                              eligible: bool, gaps: List, strengths: List) -> int:
        """Save eligibility check result (audit trail)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO eligibility_checks
                (client_id, visa_id, visa_version, profile_snapshot,
                 requirements_snapshot, score, eligible, gaps, strengths)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client_id, visa_id, visa_version,
                json.dumps(profile_snapshot),
                json.dumps(requirements_snapshot),
                score, eligible,
                json.dumps(gaps),
                json.dumps(strengths)
            ))

            return cursor.lastrowid

    def get_client_checks(self, client_id: int) -> List[Dict]:
        """Get all eligibility checks for a client"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ec.*, v.visa_type, v.country
                FROM eligibility_checks ec
                JOIN visas v ON ec.visa_id = v.id
                WHERE ec.client_id = ?
                ORDER BY ec.check_date DESC
            """, (client_id,))

            return [dict(row) for row in cursor.fetchall()]

    # ============ EMBEDDINGS ============

    def save_embedding(self, visa_id: int, embedding: bytes, model_name: str = "all-MiniLM-L6-v2") -> int:
        """Save embedding for a visa"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Delete old embedding for this visa+model if exists
            cursor.execute("""
                DELETE FROM embeddings
                WHERE visa_id = ? AND model_name = ?
            """, (visa_id, model_name))

            # Insert new embedding
            cursor.execute("""
                INSERT INTO embeddings (visa_id, embedding, model_name)
                VALUES (?, ?, ?)
            """, (visa_id, embedding, model_name))

            return cursor.lastrowid

    def get_embeddings(self, model_name: str = "all-MiniLM-L6-v2") -> List[Dict]:
        """Get all embeddings for a specific model"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.*, v.visa_type, v.country
                FROM embeddings e
                JOIN visas v ON e.visa_id = v.id
                WHERE e.model_name = ? AND v.is_latest = 1
            """, (model_name,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'visa_id': row['visa_id'],
                    'embedding': row['embedding'],
                    'visa_type': row['visa_type'],
                    'country': row['country'],
                    'indexed_at': row['indexed_at']
                })

            return results

    def get_embedding(self, visa_id: int, model_name: str = "all-MiniLM-L6-v2") -> Optional[bytes]:
        """Get embedding for a specific visa"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT embedding FROM embeddings
                WHERE visa_id = ? AND model_name = ?
            """, (visa_id, model_name))

            row = cursor.fetchone()
            return row['embedding'] if row else None

    # ============ STATISTICS ============

    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Pages crawled
            cursor.execute("SELECT COUNT(*) as count FROM crawled_pages WHERE is_latest = 1")
            stats['pages_crawled'] = cursor.fetchone()['count']

            # Visas
            cursor.execute("SELECT COUNT(*) as count FROM visas WHERE is_latest = 1")
            stats['visas_total'] = cursor.fetchone()['count']

            # Countries - count from crawled_pages if no visas, otherwise from visas
            if stats['visas_total'] > 0:
                cursor.execute("SELECT COUNT(DISTINCT country) as count FROM visas WHERE is_latest = 1")
            else:
                cursor.execute("SELECT COUNT(DISTINCT country) as count FROM crawled_pages WHERE is_latest = 1")
            stats['countries'] = cursor.fetchone()['count']

            # Clients
            cursor.execute("SELECT COUNT(*) as count FROM clients")
            stats['clients'] = cursor.fetchone()['count']

            # Checks
            cursor.execute("SELECT COUNT(*) as count FROM eligibility_checks")
            stats['checks_performed'] = cursor.fetchone()['count']

            # Embeddings
            cursor.execute("SELECT COUNT(*) as count FROM embeddings")
            stats['embeddings'] = cursor.fetchone()['count']

            return stats
