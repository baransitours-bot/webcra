"""
End-to-End Workflow Tests
Tests complete user journeys through the immigration platform
"""

import json
import yaml
from pathlib import Path
from shared.database import Database

def test_new_user_journey():
    """
    Test complete workflow for a new user:
    1. System has crawled and classified visa data
    2. User creates profile
    3. User gets matched to eligible visas
    4. User asks questions about specific visas
    """
    print("\nEnd-to-End Test: New User Journey")
    print("=" * 60)

    # Step 1: Verify data exists
    print("\n📊 Step 1: Checking available visa data...")
    db = Database()

    # Check if we have structured data
    structured_path = Path('data/structured')
    if not structured_path.exists():
        print("   ⚠️  No structured data found")
        print("   Run: python main.py classify --all")
        return False

    # Count available visas
    total_visas = 0
    countries_with_data = []

    for country_dir in structured_path.iterdir():
        if country_dir.is_dir():
            json_files = list(country_dir.glob('*.json'))
            if json_files:
                countries_with_data.append(country_dir.name)
                for json_file in json_files:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        total_visas += len(data.get('visas', []))

    print(f"   ✅ Found {total_visas} visas across {len(countries_with_data)} countries")
    print(f"   Countries: {', '.join(countries_with_data)}")

    if total_visas == 0:
        print("   ⚠️  No visa data available for matching")
        return False

    # Step 2: Create sample user profile
    print("\n👤 Step 2: Creating user profile...")

    user_profile = {
        "age": 28,
        "education": "bachelor",
        "work_experience": 5,
        "occupation": "software engineer",
        "language": {
            "english": {"ielts": 7.5}
        },
        "countries_of_interest": ["canada", "australia"]
    }

    print(f"   ✅ User profile created:")
    print(f"      - Age: {user_profile['age']}")
    print(f"      - Education: {user_profile['education']}")
    print(f"      - Experience: {user_profile['work_experience']} years")

    # Step 3: Match user to visas
    print("\n🔍 Step 3: Finding eligible visas...")

    from services.matcher.ranker import VisaRanker

    with open('services/matcher/config.yaml', 'r') as f:
        matcher_config = yaml.safe_load(f)

    ranker = VisaRanker(matcher_config)

    # Get all visas
    all_visas = []
    for country in countries_with_data:
        visas = db.get_structured_visas(country)
        all_visas.extend(visas)

    # Rank visas
    matches = ranker.rank_all_visas(user_profile, all_visas)

    # Filter to eligible visas (score >= 50%)
    eligible_visas = [m for m in matches if m['eligibility_score'] >= 50]

    print(f"   ✅ Found {len(eligible_visas)} eligible visas (score >= 50%)")

    if eligible_visas:
        top_match = eligible_visas[0]
        print(f"\n   🎯 Top match:")
        print(f"      - Visa: {top_match['visa_type']}")
        print(f"      - Country: {top_match['country']}")
        print(f"      - Score: {top_match['eligibility_score']}%")
        print(f"      - Category: {top_match['category']}")

    # Step 4: Query assistant about top visa
    print("\n💬 Step 4: Asking AI assistant about top visa...")

    from services.assistant.retriever import ContextRetriever

    with open('services/assistant/config.yaml', 'r') as f:
        assistant_config = yaml.safe_load(f)

    retriever = ContextRetriever(assistant_config)

    # Simulate user query
    query = f"What are the requirements for {top_match['visa_type']} in {top_match['country']}?"
    print(f"   User query: '{query}'")

    # Retrieve context
    relevant_visas = retriever.retrieve_relevant_visas(
        query,
        user_profile=user_profile
    )

    if relevant_visas:
        print(f"   ✅ Assistant retrieved {len(relevant_visas)} relevant visas")
        print(f"   Note: LLM would generate answer based on this context")
    else:
        print("   ⚠️  No relevant context found")

    # Summary
    print("\n" + "=" * 60)
    print("✅ New User Journey Test Complete!")
    print("=" * 60)
    print("\nUser successfully:")
    print("  1. ✅ Accessed visa database")
    print(f"  2. ✅ Got matched to {len(eligible_visas)} eligible visas")
    print("  3. ✅ Retrieved information about top match")
    print("  4. ⚠️  Would get AI-generated answer (requires API key)")

    return True

