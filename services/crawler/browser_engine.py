"""
Browser Crawler Engine - CORE LOGIC LAYER

Uses browser automation (Playwright) to bypass bot detection.
Follows same Engine/Fuel pattern as CrawlerEngine.

Use this when:
- Government sites block simple HTTP requests (403 errors)
- Sites require JavaScript execution
- Anti-bot protection is present
"""

from playwright.sync_api import sync_playwright, Browser, Page
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from datetime import datetime
import time
from typing import List, Dict, Set, Optional

from shared.models import CrawledPage
from shared.logger import setup_logger
from services.crawler.repository import CrawlerRepository


class BrowserCrawlerEngine:
    """
    Browser-based crawling logic using Playwright.

    Responsibilities:
    - Launch browser and navigate pages
    - Extract content from rendered pages
    - Handle JavaScript-heavy sites
    - Bypass basic bot detection

    Does NOT:
    - Access database directly (uses repository)
    - Know about UI
    - Handle configuration loading
    """

    def __init__(self, config: dict, repository: CrawlerRepository):
        """
        Initialize browser engine.

        Args:
            config: Crawler configuration
            repository: Data access layer
        """
        self.config = config
        self.repo = repository
        self.logger = setup_logger('browser_crawler_engine')

        # Crawl state
        self.visited: Set[str] = set()
        self.to_visit: deque = deque()

        # Browser instances (initialized on demand)
        self.playwright = None
        self.browser: Optional[Browser] = None

    def __enter__(self):
        """Context manager entry - start browser"""
        self._start_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop browser"""
        self._stop_browser()

    def _start_browser(self):
        """Start Playwright browser"""
        try:
            self.playwright = sync_playwright().start()

            # Launch browser (headless mode)
            browser_config = self.config.get('browser', {})
            headless = browser_config.get('headless', True)

            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )

            self.logger.info(f"✅ Browser launched (headless={headless})")

        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            raise

    def _stop_browser(self):
        """Stop Playwright browser"""
        try:
            if self.browser:
                self.browser.close()
                self.logger.info("Browser closed")

            if self.playwright:
                self.playwright.stop()

        except Exception as e:
            self.logger.warning(f"Error stopping browser: {e}")

    def crawl_country(self, country_name: str, seed_urls: List[str]) -> Dict:
        """
        Crawl a country's immigration website using browser.

        Args:
            country_name: Country to crawl
            seed_urls: Starting URLs

        Returns:
            Crawl statistics
        """
        self.logger.info(f"Starting browser crawl for {country_name}")

        # Initialize queue
        for url in seed_urls:
            self.to_visit.append((url, 0))  # (url, depth)

        # Crawl limits
        max_pages = self.config['crawling']['max_pages_per_country']
        max_depth = self.config['crawling']['max_depth']
        delay = self.config['crawling']['delay_between_requests']

        pages_crawled = 0
        pages_saved = 0

        # Create browser context (simulates real user)
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ignore_https_errors=True  # Bypass SSL errors for testing
        )

        try:
            while self.to_visit and pages_crawled < max_pages:
                url, depth = self.to_visit.popleft()

                # Skip if already visited or too deep
                if url in self.visited or depth > max_depth:
                    continue

                # Crawl page
                page_data = self._crawl_page(context, url, country_name, depth)

                if page_data:
                    # Save via repository
                    self.repo.save_page(page_data)
                    pages_saved += 1

                    # Add new links to queue
                    for link in page_data.links:
                        if link not in self.visited:
                            self.to_visit.append((link, depth + 1))

                    self.logger.info(f"✓ Saved: {page_data.title[:60]}")

                self.visited.add(url)
                pages_crawled += 1

                # Rate limiting
                time.sleep(delay)

        finally:
            context.close()

        self.logger.info(f"Browser crawl complete: {pages_saved}/{pages_crawled} pages saved")

        return {
            'country': country_name,
            'pages_crawled': pages_crawled,
            'pages_saved': pages_saved,
            'urls_queued': len(self.to_visit)
        }

    def _crawl_page(self, context, url: str, country: str, depth: int) -> Optional[CrawledPage]:
        """
        Fetch and parse a single page using browser.

        Args:
            context: Browser context
            url: URL to crawl
            country: Country name
            depth: Current crawl depth

        Returns:
            CrawledPage or None if failed
        """
        try:
            self.logger.info(f"Crawling (depth {depth}): {url}")

            # Create new page
            page = context.new_page()

            try:
                # Navigate to URL with timeout
                timeout = self.config['crawling'].get('timeout', 30) * 1000  # Convert to ms
                page.goto(url, wait_until='domcontentloaded', timeout=timeout)

                # Wait a bit for dynamic content
                page.wait_for_timeout(2000)  # 2 seconds

                # Get page content
                html_content = page.content()

                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract title
                title = soup.title.string if soup.title else url
                title = title.strip()

                # Extract text content
                # Remove script and style elements
                for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                    script.decompose()

                text_content = soup.get_text(separator=' ', strip=True)

                # Check if relevant
                if not self._is_relevant(text_content, title):
                    self.logger.info(f"Skipping non-relevant page: {title}")
                    return None

                # Extract links
                links = self._extract_links(soup, url)

                # Create CrawledPage model
                crawled_page = CrawledPage(
                    url=url,
                    country=country,
                    title=title,
                    content=text_content[:50000],  # Limit to 50k chars
                    html=html_content[:100000],  # Limit HTML to 100k chars
                    links=links,
                    crawled_at=datetime.now(),
                    status='success',
                    depth=depth,
                    metadata={'method': 'browser', 'user_agent': 'Chrome/120'}
                )

                return crawled_page

            finally:
                page.close()

        except Exception as e:
            self.logger.error(f"Failed to crawl {url}: {e}")
            return None

    def _is_relevant(self, content: str, title: str) -> bool:
        """
        Check if page content is relevant to immigration/visas.

        Args:
            content: Page text content
            title: Page title

        Returns:
            True if relevant
        """
        keywords = self.config.get('keywords', [
            'visa', 'immigration', 'permit', 'residence',
            'eligibility', 'requirements', 'application',
            'skilled', 'worker', 'student'
        ])

        # Combine title and first 1000 chars of content
        text_to_check = (title + ' ' + content[:1000]).lower()

        # Check if any keyword appears
        return any(keyword.lower() in text_to_check for keyword in keywords)

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract and filter relevant links from page.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links

        Returns:
            List of absolute URLs
        """
        links = []
        base_domain = urlparse(base_url).netloc

        for link in soup.find_all('a', href=True):
            href = link['href']

            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)

            # Parse URL
            parsed = urlparse(absolute_url)

            # Filter criteria
            if (
                parsed.scheme in ['http', 'https'] and  # Valid scheme
                parsed.netloc == base_domain and  # Same domain
                not any(exc in absolute_url for exc in self.config.get('exclude_patterns', [])) and  # Not excluded
                absolute_url not in links  # No duplicates
            ):
                links.append(absolute_url)

        return links[:50]  # Limit to 50 links per page
