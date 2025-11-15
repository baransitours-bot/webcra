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


# Global instance
_config = None

def get_config() -> ConfigManager:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config
