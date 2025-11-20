#!/usr/bin/env python3
"""
Add sample immigration data for testing
This simulates what the Crawler and Classifier would extract
"""

from shared.database import Database
from shared.models import Visa, GeneralContent
from datetime import datetime

db = Database()

print("Adding sample visa data...")

# Sample visas (using correct save_visa signature)
sample_visas = [
    {
        'visa_type': 'Skilled Worker Visa',
        'country': 'Canada',
        'category': 'Work',
        'requirements': {
            'age': '18-45 years',
            'education': 'Bachelor degree or higher',
            'experience_years': '2+ years',
            'language': 'IELTS 6.0 or equivalent',
            'skills': 'NOC skill level 0, A or B'
        },
        'fees': {
            'application_fee': 850,
            'processing_fee': 500,
            'currency': 'CAD'
        },
        'processing_time': '6-12 months',
        'documents_required': ['Passport', 'Educational credentials', 'Language test results', 'Work experience letters'],
        'source_urls': ['https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html']
    },
    {
        'visa_type': 'Skilled Independent Visa (Subclass 189)',
        'country': 'Australia',
        'category': 'Permanent Residence',
        'requirements': {
            'age': 'Under 45 years',
            'education': 'Recognized qualifications',
            'experience_years': '3+ years in nominated occupation',
            'language': 'IELTS 6.0 minimum (higher scores preferred)',
            'skills': 'Occupation on skilled occupation list'
        },
        'fees': {
            'application_fee': 4240,
            'currency': 'AUD'
        },
        'processing_time': '8-12 months',
        'documents_required': ['Passport', 'Skills assessment', 'English language test', 'Police certificates'],
        'source_urls': ['https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/skilled-independent-189']
    },
    {
        'visa_type': 'Graduate Visa',
        'country': 'UK',
        'category': 'Post-Study Work',
        'requirements': {
            'education': 'Completed UK degree',
            'other': 'Must apply within visa expiry'
        },
        'fees': {
            'application_fee': 715,
            'currency': 'GBP'
        },
        'processing_time': '8 weeks',
        'documents_required': ['Passport', 'Proof of degree completion', 'TB test results'],
        'source_urls': ['https://www.gov.uk/graduate-visa']
    }
]

# Add visas to database
for visa_data in sample_visas:
    db.save_visa(**visa_data)
    print(f"✓ Added: {visa_data['visa_type']} ({visa_data['country']})")

print(f"\n{len(sample_visas)} visas added!\n")

# Sample general content
print("Adding sample general content...")

sample_general = [
    {
        'title': 'Employment Services for New Immigrants',
        'country': 'Canada',
        'content_type': 'employment',
        'summary': 'Free employment services including job search assistance, resume writing workshops, and interview preparation for newcomers to Canada.',
        'key_points': [
            'Free job search assistance',
            'Resume and cover letter workshops',
            'Interview preparation',
            'Employer connections',
            'Skills assessment and recognition'
        ],
        'application_links': [
            {'label': 'Find Employment Services', 'url': 'https://www.canada.ca/en/employment-social-development/services/foreign-workers.html'}
        ],
        'source_url': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/new-immigrants/prepare-life-canada/prepare-work.html',
        'metadata': {
            'topics': ['employment', 'job search', 'career'],
            'audience': 'newcomers, immigrants',
            'last_updated': datetime.now().isoformat()
        }
    },
    {
        'title': 'Healthcare Coverage for Immigrants',
        'country': 'Australia',
        'content_type': 'healthcare',
        'summary': 'Information about Medicare eligibility, health insurance requirements, and accessing healthcare services in Australia.',
        'key_points': [
            'Medicare eligibility for permanent residents',
            'Overseas Visitor Health Cover (OVHC) for temporary visa holders',
            'How to enroll in Medicare',
            'Finding doctors and hospitals',
            'Emergency services'
        ],
        'application_links': [
            {'label': 'Medicare Enrollment', 'url': 'https://www.servicesaustralia.gov.au/medicare'}
        ],
        'source_url': 'https://immi.homeaffairs.gov.au/help-support/meeting-our-requirements/health',
        'metadata': {
            'topics': ['healthcare', 'medicare', 'health insurance'],
            'audience': 'all immigrants',
            'last_updated': datetime.now().isoformat()
        }
    },
    {
        'title': 'Family Benefits and Support',
        'country': 'UK',
        'content_type': 'benefits',
        'summary': 'Overview of family benefits, child care support, and financial assistance available to families in the UK.',
        'key_points': [
            'Child Benefit payments',
            'Universal Credit for families',
            'Free childcare hours',
            'Maternity and paternity benefits',
            'Housing support for families'
        ],
        'application_links': [
            {'label': 'Apply for Child Benefit', 'url': 'https://www.gov.uk/child-benefit'},
            {'label': 'Universal Credit', 'url': 'https://www.gov.uk/universal-credit'}
        ],
        'source_url': 'https://www.gov.uk/browse/benefits/families',
        'metadata': {
            'topics': ['family', 'benefits', 'childcare'],
            'audience': 'families, parents',
            'last_updated': datetime.now().isoformat()
        }
    },
    {
        'title': 'Language Training Programs',
        'country': 'Canada',
        'content_type': 'education',
        'summary': 'Free language training programs for permanent residents and convention refugees to improve English or French language skills.',
        'key_points': [
            'Free language classes (LINC/CLIC)',
            'Online and in-person options',
            'Childcare provided during classes',
            'Assessment of language levels',
            'Help with finding classes near you'
        ],
        'application_links': [
            {'label': 'Find Language Classes', 'url': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/new-immigrants/new-life-canada/improve-english-french.html'}
        ],
        'source_url': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/new-immigrants/new-life-canada/improve-english-french.html',
        'metadata': {
            'topics': ['education', 'language', 'ESL', 'FSL'],
            'audience': 'permanent residents',
            'last_updated': datetime.now().isoformat()
        }
    }
]

# Add general content to database
for content_data in sample_general:
    # Add empty 'content' field
    content_data['content'] = content_data['summary']  # Use summary as content
    db.save_general_content(**content_data)
    print(f"✓ Added: {content_data['title']} ({content_data['country']})")

print(f"\n{len(sample_general)} general content items added!\n")

print("="*60)
print("✅ Sample data added successfully!")
print("="*60)
print(f"\nDatabase now contains:")
print(f"  - {len(sample_visas)} visa programs")
print(f"  - {len(sample_general)} general content items")
print("\nYou can now:")
print("  1. Start Streamlit: streamlit run app.py")
print("  2. Go to Assistant page")
print("  3. Ask questions like:")
print("     - 'What work visas are available?'")
print("     - 'Tell me about employment services in Canada'")
print("     - 'What healthcare options exist for immigrants?'")
print("     - 'What family benefits are available in the UK?'")
