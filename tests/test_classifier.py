"""
Test Classifier Functionality
"""

import os
import sys
import json
sys.path.insert(0, os.path.abspath('.'))

from services.classifier.extractor import RequirementExtractor
from services.classifier.structurer import VisaStructurer
from shared.database import DataStore
import yaml

def create_sample_data():
    """Create sample raw pages for testing"""
    print("Creating sample data...")

    # Sample visa pages
    sample_pages = [
        {
            "url": "http://example.com/skilled-worker-visa",
            "country": "TestCountry",
            "title": "Skilled Worker Visa (Subclass 189)",
            "content_text": """
                Skilled Worker Visa Requirements

                This visa is for skilled workers who want to live and work in TestCountry permanently.

                Eligibility Requirements:
                - Age: You must be under 45 years old at the time of invitation
                - Education: Bachelor's degree or higher qualification
                - Work Experience: Minimum 3 years of relevant work experience
                - Language: IELTS score of 6.5 or equivalent
                - Application Fee: $4,115 for main applicant
                - Processing Time: 6 to 8 months

                You must have an occupation on the relevant skilled occupation list.
            """,
            "breadcrumbs": ["Home", "Visas", "Work Visas"],
            "links": [],
            "attachments": [],
            "crawled_date": "2025-11-13T10:00:00Z",
            "depth": 0
        },
        {
            "url": "http://example.com/student-visa",
            "country": "TestCountry",
            "title": "Student Visa for International Students",
            "content_text": """
                Student Visa Information

                This visa allows you to study full-time at an educational institution in TestCountry.

                Requirements:
                - Age: Between 18 and 30 years old
                - Admission: Must have a confirmed offer from a registered institution
                - English proficiency: TOEFL score of 80 or IELTS 6.0
                - Fees: Application fee is $630
                - Processing: Usually processed within 4 to 6 weeks
                - Financial capacity: Must demonstrate sufficient funds
            """,
            "breadcrumbs": ["Home", "Visas", "Study Visas"],
            "links": [],
            "attachments": [],
            "crawled_date": "2025-11-13T10:00:00Z",
            "depth": 0
        },
        {
            "url": "http://example.com/family-visa",
            "country": "TestCountry",
            "title": "Partner Visa (Family Reunion)",
            "content_text": """
                Partner and Spouse Visa

                This visa is for partners and spouses of TestCountry citizens or permanent residents.

                Eligibility:
                - You must be in a genuine relationship with an eligible sponsor
                - No specific age requirement
                - Visa application charge: $7,850
                - Processing time: 12 to 24 months
                - Must meet health and character requirements
            """,
            "breadcrumbs": ["Home", "Visas", "Family Visas"],
            "links": [],
            "attachments": [],
            "crawled_date": "2025-11-13T10:00:00Z",
            "depth": 0
        },
        {
            "url": "http://example.com/business-investor-visa",
            "country": "TestCountry",
            "title": "Business Innovation and Investment Visa",
            "content_text": """
                Business and Investor Visa Program

                For business owners, investors, and entrepreneurs.

                Requirements:
                - Age: Usually under 55 (some exemptions apply)
                - Investment: Minimum investment of $1,500,000
                - Business experience: At least 5 years of successful business experience
                - Application fee: $5,375
                - Processing: 10 to 12 months typically
            """,
            "breadcrumbs": ["Home", "Visas", "Business Visas"],
            "links": [],
            "attachments": [],
            "crawled_date": "2025-11-13T10:00:00Z",
            "depth": 0
        }
    ]

    # Save sample data
    data_store = DataStore()
    for page in sample_pages:
        data_store.save_raw_page('TestCountry', page)

    print(f"✅ Created {len(sample_pages)} sample pages")
    return len(sample_pages)

