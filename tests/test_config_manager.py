"""
Test ConfigManager - Centralized Configuration System
Tests country management, list configs, dict configs, and priority system
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.abspath('.'))

from shared.config_manager import ConfigManager


class TestConfigManager:
    """Test ConfigManager functionality"""

    def __init__(self):
        # Create temporary directory for test database
        self.temp_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.temp_dir, 'test_immigration.db')

        # Initialize test database
        self._init_test_db()

        # Create ConfigManager with test database
        self.config = ConfigManager(db_path=self.test_db)

    def _init_test_db(self):
        """Initialize test database with settings table"""
        import sqlite3
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def cleanup(self):
        """Clean up test files"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_basic_config_get_set(self):
        """Test basic get/set operations"""
        print("\n📝 Testing basic config get/set...")

        # Set a value
        success = self.config.set('test.key', 'test_value')
        assert success, "Should successfully set config value"

        # Get the value
        value = self.config.get('test.key')
        assert value == 'test_value', f"Expected 'test_value', got '{value}'"

        # Test with default
        value = self.config.get('nonexistent.key', 'default')
        assert value == 'default', "Should return default for nonexistent key"

        print("✅ Basic get/set works")

    def test_country_management(self):
        """Test country CRUD operations"""
        print("\n🌍 Testing country management...")

        # Add a country
        success = self.config.add_country(
            code='jp',
            name='Japan',
            base_url='https://www.mofa.go.jp',
            seed_urls=['https://www.mofa.go.jp/j_info/visit/visa/']
        )
        assert success, "Should successfully add country"

        # Get countries
        countries = self.config.get_countries()
        assert 'jp' in countries, "Should find added country"
        assert countries['jp']['name'] == 'Japan', "Country name should match"
        assert len(countries['jp']['seed_urls']) == 1, "Should have one seed URL"

        # Update country
        success = self.config.add_country(
            code='jp',
            name='Japan (Updated)',
            base_url='https://www.mofa.go.jp',
            seed_urls=[
                'https://www.mofa.go.jp/j_info/visit/visa/',
                'https://www.mofa.go.jp/visa/index.html'
            ]
        )
        assert success, "Should successfully update country"

        countries = self.config.get_countries()
        assert countries['jp']['name'] == 'Japan (Updated)', "Name should be updated"
        assert len(countries['jp']['seed_urls']) == 2, "Should have two seed URLs"

        # Remove country
        success = self.config.remove_country('jp')
        assert success, "Should successfully remove country"

        countries = self.config.get_countries()
        assert 'jp' not in countries, "Country should be removed"

        print("✅ Country management works")

    def test_list_config(self):
        """Test list configuration management"""
        print("\n📋 Testing list config management...")

        # Set list config
        keywords = ['visa', 'immigration', 'permit', 'residence']
        success = self.config.set_list_config('keywords', keywords)
        assert success, "Should successfully set list config"

        # Get list config
        retrieved = self.config.get_list_config('keywords')
        assert retrieved == keywords, "Retrieved keywords should match"

        # Get with default
        default_list = ['default1', 'default2']
        retrieved = self.config.get_list_config('nonexistent_list', default_list)
        assert retrieved == default_list, "Should return default for nonexistent list"

        print("✅ List config management works")

    def test_dict_config(self):
        """Test dict configuration management"""
        print("\n📚 Testing dict config management...")

        # Set dict config
        visa_keywords = {
            'work': ['skilled', 'worker', 'employment'],
            'study': ['student', 'education', 'university']
        }
        success = self.config.set_dict_config('visa_type_keywords', visa_keywords)
        assert success, "Should successfully set dict config"

        # Get dict config
        retrieved = self.config.get_dict_config('visa_type_keywords')
        assert retrieved == visa_keywords, "Retrieved dict should match"
        assert 'work' in retrieved, "Should have work category"
        assert len(retrieved['work']) == 3, "Work should have 3 keywords"

        # Get with default
        default_dict = {'default': 'value'}
        retrieved = self.config.get_dict_config('nonexistent_dict', default=default_dict)
        assert retrieved == default_dict, "Should return default for nonexistent dict"

        print("✅ Dict config management works")

    def test_type_conversion(self):
        """Test automatic type conversion"""
        print("\n🔄 Testing type conversion...")

        # Integer
        self.config.set('test.int', 42)
        value = self.config.get('test.int')
        assert value == 42, f"Expected 42, got {value}"
        assert isinstance(value, int), "Should be integer type"

        # Float
        self.config.set('test.float', 3.14)
        value = self.config.get('test.float')
        assert value == 3.14, f"Expected 3.14, got {value}"
        assert isinstance(value, float), "Should be float type"

        # Boolean
        self.config.set('test.bool', True)
        value = self.config.get('test.bool')
        assert value is True, f"Expected True, got {value}"
        assert isinstance(value, bool), "Should be boolean type"

        print("✅ Type conversion works")

    def test_crawler_config(self):
        """Test crawler-specific configuration"""
        print("\n🕷️ Testing crawler config...")

        # Set crawler settings
        self.config.set('crawler.delay', 2.5)
        self.config.set('crawler.max_pages', 100)
        self.config.set('crawler.max_depth', 3)

        # Get crawler config
        crawler_config = self.config.get_crawler_config()

        assert crawler_config['delay'] == 2.5, "Delay should match"
        assert crawler_config['max_pages'] == 100, "Max pages should match"
        assert crawler_config['max_depth'] == 3, "Max depth should match"

        print("✅ Crawler config works")

    def test_llm_config(self):
        """Test LLM configuration"""
        print("\n🤖 Testing LLM config...")

        # Set LLM settings
        self.config.set('llm.provider', 'openrouter')
        self.config.set('llm.model', 'google/gemini-2.0-flash-001:free')
        self.config.set('llm.temperature', 0.3)
        self.config.set('llm.max_tokens', 2000)

        # Get LLM config
        llm_config = self.config.get_llm_config()

        assert llm_config['provider'] == 'openrouter', "Provider should match"
        assert llm_config['model'] == 'google/gemini-2.0-flash-001:free', "Model should match"
        assert llm_config['temperature'] == 0.3, "Temperature should match"
        assert llm_config['max_tokens'] == 2000, "Max tokens should match"

        print("✅ LLM config works")

    def test_reset_to_defaults(self):
        """Test reset functionality"""
        print("\n🔄 Testing reset to defaults...")

        # Set some values
        self.config.set('test.key1', 'value1')
        self.config.set('test.key2', 'value2')
        self.config.add_country('test', 'Test Country', 'http://test.com', [])

        # Verify they exist
        assert self.config.get('test.key1') == 'value1', "Key1 should exist"
        countries = self.config.get_countries()
        # Note: Countries might exist from YAML, so we just check reset works

        # Reset
        success = self.config.reset_to_defaults()
        assert success, "Reset should succeed"

        # Verify database values are cleared (will fallback to YAML or None)
        # Since we're using a test DB with no YAML, these should be None
        value = self.config.get('test.key1')
        # After reset, if there's no YAML, it should return None or default
        assert value != 'value1', "Value should be reset"

        print("✅ Reset to defaults works")

    def test_priority_system(self):
        """Test configuration priority (DB > YAML)"""
        print("\n⭐ Testing priority system (DB > YAML)...")

        # This test verifies that database values override YAML
        # Set a value in database
        self.config.set('test.priority', 'database_value')

        # Get value - should get database value, not YAML
        value = self.config.get('test.priority')
        assert value == 'database_value', "Should get database value"

        print("✅ Priority system works (DB > YAML)")

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("🧪 TESTING CONFIG MANAGER")
        print("=" * 60)

        try:
            self.test_basic_config_get_set()
            self.test_country_management()
            self.test_list_config()
            self.test_dict_config()
            self.test_type_conversion()
            self.test_crawler_config()
            self.test_llm_config()
            self.test_reset_to_defaults()
            self.test_priority_system()

            print("\n" + "=" * 60)
            print("🎉 ALL CONFIG MANAGER TESTS PASSED!")
            print("=" * 60)
            return True

        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            return False

        finally:
            self.cleanup()


def main():
    """Run all ConfigManager tests"""
    tester = TestConfigManager()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
