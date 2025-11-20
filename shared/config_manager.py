"""
Unified Configuration Manager
Reads settings from: .env > Database > YAML (in priority order)
"""

import os
import yaml
from pathlib import Path
from typing import Any, Optional, Dict
from dotenv import load_dotenv
import sqlite3


class ConfigManager:
    """
    Centralized configuration management
    Priority: .env > Database > YAML defaults
    """

    def __init__(self, db_path: str = "data/immigration.db"):
        self.db_path = Path(db_path)

        # Load .env file if exists
        env_file = Path('.env')
        if env_file.exists():
            load_dotenv(env_file)

        # Cache for database settings
        self._db_cache = None
        self._yaml_cache = {}

    def get(self, key: str, default: Any = None, service: Optional[str] = None) -> Any:
        """
        Get configuration value with priority: .env > Database > YAML

        Args:
            key: Config key (e.g., 'llm.provider', 'OPENROUTER_API_KEY')
            default: Default value if not found
            service: Service name for YAML lookup (e.g., 'crawler', 'classifier')

        Returns:
            Configuration value
        """
        # 1. Check environment variables (highest priority)
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return self._convert_type(env_value)

        # 2. Check database settings
        db_value = self._get_from_db(key)
        if db_value is not None:
            return db_value

        # 3. Check YAML config (lowest priority)
        if service:
            yaml_value = self._get_from_yaml(service, key)
            if yaml_value is not None:
                return yaml_value

        return default

    def set(self, key: str, value: Any) -> bool:
        """
        Save setting to database

        Args:
            key: Setting key (e.g., 'llm.provider')
            value: Setting value

        Returns:
            True if successful
        """
        try:
            # Determine type
            value_type = type(value).__name__
            if value_type == 'int':
                value_type = 'integer'
            elif value_type == 'float':
                value_type = 'float'
            elif value_type == 'bool':
                value_type = 'boolean'
            else:
                value_type = 'string'

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, type, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, str(value), value_type))

            conn.commit()
            conn.close()

            # Clear cache
            self._db_cache = None
            return True

        except Exception:
            return False

    def get_all(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all settings, optionally filtered by category

        Args:
            category: Filter by category (e.g., 'llm', 'crawler')

        Returns:
            Dictionary of settings
        """
        settings = {}

        # Get from database
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if category:
                cursor.execute("""
                    SELECT key, value, type FROM settings
                    WHERE category = ?
                """, (category,))
            else:
                cursor.execute("SELECT key, value, type FROM settings")

            for row in cursor.fetchall():
                settings[row['key']] = self._convert_type_from_db(
                    row['value'],
                    row['type']
                )

            conn.close()

        except Exception:
            pass

        return settings

    def get_api_key(self, provider: str = None) -> Optional[str]:
        """
        Get API key for LLM provider

        Args:
            provider: 'openrouter' or 'openai' (defaults to current provider)

        Returns:
            API key or None
        """
        if not provider:
            provider = self.get('llm.provider', 'openrouter')

        # Try environment variable first
        env_keys = {
            'openrouter': 'OPENROUTER_API_KEY',
            'openai': 'OPENAI_API_KEY'
        }

        env_key = env_keys.get(provider.lower())
        if env_key:
            api_key = os.getenv(env_key)
            if api_key:
                return api_key

        # Try database
        db_key = f'{provider}.api_key'
        return self.get(db_key)

    def _get_from_db(self, key: str) -> Optional[Any]:
        """Get value from database"""
        try:
            # Load cache if needed
            if self._db_cache is None and self.db_path.exists():
                self._db_cache = {}
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("SELECT key, value, type FROM settings")
                for row in cursor.fetchall():
                    self._db_cache[row['key']] = self._convert_type_from_db(
                        row['value'],
                        row['type']
                    )

                conn.close()

            if self._db_cache and key in self._db_cache:
                return self._db_cache[key]

        except Exception:
            pass

        return None

    def _get_from_yaml(self, service: str, key: str) -> Optional[Any]:
        """Get value from service YAML config"""
        try:
            # Load cache if needed
            if service not in self._yaml_cache:
                if service == 'global':
                    yaml_path = Path("config.yaml")
                else:
                    yaml_path = Path(f"services/{service}/config.yaml")
                    if not yaml_path.exists():
                        yaml_path = Path("config.yaml")

                if yaml_path.exists():
                    with open(yaml_path, 'r') as f:
                        self._yaml_cache[service] = yaml.safe_load(f)
                else:
                    self._yaml_cache[service] = {}

            # Navigate nested keys (e.g., 'llm.provider' -> config['llm']['provider'])
            config = self._yaml_cache[service]
            parts = key.split('.')

            for part in parts:
                if isinstance(config, dict) and part in config:
                    config = config[part]
                else:
                    return None

            return config

        except Exception:
            return None

    def _convert_type(self, value: str) -> Any:
        """Convert string value to appropriate type"""
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False

        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def _convert_type_from_db(self, value: str, value_type: str) -> Any:
        """Convert database value to appropriate type"""
        if value_type == 'integer':
            return int(value)
        elif value_type == 'float':
            return float(value)
        elif value_type == 'boolean':
            return value.lower() in ('true', '1', 'yes')
        else:
            return value

    def get_llm_config(self) -> Dict[str, Any]:
        """Get complete LLM configuration"""
        provider = self.get('llm.provider', 'openrouter')

        return {
            'provider': provider,
            'model': self.get('llm.model', 'google/gemini-2.0-flash-001:free'),
            'temperature': self.get('llm.temperature', 0.3),
            'max_tokens': self.get('llm.max_tokens', 2000),
            'api_key': self.get_api_key(provider)
        }

    def get_crawler_config(self) -> Dict[str, Any]:
        """Get crawler configuration"""
        return {
            'delay': self.get('crawler.delay', 2.0),
            'max_pages': self.get('crawler.max_pages', 50),
            'max_depth': self.get('crawler.max_depth', 3)
        }

    # === Country Management ===

    def get_countries(self) -> Dict[str, Dict]:
        """
        Get all country configurations

        Returns:
            Dict of country configs with country code as key
        """
        # Try database first
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT value FROM settings
                WHERE key = 'countries' AND type = 'json'
            """)

            row = cursor.fetchone()
            conn.close()

            if row:
                import json
                return json.loads(row['value'])

        except Exception:
            pass

        # Fallback to YAML
        return self._get_from_yaml('global', 'countries') or {}

    def set_countries(self, countries: Dict[str, Dict]) -> bool:
        """
        Save country configurations to database

        Args:
            countries: Dict of country configs

        Returns:
            True if successful
        """
        try:
            import json
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, type, updated_at)
                VALUES ('countries', ?, 'json', CURRENT_TIMESTAMP)
            """, (json.dumps(countries),))

            conn.commit()
            conn.close()

            self._db_cache = None
            return True

        except Exception as e:
            print(f"Error saving countries: {e}")
            return False

    def add_country(self, code: str, name: str, base_url: str, seed_urls: list) -> bool:
        """
        Add or update a country configuration

        Args:
            code: Country code (e.g., 'ca', 'uk')
            name: Country name
            base_url: Base URL for the country site
            seed_urls: List of seed URLs to start crawling

        Returns:
            True if successful
        """
        countries = self.get_countries()

        countries[code] = {
            'name': name,
            'code': code.upper(),
            'base_url': base_url,
            'seed_urls': seed_urls
        }

        return self.set_countries(countries)

    def remove_country(self, code: str) -> bool:
        """Remove a country configuration"""
        countries = self.get_countries()

        if code in countries:
            del countries[code]
            return self.set_countries(countries)

        return False

    # === List Config Management ===

    def get_list_config(self, key: str, default: list = None) -> list:
        """
        Get a list configuration (e.g., keywords, visa_categories)

        Args:
            key: Config key (e.g., 'keywords', 'visa_categories')
            default: Default value

        Returns:
            List configuration
        """
        # Try database first
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT value FROM settings
                WHERE key = ? AND type = 'json'
            """, (key,))

            row = cursor.fetchone()
            conn.close()

            if row:
                import json
                return json.loads(row['value'])

        except Exception:
            pass

        # Fallback to YAML
        yaml_value = self._get_from_yaml('global', key)
        if yaml_value is not None:
            return yaml_value

        return default or []

    def set_list_config(self, key: str, value: list) -> bool:
        """
        Save a list configuration to database

        Args:
            key: Config key
            value: List value

        Returns:
            True if successful
        """
        try:
            import json
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, type, updated_at)
                VALUES (?, ?, 'json', CURRENT_TIMESTAMP)
            """, (key, json.dumps(value)))

            conn.commit()
            conn.close()

            self._db_cache = None
            return True

        except Exception as e:
            print(f"Error saving list config: {e}")
            return False

    # === Dict Config Management ===

    def get_dict_config(self, key: str, service: str = 'global', default: dict = None) -> dict:
        """
        Get a dict configuration (e.g., patterns, visa_type_keywords)

        Args:
            key: Config key
            service: Service name for YAML lookup
            default: Default value

        Returns:
            Dict configuration
        """
        # Try database first
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT value FROM settings
                WHERE key = ? AND type = 'json'
            """, (key,))

            row = cursor.fetchone()
            conn.close()

            if row:
                import json
                return json.loads(row['value'])

        except Exception:
            pass

        # Fallback to YAML
        yaml_value = self._get_from_yaml(service, key)
        if yaml_value is not None:
            return yaml_value

        return default or {}

    def set_dict_config(self, key: str, value: dict) -> bool:
        """
        Save a dict configuration to database

        Args:
            key: Config key
            value: Dict value

        Returns:
            True if successful
        """
        try:
            import json
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, type, updated_at)
                VALUES (?, ?, 'json', CURRENT_TIMESTAMP)
            """, (key, json.dumps(value)))

            conn.commit()
            conn.close()

            self._db_cache = None
            return True

        except Exception as e:
            print(f"Error saving dict config: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """
        Clear all database settings to reset to YAML defaults

        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM settings")

            conn.commit()
            conn.close()

            self._db_cache = None
            self._yaml_cache = {}
            return True

        except Exception as e:
            print(f"Error resetting config: {e}")
            return False


# Global instance
_config = None

def get_config() -> ConfigManager:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config
