"""
Test Assistant Functionality
"""

import os
import sys
import json
sys.path.insert(0, os.path.abspath('.'))

from services.assistant.retriever import ContextRetriever
from services.assistant.prompts import (
    SYSTEM_PROMPT,
    GENERAL_QUERY_PROMPT_TEMPLATE,
    ELIGIBILITY_PROMPT_TEMPLATE
)
from shared.database import DataStore
import yaml

def test_retriever():
    """Test the context retriever"""
    print("\nTesting Context Retriever...")
    print("=" * 60)

    # Load config
    with open('services/assistant/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    retriever = ContextRetriever(config)

    # Ensure we have test data
    data_store = DataStore()
    test_visas = data_store.load_structured_visas()

    if not test_visas:
        print("Creating test visa data...")
        test_visas = [
            {
                'visa_type': 'Skilled Worker Visa',
                'country': 'TestCountry',
                'category': 'work',
                'requirements': {
                    'age': {'min': None, 'max': 45},
                    'education': 'bachelors',
                    'experience_years': 3
                },
                'fees': {'application_fee': '$4115'},
                'processing_time': '6-8 months',
                'language': 'IELTS 6.5',
                'source_urls': ['http://example.com/visa1']
            },
            {
                'visa_type': 'Student Visa for International Students',
                'country': 'TestCountry',
                'category': 'study',
                'requirements': {
                    'age': {'min': 18, 'max': 30}
                },
                'fees': {'application_fee': '$630'},
                'processing_time': '4-6 weeks',
                'language': 'IELTS 6.0',
                'source_urls': ['http://example.com/visa2']
            },
            {
                'visa_type': 'Business Innovation Visa',
                'country': 'AnotherCountry',
                'category': 'investment',
                'requirements': {
                    'age': {'min': None, 'max': 55},
                    'experience_years': 5
                },
                'fees': {'application_fee': '$5375'},
                'processing_time': '10-12 months',
                'source_urls': ['http://example.com/visa3']
            }
        ]
        data_store.save_structured_visas(test_visas)

    # Test country-based retrieval
    query1 = "What visas are available in TestCountry?"
    relevant1 = retriever.retrieve_relevant_visas(query1)
    assert len(relevant1) > 0, "Should find visas for TestCountry"
    assert all(v['country'] == 'TestCountry' for v in relevant1), "Should only return TestCountry visas"
    print("✅ Country-based retrieval works")

    # Test category-based retrieval
    query2 = "Tell me about work visas"
    relevant2 = retriever.retrieve_relevant_visas(query2)
    assert len(relevant2) > 0, "Should find work visas"
    print("✅ Category-based retrieval works")

    # Test keyword retrieval
    query3 = "Student visa requirements"
    relevant3 = retriever.retrieve_relevant_visas(query3)
    assert len(relevant3) > 0, "Should find student visas"
    assert any('student' in v['visa_type'].lower() for v in relevant3), "Should include student visas"
    print("✅ Keyword-based retrieval works")

    # Test profile-based filtering
    user_profile = {
        'age': 32,
        'education': 'bachelors',
        'experience_years': 5
    }
    query4 = "What visas am I eligible for?"
    relevant4 = retriever.retrieve_relevant_visas(query4, user_profile)
    assert len(relevant4) > 0, "Should find visas with profile"
    print("✅ Profile-based filtering works")

    # Test context formatting
    context = retriever.format_context_for_llm(relevant1[:2])
    assert 'Visa 1:' in context, "Should format visa information"
    assert 'Country:' in context, "Should include country"
    assert 'Requirements:' in context, "Should include requirements"
    print("✅ Context formatting works")

def test_prompt_templates():
    """Test prompt template formatting"""
    print("\nTesting Prompt Templates...")
    print("=" * 60)

    # Test general query template
    context = "Test visa context"
    query = "Test query"
    general_prompt = GENERAL_QUERY_PROMPT_TEMPLATE.format(
        context=context,
        query=query
    )
    assert context in general_prompt, "Should include context"
    assert query in general_prompt, "Should include query"
    print("✅ General query template works")

    # Test eligibility template
    user_profile = {'age': 30, 'education': 'bachelors'}
    eligibility_prompt = ELIGIBILITY_PROMPT_TEMPLATE.format(
        user_profile=json.dumps(user_profile),
        context=context,
        query=query
    )
    assert 'age' in eligibility_prompt, "Should include profile"
    assert context in eligibility_prompt, "Should include context"
    print("✅ Eligibility template works")

    # Test system prompt
    assert len(SYSTEM_PROMPT) > 0, "System prompt should not be empty"
    assert 'immigration' in SYSTEM_PROMPT.lower(), "Should mention immigration"
    print("✅ System prompt is defined")

def test_assistant_without_api():
    """Test assistant components that don't require API key"""
    print("\nTesting Assistant Components (No API Required)...")
    print("=" * 60)

    # Load config
    with open('services/assistant/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Test config
    assert 'llm' in config, "Config should have llm section"
    assert 'context' in config, "Config should have context section"
    assert config['llm']['model'], "Should specify model"
    print("✅ Configuration is valid")

    # Test retriever initialization
    retriever = ContextRetriever(config)
    assert retriever.config == config, "Should store config"
    print("✅ Retriever initializes correctly")

    # Test retrieval functionality
    data_store = DataStore()
    visas = data_store.load_structured_visas()
    if visas:
        relevant = retriever.retrieve_relevant_visas("test query")
        assert isinstance(relevant, list), "Should return a list"
        print("✅ Retrieval returns proper format")
    else:
        print("⚠️  No visa data available for retrieval test")

def test_llm_client_initialization():
    """Test LLM client initialization (without making API calls)"""
    print("\nTesting LLM Client Initialization...")
    print("=" * 60)

    # Load config
    with open('services/assistant/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Test without API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set - testing error handling")
        try:
            from services.assistant.llm_client import LLMClient
            client = LLMClient(config)
            print("❌ Should have raised ValueError for missing API key")
        except ValueError as e:
            assert 'API key not found' in str(e), "Should show helpful error message"
            print("✅ Properly handles missing API key")
    else:
        print("ℹ️  OPENAI_API_KEY is set - skipping error test")
        try:
            from services.assistant.llm_client import LLMClient
            client = LLMClient(config)
            print("✅ LLM client initializes with API key")
        except Exception as e:
            print(f"⚠️  LLM client initialization issue: {e}")

def display_usage_instructions():
    """Display usage instructions for the assistant"""
    print("\n" + "=" * 60)
    print("ASSISTANT SERVICE - USAGE INSTRUCTIONS")
    print("=" * 60)

    print("\n📋 To use the AI Assistant, you need:")
    print("1. OpenAI API key (get from: https://platform.openai.com/api-keys)")
    print("2. Structured visa data (run: python main.py classify --all)")
    print("3. Set environment variable: export OPENAI_API_KEY='your-key'")

    print("\n💬 Single Query Mode:")
    print("  python main.py assist --query 'What visas are available in Canada?'")

    print("\n🤖 Chat Mode (Interactive):")
    print("  python main.py assist --chat")

    print("\n👤 With User Profile:")
    print("  python main.py assist --query 'Am I eligible?' --profile user.json")

    print("\n📝 Note:")
    print("  - The assistant uses gpt-4o-mini (cost-effective)")
    print("  - It retrieves relevant visa data automatically")
    print("  - Answers are based on your structured visa database")
    print("  - Citations include source URLs when available")

if __name__ == '__main__':
    print("Testing Assistant Service")
    print("=" * 60)

    try:
        test_retriever()
        test_prompt_templates()
        test_assistant_without_api()
        test_llm_client_initialization()

        print("\n" + "=" * 60)
        print("🎉 All assistant tests passed!")
        print("=" * 60)

        display_usage_instructions()

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