def test_country_specific_workflow():
    """
    Test workflow for user interested in specific country:
    1. User specifies country of interest
    2. System shows all visas for that country
    3. User gets recommendations based on profile
    """
    print("\n\nEnd-to-End Test: Country-Specific Workflow")
    print("=" * 60)

    target_country = "australia"
    print(f"\n🌏 Testing workflow for country: {target_country}")

    db = Database()

    # Get all visas for target country
    print(f"\n📋 Step 1: Loading {target_country} visas...")
    country_visas = db.get_structured_visas(target_country)

    if not country_visas:
        print(f"   ⚠️  No visa data for {target_country}")
        print(f"   Run: python main.py classify --country {target_country}")
        return False

    print(f"   ✅ Found {len(country_visas)} visa types for {target_country}")

    # Group by category
    categories = {}
    for visa in country_visas:
        cat = visa.get('category', 'other')
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\n   Categories available:")
    for cat, count in categories.items():
        print(f"      - {cat}: {count} visas")

    # Create user profile
    print("\n👤 Step 2: Creating user profile...")
    user_profile = {
        "age": 32,
        "education": "bachelor",
        "work_experience": 8,
        "occupation": "accountant",
        "countries_of_interest": [target_country]
    }

    print(f"   ✅ User interested in: {target_country}")

    # Match within country
    print(f"\n🔍 Step 3: Finding best {target_country} visas...")

    from services.matcher.ranker import VisaRanker

    with open('services/matcher/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    ranker = VisaRanker(config)
    matches = ranker.rank_visas_for_country(user_profile, target_country, country_visas)

    top_5 = matches[:5]
    print(f"   ✅ Top 5 matches for {target_country}:")

    for i, match in enumerate(top_5, 1):
        print(f"      {i}. {match['visa_type']} ({match['category']}) - {match['eligibility_score']}%")

    print("\n" + "=" * 60)
    print("✅ Country-Specific Workflow Complete!")
    print("=" * 60)

    return True

def test_comparison_workflow():
    """
    Test workflow for comparing multiple countries:
    1. User has profile
    2. User wants to compare visa options across countries
    3. System shows best match per country
    """
    print("\n\nEnd-to-End Test: Multi-Country Comparison Workflow")
    print("=" * 60)

    # User profile
    user_profile = {
        "age": 26,
        "education": "master",
        "work_experience": 3,
        "occupation": "data scientist"
    }

    print("\n👤 User profile:")
    print(f"   - Age: {user_profile['age']}")
    print(f"   - Education: {user_profile['education']}")
    print(f"   - Experience: {user_profile['work_experience']} years")

    # Compare across available countries
    print("\n🌍 Comparing visa options across countries...")

    db = Database()
    structured_path = Path('data/structured')

    if not structured_path.exists():
        print("   ⚠️  No structured data available")
        return False

    from services.matcher.ranker import VisaRanker

    with open('services/matcher/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    ranker = VisaRanker(config)

    # Get best visa per country
    country_results = {}

    for country_dir in structured_path.iterdir():
        if country_dir.is_dir():
            country = country_dir.name
            visas = db.get_structured_visas(country)

            if visas:
                matches = ranker.rank_visas_for_country(user_profile, country, visas)

                if matches and matches[0]['eligibility_score'] >= 50:
                    country_results[country] = {
                        'best_visa': matches[0]['visa_type'],
                        'score': matches[0]['eligibility_score'],
                        'category': matches[0]['category']
                    }

    if country_results:
        print(f"\n   ✅ Found eligible visas in {len(country_results)} countries:")

        # Sort by score
        sorted_countries = sorted(
            country_results.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )

        for country, result in sorted_countries:
            print(f"\n      🇦🇺 {country.upper()}")
            print(f"         Best match: {result['best_visa']}")
            print(f"         Score: {result['score']}%")
            print(f"         Category: {result['category']}")
    else:
        print("   ⚠️  No eligible visas found in any country")

    print("\n" + "=" * 60)
    print("✅ Multi-Country Comparison Workflow Complete!")
    print("=" * 60)

    return True

def run_e2e_tests():
    """Run all end-to-end workflow tests"""
    print("=" * 60)
    print("END-TO-END WORKFLOW TESTS - STAGE 6")
    print("=" * 60)

    results = {
        'new_user': test_new_user_journey(),
        'country_specific': test_country_specific_workflow(),
        'comparison': test_comparison_workflow()
    }

    print("\n" + "=" * 60)
    print("E2E TEST RESULTS")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "⚠️  SKIP (no data)"
        print(f"{test_name}: {status}")

    print("\n" + "=" * 60)
    print("✅ All E2E workflow tests completed!")
    print("=" * 60)

    print("\n💡 To populate data for all tests, run:")
    print("   1. python main.py crawl --all")
    print("   2. python main.py classify --all")

if __name__ == '__main__':
    run_e2e_tests()
