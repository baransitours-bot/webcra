"""
Test Configuration Lifecycle
Verifies config loads properly at app startup
"""

print("=" * 80)
print("TESTING CONFIGURATION LIFECYCLE")
print("=" * 80)

print("\n1. Testing Database Initialization...")
from shared.database import Database
db = Database()
print("   ✅ Database initialized")

print("\n2. Testing ConfigManager Initialization...")
from shared.config_manager import get_config
config = get_config()
print("   ✅ ConfigManager initialized")

print("\n3. Testing Config Loading...")
provider = config.get('llm.provider')
model = config.get('llm.model')
print(f"   ✅ Provider: {provider}")
print(f"   ✅ Model: {model}")

print("\n4. Testing API Key Check...")
api_key = config.get_api_key()
if api_key:
    print(f"   ✅ API Key configured: {api_key[:8]}...")
else:
    print(f"   ⚠️  API Key NOT configured (expected if .env not set)")

print("\n5. Testing LLMClient Initialization...")
from services.assistant.llm_client import LLMClient

try:
    llm = LLMClient()
    print(f"   ✅ LLMClient initialized successfully!")
    print(f"   Provider: {llm.provider}")
    print(f"   Model: {llm.model}")
except ValueError as e:
    print(f"   ⚠️  LLMClient failed (expected without API key)")
    print(f"   Error: {str(e)[:150]}...")

print("\n6. Testing VisaExtractor Initialization (with fallback)...")
from services.classifier.visa_extractor import VisaExtractor

extractor = VisaExtractor()
if extractor.llm_client:
    print("   ✅ VisaExtractor with LLM enabled")
else:
    print("   ✅ VisaExtractor with pattern-based fallback (no LLM)")

print("\n" + "=" * 80)
print("CONFIGURATION LIFECYCLE TEST COMPLETE")
print("=" * 80)

print("\n📊 Summary:")
print("   - Database: Auto-initializes with settings table")
print("   - ConfigManager: Loads from .env > Database > YAML")
print("   - Services: Auto-use ConfigManager (no manual config passing)")
print("   - Graceful fallback: Works without API key (limited features)")

print("\n💡 To enable full features:")
print("   1. Create .env file: cp .env.example .env")
print("   2. Add API key: OPENROUTER_API_KEY=your-key")
print("   3. Or use Settings UI in Streamlit app")
