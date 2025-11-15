"""
System Test - Validate All Operations
Tests all components and shows configuration sources
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from shared.database import Database


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_config_sources():
    """Test where configurations are being read from"""
    print_section("CONFIG SOURCE TEST")

    configs_to_check = {
        "Crawler": "services/crawler/config.yaml",
        "Classifier": "services/classifier/config.yaml",
        "Matcher": "services/matcher/config.yaml",
        "Assistant": "services/assistant/config.yaml"
    }

    for service, config_path in configs_to_check.items():
        print(f"\n{service} Config:")
        print(f"  File: {config_path}")

        if not Path(config_path).exists():
            print(f"  ❌ File not found")
            continue

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Check if it has LLM config
            if 'llm' in config:
                provider = config['llm'].get('provider', 'N/A')
                print(f"  LLM Provider: {provider}")

                # Check API key source
                if provider == 'openrouter':
                    api_key_env = config['llm']['openrouter'].get('api_key_env', 'N/A')
                elif provider == 'openai':
                    api_key_env = config['llm']['openai'].get('api_key_env', 'N/A')
                else:
                    api_key_env = 'N/A'

                print(f"  API Key Config: {api_key_env}")

                # Check if it's direct key or env variable
                if api_key_env.startswith('sk-'):
                    print(f"  ✅ Source: DIRECT KEY in YAML file")
                else:
                    env_value = os.getenv(api_key_env)
                    if env_value:
                        print(f"  ✅ Source: ENVIRONMENT VARIABLE ({api_key_env})")
                        print(f"  ✅ Value exists: {env_value[:10]}...")
                    else:
                        print(f"  ⚠️  Source: ENVIRONMENT VARIABLE ({api_key_env})")
                        print(f"  ❌ NOT SET in environment")
            else:
                print(f"  ⚠️  No LLM config in this service")

        except Exception as e:
            print(f"  ❌ Error reading config: {str(e)}")


def test_config_manager():
    """Test unified config manager"""
    print_section("CONFIG MANAGER TEST")

    try:
        from shared.config_manager import get_config
        from pathlib import Path

        config = get_config()
        print("✅ ConfigManager imported successfully")

        # Check .env file
        env_file = Path('.env')
        if env_file.exists():
            print("✅ .env file found")
        else:
            print("⚠️  No .env file (will use Database/YAML)")

        # Test getting settings
        llm_provider = config.get('llm.provider', 'unknown')
        llm_model = config.get('llm.model', 'unknown')

        print(f"\nActive Configuration:")
        print(f"  Provider: {llm_provider}")
        print(f"  Model: {llm_model}")

        # Check API key
        api_key = config.get_api_key()
        if api_key:
            print(f"  ✅ API Key: {api_key[:8]}... (configured)")
        else:
            print(f"  ⚠️  API Key: Not configured")

        # Show priority
        print(f"\nConfig Priority: .env > Database > YAML")

    except Exception as e:
        print(f"❌ ConfigManager test failed: {str(e)}")


def test_database():
    """Test database connection and structure"""
    print_section("DATABASE TEST")

    try:
        db = Database()
        print("✅ Database initialized: data/immigration.db")

        # Test tables exist
        print("\nChecking tables...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table'
                ORDER BY name
            """)
            tables = [row['name'] for row in cursor.fetchall()]

        expected_tables = [
            'crawled_pages', 'visas', 'clients',
            'eligibility_checks', 'documents',
            'process_tracking', 'embeddings', 'settings'
        ]

        for table in expected_tables:
            if table in tables:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} - MISSING")

        # Show stats
        stats = db.get_stats()
        print("\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")

    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")


