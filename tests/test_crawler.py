"""
Test Crawler Functionality
"""

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from services.crawler.spider import ImmigrationCrawler
from shared.database import DataStore
import yaml

def test_crawler_components():
    """Test individual crawler components"""

    print("Testing Crawler Components...")
    print("=" * 60)

    # Load config
    with open('services/crawler/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Create crawler instance
    countries = [{'name': 'TestCountry', 'seed_urls': ['http://example.com']}]
    crawler = ImmigrationCrawler(countries, config)

    # Test keyword relevance
    relevant_text = "This page contains information about visa requirements and immigration"
    irrelevant_text = "This is just a regular page about nothing specific"

    assert crawler.is_relevant(relevant_text), "Should detect relevant keywords"
    assert not crawler.is_relevant(irrelevant_text), "Should reject irrelevant content"
    print("✅ Keyword filtering works")

    # Test URL exclusion
    excluded_url = "https://example.com/news/article"
    normal_url = "https://example.com/visas/info"

    assert crawler.should_exclude(excluded_url), "Should exclude news URLs"
    assert not crawler.should_exclude(normal_url), "Should not exclude visa URLs"
    print("✅ URL exclusion works")

    # Test data extraction with sample HTML
    sample_html = """
    <html>
    <head><title>Visa Information Page</title></head>
    <body>
        <nav aria-label="breadcrumb">
            <a href="/">Home</a>
            <a href="/visas">Visas</a>
        </nav>
        <main>
            <h1>Skilled Worker Visa Requirements</h1>
            <p>Information about visa requirements, eligibility, and application process.</p>
            <a href="/visas/skilled-worker">More info</a>
            <a href="/documents/form.pdf">Application Form (PDF)</a>
        </main>
    </body>
    </html>
    """

    page_data = crawler.extract_page_data(
        'http://example.com/visa-info',
        sample_html,
        'TestCountry',
        0
    )

    assert page_data['title'] == 'Visa Information Page', "Should extract title"
    assert isinstance(page_data['breadcrumbs'], list), "Should have breadcrumbs list"
    assert 'visa' in page_data['content_text'].lower(), "Should extract content"
    assert len(page_data['attachments']) > 0, "Should find PDF attachment"
    assert page_data['attachments'][0]['type'] == 'pdf', "Should identify PDF type"
    print("✅ Data extraction works")

    # Test data storage
    data_store = DataStore()
    data_store.save_raw_page('TestCountry', page_data)

    loaded_pages = data_store.load_raw_pages('TestCountry')
    assert len(loaded_pages) > 0, "Should save and load pages"
    print("✅ Data storage works")

    print("\n" + "=" * 60)
    print("🎉 All crawler components working correctly!")
    print("\nNote: Real website crawling may be blocked by 403 errors.")
    print("This is common with government sites. For production:")
    print("  - Use official APIs when available")
    print("  - Request permission for crawling")
    print("  - Use more sophisticated scraping techniques")
    print("  - Consider using Selenium for JavaScript-heavy sites")

if __name__ == '__main__':
    test_crawler_components()
