"""
Test logger Unicode/emoji support (especially for Windows)
"""

import sys
sys.path.insert(0, '.')

from shared.logger import setup_logger

def test_logger_unicode():
    """Test that logger can handle Unicode characters and emojis"""
    print("Testing logger Unicode support...")
    print("=" * 60)

    logger = setup_logger('test_unicode')

    # Test various emojis and Unicode characters
    logger.info("✅ Checkmark emoji test")
    logger.info("❌ Cross mark emoji test")
    logger.info("🕷️ Spider emoji test")
    logger.info("🔄 Refresh emoji test")
    logger.info("🎯 Target emoji test")
    logger.info("🤖 Robot emoji test")
    logger.info("Starting crawl for Australia")
    logger.error("Error message test")

    print("\n" + "=" * 60)
    print("✅ Logger Unicode test complete!")
    print("If you see all the emojis above without errors, the fix works!")

if __name__ == '__main__':
    test_logger_unicode()