def test_crawler():
    """Test crawler components"""
    print_section("CRAWLER TEST")

    try:
        # Check if crawler can be imported
        from services.crawler.spider import ImmigrationCrawler
        print("✅ Crawler module imports successfully")

        # Check config
        with open('services/crawler/config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        print(f"✅ Crawler config loaded")
        print(f"  Keywords: {len(config.get('keywords', []))} defined")
        print(f"  Exclude patterns: {len(config.get('exclude_patterns', []))} defined")

        # Check if we have crawled data
        db = Database()
        pages = db.get_latest_pages()
        print(f"  Crawled pages in DB: {len(pages)}")

        if pages:
            countries = set(p['country'] for p in pages)
            print(f"  Countries: {', '.join(countries)}")

    except Exception as e:
        print(f"❌ Crawler test failed: {str(e)}")


def test_classifier():
    """Test classifier components"""
    print_section("CLASSIFIER TEST")

    try:
        # Check if extractor can be imported
        from services.classifier.visa_extractor import VisaExtractor
        print("✅ Classifier module imports successfully")

        # Check config
        with open('services/classifier/config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        print(f"✅ Classifier config loaded")

        if 'llm' in config:
            provider = config['llm'].get('provider')
            model = config['llm'].get(provider, {}).get('model')
            print(f"  LLM Provider: {provider}")
            print(f"  Model: {model}")

        # Check if we have classified visas
        db = Database()
        visas = db.get_latest_visas()
        print(f"  Visas in DB: {len(visas)}")

        if visas:
            countries = set(v['country'] for v in visas)
            categories = set(v['category'] for v in visas)
            print(f"  Countries: {', '.join(countries)}")
            print(f"  Categories: {', '.join(categories)}")

    except Exception as e:
        print(f"❌ Classifier test failed: {str(e)}")


def test_matcher():
    """Test matcher components"""
    print_section("MATCHER TEST")

    try:
        # Check if matcher can be imported
        from services.matcher.ranker import VisaRanker
        from services.matcher.scorer import EligibilityScorer
        print("✅ Matcher modules import successfully")

        # Check config
        with open('services/matcher/config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        print(f"✅ Matcher config loaded")
        print(f"  Education levels: {len(config.get('education_levels', {}))} defined")
        print(f"  Scoring weights configured: {bool(config.get('scoring'))}")

        # Test a sample match
        db = Database()
        visas = db.get_latest_visas()

        if visas:
            sample_profile = {
                'age': 28,
                'education': 'bachelor',
                'experience_years': 5,
                'target_countries': ['usa']
            }

            ranker = VisaRanker(config)
            matches = ranker.rank_all_visas(sample_profile, visas)

            print(f"  Test profile matched: {len(matches)} visas")
            if matches:
                top_match = matches[0]
                print(f"  Top match: {top_match['visa_type']}")
                print(f"  Score: {top_match['eligibility_score']}%")
        else:
            print("  ⚠️  No visas to test matching")

    except Exception as e:
        print(f"❌ Matcher test failed: {str(e)}")


def test_embeddings():
    """Test embeddings/semantic search"""
    print_section("EMBEDDINGS TEST")

    try:
        db = Database()
        embeddings = db.get_embeddings()

        print(f"  Embeddings in DB: {len(embeddings)}")

        if embeddings:
            print(f"  ✅ Semantic search ready")
            print(f"  Model: {embeddings[0].get('model_name', 'all-MiniLM-L6-v2')}")

            # Try to load model
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L6-v2')
                print(f"  ✅ Sentence transformer model loaded")
            except ImportError:
                print(f"  ⚠️  sentence-transformers not installed")
        else:
            print(f"  ⚠️  No embeddings indexed yet")
            print(f"  Run: python scripts/index_embeddings.py")

    except Exception as e:
        print(f"❌ Embeddings test failed: {str(e)}")


def test_assistant():
    """Test assistant components"""
    print_section("ASSISTANT TEST")

    try:
        # Check if assistant modules can be imported
        from services.assistant.llm_client import LLMClient
        print("✅ Assistant modules import successfully")

        # Check config
        with open('services/assistant/config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        print(f"✅ Assistant config loaded")

        provider = config['llm'].get('provider')
        print(f"  LLM Provider: {provider}")

        # Check API key availability
        if provider == 'openrouter':
            api_key_env = config['llm']['openrouter']['api_key_env']
        else:
            api_key_env = config['llm']['openai']['api_key_env']

        if api_key_env.startswith('sk-'):
            print(f"  ✅ API key configured directly in YAML")
        else:
            env_value = os.getenv(api_key_env)
            if env_value:
                print(f"  ✅ API key found in environment: {api_key_env}")
            else:
                print(f"  ⚠️  API key NOT found: {api_key_env}")
                print(f"  Set with: export {api_key_env}='your-key'")

    except Exception as e:
        print(f"❌ Assistant test failed: {str(e)}")


def test_file_structure():
    """Test project file structure"""
    print_section("FILE STRUCTURE TEST")

    important_paths = {
        "Main entry": "main.py",
        "Web UI": "app.py",
        "Database": "data/immigration.db",
        "Global config": "config.yaml",
        "Crawler service": "services/crawler/",
        "Classifier service": "services/classifier/",
        "Matcher service": "services/matcher/",
        "Assistant service": "services/assistant/",
        "Scripts dir": "scripts/",
        "Pages dir": "pages/"
    }

    for name, path in important_paths.items():
        if Path(path).exists():
            if Path(path).is_file():
                size = Path(path).stat().st_size
                print(f"  ✅ {name}: {path} ({size:,} bytes)")
            else:
                files = len(list(Path(path).rglob("*")))
                print(f"  ✅ {name}: {path} ({files} files)")
        else:
            print(f"  ⚠️  {name}: {path} - NOT FOUND")


def main():
    """Run all tests"""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  IMMIGRATION PLATFORM - SYSTEM TEST".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    # Run all tests
    test_file_structure()
    test_config_sources()
    test_config_manager()
    test_database()
    test_crawler()
    test_classifier()
    test_matcher()
    test_embeddings()
    test_assistant()

    # Summary
    print_section("TEST COMPLETE")
    print("\nAll components tested. Check output above for any ❌ failures.")
    print("\nNext steps:")
    print("  1. If configs show ❌ - Set API keys in .env or config.yaml")
    print("  2. If data shows 0 - Run Crawler and Classifier UI")
    print("  3. If embeddings show 0 - Run: python scripts/index_embeddings.py")
    print()


if __name__ == "__main__":
    main()
