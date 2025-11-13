"""
Test Matcher Functionality
"""

import os
import sys
import json
sys.path.insert(0, os.path.abspath('.'))

from services.matcher.scorer import EligibilityScorer
from services.matcher.ranker import VisaRanker
from shared.database import DataStore
import yaml

def test_scorer():
    """Test the eligibility scorer"""
    print("\nTesting Eligibility Scorer...")
    print("=" * 60)

    # Load config
    with open('services/matcher/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    scorer = EligibilityScorer(config)

    # Test age scoring
    assert scorer.score_age(30, {'min': 18, 'max': 45}) == 1.0, "Age within range should score 1.0"
    assert scorer.score_age(50, {'min': 18, 'max': 45}) == 0.0, "Age above max should score 0.0"
    assert scorer.score_age(15, {'min': 18, 'max': 45}) == 0.0, "Age below min should score 0.0"
    assert scorer.score_age(30, {}) == 1.0, "No age requirement should score 1.0"
    print("✅ Age scoring works")

    # Test education scoring
    assert scorer.score_education('masters', 'bachelors') == 1.0, "Higher education should match"
    assert scorer.score_education('bachelors', 'masters') < 1.0, "Lower education should score less"
    assert scorer.score_education('bachelors', None) == 1.0, "No requirement should score 1.0"
    print("✅ Education scoring works")

    # Test experience scoring
    assert scorer.score_experience(5, 3) == 1.0, "More experience should match"
    assert scorer.score_experience(2, 3) < 1.0, "Less experience should score less"
    assert scorer.score_experience(2, 3) == 2/3, "Partial experience should be proportional"
    assert scorer.score_experience(5, 0) == 1.0, "No requirement should score 1.0"
    print("✅ Experience scoring works")

    # Test total score calculation
    user_profile = {
        'age': 30,
        'education': 'bachelors',
        'experience_years': 5
    }

    visa_requirements = {
        'age': {'min': 18, 'max': 45},
        'education': 'bachelors',
        'experience_years': 3
    }

    score = scorer.calculate_total_score(user_profile, visa_requirements)
    assert score == 100.0, "Perfect match should score 100%"
    print("✅ Total score calculation works")

    # Test gap identification
    user_profile_gaps = {
        'age': 50,
        'education': 'diploma',
        'experience_years': 2
    }

    gaps = scorer.identify_gaps(user_profile_gaps, visa_requirements)
    assert len(gaps) > 0, "Should identify gaps"
    assert any('age' in gap.lower() for gap in gaps), "Should identify age gap"
    assert any('education' in gap.lower() or 'degree' in gap.lower() for gap in gaps), "Should identify education gap"
    assert any('experience' in gap.lower() for gap in gaps), "Should identify experience gap"
    print("✅ Gap identification works")

def test_ranker():
    """Test the visa ranker"""
    print("\nTesting Visa Ranker...")
    print("=" * 60)

    # Load config
    with open('services/matcher/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    ranker = VisaRanker(config)

    # Create sample user profile
    user_profile = {
        'age': 32,
        'nationality': 'Test',
        'education': 'masters',
        'profession': 'Software Engineer',
        'experience_years': 5,
        'target_countries': ['TestCountry']
    }

    # Create sample visas
    sample_visas = [
        {
            'visa_type': 'Skilled Worker Visa',
            'country': 'TestCountry',
            'category': 'work',
            'requirements': {
                'age': {'min': None, 'max': 45},
                'education': 'bachelors',
                'experience_years': 3
            },
            'fees': {'application_fee': '$4,115'},
            'processing_time': '6-8 months',
            'language': 'IELTS 6.5',
            'source_urls': ['http://example.com/visa1']
        },
        {
            'visa_type': 'Student Visa',
            'country': 'TestCountry',
            'category': 'study',
            'requirements': {
                'age': {'min': 18, 'max': 30},
            },
            'fees': {'application_fee': '$630'},
            'processing_time': '4-6 weeks',
            'language': 'IELTS 6.0',
            'source_urls': ['http://example.com/visa2']
        },
        {
            'visa_type': 'Business Visa',
            'country': 'TestCountry',
            'category': 'investment',
            'requirements': {
                'age': {'min': None, 'max': 55},
                'experience_years': 5
            },
            'fees': {'application_fee': '$5,375'},
            'processing_time': '10-12 months',
            'source_urls': ['http://example.com/visa3']
        }
    ]

    # Test single visa matching
    match = ranker.match_user_to_visa(user_profile, sample_visas[0])
    assert match['visa_type'] == 'Skilled Worker Visa'
    assert match['eligibility_score'] > 0
    assert 'gaps' in match
    assert 'eligible' in match
    print("✅ Single visa matching works")

    # Test ranking all visas
    matches = ranker.rank_all_visas(user_profile, sample_visas)
    assert len(matches) == 3, "Should match all visas"
    assert matches[0]['eligibility_score'] >= matches[1]['eligibility_score'], "Should be sorted by score"
    print("✅ Visa ranking works")

    # Test country filtering
    user_profile_filtered = {
        **user_profile,
        'target_countries': ['OtherCountry']
    }
    matches_filtered = ranker.rank_all_visas(user_profile_filtered, sample_visas)
    assert len(matches_filtered) == 0, "Should filter by target countries"
    print("✅ Country filtering works")

def test_full_pipeline():
    """Test the complete matching pipeline with real data"""
    print("\nTesting Full Matching Pipeline...")
    print("=" * 60)

    # First, ensure we have test data from classifier
    data_store = DataStore()

    # Load or create test visa data
    test_visas = data_store.load_structured_visas()

    if not test_visas:
        print("Creating test visa data...")
        # Create sample structured visa data
        test_visas = [
            {
                'visa_type': 'Skilled Worker Visa (Subclass 189)',
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
                'visa_type': 'Student Visa',
                'country': 'TestCountry',
                'category': 'study',
                'requirements': {
                    'age': {'min': 18, 'max': 30}
                },
                'fees': {},
                'processing_time': '4-6 weeks',
                'language': 'IELTS 6.0',
                'source_urls': ['http://example.com/visa2']
            }
        ]
        data_store.save_structured_visas(test_visas)

    print(f"Loaded {len(test_visas)} test visas")

    # Create test user profiles
    test_profiles = [
        {
            'name': 'Perfect Match - Skilled Worker',
            'profile': {
                'age': 32,
                'nationality': 'Test',
                'education': 'masters',
                'profession': 'Software Engineer',
                'experience_years': 5,
                'target_countries': ['TestCountry']
            },
            'expected_top_category': 'work'
        },
        {
            'name': 'Young Student',
            'profile': {
                'age': 22,
                'nationality': 'Test',
                'education': 'bachelors',
                'profession': 'Student',
                'experience_years': 0,
                'target_countries': ['TestCountry']
            },
            'expected_contains': 'Student'  # Look for student visa in results
        }
    ]

    # Load config
    with open('services/matcher/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    ranker = VisaRanker(config)

    # Test each profile
    for test_case in test_profiles:
        print(f"\nTesting: {test_case['name']}")
        matches = ranker.rank_all_visas(test_case['profile'], test_visas)

        assert len(matches) > 0, f"Should find matches for {test_case['name']}"

        top_match = matches[0]
        print(f"  Top Match: {top_match['visa_type']}")
        print(f"  Score: {top_match['eligibility_score']}%")
        print(f"  Category: {top_match['category']}")

        if test_case.get('expected_top_category'):
            assert top_match['category'] == test_case['expected_top_category'], \
                f"Expected {test_case['expected_top_category']}, got {top_match['category']}"

        if test_case.get('expected_contains'):
            assert test_case['expected_contains'] in top_match['visa_type'] or \
                   any(test_case['expected_contains'] in m['visa_type'] for m in matches[:3]), \
                f"Expected to find '{test_case['expected_contains']}' in top 3 matches"

        print(f"  ✅ {test_case['name']} matched correctly")

    print("\n✅ Full pipeline works correctly")

if __name__ == '__main__':
    print("Testing Matcher Service")
    print("=" * 60)

    try:
        test_scorer()
        test_ranker()
        test_full_pipeline()

        print("\n" + "=" * 60)
        print("🎉 All matcher tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
