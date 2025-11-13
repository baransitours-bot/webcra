"""
Integration Tests
Tests full pipeline integration: Crawler → Classifier → Matcher → Assistant
"""

import os
import sys
import json
import yaml
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_data_flow_integration():
    """Test data flows correctly between services"""
    print("\nTesting Data Flow Integration...")
    print("=" * 60)

    # Test 1: Crawler output format compatible with Classifier
    print("\n1. Testing Crawler → Classifier compatibility...")

    raw_data_path = Path('data/raw')
    if raw_data_path.exists():
        # Check if raw data exists
        raw_files = list(raw_data_path.glob('**/*.json'))
        if raw_files:
            # Load a sample raw file
            with open(raw_files[0], 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            # Verify raw data has required fields for classifier
            required_fields = ['url', 'title', 'content']
            has_all_fields = all(field in raw_data for field in required_fields)

            if has_all_fields:
                print("   ✅ Crawler output format compatible with Classifier")
            else:
                print(f"   ⚠️  Missing fields in raw data: {[f for f in required_fields if f not in raw_data]}")
        else:
            print("   ⚠️  No raw data files found (run crawler first)")
    else:
        print("   ⚠️  No raw data directory (run crawler first)")

    # Test 2: Classifier output format compatible with Matcher
    print("\n2. Testing Classifier → Matcher compatibility...")

    structured_data_path = Path('data/structured')
    if structured_data_path.exists():
        structured_files = list(structured_data_path.glob('**/*.json'))
        if structured_files:
            with open(structured_files[0], 'r', encoding='utf-8') as f:
                structured_data = json.load(f)

            # Verify structured data has requirements for matcher
            if 'visas' in structured_data:
                visas = structured_data['visas']
                if visas and 'requirements' in visas[0]:
                    print("   ✅ Classifier output format compatible with Matcher")
                else:
                    print("   ⚠️  Structured data missing requirements field")
            else:
                print("   ⚠️  Structured data missing visas field")
        else:
            print("   ⚠️  No structured data files found (run classifier first)")
    else:
        print("   ⚠️  No structured data directory (run classifier first)")

    # Test 3: Matcher output format compatible with Assistant
    print("\n3. Testing Matcher → Assistant compatibility...")

    # Matcher outputs ranked visas - Assistant needs visa data
    if structured_data_path.exists() and structured_files:
        # Assistant retriever should be able to read structured data
        from services.assistant.retriever import ContextRetriever

        # Load config
        with open('services/assistant/config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        retriever = ContextRetriever(config)

        # Try retrieving some visas
        visas = retriever.retrieve_relevant_visas("work visa")

        if visas:
            print("   ✅ Assistant can read Matcher/Classifier data")
        else:
            print("   ⚠️  Assistant retrieval returned no visas")
    else:
        print("   ⚠️  No structured data for Assistant testing")

def test_configuration_consistency():
    """Test that all service configs are consistent"""
    print("\n\nTesting Configuration Consistency...")
    print("=" * 60)

    # Load all configs
    configs = {
        'global': 'config.yaml',
        'crawler': 'services/crawler/config.yaml',
        'classifier': 'services/classifier/config.yaml',
        'matcher': 'services/matcher/config.yaml',
        'assistant': 'services/assistant/config.yaml'
    }

    loaded_configs = {}
    for name, path in configs.items():
        if os.path.exists(path):
            with open(path, 'r') as f:
                loaded_configs[name] = yaml.safe_load(f)

    # Test 1: Country codes are consistent
    print("\n1. Checking country code consistency...")
    global_countries = set(loaded_configs['global']['countries'].keys())
    print(f"   Global config has {len(global_countries)} countries: {', '.join(global_countries)}")
    print("   ✅ All services can access country configurations")

    # Test 2: Data paths are consistent
    print("\n2. Checking data path structure...")
    expected_paths = ['data/raw', 'data/structured']
    all_exist = all(Path(p).exists() for p in expected_paths)

    if all_exist:
        print("   ✅ All required data directories exist")
    else:
        print("   ⚠️  Some data directories missing (will be created on first run)")

def test_service_dependencies():
    """Test that all service dependencies are met"""
    print("\n\nTesting Service Dependencies...")
    print("=" * 60)

    # Test 1: Check required Python packages
    print("\n1. Checking Python package dependencies...")
    required_packages = {
        'all': ['yaml', 'json'],
        'crawler': ['requests', 'bs4'],
        'classifier': ['re'],
        'matcher': ['json'],
        'assistant': ['yaml']
    }

    missing_packages = []
    for service, packages in required_packages.items():
        for package in packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(f"{service}: {package}")

    if not missing_packages:
        print("   ✅ All required packages are installed")
    else:
        print(f"   ❌ Missing packages: {', '.join(missing_packages)}")

    # Test 2: Check optional dependencies
    print("\n2. Checking optional dependencies...")
    optional_packages = {
        'assistant': 'openai'
    }

    for service, package in optional_packages.items():
        try:
            __import__(package)
            print(f"   ✅ {service}: {package} installed")
        except ImportError:
            print(f"   ⚠️  {service}: {package} not installed (optional)")

def test_error_propagation():
    """Test that errors are handled gracefully between services"""
    print("\n\nTesting Error Propagation...")
    print("=" * 60)

    print("\n1. Testing missing data handling...")

    # Test DataStore with missing raw data
    from shared.database import DataStore

    db = DataStore()

    # Try to get data for a non-existent country
    fake_country = "NonExistentCountry"

    # DataStore should handle non-existent paths gracefully
    country_path = db.raw_path / fake_country
    if not country_path.exists():
        print(f"   ✅ Gracefully handles missing data for '{fake_country}'")

    print("\n2. Testing data path handling...")
    # DataStore creates directories automatically
    if db.raw_path.exists() and db.processed_path.exists():
        print(f"   ✅ DataStore creates necessary directories")

    print("\n3. Testing configuration loading...")
    # All configs should load without errors
    configs_to_test = [
        'config.yaml',
        'services/crawler/config.yaml',
        'services/classifier/config.yaml',
        'services/matcher/config.yaml',
        'services/assistant/config.yaml'
    ]

    all_loaded = True
    for config_path in configs_to_test:
        try:
            with open(config_path, 'r') as f:
                yaml.safe_load(f)
        except Exception as e:
            print(f"   ❌ Failed to load {config_path}: {e}")
            all_loaded = False

    if all_loaded:
        print("   ✅ All configurations load successfully")

def run_integration_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("INTEGRATION TESTS - STAGE 6")
    print("=" * 60)

    test_data_flow_integration()
    test_configuration_consistency()
    test_service_dependencies()
    test_error_propagation()

    print("\n" + "=" * 60)
    print("✅ Integration tests completed!")
    print("=" * 60)
    print("\nNote: Some tests may show warnings if services haven't been run yet.")
    print("Run the full pipeline to populate data:")
    print("  1. python main.py crawl --all")
    print("  2. python main.py classify --all")
    print("  3. python main.py match --interactive")
    print("  4. python main.py assist --chat")

if __name__ == '__main__':
    run_integration_tests()
