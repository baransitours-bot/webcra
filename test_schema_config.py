#!/usr/bin/env python3
"""
Test configurable extraction schema system end-to-end
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from shared.config_manager import get_config
from shared.extraction_schema import SCHEMA_PRESETS, validate_schema, build_extraction_prompt
from shared.service_config import get_service_config

def test_schema_presets():
    """Test that all presets are valid"""
    print("=" * 60)
    print("TEST 1: Schema Presets Validation")
    print("=" * 60)

    for preset_name, preset_config in SCHEMA_PRESETS.items():
        print(f"\nTesting preset: {preset_name}")
        is_valid, errors = validate_schema(preset_config)

        if is_valid:
            print(f"  ✅ {preset_name.capitalize()} preset is valid")
        else:
            print(f"  ❌ {preset_name.capitalize()} preset has errors: {errors}")
            return False

    print("\n✅ All presets are valid")
    return True


def test_config_manager_schema():
    """Test ConfigManager schema methods"""
    print("\n" + "=" * 60)
    print("TEST 2: ConfigManager Schema Methods")
    print("=" * 60)

    config_mgr = get_config()

    # Test getting default schema
    print("\n1. Testing get_extraction_schema()...")
    schema = config_mgr.get_extraction_schema()

    if 'fields' in schema:
        print(f"  ✅ Got schema with {len(schema['fields'])} fields")
    else:
        print("  ❌ Schema missing 'fields' key")
        return False

    # Test loading presets
    print("\n2. Testing load_schema_preset()...")
    for preset_name in ['basic', 'standard', 'comprehensive']:
        print(f"  Loading {preset_name}...")
        success = config_mgr.load_schema_preset(preset_name)

        if success:
            loaded_schema = config_mgr.get_extraction_schema()
            if loaded_schema['fields'] == SCHEMA_PRESETS[preset_name]['fields']:
                print(f"    ✅ {preset_name.capitalize()} preset loaded correctly")
            else:
                print(f"    ❌ {preset_name.capitalize()} preset fields don't match")
                return False
        else:
            print(f"    ❌ Failed to load {preset_name} preset")
            return False

    # Test setting custom schema
    print("\n3. Testing set_extraction_schema()...")
    custom_schema = SCHEMA_PRESETS['basic'].copy()
    custom_schema['fields']['processing_time']['enabled'] = False

    success = config_mgr.set_extraction_schema(custom_schema)
    if success:
        loaded_schema = config_mgr.get_extraction_schema()
        if not loaded_schema['fields']['processing_time']['enabled']:
            print("  ✅ Custom schema saved correctly")
        else:
            print("  ❌ Custom schema not applied")
            return False
    else:
        print("  ❌ Failed to save custom schema")
        return False

    print("\n✅ ConfigManager schema methods working")
    return True


def test_service_config_integration():
    """Test ServiceConfigLoader integration"""
    print("\n" + "=" * 60)
    print("TEST 3: ServiceConfigLoader Integration")
    print("=" * 60)

    # Load standard preset first
    config_mgr = get_config()
    config_mgr.load_schema_preset('standard')

    # Get classifier config
    service_config = get_service_config()
    classifier_config = service_config.get_classifier_config()

    if 'extraction_schema' in classifier_config:
        schema = classifier_config['extraction_schema']
        print(f"  ✅ Classifier config includes extraction_schema")
        print(f"  ✅ Schema has {len(schema.get('fields', {}))} fields")

        # Check it matches what we set
        direct_schema = config_mgr.get_extraction_schema()
        if schema['fields'] == direct_schema['fields']:
            print("  ✅ Schema matches ConfigManager")
        else:
            print("  ❌ Schema doesn't match ConfigManager")
            return False
    else:
        print("  ❌ Classifier config missing extraction_schema")
        return False

    print("\n✅ ServiceConfigLoader integration working")
    return True


def test_prompt_building():
    """Test dynamic prompt building"""
    print("\n" + "=" * 60)
    print("TEST 4: Dynamic Prompt Building")
    print("=" * 60)

    config_mgr = get_config()
    sample_text = "Australia Skilled Worker Visa (subclass 189). Requirements: Age 18-44, IELTS 6, Bachelor's degree. Fee: $4,240 AUD. Processing: 5-8 months."

    # Test with different presets
    for preset_name in ['basic', 'standard', 'comprehensive']:
        print(f"\nTesting prompt with {preset_name} preset...")

        # Load preset
        config_mgr.load_schema_preset(preset_name)
        schema = config_mgr.get_extraction_schema()

        # Build prompt
        prompt = build_extraction_prompt(schema, sample_text, "Australia")

        # Check prompt contains enabled fields
        fields = schema['fields']
        enabled_field_names = [f for f, cfg in fields.items() if cfg.get('enabled', False)]

        print(f"  Schema has {len(enabled_field_names)} enabled fields")

        # Verify prompt length increases with more fields
        token_estimate = len(prompt.split())
        print(f"  Prompt length: ~{token_estimate} words (~{int(token_estimate * 1.3)} tokens)")

        # Check key fields are mentioned
        if 'visa_type' in enabled_field_names:
            if 'visa_type' in prompt:
                print("  ✅ Prompt includes visa_type")
            else:
                print("  ❌ Prompt missing visa_type")
                return False

        # Check comprehensive has more content than basic
        if preset_name == 'comprehensive':
            if token_estimate > 500:
                print("  ✅ Comprehensive prompt is detailed")
            else:
                print("  ⚠️ Comprehensive prompt seems short")
        elif preset_name == 'basic':
            if token_estimate < 400:
                print("  ✅ Basic prompt is concise")
            else:
                print("  ⚠️ Basic prompt seems long")

    print("\n✅ Prompt building working correctly")
    return True


def test_validation():
    """Test schema validation"""
    print("\n" + "=" * 60)
    print("TEST 5: Schema Validation")
    print("=" * 60)

    # Valid schema
    print("\n1. Testing valid schema...")
    valid_schema = {
        'fields': {
            'visa_type': {'enabled': True, 'required': True},
            'country': {'enabled': True, 'required': True},
            'category': {'enabled': True}
        }
    }

    is_valid, errors = validate_schema(valid_schema)
    if is_valid:
        print("  ✅ Valid schema passes validation")
    else:
        print(f"  ❌ Valid schema failed: {errors}")
        return False

    # Invalid schema - missing visa_type
    print("\n2. Testing invalid schema (missing visa_type)...")
    invalid_schema = {
        'fields': {
            'country': {'enabled': True, 'required': True},
            'category': {'enabled': True}
        }
    }

    is_valid, errors = validate_schema(invalid_schema)
    if not is_valid:
        print(f"  ✅ Invalid schema correctly rejected: {errors[0]}")
    else:
        print("  ❌ Invalid schema incorrectly accepted")
        return False

    # Invalid schema - no fields key
    print("\n3. Testing invalid schema (no fields key)...")
    invalid_schema2 = {'something': 'else'}

    is_valid, errors = validate_schema(invalid_schema2)
    if not is_valid:
        print(f"  ✅ Invalid schema correctly rejected: {errors[0]}")
    else:
        print("  ❌ Invalid schema incorrectly accepted")
        return False

    print("\n✅ Schema validation working correctly")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CONFIGURABLE EXTRACTION SCHEMA - END-TO-END TEST")
    print("=" * 60)

    tests = [
        test_schema_presets,
        test_config_manager_schema,
        test_service_config_integration,
        test_prompt_building,
        test_validation
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test {test_func.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total} tests")

    if all(results):
        print("\n🎉 ALL TESTS PASSED! Schema configuration system is working!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED! Please review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
