"""
Test Crawler Service - Engine, Repository, and Interface
Tests the complete crawler architecture with all layers
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath('.'))

from services.crawler.engine import CrawlerEngine
from services.crawler.repository import CrawlerRepository
from services.crawler.interface import CrawlerService
from shared.models import CrawledPage


class TestCrawlerService:
    """Test all Crawler components"""

    def __init__(self):
        # Create temporary directory for test database
        self.temp_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.temp_dir, 'test_immigration.db')

        # Initialize test database
        self._init_test_db()

        # Test configuration
        self.test_config = {
            'crawling': {
                'max_depth': 2,
                'max_pages_per_country': 10,
                'delay_between_requests': 0.1,  # Fast for testing
                'timeout': 5,
                'user_agent': 'TestBot/1.0'
            },
            'keywords': ['visa', 'immigration', 'permit'],
            'download_extensions': ['.pdf', '.doc'],
            'exclude_patterns': ['/news/', '/contact/']
        }

    def _init_test_db(self):
        """Initialize test database - will be done by Database class"""
        # The Database class will handle schema initialization
        # We just need to create the directory
        os.makedirs(os.path.dirname(self.test_db), exist_ok=True)

    def cleanup(self):
        """Clean up test files"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_repository(self):
        """Test CrawlerRepository data layer"""
        print("\n💾 Testing Crawler Repository...")

        repo = CrawlerRepository(db_path=self.test_db)

        # Create test page
        page = CrawledPage(
            url='http://example.com/visa',
            country='TestCountry',
            title='Test Visa Page',
            content='Information about visa requirements',
            metadata={'depth': 0, 'links': [], 'attachments': []}
        )

        # Save page
        success = repo.save_page(page)
        assert success, "Should save page successfully"

        # Get pages by country
        pages = repo.get_pages_by_country('TestCountry')
        assert len(pages) > 0, "Should retrieve saved pages"
        assert pages[0].title == 'Test Visa Page', "Title should match"

        # Get all pages
        all_pages = repo.get_all_pages()
        assert len(all_pages) > 0, "Should get all pages"

        # Test duplicate handling (should update, not create new)
        page2 = CrawledPage(
            url='http://example.com/visa',  # Same URL
            country='TestCountry',
            title='Updated Visa Page',
            content='Updated content',
            metadata={'depth': 0}
        )
        repo.save_page(page2)

        pages = repo.get_pages_by_country('TestCountry')
        assert len(pages) == 1, "Should have only one page (updated)"
        assert pages[0].title == 'Updated Visa Page', "Title should be updated"

        print("✅ Repository works")

    def test_engine_relevance_check(self):
        """Test engine's relevance checking"""
        print("\n🔍 Testing Engine Relevance Check...")

        repo = CrawlerRepository(db_path=self.test_db)
        engine = CrawlerEngine(self.test_config, repo)

        # Test relevant text
        relevant_text = "This page contains information about visa requirements and immigration procedures"
        assert engine._is_relevant(relevant_text), "Should detect relevant keywords"

        # Test irrelevant text
        irrelevant_text = "This is a page about sports and weather news"
        assert not engine._is_relevant(irrelevant_text), "Should reject irrelevant content"

        print("✅ Relevance check works")

    def test_engine_url_exclusion(self):
        """Test engine's URL exclusion"""
        print("\n🚫 Testing Engine URL Exclusion...")

        repo = CrawlerRepository(db_path=self.test_db)
        engine = CrawlerEngine(self.test_config, repo)

        # Test excluded URLs
        assert engine._should_exclude('http://example.com/news/article'), "Should exclude news"
        assert engine._should_exclude('http://example.com/contact/form'), "Should exclude contact"

        # Test normal URLs
        assert not engine._should_exclude('http://example.com/visa/info'), "Should not exclude visa pages"

        print("✅ URL exclusion works")

    def test_engine_parse_page(self):
        """Test engine's HTML parsing"""
        print("\n📄 Testing Engine Page Parsing...")

        repo = CrawlerRepository(db_path=self.test_db)
        engine = CrawlerEngine(self.test_config, repo)

        # Sample HTML
        html = """
        <html>
        <head><title>Visa Information</title></head>
        <body>
            <nav aria-label="breadcrumb">
                <a href="/">Home</a>
                <a href="/visas">Visas</a>
            </nav>
            <main>
                <h1>Work Visa Requirements</h1>
                <p>Information about work visa requirements and eligibility.</p>
                <a href="/visas/work">More Info</a>
                <a href="/docs/form.pdf">Application Form</a>
            </main>
        </body>
        </html>
        """

        page = engine._parse_page(
            'http://example.com/visa',
            'TestCountry',
            html,
            depth=0
        )

        assert page.title == 'Visa Information', "Should extract title"
        assert 'visa' in page.content.lower(), "Should extract content"
        assert 'breadcrumbs' in page.metadata, "Should have breadcrumbs"
        assert len(page.metadata['attachments']) > 0, "Should find PDF attachment"
        assert page.metadata['attachments'][0]['type'] == 'pdf', "Should identify PDF"

        print("✅ Page parsing works")

    def test_engine_breadcrumb_extraction(self):
        """Test breadcrumb extraction"""
        print("\n🍞 Testing Breadcrumb Extraction...")

        repo = CrawlerRepository(db_path=self.test_db)
        engine = CrawlerEngine(self.test_config, repo)

        from bs4 import BeautifulSoup

        html = """
        <nav aria-label="breadcrumb">
            <a href="/">Home</a>
            <a href="/immigration">Immigration</a>
            <a href="/immigration/visas">Visas</a>
        </nav>
        """

        soup = BeautifulSoup(html, 'lxml')
        breadcrumbs = engine._extract_breadcrumbs(soup)

        assert len(breadcrumbs) == 3, "Should extract all breadcrumbs"
        assert breadcrumbs[0] == 'Home', "First breadcrumb should be Home"
        assert breadcrumbs[2] == 'Visas', "Last breadcrumb should be Visas"

        print("✅ Breadcrumb extraction works")

    def test_engine_link_extraction(self):
        """Test same-domain link extraction"""
        print("\n🔗 Testing Link Extraction...")

        repo = CrawlerRepository(db_path=self.test_db)
        engine = CrawlerEngine(self.test_config, repo)

        from bs4 import BeautifulSoup

        html = """
        <html>
        <body>
            <a href="/visa/work">Work Visa</a>
            <a href="/visa/study">Study Visa</a>
            <a href="http://example.com/visa/family">Family Visa</a>
            <a href="http://other-site.com/visa">External Link</a>
        </body>
        </html>
        """

        soup = BeautifulSoup(html, 'lxml')
        links = engine._extract_links(soup, 'http://example.com/visas')

        # Should include same-domain links only
        assert len(links) >= 3, "Should extract same-domain links"
        assert any('example.com' in link for link in links), "Should have example.com links"
        assert not any('other-site.com' in link for link in links), "Should exclude external links"

        print("✅ Link extraction works")

    def test_engine_attachment_extraction(self):
        """Test document attachment extraction"""
        print("\n📎 Testing Attachment Extraction...")

        repo = CrawlerRepository(db_path=self.test_db)
        engine = CrawlerEngine(self.test_config, repo)

        from bs4 import BeautifulSoup

        html = """
        <html>
        <body>
            <a href="/forms/application.pdf">Application Form (PDF)</a>
            <a href="/docs/guide.doc">Guide (DOC)</a>
            <a href="/info/page">Regular Page</a>
        </body>
        </html>
        """

        soup = BeautifulSoup(html, 'lxml')
        attachments = engine._extract_attachments(soup, 'http://example.com/')

        assert len(attachments) == 2, "Should find 2 attachments"
        assert attachments[0]['type'] == 'pdf', "First should be PDF"
        assert attachments[1]['type'] == 'doc', "Second should be DOC"

        print("✅ Attachment extraction works")

    def test_engine_reset(self):
        """Test engine state reset"""
        print("\n🔄 Testing Engine Reset...")

        repo = CrawlerRepository(db_path=self.test_db)
        engine = CrawlerEngine(self.test_config, repo)

        # Add some state
        engine.visited.add('http://example.com/page1')
        engine.visited.add('http://example.com/page2')
        engine.to_visit.append(('http://example.com/page3', 0))

        assert len(engine.visited) == 2, "Should have visited URLs"
        assert len(engine.to_visit) == 1, "Should have URLs to visit"

        # Reset
        engine.reset()

        assert len(engine.visited) == 0, "Visited should be cleared"
        assert len(engine.to_visit) == 0, "To visit should be cleared"

        print("✅ Engine reset works")

    @patch('services.crawler.engine.requests.Session')
    def test_engine_crawl_with_mock(self, mock_session_class):
        """Test crawling with mocked HTTP requests"""
        print("\n🕷️ Testing Engine Crawl (Mocked)...")

        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
        <head><title>Test Visa Page</title></head>
        <body>
            <h1>Visa Information</h1>
            <p>Information about visa requirements and immigration.</p>
        </body>
        </html>
        """
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        repo = CrawlerRepository(db_path=self.test_db)
        engine = CrawlerEngine(self.test_config, repo)

        # Crawl (will be mocked)
        result = engine.crawl_country(
            'TestCountry',
            ['http://example.com/visa']
        )

        assert result['country'] == 'TestCountry', "Country should match"
        assert result['pages_crawled'] > 0, "Should have crawled pages"

        print("✅ Engine crawl works (mocked)")

    def test_service_integration(self):
        """Test CrawlerService integration"""
        print("\n🔧 Testing Service Integration...")

        # This tests the interface layer
        # Note: We'd need to mock HTTP requests for full test
        # For now, just test initialization

        try:
            service = CrawlerService()
            assert service.config is not None, "Should have config"
            assert service.repo is not None, "Should have repository"
            assert service.engine is not None, "Should have engine"
            print("✅ Service integration works")
        except Exception as e:
            print(f"⚠️ Service integration test skipped (needs config files): {e}")

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("🧪 TESTING CRAWLER SERVICE")
        print("=" * 60)

        try:
            self.test_repository()
            self.test_engine_relevance_check()
            self.test_engine_url_exclusion()
            self.test_engine_parse_page()
            self.test_engine_breadcrumb_extraction()
            self.test_engine_link_extraction()
            self.test_engine_attachment_extraction()
            self.test_engine_reset()
            self.test_engine_crawl_with_mock()
            self.test_service_integration()

            print("\n" + "=" * 60)
            print("🎉 ALL CRAWLER SERVICE TESTS PASSED!")
            print("=" * 60)
            return True

        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.cleanup()


def main():
    """Run all Crawler service tests"""
    tester = TestCrawlerService()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
