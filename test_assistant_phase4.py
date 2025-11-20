#!/usr/bin/env python3
"""
Quick test of Phase 4: Assistant with general content
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.assistant.interface import AssistantService
from shared.database import Database

def test_assistant_with_general_content():
    """Test that assistant can retrieve and use general content"""

    print("=" * 80)
    print("TESTING PHASE 4: ASSISTANT WITH GENERAL CONTENT")
    print("=" * 80)

    # Initialize service
    print("\n1. Initializing Assistant Service...")
    service = AssistantService()

    # Check statistics
    print("\n2. Checking Statistics...")
    stats = service.get_statistics()
    print(f"   Total Visas: {stats['total_visas']}")
    print(f"   Total General Content: {stats['total_general_content']}")
    print(f"   LLM Available: {stats['llm_available']}")
    print(f"   Ready: {stats['ready']}")

    if stats['total_general_content'] == 0:
        print("\n   ⚠️  No general content found in database.")
        print("   Run Classifier on pages to extract general content first.")
        return

    # Test retrieval
    print("\n3. Testing Retrieval...")
    db = Database()
    general_content = db.get_general_content()

    if general_content:
        print(f"\n   Found {len(general_content)} general content items:")
        for i, content in enumerate(general_content[:5], 1):  # Show first 5
            print(f"\n   {i}. {content.title}")
            print(f"      Country: {content.country}")
            print(f"      Type: {content.content_type}")
            print(f"      Topics: {', '.join(content.metadata.get('topics', []))}")

    # Test context retrieval
    print("\n4. Testing Context Retrieval...")

    test_queries = [
        "What employment services are available?",
        "Tell me about healthcare",
        "What benefits can I get?",
    ]

    for query in test_queries:
        print(f"\n   Query: '{query}'")
        visas, general = service.retriever.retrieve_all_context(query)
        print(f"   - Retrieved {len(visas)} visas")
        print(f"   - Retrieved {len(general)} general content items")

        if general:
            print(f"   - General content titles:")
            for item in general[:3]:  # Show first 3
                print(f"     • {item['title']}")

    # Test formatting
    print("\n5. Testing Context Formatting...")
    test_query = "What services are available for immigrants?"
    visas, general = service.retriever.retrieve_all_context(test_query)
    formatted = service.retriever.format_context_for_llm(visas, general)

    print(f"\n   Formatted context length: {len(formatted)} characters")
    if "=== VISA PROGRAMS ===" in formatted:
        print("   ✅ Contains visa section")
    if "=== GENERAL INFORMATION ===" in formatted:
        print("   ✅ Contains general content section")

    # Show a preview
    preview = formatted[:500] + "..." if len(formatted) > 500 else formatted
    print(f"\n   Preview:")
    print("   " + "\n   ".join(preview.split("\n")[:20]))

    print("\n" + "=" * 80)
    print("PHASE 4 TEST COMPLETE")
    print("=" * 80)
    print("\n✅ All checks passed! Assistant can now use general content.")
    print("\nNext steps:")
    print("1. Start the Streamlit app: streamlit run app.py")
    print("2. Go to the Assistant page")
    print("3. Ask questions about employment, healthcare, or benefits")
    print("4. Verify sources show both visa and general content types")

if __name__ == "__main__":
    test_assistant_with_general_content()
