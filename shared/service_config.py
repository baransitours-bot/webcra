"""
Centralized Configuration System
All services get configuration from database via ConfigManager
YAML files are ONLY used as defaults on first run
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import sqlite3
from shared.config_manager import ConfigManager


class ServiceConfigLoader:
    """
    Centralized configuration loader for all services
    Priority: Runtime > Database > YAML Defaults
    """

    def __init__(self):
        self.config_mgr = ConfigManager()
        self._initialized = False

    def initialize_from_yaml_if_empty(self):
        """
        Load defaults from YAML files into database if database is empty
        This runs ONCE on first setup
        """
        if self._initialized:
            return

        # Check if database has configuration
        countries = self.config_mgr.get_countries()

        if not countries:
            # Database is empty, load from YAML defaults
            print("📥 First-time setup: Loading configuration defaults from YAML...")
            self._load_yaml_defaults()

        self._initialized = True

    def _load_yaml_defaults(self):
        """Load all configuration defaults from YAML files into database"""

        # 1. Load global config.yaml
        global_config_path = Path('config.yaml')
        if global_config_path.exists():
            with open(global_config_path, 'r') as f:
                global_config = yaml.safe_load(f)

            # Load countries
            if 'countries' in global_config:
                self.config_mgr.set_countries(global_config['countries'])
                print(f"  ✓ Loaded {len(global_config['countries'])} countries")

            # Load keywords
            if 'keywords' in global_config:
                self.config_mgr.set_list_config('keywords', global_config['keywords'])
                print(f"  ✓ Loaded {len(global_config['keywords'])} keywords")

            # Load visa categories
            if 'visa_categories' in global_config:
                self.config_mgr.set_list_config('visa_categories', global_config['visa_categories'])
                print(f"  ✓ Loaded {len(global_config['visa_categories'])} visa categories")

        # 2. Load service-specific configs
        self._load_service_yaml('crawler')
        self._load_service_yaml('classifier')
        self._load_service_yaml('matcher')
        self._load_service_yaml('assistant')

        print("✅ Configuration defaults loaded into database")

    def _load_service_yaml(self, service_name: str):
        """Load service-specific YAML config into database"""
        config_path = Path(f'services/{service_name}/config.yaml')

        if not config_path.exists():
            return

        with open(config_path, 'r') as f:
            service_config = yaml.safe_load(f)

        # Store service config as JSON in database
        if service_config:
            self.config_mgr.set_dict_config(f'{service_name}_config', service_config)
            print(f"  ✓ Loaded {service_name} configuration")

    # ========== SERVICE CONFIG GETTERS ==========

    def get_crawler_config(self) -> Dict[str, Any]:
        """Get complete crawler configuration from database"""
        self.initialize_from_yaml_if_empty()

        # Load from ConfigManager (DB > YAML defaults)
        service_config = self.config_mgr.get_dict_config('crawler_config', service='crawler', default={})

        config = {
            'crawling': {
                'max_depth': self.config_mgr.get('crawler.max_depth', 3),
                'max_pages_per_country': self.config_mgr.get('crawler.max_pages', 100),
                'delay_between_requests': self.config_mgr.get('crawler.delay', 1.0),
                'concurrent_requests': service_config.get('crawling', {}).get('concurrent_requests', 1),
                'timeout': service_config.get('crawling', {}).get('timeout', 30),
                'robots_txt': service_config.get('crawling', {}).get('robots_txt', True),
                'user_agent': service_config.get('crawling', {}).get('user_agent', 'Mozilla/5.0 (compatible; ImmigrationBot/1.0)')
            },
            'keywords': self.config_mgr.get_list_config('keywords', []),
            'download_extensions': service_config.get('download_extensions', ['.pdf', '.doc', '.docx', '.xlsx']),
            'exclude_patterns': service_config.get('exclude_patterns', ['/news/', '/media/', '/contact/', '/about/'])
        }

        return config

    def get_classifier_config(self) -> Dict[str, Any]:
        """Get complete classifier configuration from database"""
        self.initialize_from_yaml_if_empty()

        service_config = self.config_mgr.get_dict_config('classifier_config', service='classifier', default={})
        llm_config = self.config_mgr.get_llm_config()

        config = {
            'llm': llm_config,
            'visa_categories': self.config_mgr.get_list_config('visa_categories', []),
            'visa_type_keywords': self.config_mgr.get_dict_config('visa_type_keywords', service='classifier', default={}),
            'extraction_fields': service_config.get('extraction_fields', []),
            'batch_size': service_config.get('batch_size', 1),
            'retry_attempts': service_config.get('retry_attempts', 2)
        }

        return config

    def get_matcher_config(self) -> Dict[str, Any]:
        """Get complete matcher configuration from database"""
        self.initialize_from_yaml_if_empty()

        service_config = self.config_mgr.get_dict_config('matcher_config', service='matcher', default={})

        config = {
            'matching': {
                'strict_mode': service_config.get('matching', {}).get('strict_mode', False),
                'partial_match_score': service_config.get('matching', {}).get('partial_match_score', 0.5),
                'minimum_score': service_config.get('matching', {}).get('minimum_score', 0.3)
            },
            'scoring_weights': service_config.get('scoring_weights', {
                'age': 0.15,
                'education': 0.25,
                'experience': 0.25,
                'language': 0.20,
                'funds': 0.15
            })
        }

        return config

    def get_assistant_config(self) -> Dict[str, Any]:
        """Get complete assistant configuration from database"""
        self.initialize_from_yaml_if_empty()

        service_config = self.config_mgr.get_dict_config('assistant_config', service='assistant', default={})
        llm_config = self.config_mgr.get_llm_config()

        config = {
            'llm': llm_config,
            'retrieval': service_config.get('retrieval', {
                'top_k': 5,
                'similarity_threshold': 0.7
            }),
            'response_style': service_config.get('response_style', 'professional')
        }

        return config

    def get_countries(self) -> Dict[str, Dict]:
        """Get all countries from database"""
        self.initialize_from_yaml_if_empty()
        return self.config_mgr.get_countries()

    def get_country_list(self) -> list:
        """Get list of country codes"""
        countries = self.get_countries()
        return list(countries.keys())


# Global instance
_service_config = None


def get_service_config() -> ServiceConfigLoader:
    """Get global service config loader instance"""
    global _service_config
    if _service_config is None:
        _service_config = ServiceConfigLoader()
    return _service_config
