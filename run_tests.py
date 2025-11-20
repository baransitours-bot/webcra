#!/usr/bin/env python3
"""
Comprehensive Test Runner
Runs all unit tests for the Immigration Platform
"""

import subprocess
import sys
from pathlib import Path


def run_test(test_file: str, description: str) -> bool:
    """
    Run a single test file.

    Args:
        test_file: Path to test file
        description: Test description

    Returns:
        True if test passed, False otherwise
    """
    print(f"\n{'=' * 70}")
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print('=' * 70)

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ {description} PASSED")
            return True
        else:
            print(f"❌ {description} FAILED")
            return False

    except Exception as e:
        print(f"❌ {description} ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 IMMIGRATION PLATFORM - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    tests = [
        ("tests/test_config_manager.py", "ConfigManager - Centralized Configuration"),
        ("tests/test_crawler_service.py", "Crawler - Engine, Repository, Interface"),
    ]

    results = {}

    for test_file, description in tests:
        if Path(test_file).exists():
            results[description] = run_test(test_file, description)
        else:
            print(f"\n⚠️ Test file not found: {test_file}")
            results[description] = False

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for description, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{status:12} | {description}")

    print("=" * 70)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉\n")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