def test_extractor():
    """Test the requirement extractor"""
    print("\nTesting Requirement Extractor...")
    print("=" * 60)

    # Load config
    with open('services/classifier/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    extractor = RequirementExtractor(config)

    # Test visa category identification
    work_text = "This is a skilled worker visa for employment in the country"
    study_text = "Student visa for university education and training"
    family_text = "Partner and spouse visa for family reunion"

    assert extractor.identify_visa_category(work_text) == "work"
    assert extractor.identify_visa_category(study_text) == "study"
    assert extractor.identify_visa_category(family_text) == "family"
    print("✅ Visa category identification works")

    # Test age extraction
    age_text1 = "You must be under 45 years old"
    age_text2 = "Age between 18 and 30 years old"
    age_text3 = "Applicants must be at least 21 years old"

    age1 = extractor.extract_age_requirement(age_text1)
    age2 = extractor.extract_age_requirement(age_text2)
    age3 = extractor.extract_age_requirement(age_text3)

    assert age1.get('max') == 45
    assert age2.get('min') == 18 and age2.get('max') == 30
    assert age3.get('min') == 21
    print("✅ Age extraction works")

    # Test education extraction
    edu_text1 = "Bachelor's degree or higher qualification required"
    edu_text2 = "Must have a Master's degree"
    edu_text3 = "High school or secondary education required"
    edu_text4 = "Diploma qualification needed"

    assert extractor.extract_education_requirement(edu_text1) == "bachelors"
    assert extractor.extract_education_requirement(edu_text2) == "masters"
    assert extractor.extract_education_requirement(edu_text3) == "secondary"
    assert extractor.extract_education_requirement(edu_text4) == "diploma"
    print("✅ Education extraction works")

    # Test experience extraction
    exp_text1 = "Minimum 3 years of relevant work experience"
    exp_text2 = "At least 5 years of successful business experience"

    assert extractor.extract_experience_requirement(exp_text1) == 3
    assert extractor.extract_experience_requirement(exp_text2) == 5
    print("✅ Experience extraction works")

    # Test fee extraction
    fee_text1 = "Application Fee: $4,115 for main applicant"
    fee_text2 = "Visa application charge: $7,850"

    fees1 = extractor.extract_fees(fee_text1)
    fees2 = extractor.extract_fees(fee_text2)

    assert '$4,115' in fees1.values() or '$4115' in fees1.values()
    assert '$7,850' in fees2.values() or '$7850' in fees2.values()
    print("✅ Fee extraction works")

    # Test processing time extraction
    time_text1 = "Processing Time: 6 to 8 months"
    time_text2 = "Usually processed within 4 to 6 weeks"

    time1 = extractor.extract_processing_time(time_text1)
    time2 = extractor.extract_processing_time(time_text2)

    assert time1 and '6' in time1 and '8' in time1
    assert time2 and '4' in time2 and '6' in time2
    print("✅ Processing time extraction works")

    # Test language extraction
    lang_text1 = "IELTS score of 6.5 or equivalent"
    lang_text2 = "TOEFL score of 80"

    lang1 = extractor.extract_language_requirement(lang_text1)
    lang2 = extractor.extract_language_requirement(lang_text2)

    assert lang1 and 'IELTS' in lang1
    assert lang2 and 'TOEFL' in lang2
    print("✅ Language extraction works")

def test_structurer():
    """Test the visa structurer"""
    print("\nTesting Visa Structurer...")
    print("=" * 60)

    structurer = VisaStructurer()

    # Test visa name normalization
    name1 = "Skilled Worker Visa (Subclass 189)"
    name2 = "Student Visa for International Students"

    normalized1 = structurer.normalize_visa_name(name1)
    normalized2 = structurer.normalize_visa_name(name2)

    assert 'skilled' in normalized1.lower()
    assert 'student' in normalized2.lower()
    print("✅ Visa name normalization works")

    # Test merging
    sample_data = [
        {
            'title': 'Skilled Worker Visa',
            'country': 'TestCountry',
            'category': 'work',
            'age': {'max': 45},
            'education': 'bachelors',
            'experience_years': 3,
            'fees': {'application_fee': '$4,115'},
            'processing_time': '6-8 months',
            'language': 'IELTS 6.5',
            'url': 'http://example.com/visa1'
        }
    ]

    merged = structurer.merge_requirements(sample_data)
    assert merged['visa_type'] == 'Skilled Worker Visa'
    assert merged['category'] == 'work'
    assert merged['requirements'].get('age') == {'max': 45}
    print("✅ Requirement merging works")

def test_full_pipeline():
    """Test the complete classification pipeline"""
    print("\nTesting Full Classification Pipeline...")
    print("=" * 60)

    # Load config
    with open('services/classifier/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Initialize components
    data_store = DataStore()
    extractor = RequirementExtractor(config)
    structurer = VisaStructurer()

    # Load sample data
    raw_pages = data_store.load_raw_pages('TestCountry')
    print(f"Loaded {len(raw_pages)} sample pages")

    # Extract requirements
    extracted_data = []
    for page in raw_pages:
        requirements = extractor.extract_all_requirements(page)
        extracted_data.append(requirements)

    print(f"Extracted requirements from {len(extracted_data)} pages")

    # Check extractions
    work_visa = next((d for d in extracted_data if d['category'] == 'work'), None)
    student_visa = next((d for d in extracted_data if d['category'] == 'study'), None)

    assert work_visa is not None, "Should find work visa"
    assert student_visa is not None, "Should find student visa"
    assert work_visa['age'] is not None, "Work visa should have age requirement"
    assert work_visa['experience_years'] == 3, "Work visa should require 3 years experience"
    print("✅ Requirements extracted correctly")

    # Structure visas
    structured_visas = structurer.structure_all_visas(extracted_data)
    print(f"Structured {len(structured_visas)} visa profiles")

    assert len(structured_visas) > 0, "Should create structured visas"
    print("✅ Visa structuring works")

    # Save and verify
    data_store.save_structured_visas(structured_visas)
    loaded_visas = data_store.load_structured_visas()

    assert len(loaded_visas) == len(structured_visas), "Should save and load correctly"
    print("✅ Data persistence works")

    return structured_visas

def display_results(structured_visas):
    """Display the structured visa results"""
    print("\n" + "=" * 60)
    print("STRUCTURED VISA PROFILES")
    print("=" * 60)

    for i, visa in enumerate(structured_visas, 1):
        print(f"\n{i}. {visa['visa_type']}")
        print(f"   Country: {visa['country']}")
        print(f"   Category: {visa['category']}")

        if visa['requirements']:
            print(f"   Requirements:")
            for key, value in visa['requirements'].items():
                print(f"      - {key}: {value}")

        if visa.get('language'):
            print(f"   Language: {visa['language']}")

        if visa['fees']:
            print(f"   Fees: {visa['fees']}")

        if visa['processing_time']:
            print(f"   Processing Time: {visa['processing_time']}")

        print(f"   Sources: {len(visa['source_urls'])} page(s)")

def cleanup_test_data():
    """Clean up test data"""
    import shutil
    test_dir = 'data/raw/TestCountry'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    print("\n✅ Test data cleaned up")

if __name__ == '__main__':
    print("Testing Classifier Service")
    print("=" * 60)

    try:
        # Create sample data
        create_sample_data()

        # Run tests
        test_extractor()
        test_structurer()
        structured_visas = test_full_pipeline()

        # Display results
        display_results(structured_visas)

        print("\n" + "=" * 60)
        print("🎉 All classifier tests passed!")
        print("=" * 60)

    finally:
        # Clean up
        cleanup_test_data()
